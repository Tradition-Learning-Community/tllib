#pragma once
#include <tllib/core/identity.hpp>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <utility>
namespace tllib::binder_spike {
struct Value {
  std::string text;
  explicit Value(std::string input):text(std::move(input)){}
};
enum class State { ready, blocked };
inline std::string state_name(State s) {return s==State::ready?"ready":"blocked";}
inline std::string canonical(std::string input) {
  auto parsed=tllib::core::FeatureId::parse(input);
  if(!parsed)throw std::invalid_argument("INVALID_IDENTIFIER");
  return parsed.value_if()->str();
}
} // namespace tllib::binder_spike
