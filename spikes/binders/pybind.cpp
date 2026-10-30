#include "common.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cstdint>
namespace py=pybind11;
namespace s=tllib::binder_spike;
PYBIND11_MODULE(_spike_pybind,m) {
  py::class_<s::Value>(m,"Value")
    .def(py::init<std::string>())
    .def_property_readonly("text",[](const s::Value& value){return value.text;});
  py::enum_<s::State>(m,"State").value("ready",s::State::ready).value("blocked",s::State::blocked);
  m.def("state_name",&s::state_name,py::arg("state"));
  m.def("error_details",[](const std::string& id){
    auto parsed=tllib::core::FeatureId::parse(id);
    if(parsed)throw std::invalid_argument("Expected invalid ID in error fixture");
    const auto& error=*parsed.error_if();
    py::dict details;
    details["code"]="INVALID_IDENTIFIER";
    details["message"]=error.message;
    details["feature_id"]=py::none();
    details["specs_provenance"]=py::none();
    details["context"]=py::dict();
    return details;
  },py::arg("invalid_id"));
  m.def("canonical",&s::canonical,py::arg("text"));
  m.def("buffer_address",[](py::array_t<double,py::array::c_style> a)->std::uintptr_t {
    return reinterpret_cast<std::uintptr_t>(a.data());
  },py::arg("array").noconvert());
  m.def("call_provider",[](py::function callback)->py::object {
    return callback("demo",py::bytes("payload"));
  });
}
