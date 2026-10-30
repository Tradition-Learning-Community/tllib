#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "python_version.hpp"
#include <tllib/providers/provider.hpp>
#include <tllib/core/array_view.hpp>
#include <array>
#include <cstdint>
#include <limits>
#include <span>
#include <tllib/runtime/execution_context.hpp>
#include <chrono>
#include <memory>
#include <new>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace {
using tllib::core::Error;
using tllib::core::Result;
namespace p=tllib::providers;
namespace r=tllib::runtime;
constexpr const char* registry_capsule="tllib.native.ProviderRegistry";
constexpr const char* cancellation_capsule="tllib.native.CancellationSource";
PyObject* error_class=nullptr;

class OwnedCallable {
 public:
  explicit OwnedCallable(PyObject* object):object_(object){Py_INCREF(object_);}
  ~OwnedCallable(){
    if(Py_IsInitialized()){
      const auto gil=PyGILState_Ensure();
      Py_DECREF(object_);
      PyGILState_Release(gil);
    }
  }
  OwnedCallable(const OwnedCallable&)=delete;
  OwnedCallable& operator=(const OwnedCallable&)=delete;
  PyObject* get() const noexcept {return object_;}
 private:
  PyObject* object_;
};
using Callable=std::shared_ptr<OwnedCallable>;
struct GIL {
  GIL():state_(PyGILState_Ensure()){}
  ~GIL(){PyGILState_Release(state_);}
  GIL(const GIL&)=delete;
  GIL& operator=(const GIL&)=delete;
 private:
  PyGILState_STATE state_;
};
bool text_field(PyObject* dict,const char* key,std::string& output){
  PyObject* item=PyDict_GetItemString(dict,key);
  if(!item || !PyUnicode_Check(item)){
    PyErr_Format(PyExc_TypeError,"%s must be a string",key);
    return false;
  }
  Py_ssize_t size=0;
  const char* data=PyUnicode_AsUTF8AndSize(item,&size);
  if(!data)return false;
  output.assign(data,static_cast<std::size_t>(size));
  if(output.find('\0')!=std::string::npos){
    PyErr_Format(PyExc_ValueError,"%s cannot contain NUL",key);
    return false;
  }
  return true;
}
bool callable_field(PyObject* dict,const char* key,Callable& output){
  PyObject* item=PyDict_GetItemString(dict,key);
  if(!item || !PyCallable_Check(item)){
    PyErr_Format(PyExc_TypeError,"%s must be callable",key);
    return false;
  }
  output=std::make_shared<OwnedCallable>(item);
  return true;
}
bool payload_field(PyObject* dict,const char* key,std::string& output){
  PyObject* item=PyDict_GetItemString(dict,key);
  if(!item || !PyBytes_Check(item)){
    PyErr_Format(PyExc_TypeError,"%s must be bytes",key);
    return false;
  }
  output.assign(PyBytes_AS_STRING(item),static_cast<std::size_t>(PyBytes_GET_SIZE(item)));
  return true;
}
Error callback_failure(){
  return {tllib::core::ErrorCode::unavailable_capability,
    "Python provider callback failed; reconcile effects before retry",
    {},{},{{"retry","reconciliation_required"}},"OUTCOME_INDETERMINATE"};
}
class PythonProvider final: public p::Provider {
 public:
  explicit PythonProvider(Callable callback):callback_(std::move(callback)){}
  Result<p::ProviderResponse> invoke(const p::ProviderRequest& req,
                                      const r::ExecutionContext&) const override {
    GIL gil;
    PyObject* args=PyTuple_New(5);
    if(!args){PyErr_Clear();return callback_failure();}
    PyObject* parts[]={
      PyUnicode_FromStringAndSize(req.feature_id.str().data(),static_cast<Py_ssize_t>(req.feature_id.str().size())),
      PyUnicode_FromStringAndSize(req.operation_id.data(),static_cast<Py_ssize_t>(req.operation_id.size())),
      PyBytes_FromStringAndSize(req.payload.data(),static_cast<Py_ssize_t>(req.payload.size())),
      PyUnicode_FromStringAndSize(req.correlation_id.data(),static_cast<Py_ssize_t>(req.correlation_id.size())),
      PyUnicode_FromStringAndSize(req.specs_fingerprint.data(),static_cast<Py_ssize_t>(req.specs_fingerprint.size()))
    };
    for(int i=0;i<5;++i) {
      if(!parts[i]) {
        for(int j=0;j<5;++j)Py_XDECREF(parts[j]);
        Py_DECREF(args);PyErr_Clear();return callback_failure();
      }
      PyTuple_SET_ITEM(args,i,parts[i]); // steals reference
    }
    PyObject* result=PyObject_CallObject(callback_->get(),args);
    Py_DECREF(args);
    if(!result){PyErr_Clear();return callback_failure();}
    const bool valid=PyTuple_Check(result) && PyTuple_GET_SIZE(result)==2 &&
      PyUnicode_Check(PyTuple_GET_ITEM(result,0)) && PyBytes_Check(PyTuple_GET_ITEM(result,1));
    if(!valid){
      Py_DECREF(result);
      return Error{tllib::core::ErrorCode::invalid_argument,
        "Python provider must return (output_contract: str, payload: bytes)",
        {},{},{},"INVALID_PROVIDER_OUTPUT"};
    }
    PyObject* label=PyTuple_GET_ITEM(result,0);
    PyObject* bytes=PyTuple_GET_ITEM(result,1);
    Py_ssize_t size=0;
    const char* str=PyUnicode_AsUTF8AndSize(label,&size);
    if(!str){Py_DECREF(result);PyErr_Clear();return callback_failure();}
    p::ProviderResponse response{
      std::string(str,static_cast<std::size_t>(size)),
      std::string(PyBytes_AS_STRING(bytes),static_cast<std::size_t>(PyBytes_GET_SIZE(bytes)))};
    Py_DECREF(result);
    return response;
  }
 private:
  Callable callback_;
};
p::PayloadValidator validator(Callable callback){
  return [callback=std::move(callback)](std::string_view payload)->bool {
    GIL gil;
    PyObject* arg=PyBytes_FromStringAndSize(payload.data(),static_cast<Py_ssize_t>(payload.size()));
    if(!arg){PyErr_Clear();return false;}
    PyObject* answer=PyObject_CallOneArg(callback->get(),arg);
    Py_DECREF(arg);
    if(!answer){PyErr_Clear();return false;}
    // Boolean contract: never silently coerce arbitrary Python objects.
    const bool valid=PyBool_Check(answer);
    const bool accepted=valid && answer==Py_True;
    Py_DECREF(answer);
    return accepted;
  };
}
PyObject* set_error(const Error& error){
  if(!error_class){PyErr_SetString(PyExc_RuntimeError,"Native provider error class unavailable");return nullptr;}
  PyObject* instance=PyObject_CallFunction(error_class,"s",error.message.c_str());
  if(!instance)return nullptr;
  const auto generic_code=[](tllib::core::ErrorCode category)->std::string {
    switch(category){
      case tllib::core::ErrorCode::invalid_argument:return "INVALID_ARGUMENT";
      case tllib::core::ErrorCode::invalid_identifier:return "INVALID_IDENTIFIER";
      case tllib::core::ErrorCode::unsupported_version:return "UNSUPPORTED_VERSION";
      case tllib::core::ErrorCode::invalid_shape:return "INVALID_SHAPE";
      case tllib::core::ErrorCode::out_of_range:return "OUT_OF_RANGE";
      case tllib::core::ErrorCode::invalid_domain:return "INVALID_DOMAIN";
      case tllib::core::ErrorCode::unavailable_capability:return "UNAVAILABLE_CAPABILITY";
      case tllib::core::ErrorCode::internal_error:return "INTERNAL_ERROR";
    }
    return "INTERNAL_ERROR";
  };
  const std::string code=error.stable_code.value_or(generic_code(error.code));
  auto attr=[&](const char* key,PyObject* obj)->bool {
    if(!obj)return false;
    const int status=PyObject_SetAttrString(instance,key,obj);
    Py_DECREF(obj);return status==0;
  };
  PyObject* ctx=PyDict_New();
  if(!ctx){Py_DECREF(instance);return nullptr;}
  for(const auto& [key,value]:error.context){
    PyObject* val=PyUnicode_FromStringAndSize(value.data(),static_cast<Py_ssize_t>(value.size()));
    if(!val || PyDict_SetItemString(ctx,key.c_str(),val)<0){
      Py_XDECREF(val);Py_DECREF(ctx);Py_DECREF(instance);return nullptr;
    }
    Py_DECREF(val);
  }
  PyObject* feature=error.feature_id?PyUnicode_FromString(error.feature_id->c_str()):Py_NewRef(Py_None);
  PyObject* provenance=error.provenance?PyUnicode_FromString(error.provenance->c_str()):Py_NewRef(Py_None);
  const bool ok=attr("code",PyUnicode_FromString(code.c_str()))&&
    attr("feature_id",feature)&&attr("specs_provenance",provenance)&&attr("context",ctx);
  if(!ok){Py_DECREF(instance);return nullptr;}
  PyErr_SetObject(error_class,instance);
  Py_DECREF(instance);
  return nullptr;
}
void registry_destroy(PyObject* capsule){
  void* data=PyCapsule_GetPointer(capsule,registry_capsule);
  if(data)delete static_cast<p::ProviderRegistry*>(data);
  else PyErr_Clear();
}
void cancellation_destroy(PyObject* capsule){
  void* data=PyCapsule_GetPointer(capsule,cancellation_capsule);
  if(data)delete static_cast<r::CancellationSource*>(data);
  else PyErr_Clear();
}
PyObject* create_registry(PyObject*,PyObject* args){
  PyObject* items=nullptr;
  if(!PyArg_ParseTuple(args,"O",&items))return nullptr;
  PyObject* seq=PySequence_Fast(items,"registrations must be a finite sequence");
  if(!seq)return nullptr;
  p::ProviderRegistry::Builder builder;
  const Py_ssize_t count=PySequence_Fast_GET_SIZE(seq);
  for(Py_ssize_t i=0;i<count;++i){
    PyObject* item=PySequence_Fast_GET_ITEM(seq,i);
    if(!PyDict_Check(item)){
      Py_DECREF(seq);PyErr_SetString(PyExc_TypeError,"registration must be a dict");return nullptr;
    }
    std::string cid,version,id,input,output,provenance;
    Callable callback,input_check,output_check;
    if(!text_field(item,"capability_id",cid) || !text_field(item,"interface_version",version) ||
      !text_field(item,"provider_id",id) || !text_field(item,"input_contract",input) ||
      !text_field(item,"output_contract",output) || !text_field(item,"provenance",provenance) ||
      !callable_field(item,"callback",callback) ||
      !callable_field(item,"validate_input",input_check) ||
      !callable_field(item,"validate_output",output_check)){
      Py_DECREF(seq);return nullptr;
    }
    PyObject* safety=PyDict_GetItemString(item,"concurrent_safe");
    if(safety && !PyBool_Check(safety)){
      Py_DECREF(seq);PyErr_SetString(PyExc_TypeError,"concurrent_safe must be bool");return nullptr;
    }
    auto cap=p::CapabilityId::parse(cid);
    auto ver=tllib::core::Version::parse(version);
    if(!cap || !ver){
      Py_DECREF(seq);return set_error(!cap?*cap.error_if():*ver.error_if());
    }
    p::ProviderRegistration registration{{
      *cap.value_if(),*ver.value_if(),std::move(id),std::move(input),std::move(output),
      std::move(provenance),safety==Py_True},
      std::make_shared<PythonProvider>(std::move(callback)),
      validator(std::move(input_check)),validator(std::move(output_check))};
    auto inserted=builder.add(std::move(registration));
    if(!inserted){Py_DECREF(seq);return set_error(*inserted.error_if());}
  }
  Py_DECREF(seq);
  auto frozen=builder.freeze();
  if(!frozen)return set_error(*frozen.error_if());
  auto* owner=new p::ProviderRegistry(*frozen.value_if());
  PyObject* capsule=PyCapsule_New(owner,registry_capsule,registry_destroy);
  if(!capsule)delete owner;
  return capsule;
}
PyObject* new_source(PyObject*,PyObject*){
  auto* ptr=new r::CancellationSource();
  PyObject* capsule=PyCapsule_New(ptr,cancellation_capsule,cancellation_destroy);
  if(!capsule)delete ptr;
  return capsule;
}
PyObject* request_stop(PyObject*,PyObject* args){
  PyObject* obj=nullptr;
  if(!PyArg_ParseTuple(args,"O",&obj))return nullptr;
  auto* ptr=static_cast<r::CancellationSource*>(PyCapsule_GetPointer(obj,cancellation_capsule));
  if(!ptr)return nullptr;
  if(ptr->request_stop())Py_RETURN_TRUE;
  Py_RETURN_FALSE;
}
PyObject* invoke(PyObject*,PyObject* args){
  PyObject *owner=nullptr,*request=nullptr,*settings=nullptr;
  if(!PyArg_ParseTuple(args,"OOO",&owner,&request,&settings))return nullptr;
  auto* registry=static_cast<p::ProviderRegistry*>(PyCapsule_GetPointer(owner,registry_capsule));
  if(!registry)return nullptr;
  if(!PyDict_Check(request)||!PyDict_Check(settings)){
    PyErr_SetString(PyExc_TypeError,"request and context must be dictionaries");return nullptr;
  }
  std::string feature,capability,operation,input_contract,payload,snapshot,correlation,version;
  if(!text_field(request,"feature_id",feature) ||
     !text_field(request,"capability_id",capability) ||
     !text_field(request,"operation_id",operation) ||
     !text_field(request,"input_contract",input_contract) ||
     !payload_field(request,"payload",payload) ||
     !text_field(request,"specs_fingerprint",snapshot) ||
     !text_field(request,"correlation_id",correlation) ||
     !text_field(request,"interface_version",version))return nullptr;
  auto fid=tllib::core::FeatureId::parse(feature);
  auto cap=p::CapabilityId::parse(capability);
  auto ver=tllib::core::Version::parse(version);
  auto fingerprint=tllib::core::Fingerprint::parse(snapshot);
  if(!fid)return set_error(*fid.error_if());
  if(!cap)return set_error(*cap.error_if());
  if(!ver)return set_error(*ver.error_if());
  if(!fingerprint)return set_error(*fingerprint.error_if());
  p::ProviderRequest req{*fid.value_if(),*cap.value_if(),std::move(operation),
    std::move(input_contract),std::move(payload),std::move(snapshot),std::move(correlation)};
  r::ExecutionContext context;
  PyObject* token=PyDict_GetItemString(settings,"source");
  if(token && token!=Py_None){
    auto* source=static_cast<r::CancellationSource*>(PyCapsule_GetPointer(token,cancellation_capsule));
    if(!source)return nullptr;
    context.cancellation=source->token();
  }
  PyObject* timeout=PyDict_GetItemString(settings,"timeout_ms");
  if(timeout && timeout!=Py_None){
    if(!PyLong_Check(timeout) || PyBool_Check(timeout)){
      PyErr_SetString(PyExc_TypeError,"timeout_ms must be a nonnegative integer");return nullptr;
    }
    const long long ms=PyLong_AsLongLong(timeout);
    if(PyErr_Occurred())return nullptr;
    if(ms<0 || ms>86400000LL){
      PyErr_SetString(PyExc_ValueError,"timeout_ms out of range 0..86400000");return nullptr;
    }
    context.deadline=std::chrono::steady_clock::now()+std::chrono::milliseconds(ms);
  }
  std::optional<Result<p::ProviderResponse>> response;
  // Only native code runs without the GIL. PythonProvider and Python validators reacquire it.
  PyThreadState* state=PyEval_SaveThread();
  try{response.emplace(registry->invoke(req,*ver.value_if(),context));}
  catch(...){response.emplace(callback_failure());}
  PyEval_RestoreThread(state);
  if(!*response)return set_error(*response->error_if());
  const auto& value=*response->value_if();
  PyObject* contract=PyUnicode_FromStringAndSize(value.output_contract.data(),
    static_cast<Py_ssize_t>(value.output_contract.size()));
  PyObject* bytes=PyBytes_FromStringAndSize(value.payload.data(),
    static_cast<Py_ssize_t>(value.payload.size()));
  if(!contract || !bytes){Py_XDECREF(contract);Py_XDECREF(bytes);return nullptr;}
  PyObject* pair=PyTuple_Pack(2,contract,bytes);
  Py_DECREF(contract);Py_DECREF(bytes);
  return pair;
}
// No C++ exception may cross the CPython extension boundary.
using NativeEntry=PyObject* (*)(PyObject*,PyObject*);
PyObject* guarded(NativeEntry entry,PyObject* self,PyObject* args){
  try{return entry(self,args);}
  catch(const std::bad_alloc&){return PyErr_NoMemory();}
  catch(...){
    PyErr_SetString(PyExc_RuntimeError,"Native provider bridge failed");
    return nullptr;
  }
}
PyObject* safe_create_registry(PyObject* self,PyObject* args){return guarded(create_registry,self,args);}
PyObject* safe_invoke(PyObject* self,PyObject* args){return guarded(invoke,self,args);}
PyObject* safe_new_source(PyObject* self,PyObject* args){return guarded(new_source,self,args);}
PyObject* safe_request_stop(PyObject* self,PyObject* args){return guarded(request_stop,self,args);}
PyObject* safe_inspect_buffer(PyObject* self,PyObject* args){return guarded(inspect_buffer,self,args);}
PyObject* native_version(PyObject*,PyObject*){return PyUnicode_FromString(TLLIB_PACKAGE_VERSION);}

struct BufferLease final {
  Py_buffer buffer{};
  bool held=false;
  explicit BufferLease(PyObject* source) {
    held=PyObject_GetBuffer(source,&buffer,PyBUF_FORMAT|PyBUF_STRIDES)==0;
  }
  ~BufferLease(){if(held)PyBuffer_Release(&buffer);}
  BufferLease(const BufferLease&)=delete;
  BufferLease& operator=(const BufferLease&)=delete;
};

// Only borrows a numeric Python buffer during this synchronous call.
// No pointer or ArrayView survives the PyBuffer_Release at function exit.
PyObject* inspect_buffer(PyObject*,PyObject* args) {
  PyObject* source=nullptr;
  if(!PyArg_ParseTuple(args,"O",&source))return nullptr;
  BufferLease lease(source);
  const auto fail=[](const char* message,const char* code)->PyObject* {
    return set_error(Error{tllib::core::ErrorCode::invalid_argument,message,{},{},{},code});
  };
  if(!lease.held) {PyErr_Clear();return fail("Object does not export a buffer","NOT_A_BUFFER");}
  const auto& b=lease.buffer;
  if(b.ndim<1 || b.ndim>2 || !b.shape)
    return fail("Only 1D/2D numeric buffers are supported","INVALID_SHAPE");
  if(b.len<0 || b.itemsize<=0)
    return fail("Invalid buffer size","INVALID_BUFFER");
  if(PyBuffer_IsContiguous(&lease.buffer,'A')!=1)
    return fail("Buffer is not contiguous; explicit user copy is required","NON_CONTIGUOUS_BUFFER");
  tllib::core::DType dtype{};
  const std::string_view format=b.format?b.format:"";
  const char* dtype_name=nullptr;
  if((format=="i" || format=="@i" || format=="=i") && b.itemsize==4) {
    dtype=tllib::core::DType::int32;dtype_name="int32";
  }else if((format=="d" || format=="@d" || format=="=d") && b.itemsize==8) {
    dtype=tllib::core::DType::float64;dtype_name="float64";
  }else return fail("Unsupported or non-native numeric buffer dtype","UNSUPPORTED_DTYPE");
  std::array<std::size_t,2> shape{};
  std::array<std::ptrdiff_t,2> strides{};
  for(int i=0;i<b.ndim;++i){
    if(b.shape[i]<0)return fail("Negative dimension","INVALID_SHAPE");
    shape[static_cast<std::size_t>(i)]=static_cast<std::size_t>(b.shape[i]);
    if(b.strides)strides[static_cast<std::size_t>(i)]=static_cast<std::ptrdiff_t>(b.strides[i]);
  }
  if(!b.strides){
    std::size_t next=static_cast<std::size_t>(b.itemsize);
    for(int i=b.ndim-1;i>=0;--i) {
      if(next>static_cast<std::size_t>(std::numeric_limits<std::ptrdiff_t>::max()))
        return fail("Implicit stride overflow","SHAPE_OVERFLOW");
      strides[static_cast<std::size_t>(i)]=static_cast<std::ptrdiff_t>(next);
      if(shape[static_cast<std::size_t>(i)]>0 &&
         next>std::numeric_limits<std::size_t>::max()/shape[static_cast<std::size_t>(i)])
        return fail("Implicit stride overflow","SHAPE_OVERFLOW");
      next*=shape[static_cast<std::size_t>(i)];
    }
  }
  const std::size_t rank=static_cast<std::size_t>(b.ndim);
  const std::size_t nbytes=static_cast<std::size_t>(b.len);
  tllib::core::Result<tllib::core::ArrayView> checked =
      b.readonly ? tllib::core::ArrayView::create(
        std::span<const std::byte>(reinterpret_cast<const std::byte*>(b.buf),nbytes),
        0,dtype,std::span(shape.data(),rank),std::span(strides.data(),rank))
      : tllib::core::ArrayView::create_mutable(
        std::span<std::byte>(reinterpret_cast<std::byte*>(b.buf),nbytes),
        0,dtype,std::span(shape.data(),rank),std::span(strides.data(),rank));
  if(!checked)return set_error(*checked.error_if());
  PyObject* dimensions=PyTuple_New(b.ndim);
  PyObject* steps=PyTuple_New(b.ndim);
  if(!dimensions || !steps){Py_XDECREF(dimensions);Py_XDECREF(steps);return nullptr;}
  for(int i=0;i<b.ndim;++i){
    PyObject* dim=PyLong_FromSize_t(shape[static_cast<std::size_t>(i)]);
    PyObject* step=PyLong_FromLongLong(static_cast<long long>(strides[static_cast<std::size_t>(i)]));
    if(!dim || !step){Py_XDECREF(dim);Py_XDECREF(step);Py_DECREF(dimensions);Py_DECREF(steps);return nullptr;}
    PyTuple_SET_ITEM(dimensions,i,dim);PyTuple_SET_ITEM(steps,i,step);
  }
  PyObject* result=PyDict_New();
  if(!result){Py_DECREF(dimensions);Py_DECREF(steps);return nullptr;}
  const auto put=[&](const char* key,PyObject* value)->bool {
    if(!value)return false;
    const int rc=PyDict_SetItemString(result,key,value);
    Py_DECREF(value);return rc==0;
  };
  const char* layout=checked.value_if()->layout()==tllib::core::Layout::row_major?"row_major":
    checked.value_if()->layout()==tllib::core::Layout::column_major?"column_major":"strided";
  const bool ok=put("dtype",PyUnicode_FromString(dtype_name)) &&
    put("shape",dimensions) && put("strides",steps) &&
    put("layout",PyUnicode_FromString(layout)) &&
    put("readonly",PyBool_FromLong(b.readonly)) &&
    put("address",PyLong_FromUnsignedLongLong(static_cast<unsigned long long>(
      reinterpret_cast<std::uintptr_t>(b.buf)))) &&
    put("nbytes",PyLong_FromSize_t(nbytes)) &&
    put("zero_copy",PyBool_FromLong(1));
  if(!ok){Py_DECREF(result);return nullptr;}
  return result;
}


PyMethodDef methods[]={
  {"inspect_buffer",safe_inspect_buffer,METH_VARARGS,"Inspect a borrowed contiguous numeric buffer; no copy."},
  {"native_version",native_version,METH_NOARGS,"Version of the compiled C++ package."},
  {"create_provider_registry",safe_create_registry,METH_VARARGS,"Freeze explicit native provider registrations."},
  {"invoke_provider",safe_invoke,METH_VARARGS,"Invoke native provider with structured errors."},
  {"new_cancellation_source",safe_new_source,METH_NOARGS,"Create cooperative cancellation source."},
  {"request_stop",safe_request_stop,METH_VARARGS,"Request cooperative cancellation."},
  {nullptr,nullptr,0,nullptr}
};
PyModuleDef definition={PyModuleDef_HEAD_INIT,"_native","Narrow native provider bridge; no science.",-1,methods,nullptr,nullptr,nullptr,nullptr};
} // namespace
PyMODINIT_FUNC PyInit__native(){
  PyObject* module=PyModule_Create(&definition);
  if(!module)return nullptr;
  error_class=PyErr_NewException("tllib._native.TllibError",PyExc_Exception,nullptr);
  if(!error_class){Py_DECREF(module);return nullptr;}
  if(PyModule_AddObject(module,"TllibError",error_class)<0){
    Py_DECREF(error_class);Py_DECREF(module);return nullptr;
  }
  return module;
}
