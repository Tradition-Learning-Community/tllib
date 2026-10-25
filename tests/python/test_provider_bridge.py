"""C++ provider port injected with actual Python callbacks (no scientific providers)."""
import gc
import threading
import time
import unittest
import weakref

from tllib import (
    CancellationSource,
    ProviderRegistration,
    ProviderRegistry,
    ProviderRequest,
    ProviderResponse,
    TllibError,
)

SHA = "a" * 40
REQUEST = ProviderRequest(
    feature_id="TLC-FC-00-MASTER-005",
    capability_id="test.cap",
    operation_id="test.operation",
    input_contract="test.input",
    payload=b"in\x00",
    specs_fingerprint=SHA,
    correlation_id="trace-1",
    interface_version="1.0.0",
)


def registration(callback=None, *, output_validation=None, input_validation=None, **overrides):
    fields = dict(
        capability_id="test.cap",
        interface_version="1.0.0",
        provider_id="test.provider",
        input_contract="test.input",
        output_contract="test.output",
        provenance="test fixture only",
        callback=callback or (lambda feature, operation, payload, corr, specs: ("test.output", b"out\x00")),
        validate_input=input_validation or (lambda value: value == b"in\x00"),
        validate_output=output_validation or (lambda value: value == b"out\x00"),
        concurrent_safe=False,
    )
    fields.update(overrides)
    return ProviderRegistration(**fields)


def expect_code(case, error, code):
    case.assertEqual(error.exception.code, code)
    case.assertEqual(error.exception.feature_id, REQUEST.feature_id)
    case.assertEqual(error.exception.specs_provenance, SHA)
    case.assertIsInstance(error.exception.context, dict)


class NativeProviderTests(unittest.TestCase):
    def test_real_native_call_and_bytes(self):
        seen = []

        def callback(feature, operation, payload, correlation, fingerprint):
            seen.append((feature, operation, payload, correlation, fingerprint))
            return "test.output", b"out\x00"

        registry = ProviderRegistry([registration(callback)])
        self.assertEqual(registry.invoke(REQUEST), ProviderResponse("test.output", b"out\x00"))
        self.assertEqual(seen, [(REQUEST.feature_id, REQUEST.operation_id, b"in\x00", "trace-1", SHA)])

    def test_absent_and_version_mismatch(self):
        with self.assertRaises(TllibError) as missing:
            ProviderRegistry([]).invoke(REQUEST)
        expect_code(self, missing, "PROVIDER_REQUIRED")

        bad = ProviderRequest(**{**vars(REQUEST), "interface_version": "2.0.0"})
        with self.assertRaises(TllibError) as incompatible:
            ProviderRegistry([registration()]).invoke(bad)
        expect_code(self, incompatible, "PROVIDER_INCOMPATIBLE")

    def test_duplicate_and_invalid_registration(self):
        entry = registration()
        with self.assertRaises(TllibError) as duplicate:
            ProviderRegistry([entry, entry])
        self.assertEqual(duplicate.exception.code, "DUPLICATE_PROVIDER")
        with self.assertRaises(TypeError):
            ProviderRegistry([registration(callback=42)])
        with self.assertRaises(TllibError):
            ProviderRegistry([registration(input_contract="")])
        with self.assertRaises(TllibError):
            ProviderRegistry([registration(interface_version="01.0.0")])

    def test_input_and_output_validation(self):
        called = []
        registry = ProviderRegistry([registration(lambda *args: (called.append(1), ("test.output", b"out\x00"))[1])])
        invalid_request = ProviderRequest(**{**vars(REQUEST), "payload": b"bad"})
        with self.assertRaises(TllibError) as bad_input:
            registry.invoke(invalid_request)
        expect_code(self, bad_input, "INVALID_PROVIDER_INPUT")
        self.assertEqual(called, [])
        with self.assertRaises(TllibError) as bad_output:
            ProviderRegistry([registration(output_validation=lambda value: False)]).invoke(REQUEST)
        expect_code(self, bad_output, "INVALID_PROVIDER_OUTPUT")
        with self.assertRaises(TllibError) as bad_contract:
            ProviderRegistry([registration(lambda *args: ("wrong.contract", b"out\x00"))]).invoke(REQUEST)
        expect_code(self, bad_contract, "INVALID_PROVIDER_OUTPUT")
        with self.assertRaises(TllibError) as malformed:
            ProviderRegistry([registration(lambda *args: {"payload": b"out\x00"})]).invoke(REQUEST)
        expect_code(self, malformed, "INVALID_PROVIDER_OUTPUT")
        with self.assertRaises(TllibError) as dishonest_validator:
            ProviderRegistry([registration(input_validation=lambda value: "yes")]).invoke(REQUEST)
        expect_code(self, dishonest_validator, "INVALID_PROVIDER_INPUT")

    def test_callback_exception_has_no_secret_leakage(self):
        def boom(*args):
            raise RuntimeError("SENSITIVE-DO-NOT-LOG")
        with self.assertRaises(TllibError) as failed:
            ProviderRegistry([registration(boom)]).invoke(REQUEST)
        expect_code(self, failed, "OUTCOME_INDETERMINATE")
        self.assertNotIn("SENSITIVE-DO-NOT-LOG", str(failed.exception))
        self.assertIn("reconciliation_required", failed.exception.context.values())

    def test_cancelled_before_call(self):
        called = []
        source = CancellationSource()
        self.assertTrue(source.request_stop())
        self.assertFalse(source.request_stop())
        with self.assertRaises(TllibError) as cancelled:
            ProviderRegistry([registration(lambda *args: called.append(1))]).invoke(REQUEST, cancellation=source)
        expect_code(self, cancelled, "CANCELLED")
        self.assertEqual(called, [])

    def test_timeout_before_call(self):
        with self.assertRaises(TllibError) as expired:
            ProviderRegistry([registration()]).invoke(REQUEST, timeout_ms=0)
        expect_code(self, expired, "TIMEOUT")
        with self.assertRaises(ValueError):
            ProviderRegistry([registration()]).invoke(REQUEST, timeout_ms=-1)
        with self.assertRaises(TypeError):
            ProviderRegistry([registration()]).invoke(REQUEST, timeout_ms=True)

    def test_cancel_after_callback_starts_is_indeterminate(self):
        entered, proceed = threading.Event(), threading.Event()
        source = CancellationSource()

        def slow(*args):
            entered.set()
            if not proceed.wait(5):
                raise RuntimeError("test deadlock")
            return "test.output", b"out\x00"

        registry = ProviderRegistry([registration(slow)])
        outcomes = []

        def runner():
            try:
                outcomes.append(registry.invoke(REQUEST, cancellation=source))
            except TllibError as err:
                outcomes.append(err)

        thread = threading.Thread(target=runner)
        thread.start()
        try:
            self.assertTrue(entered.wait(5), "Python callback did not run")
            source.request_stop()
        finally:
            proceed.set()
            thread.join(5)
        self.assertFalse(thread.is_alive(), "callback deadlocked on GIL")
        self.assertEqual(len(outcomes), 1)
        self.assertIsInstance(outcomes[0], TllibError)
        self.assertEqual(outcomes[0].code, "OUTCOME_INDETERMINATE")

    def test_non_concurrent_provider_busy(self):
        entered, proceed = threading.Event(), threading.Event()

        def slow(*args):
            entered.set()
            if not proceed.wait(5):
                raise RuntimeError("test deadlock")
            return "test.output", b"out\x00"

        registry = ProviderRegistry([registration(slow)])
        answers = []
        thread = threading.Thread(target=lambda: answers.append(registry.invoke(REQUEST)))
        thread.start()
        try:
            self.assertTrue(entered.wait(5))
            with self.assertRaises(TllibError) as busy:
                registry.invoke(REQUEST)
            expect_code(self, busy, "PROVIDER_BUSY")
        finally:
            proceed.set()
            thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(answers, [ProviderResponse("test.output", b"out\x00")])

    def test_callback_lifetime_owned_by_native_registry(self):
        class Callback:
            def __call__(self, *args):
                return "test.output", b"out\x00"

        callback = Callback()
        weak = weakref.ref(callback)
        entry = registration(callback)
        registry = ProviderRegistry([entry])
        del callback, entry
        gc.collect()
        self.assertIsNotNone(weak())
        self.assertEqual(registry.invoke(REQUEST).payload, b"out\x00")
        del registry
        gc.collect()
        self.assertIsNone(weak(), "native registry leaked Python callback")

    def test_schema_and_fingerprint_fail_before_callback(self):
        seen = []
        registry = ProviderRegistry([registration(lambda *args: seen.append(1))])
        invalid = ProviderRequest(**{**vars(REQUEST), "feature_id": "invalid"})
        with self.assertRaises(TllibError):
            registry.invoke(invalid)
        invalid = ProviderRequest(**{**vars(REQUEST), "specs_fingerprint": "invalid"})
        with self.assertRaises(TllibError):
            registry.invoke(invalid)
        self.assertEqual(seen, [])

    def test_no_implicit_autoregistration(self):
        registry = ProviderRegistry([])
        with self.assertRaises(TllibError):
            registry.invoke(REQUEST)
        with self.assertRaises(TypeError):
            ProviderRegistry(["test.cap"])


if __name__ == "__main__":
    unittest.main()
