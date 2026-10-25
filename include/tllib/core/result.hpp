#pragma once
#include <optional>
#include <string>
#include <type_traits>
#include <utility>
#include <variant>
namespace tllib::core {
enum class ErrorCode { invalid_argument, invalid_identifier, unsupported_version, invalid_shape,
                       out_of_range, invalid_domain, unavailable_capability, internal_error };
struct Error {
  ErrorCode code;
  std::string message;
  std::optional<std::string> feature_id;
  std::optional<std::string> provenance;
};
template <class T> class [[nodiscard]] Result {
  static_assert(!std::is_reference_v<T> && !std::is_void_v<T>);
 public:
  Result(T value) : storage_(std::in_place_index<0>, std::move(value)) {}
  Result(Error error) : storage_(std::in_place_index<1>, std::move(error)) {}
  [[nodiscard]] bool has_value() const noexcept { return storage_.index() == 0; }
  [[nodiscard]] explicit operator bool() const noexcept { return has_value(); }
  [[nodiscard]] const T* value_if() const noexcept { return std::get_if<0>(&storage_); }
  [[nodiscard]] const Error* error_if() const noexcept { return std::get_if<1>(&storage_); }
 private:
  std::variant<T, Error> storage_;
};
inline Error invalid(std::string message) { return {ErrorCode::invalid_argument, std::move(message), {}, {}}; }
} // namespace tllib::core
