#include "common.hpp"
#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>
#include <cstdint>
namespace nb=nanobind;
namespace s=tllib::binder_spike;
NB_MODULE(_spike_nanobind,m) {
  nb::class_<s::Value>(m,"Value")
    .def(nb::init<std::string>())
    .def_prop_ro("text",[](const s::Value& value){return value.text;});
  nb::enum_<s::State>(m,"State").value("ready",s::State::ready).value("blocked",s::State::blocked);
  m.def("state_name",&s::state_name,nb::arg("state"));
  m.def("error_details",[](const std::string& id){
    auto parsed=tllib::core::FeatureId::parse(id);
    if(parsed)throw std::invalid_argument("Expected invalid ID in error fixture");
    const auto& error=*parsed.error_if();
    nb::dict details;
    details["code"]="INVALID_IDENTIFIER";
    details["message"]=error.message;
    details["feature_id"]=nb::none();
    details["specs_provenance"]=nb::none();
    details["context"]=nb::dict();
    return details;
  },nb::arg("invalid_id"));
  m.def("canonical",&s::canonical,nb::arg("text"));
  m.def("buffer_address",[](nb::ndarray<nb::numpy,double,nb::c_contig> a)->std::uintptr_t {
    return reinterpret_cast<std::uintptr_t>(a.data());
  },nb::arg("array").noconvert());
  m.def("call_provider",[](nb::callable callback)->nb::object {
    return callback("demo",nb::bytes("payload"));
  });
}
