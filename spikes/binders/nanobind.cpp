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
  m.def("canonical",&s::canonical,nb::arg("text"));
  m.def("buffer_address",[](nb::ndarray<nb::numpy,double,nb::c_contig> a)->std::uintptr_t {
    return reinterpret_cast<std::uintptr_t>(a.data());
  },nb::arg("array").noconvert());
  m.def("call_provider",[](nb::callable callback)->nb::object {
    return callback("demo",nb::bytes("payload"));
  });
}
