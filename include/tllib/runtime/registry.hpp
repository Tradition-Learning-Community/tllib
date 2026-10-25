#pragma once
#include <tllib/providers/provider.hpp>
#include <algorithm>
#include <atomic>
#include <functional>
#include <map>
#include <memory>
#include <set>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace tllib::runtime {
struct CapabilityRequirement {
  providers::CapabilityId id;
  core::Version version;
  std::string input_contract;
  std::string output_contract;
};
struct Invocation {
  core::FeatureId feature_id;
  std::string operation_id;
  std::string payload;
  std::string correlation_id;
};
class ProviderAccess {
 public:
  ProviderAccess(const core::FeatureId& feature, std::string_view operation,
    std::string_view snapshot, std::string_view correlation,
    const std::vector<CapabilityRequirement>& declared,
    const providers::ProviderRegistry& providers,
    const ExecutionContext& context)
    :feature_(feature),operation_(operation),snapshot_(snapshot),
     correlation_(correlation),declared_(declared),providers_(providers),context_(context){}
  [[nodiscard]] core::Result<providers::ProviderResponse> invoke(
      const providers::CapabilityId& capability,std::string payload) {
    const auto it=std::find_if(declared_.begin(),declared_.end(),
      [&](const auto& d){return d.id==capability;});
    if(it==declared_.end())return error("UNDECLARED_CAPABILITY","Capability not declared by feature");
    providers::ProviderRequest req{feature_,capability,operation_,it->input_contract,
      std::move(payload),snapshot_,correlation_};
    auto result=providers_.invoke(req,it->version,context_);
    if(result)invoked_.insert(capability.str());
    return result;
  }
  [[nodiscard]] bool complete() const {
    for(const auto& d:declared_)if(!invoked_.contains(d.id.str()))return false;
    return true;
  }
 private:
  core::Error error(std::string code,std::string message) const {
    return {core::ErrorCode::unavailable_capability,std::move(message),feature_.str(),
      snapshot_,{{"correlation_id",correlation_}},std::move(code)};
  }
  core::FeatureId feature_;
  std::string operation_,snapshot_,correlation_;
  const std::vector<CapabilityRequirement>& declared_;
  const providers::ProviderRegistry& providers_;
  const ExecutionContext& context_;
  std::set<std::string> invoked_;
};
class FeatureHandler {
 public:
  virtual ~FeatureHandler()=default;
  virtual core::Result<std::string> execute(const Invocation& invocation,
      ProviderAccess& providers,const ExecutionContext& context) const=0;
};
struct FeatureImplementation {
  core::FeatureId id;
  core::DomainId domain;
  core::Version package_version;
  core::Fingerprint specs_fingerprint;
  core::ExecutionStatus execution_status;
  std::string provenance;
  std::string operation_id;
  std::vector<CapabilityRequirement> capabilities;
  std::vector<core::FeatureId> dependencies;
  std::shared_ptr<const FeatureHandler> handler;
  providers::PayloadValidator input_validator;
  providers::PayloadValidator output_validator;
  bool concurrent_safe{false};
};
struct DomainImplementation {
  core::DomainId id;
  std::vector<FeatureImplementation> features;
};
class FeatureRegistry {
  struct Slot {
    FeatureImplementation feature;
    std::shared_ptr<std::atomic_flag> active;
  };
 public:
  class Builder {
   public:
    explicit Builder(core::Fingerprint snapshot):snapshot_(std::move(snapshot)){}
    core::Result<bool> add(FeatureImplementation feature) {
      if(frozen_)return fail("REGISTRY_FROZEN","Registry frozen");
      if(feature.specs_fingerprint!=snapshot_)return fail("INCOMPATIBLE_SPECS","Feature uses a different specs snapshot");
      if(feature.provenance.empty() || feature.operation_id.empty())
        return fail("INVALID_FEATURE_DESCRIPTOR","Feature requires source provenance and operation");
      if(features_.contains(feature.id.str()))return fail("DUPLICATE_FEATURE","Duplicate TLC-FC registration");
      const bool runnable=feature.execution_status==core::ExecutionStatus::executable ||
        feature.execution_status==core::ExecutionStatus::conditionally_executable;
      if(runnable && (!feature.handler || !feature.input_validator || !feature.output_validator))
        return fail("INVALID_FEATURE_DESCRIPTOR","Runnable feature must supply implementation and validators");
      if(!runnable && feature.handler)
        return fail("INVALID_FEATURE_DESCRIPTOR","Non-executable feature cannot expose executable handler");
      if(feature.execution_status==core::ExecutionStatus::conditionally_executable && feature.capabilities.empty())
        return fail("PROVIDER_REQUIRED","Conditional feature needs declared provider capability");
      if(feature.execution_status!=core::ExecutionStatus::conditionally_executable && !feature.capabilities.empty())
        return fail("INVALID_FEATURE_DESCRIPTOR","Provider capabilities require conditional status");
      std::set<std::string> capabilities;
      for(const auto& c:feature.capabilities) {
        if(c.input_contract.empty() || c.output_contract.empty() || !capabilities.insert(c.id.str()).second)
          return fail("INVALID_FEATURE_DESCRIPTOR","Invalid or duplicate capability requirement");
      }
      std::set<std::string> deps;
      for(const auto& dep:feature.dependencies)if(dep==feature.id || !deps.insert(dep.str()).second)
        return fail("INVALID_DEPENDENCY","Self or duplicate dependency");
      const std::string id=feature.id.str();
      features_.emplace(id,Slot{std::move(feature),std::make_shared<std::atomic_flag>()});
      return true;
    }
    core::Result<bool> add(DomainImplementation domain) {
      if(frozen_)return fail("REGISTRY_FROZEN","Registry frozen");
      std::set<std::string> local;
      for(const auto& f:domain.features) {
        if(f.domain!=domain.id || features_.contains(f.id.str()) || !local.insert(f.id.str()).second)
          return fail("INVALID_DOMAIN","Domain identity or feature collision");
      }
      // Preflight with a copy avoids observable partial registration on failure.
      Builder candidate(snapshot_);
      candidate.features_=features_;
      for(auto& f:domain.features) {
        auto r=candidate.add(std::move(f));
        if(!r)return *r.error_if();
      }
      features_=std::move(candidate.features_);
      return true;
    }
    core::Result<FeatureRegistry> freeze() {
      if(frozen_)return fail("REGISTRY_FROZEN","Registry already frozen");
      for(const auto&[id,slot]:features_)for(const auto& dep:slot.feature.dependencies)
        if(!features_.contains(dep.str()))return fail("UNKNOWN_DEPENDENCY","Missing feature dependency for "+id);
      std::map<std::string,unsigned> visiting;
      std::function<bool(const std::string&)> visit=[&](const std::string& id){
        if(visiting[id]==1)return false;
        if(visiting[id]==2)return true;
        visiting[id]=1;
        for(const auto& d:features_.at(id).feature.dependencies)if(!visit(d.str()))return false;
        visiting[id]=2;return true;
      };
      for(const auto&[id,_]:features_)if(!visit(id))return fail("CYCLIC_DEPENDENCY","Feature dependency cycle");
      frozen_=true;
      return FeatureRegistry(snapshot_,std::move(features_));
    }
   private:
    static core::Error fail(std::string code,std::string message){
      return {core::ErrorCode::invalid_argument,std::move(message),{}, {},{},std::move(code)};
    }
    core::Fingerprint snapshot_;
    bool frozen_{false};
    std::map<std::string,Slot> features_;
  };
  [[nodiscard]] const FeatureImplementation* find(const core::FeatureId& id) const noexcept {
    const auto it=features_.find(id.str());return it==features_.end()?nullptr:&it->second.feature;
  }
  [[nodiscard]] std::size_t size() const noexcept {return features_.size();}
  [[nodiscard]] core::Result<std::string> dispatch(
       const Invocation& request, const providers::ProviderRegistry& provided,
       const ExecutionContext& context) const {
    auto fail=[&](std::string code,std::string message)->core::Error{
      return {core::ErrorCode::unavailable_capability,std::move(message),request.feature_id.str(),
        snapshot_.str(),{{"correlation_id",request.correlation_id}},std::move(code)};
    };
    if(auto e=context.check()){e->feature_id=request.feature_id.str();e->provenance=snapshot_.str();return *e;}
    const auto it=features_.find(request.feature_id.str());
    if(it==features_.end())return fail("FEATURE_NOT_REGISTERED","No implementation registered for TLC-FC");
    const auto& slot=it->second;
    const auto& f=slot.feature;
    if(f.execution_status==core::ExecutionStatus::structural_only)
      return fail("STRUCTURAL_ONLY","Structural descriptor cannot execute scientific operation");
    if(f.execution_status==core::ExecutionStatus::unsupported)
      return fail("FEATURE_UNSUPPORTED","Feature execution explicitly unsupported");
    if(request.operation_id!=f.operation_id)return fail("UNSUPPORTED_OPERATION","Operation is not declared by implementation");
    if(f.execution_status==core::ExecutionStatus::conditionally_executable) {
      for(const auto& required:f.capabilities) {
        const auto* d=provided.find(required.id);
        if(!d)return fail("PROVIDER_REQUIRED","Required capability not registered: "+required.id.str());
        if(d->interface_version!=required.version ||
           d->input_contract!=required.input_contract || d->output_contract!=required.output_contract)
          return fail("PROVIDER_INCOMPATIBLE","Capability interface contracts do not match");
      }
    }
    if(!f.concurrent_safe && slot.active->test_and_set(std::memory_order_acquire))
      return fail("FEATURE_BUSY","Non-concurrent handler already executing");
    struct Guard {
      std::shared_ptr<std::atomic_flag> active;
      bool enabled;
      ~Guard(){if(enabled)active->clear(std::memory_order_release);}
    } guard{slot.active,!f.concurrent_safe};
    try {
      if(!f.input_validator(request.payload))return fail("INVALID_FEATURE_INPUT","Input failed feature validation");
      ProviderAccess access(f.id,f.operation_id,snapshot_.str(),request.correlation_id,f.capabilities,provided,context);
      auto result=f.handler->execute(request,access,context);
      if(auto e=context.after_external_call()) {
        e->feature_id=f.id.str();e->provenance=snapshot_.str();return *e;
      }
      if(!result) {
        auto e=*result.error_if();e.feature_id=f.id.str();e.provenance=snapshot_.str();return e;
      }
      if(f.execution_status==core::ExecutionStatus::conditionally_executable && !access.complete())
        return fail("PROVIDER_NOT_INVOKED","Conditional feature did not use every declared provider");
      if(!f.output_validator(*result.value_if()))
        return fail("INVALID_FEATURE_OUTPUT","Feature result failed validation");
      return *result.value_if();
    } catch (...) {
      return fail("OUTCOME_INDETERMINATE","Feature callback failed; reconcile effects before retry");
    }
  }
 private:
  FeatureRegistry(core::Fingerprint snapshot,std::map<std::string,Slot> data)
    :snapshot_(std::move(snapshot)),features_(std::move(data)){}
  core::Fingerprint snapshot_;
  std::map<std::string,Slot> features_;
};
} // namespace tllib::runtime
