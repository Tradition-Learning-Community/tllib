#pragma once
#include <tllib/core/result.hpp>
#include <chrono>
#include <map>
#include <functional>
#include <memory>
#include <optional>
#include <stop_token>
#include <string>
#include <utility>

namespace tllib::runtime {
// An executor is caller-owned. The core never starts threads or schedules work implicitly.
struct Executor {
  virtual ~Executor() = default;
  virtual void submit(std::function<void()> work) = 0;
};
struct CancellationSource {
  [[nodiscard]] std::stop_token token() const noexcept { return source_.get_token(); }
  bool request_stop() noexcept { return source_.request_stop(); }
 private:
  std::stop_source source_;
};
struct ExecutionContext {
  std::stop_token cancellation{};
  std::optional<std::chrono::steady_clock::time_point> deadline{};
  std::shared_ptr<Executor> executor{};
  std::map<std::string,std::string> options{};
  std::string correlation_id{};
  [[nodiscard]] std::optional<core::Error> check() const {
    if(cancellation.stop_requested())
      return core::Error{core::ErrorCode::unavailable_capability,"Operation cancelled",{}, {},{}, "CANCELLED"};
    if(deadline && std::chrono::steady_clock::now()>=*deadline)
      return core::Error{core::ErrorCode::unavailable_capability,"Deadline elapsed",{}, {},{}, "TIMEOUT"};
    return {};
  }
  [[nodiscard]] std::optional<core::Error> after_external_call() const {
    if(cancellation.stop_requested() ||
       (deadline && std::chrono::steady_clock::now()>=*deadline))
      return core::Error{core::ErrorCode::unavailable_capability,
        "External provider effects may have occurred; reconcile before retry",{}, {},
        {{"retry","reconciliation_required"}}, "OUTCOME_INDETERMINATE"};
    return {};
  }
};
} // namespace tllib::runtime
