#pragma once
#include <tllib/core/identity.hpp>
#include <tllib/runtime/execution_context.hpp>
#include <atomic>
#include <functional>
#include <map>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <utility>

namespace tllib::providers {
class CapabilityId {
 public:
  static core::Result<CapabilityId> parse(std::string_view text) {
    if(text.empty()) return core::invalid("Capability identifier cannot be empty");
    for(unsigned char c : text) if(c < 0x21 || c == 0x7f)
      return core::invalid("Capability identifier contains control or whitespace");
    return CapabilityId(std::string(text));
  }
  const std::string& str() const noexcept {return id_;}
  friend bool operator==(const CapabilityId&,const CapabilityId&)=default;
 private:
  explicit CapabilityId(std::string value):id_(std::move(value)){}
  std::string id_;
};
struct ProviderDescriptor {
  CapabilityId capability;
  core::Version interface_version;
  std::string provider_id;
  std::string input_contract;
  std::string output_contract;
  std::string provenance;
  bool concurrent_safe{false};
};
struct ProviderRequest {
  core::FeatureId feature_id;
  CapabilityId capability;
  std::string operation_id;
  std::string input_contract;
  std::string payload;
  std::string specs_fingerprint;
  std::string correlation_id;
};
struct ProviderResponse {
  std::string output_contract;
  std::string payload;
};
class Provider {
 public:
  virtual ~Provider() = default;
  virtual core::Result<ProviderResponse> invoke(const ProviderRequest& request,
                                                const runtime::ExecutionContext& context) const = 0;
};
using PayloadValidator=std::function<bool(std::string_view)>;
struct ProviderRegistration {
  ProviderDescriptor descriptor;
  std::shared_ptr<const Provider> implementation;
  PayloadValidator input_validator;
  PayloadValidator output_validator;
};
class ProviderRegistry {
  struct Slot {
    ProviderRegistration registration;
    std::shared_ptr<std::atomic_flag> active=std::make_shared<std::atomic_flag>();
  };
 public:
  class Builder {
   public:
    core::Result<bool> add(ProviderRegistration registration) {
      if(frozen_) return failure("PROVIDER_REGISTRY_FROZEN","Provider registry was frozen");
      auto& d=registration.descriptor;
      if(d.provider_id.empty() || d.input_contract.empty() || d.output_contract.empty() ||
         d.provenance.empty() || !registration.implementation || !registration.input_validator || !registration.output_validator)
        return failure("INVALID_PROVIDER_DESCRIPTOR","Provider requires identity, contracts, provenance, ownership and validators");
      if(slots_.contains(d.capability.str()))return failure("DUPLICATE_PROVIDER","Capability already registered");
      const std::string key=d.capability.str();
      slots_.emplace(key,Slot{std::move(registration),std::make_shared<std::atomic_flag>()});
      return true;
    }
    core::Result<ProviderRegistry> freeze() {
      if(frozen_)return failure("PROVIDER_REGISTRY_FROZEN","Provider registry was already frozen");
      frozen_=true;
      return ProviderRegistry(std::move(slots_));
    }
   private:
    bool frozen_{false};
    std::map<std::string,Slot> slots_;
  };
  [[nodiscard]] const ProviderDescriptor* find(const CapabilityId& id) const noexcept {
    const auto it=slots_.find(id.str());
    return it==slots_.end()?nullptr:&it->second.registration.descriptor;
  }
  [[nodiscard]] core::Result<ProviderResponse> invoke(const ProviderRequest& request,
      const core::Version& expected_interface, const runtime::ExecutionContext& context) const {
    auto fail=[&](std::string code,std::string message) -> core::Error {
      return {core::ErrorCode::unavailable_capability,std::move(message),request.feature_id.str(),
              request.specs_fingerprint,{{"capability",request.capability.str()},{"correlation_id",request.correlation_id}},std::move(code)};
    };
    if(auto e=context.check()) {
      e->feature_id=request.feature_id.str();e->provenance=request.specs_fingerprint;
      return *e;
    }
    const auto it=slots_.find(request.capability.str());
    if(it==slots_.end())return fail("PROVIDER_REQUIRED","Required capability has no registered provider");
    const auto& slot=it->second;
    const auto& d=slot.registration.descriptor;
    if(d.interface_version!=expected_interface || request.input_contract!=d.input_contract ||
       request.operation_id.empty() || request.specs_fingerprint.empty())
      return fail("PROVIDER_INCOMPATIBLE","Provider interface or request contract differs");
    if(!d.concurrent_safe && slot.active->test_and_set(std::memory_order_acquire))
      return fail("PROVIDER_BUSY","Non-concurrent provider is already executing");
    struct Guard {
      std::shared_ptr<std::atomic_flag> flag;
      bool release;
      ~Guard(){if(release)flag->clear(std::memory_order_release);}
    } guard{slot.active,!d.concurrent_safe};
    try {
      if(!slot.registration.input_validator(request.payload))
        return fail("INVALID_PROVIDER_INPUT","Provider input failed declared validation");
      auto response=slot.registration.implementation->invoke(request,context);
      if(auto e=context.after_external_call()) {
        e->feature_id=request.feature_id.str();e->provenance=request.specs_fingerprint;
        return *e;
      }
      if(!response) {
        auto e=*response.error_if();
        e.feature_id=request.feature_id.str();e.provenance=request.specs_fingerprint;
        if(!e.stable_code)e.stable_code="PROVIDER_EXECUTION_FAILED";
        return e;
      }
      const auto& data=*response.value_if();
      if(data.output_contract!=d.output_contract || !slot.registration.output_validator(data.payload))
        return fail("INVALID_PROVIDER_OUTPUT","Provider response failed declared validation");
      return data;
    } catch (...) {
      return fail("OUTCOME_INDETERMINATE","Provider callback threw; external effects are unknown and require reconciliation");
    }
  }
 private:
  explicit ProviderRegistry(std::map<std::string,Slot> slots):slots_(std::move(slots)){}
  static core::Error failure(std::string code,std::string message) {
    return {core::ErrorCode::unavailable_capability,std::move(message),{}, {}, {},std::move(code)};
  }
  std::map<std::string,Slot> slots_;
};
} // namespace tllib::providers
