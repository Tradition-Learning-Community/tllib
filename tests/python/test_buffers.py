"""Technical buffer interop tests; no TLC-FC science or implicit copies."""
import array
import gc
import unittest
import weakref

from tllib import BufferInfo, TllibError, inspect_buffer, _native


class BufferTests(unittest.TestCase):
    def test_stdlib_buffer_is_observed_without_copy(self):
        values = array.array("i", [7, 11, -2])
        metadata = inspect_buffer(values)
        self.assertIsInstance(metadata, BufferInfo)
        self.assertEqual(metadata.dtype, "int32")
        self.assertEqual(metadata.shape, (3,))
        self.assertEqual(metadata.strides, (4,))
        self.assertEqual(metadata.nbytes, 12)
        self.assertEqual(metadata.layout, "row_major")
        self.assertFalse(metadata.readonly)
        self.assertTrue(metadata.zero_copy)
        self.assertTrue(_native.same_buffer_start(values, memoryview(values)))
        self.assertFalse(hasattr(metadata, 'address'))
        self.assertEqual(list(values), [7, 11, -2])

    def test_structured_rejection_of_unsafe_objects(self):
        for value, code in [
            (object(), "NOT_A_BUFFER"),
            (b"not a numeric array", "UNSUPPORTED_DTYPE"),
            (memoryview(array.array("i", [1, 2, 3, 4]))[::2], "NON_CONTIGUOUS_BUFFER"),
            (array.array("f", [1.0]), "UNSUPPORTED_DTYPE"),
        ]:
            with self.subTest(code=code), self.assertRaises(TllibError) as error:
                inspect_buffer(value)
            self.assertEqual(error.exception.code, code)

    def test_optional_numpy_contiguous_f_readonly_and_lifetime(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("NumPy is optional and is not a runtime dependency")
        value = np.arange(6, dtype=np.int32).reshape(2, 3)
        info = inspect_buffer(value)
        self.assertEqual(info.shape, (2, 3))
        self.assertEqual(info.strides, (12, 4))
        self.assertTrue(_native.same_buffer_start(value, memoryview(value)))
        self.assertTrue(info.zero_copy)
        value.flags.writeable = False
        self.assertTrue(inspect_buffer(value).readonly)
        other = np.asfortranarray(np.arange(6, dtype=np.float64).reshape(2, 3))
        column = inspect_buffer(other)
        self.assertEqual(column.layout, "column_major")
        self.assertEqual(column.strides, (8, 16))
        self.assertTrue(_native.same_buffer_start(other, memoryview(other)))
        with self.assertRaises(TllibError) as sliced:
            inspect_buffer(other[:, ::2])
        self.assertEqual(sliced.exception.code, "NON_CONTIGUOUS_BUFFER")
        with self.assertRaises(TllibError) as invalid:
            inspect_buffer(np.array([1], dtype=np.float32))
        self.assertEqual(invalid.exception.code, "UNSUPPORTED_DTYPE")
        owned = np.array([1, 2], dtype=np.int32)
        weak = weakref.ref(owned)
        view = memoryview(owned)
        del owned
        gc.collect()
        self.assertIsNotNone(weak())
        self.assertEqual(inspect_buffer(view).dtype, "int32")
        del view
        gc.collect()
        self.assertIsNone(weak())


if __name__ == "__main__":
    unittest.main()
