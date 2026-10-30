"""Compare identical native value/errors/enums/NumPy/callback/ownership surfaces."""
import gc
import importlib
import json
import resource
import subprocess
import sys
import time

def single(name):
    import numpy as np
    module=importlib.import_module(name)
    canonical="TLC-FC-00-MASTER-005"
    assert module.canonical(canonical)==canonical
    for invalid in ("invalid", "", "TLC-FC-01-A-000A"):
        try: module.canonical(invalid)
        except ValueError as error: assert "INVALID_IDENTIFIER" in str(error)
        else: raise AssertionError("Invalid identity unexpectedly accepted")
    obj=module.Value("sample")
    assert obj.text=="sample"
    assert module.state_name(module.State.ready) == 'ready'
    assert module.state_name(module.State.blocked) == 'blocked'
    assert module.State.ready != module.State.blocked
    details=module.error_details('invalid')
    assert details['code']=='INVALID_IDENTIFIER'
    assert isinstance(details['message'],str)
    assert details['feature_id'] is None
    assert details['specs_provenance'] is None
    assert details['context']=={}
    del obj
    gc.collect()
    seen=[]
    def callback(label,payload):
        seen.append((label,payload))
        return ("opaque.output",b"ok")
    assert module.call_provider(callback)==("opaque.output",b"ok")
    assert seen==[("demo",b"payload")]
    values=np.arange(12,dtype=np.float64).reshape(3,4)
    assert module.buffer_address(values)==values.__array_interface__["data"][0]
    for invalid in (np.arange(4,dtype=np.float32),values[:,::2]):
        try: module.buffer_address(invalid)
        except (TypeError,ValueError): pass
        else: raise AssertionError("Unexpected conversion (possible hidden copy)")
    def measure(function,count):
        for _ in range(500):function()
        start=time.perf_counter_ns()
        for _ in range(count):function()
        return (time.perf_counter_ns()-start)/count
    # The timed callback does not append data to the correctness-only list.
    def timed_callback(label,payload):
        return ('opaque.output',b'ok')
    measurements={
       "canonical_call_ns":measure(lambda:module.canonical(canonical),20000),
       "numpy_buffer_call_ns":measure(lambda:module.buffer_address(values),20000),
       "callback_call_ns":measure(lambda:module.call_provider(timed_callback),10000),
       "maxrss_kib_linux":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    print(json.dumps({name:measurements}))
    return 0

if __name__=="__main__":
    if len(sys.argv)>1:
        sys.exit(single(sys.argv[1]))
    all_data={}
    for name in ("_spike_nanobind","_spike_pybind"):
        result=subprocess.run([sys.executable,__file__,name],capture_output=True,text=True,check=True)
        print(result.stdout.strip())
        all_data.update(json.loads(result.stdout))
    from pathlib import Path
    Path("spikes/binders/runtime-results.json").write_text(json.dumps(all_data,indent=2)+"\n")
