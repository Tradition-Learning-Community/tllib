"""Run a single, reproducible build per binder; JSON is measured, not inferred."""
import json
import pathlib
import subprocess
import sys
import time
import importlib.metadata
from datetime import datetime, timezone

build = pathlib.Path(sys.argv[1]).resolve()
data = {
    "executed_utc": datetime.now(timezone.utc).isoformat(),
    "python": sys.version,
    "nanobind": importlib.metadata.version("nanobind"),
    "pybind11": importlib.metadata.version("pybind11"),
    "cmake": subprocess.check_output(["cmake", "--version"], text=True).splitlines()[0],
    "single_trial_not_a_cross_platform_benchmark": True,
    "builds": {},
}
for name in ("_spike_nanobind", "_spike_pybind"):
    t0 = time.perf_counter()
    subprocess.run(["cmake", "--build", str(build), "--target", name, "--parallel", "2"], check=True)
    duration = time.perf_counter() - t0
    candidates = list(build.glob(f"{name}*.so"))
    if len(candidates) != 1:
        raise RuntimeError(f"Expected one extension for {name}, got {candidates}")
    data["builds"][name] = {"seconds": duration, "binary_bytes": candidates[0].stat().st_size}
path = pathlib.Path("spikes/binders/build-results.json")
path.write_text(json.dumps(data, indent=2) + "\n")
print(json.dumps(data, indent=2), flush=True)
