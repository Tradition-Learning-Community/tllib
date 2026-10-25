#pragma once
#include <tllib/core/result.hpp>
#include <string>
#include <string_view>
#include <utility>

namespace tllib::core {
class FeatureId {
 public:
  static Result<FeatureId> parse(std::string_view source) {
    constexpr std::string_view prefix = "TLC-FC-";
    if (!source.starts_with(prefix)) return invalid();
    const auto rest = source.substr(prefix.size());
    if (rest.size() < 7 || !digit(rest[0]) || !digit(rest[1]) || rest[2] != '-') return invalid();
    const auto tail = rest.rfind('-');
    if (tail == std::string_view::npos || tail <= 3 || tail + 4 != rest.size()) return invalid();
    for (std::size_t i = 3; i < tail; ++i) {
      const char c = rest[i];
      if (!((c >= 'A' && c <= 'Z') || c == '-' || (c >= '0' && c <= '9'))) return invalid();
    }
    for (std::size_t i = tail + 1; i < rest.size(); ++i) if (!digit(rest[i])) return invalid();
    return FeatureId(std::string(source));
  }
  [[nodiscard]] const std::string& str() const noexcept { return value_; }
  friend bool operator==(const FeatureId&, const FeatureId&) = default;
 private:
  explicit FeatureId(std::string value) : value_(std::move(value)) {}
  static bool digit(char c) noexcept { return c >= '0' && c <= '9'; }
  static Error invalid() { return {ErrorCode::invalid_identifier, "Invalid TLC-FC feature identifier", {}, {}}; }
  std::string value_;
};

class DomainId {
 public:
  static Result<DomainId> parse(std::string_view source) {
    if (source.empty()) return invalid();
    bool previous_dash = true;
    for (char c : source) {
      if (c == '-') { if (previous_dash) return invalid(); previous_dash = true; }
      else { if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9'))) return invalid(); previous_dash = false; }
    }
    if (previous_dash) return invalid();
    return DomainId(std::string(source));
  }
  [[nodiscard]] const std::string& str() const noexcept { return value_; }
  friend bool operator==(const DomainId&, const DomainId&) = default;
 private:
  explicit DomainId(std::string value) : value_(std::move(value)) {}
  static Error invalid() { return {ErrorCode::invalid_identifier, "Invalid domain identifier", {}, {}}; }
  std::string value_;
};
} // namespace tllib::core
