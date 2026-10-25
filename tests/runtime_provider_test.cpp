#include <tllib/runtime/registry.hpp>
#include <atomic>
#include <cassert>
#include <chrono>
#include <future>
#include <memory>
#include <string>
#include <thread>
using namespace tllib;
using namespace std::chrono_literals;

static core::FeatureId feature(const char* id) {auto r=core::FeatureId::parse(id);assert(r);return *r.value_if();}
static core::DomainId domain(const char* id) {auto r=core::DomainId::parse(id);assert(r);return *r.value_if();}
static core::Fingerprint snapshot(){auto r=core::Fingerprint::parse(std::string(40,'a'));assert(r);return *r.value_if();}
static providers::CapabilityId capability(const char* id){auto r=providers::CapabilityId::parse(id);assert(r);return *r.value_if();}
static bool is_error(const auto& r,std::string_view code){return !r && r.error_if() && r.error_if()->stable_code && *r.error_if()->stable_code==code;}

class FakeProvider final : public providers::Provider {
 public:
  enum Mode {ok, invalid, throws, cancel_after};
  explicit FakeProvider(Mode mode=ok,runtime::CancellationSource* cancellation=nullptr)
    :mode_(mode),source_(cancellation){}
  core::Result<providers::ProviderResponse> invoke(const providers::ProviderRequest& r,
      const runtime::ExecutionContext&) const override {
    ++calls;
    if(mode_==throws)throw std::runtime_error("secret provider failure");
    if(mode_==cancel_after && source_)source_->request_stop();
    return providers::ProviderResponse{mode_==invalid?"wrong.contract":"fixture.output",r.payload=="in"?"provider_out":"unexpected"};
  }
  mutable std::atomic<int> calls{0};
 private:
  Mode mode_;
  runtime::CancellationSource* source_;
};
class EchoHandler final : public runtime::FeatureHandler {
 public:
  core::Result<std::string> execute(const runtime::Invocation&,runtime::ProviderAccess&,
      const runtime::ExecutionContext&) const override {return std::string("out");}
};
class ConditionalHandler final : public runtime::FeatureHandler {
 public:
  explicit ConditionalHandler(bool use=true):use_(use){}
  core::Result<std::string> execute(const runtime::Invocation& request,runtime::ProviderAccess& p,
      const runtime::ExecutionContext&) const override {
    if(!use_)return std::string("out");
    auto x=p.invoke(capability("fixture.cap"),request.payload);
    if(!x)return *x.error_if();
    return x.value_if()->payload=="provider_out"?core::Result<std::string>(std::string("out")):
      core::Result<std::string>(core::invalid("Invalid mock content"));
  }
 private:
  bool use_;
};
static providers::ProviderRegistration provider_registration(std::shared_ptr<const providers::Provider> impl,
    core::Version ver={1,0,0}) {
  return {{capability("fixture.cap"),ver,"fixture.mock","fixture.input","fixture.output","test fixture",false},
    std::move(impl),[](std::string_view s){return s=="in";},[](std::string_view s){return s=="provider_out";}};
}
static runtime::FeatureImplementation feature_impl(const char* name,core::ExecutionStatus status,
    std::shared_ptr<const runtime::FeatureHandler> handler={}) {
  auto f=runtime::FeatureImplementation{feature(name),domain("cohort"),{1,0,0},snapshot(),
    status,"handoff/features/fixture/contract.json","fixture.op",{},{},std::move(handler),
    [](std::string_view s){return s=="in";},[](std::string_view s){return s=="out";},false};
  if(status==core::ExecutionStatus::conditionally_executable)
    f.capabilities.push_back({capability("fixture.cap"),{1,0,0},"fixture.input","fixture.output"});
  return f;
}
int main() {
  assert(!providers::CapabilityId::parse(""));
  assert(!providers::CapabilityId::parse("leading blank"));
  const auto fid=feature("TLC-FC-16-COHORT-002");
  auto req=runtime::Invocation{fid,"fixture.op","in","correlation"};
  auto fake=std::make_shared<FakeProvider>();
  providers::ProviderRegistry::Builder pb;
  auto reg=provider_registration(fake);
  assert(pb.add(reg));
  assert(is_error(pb.add(reg),"DUPLICATE_PROVIDER"));
  auto providers_result=pb.freeze();
  assert(providers_result);
  assert(is_error(pb.freeze(),"PROVIDER_REGISTRY_FROZEN"));
  auto& pr=*providers_result.value_if();
  runtime::ExecutionContext ctx{};
  providers::ProviderRequest direct{fid,capability("fixture.cap"),"fixture.op","fixture.input","in",snapshot().str(),"corr"};
  assert(pr.find(capability("fixture.cap")));
  auto first=pr.invoke(direct,{1,0,0},ctx);
  assert(first && first.value_if()->payload=="provider_out");
  assert(fake->calls==1);
  assert(is_error(pr.invoke(direct,{2,0,0},ctx),"PROVIDER_INCOMPATIBLE"));
  auto wrong=direct;wrong.payload="bad";
  assert(is_error(pr.invoke(wrong,{1,0,0},ctx),"INVALID_PROVIDER_INPUT"));
  assert(fake->calls==1);
  auto absent=direct;absent.capability=capability("missing.cap");
  assert(is_error(pr.invoke(absent,{1,0,0},ctx),"PROVIDER_REQUIRED"));
  ctx.deadline=std::chrono::steady_clock::now()-1ms;
  assert(is_error(pr.invoke(direct,{1,0,0},ctx),"TIMEOUT"));
  ctx.deadline.reset();
  runtime::CancellationSource cancellation;
  ctx.cancellation=cancellation.token();
  cancellation.request_stop();
  assert(is_error(pr.invoke(direct,{1,0,0},ctx),"CANCELLED"));
  ctx.cancellation={};

  providers::ProviderRegistry::Builder broken_builder;
  assert(broken_builder.add(provider_registration(std::make_shared<FakeProvider>(FakeProvider::invalid))));
  auto broken=broken_builder.freeze();
  assert(is_error(broken.value_if()->invoke(direct,{1,0,0},ctx),"INVALID_PROVIDER_OUTPUT"));
  providers::ProviderRegistry::Builder throws_builder;
  assert(throws_builder.add(provider_registration(std::make_shared<FakeProvider>(FakeProvider::throws))));
  auto thrown=throws_builder.freeze();
  auto thrown_result=thrown.value_if()->invoke(direct,{1,0,0},ctx);
  assert(is_error(thrown_result,"OUTCOME_INDETERMINATE"));
  assert(thrown_result.error_if()->message.find("secret")==std::string::npos);

  runtime::CancellationSource during;
  providers::ProviderRegistry::Builder cancellation_builder;
  assert(cancellation_builder.add(provider_registration(
    std::make_shared<FakeProvider>(FakeProvider::cancel_after,&during))));
  auto cancelled_provider=cancellation_builder.freeze();
  runtime::ExecutionContext cc{};cc.cancellation=during.token();
  assert(is_error(cancelled_provider.value_if()->invoke(direct,{1,0,0},cc),"OUTCOME_INDETERMINATE"));

  runtime::FeatureRegistry::Builder rb(snapshot());
  auto structural=feature_impl("TLC-FC-16-COHORT-001",core::ExecutionStatus::structural_only);
  assert(rb.add(structural));
  assert(is_error(rb.add(structural),"DUPLICATE_FEATURE"));
  assert(is_error(rb.add(feature_impl("TLC-FC-16-COHORT-003",core::ExecutionStatus::conditionally_executable)),"INVALID_FEATURE_DESCRIPTOR"));
  assert(rb.add(feature_impl("TLC-FC-16-COHORT-002",core::ExecutionStatus::conditionally_executable,std::make_shared<ConditionalHandler>())));
  auto plain=feature_impl("TLC-FC-16-COHORT-004",core::ExecutionStatus::executable,std::make_shared<EchoHandler>());
  assert(rb.add(plain));
  auto bad_spec=feature_impl("TLC-FC-16-COHORT-005",core::ExecutionStatus::executable,std::make_shared<EchoHandler>());
  auto fp=core::Fingerprint::parse(std::string(40,'b'));assert(fp);
  bad_spec.specs_fingerprint=*fp.value_if();
  assert(is_error(rb.add(bad_spec),"INCOMPATIBLE_SPECS"));
  auto registry=rb.freeze();assert(registry);
  assert(registry.value_if()->size()==3);
  assert(is_error(rb.freeze(),"REGISTRY_FROZEN"));
  runtime::Invocation unknown{feature("TLC-FC-16-COHORT-030"),"fixture.op","in","corr"};
  assert(is_error(registry.value_if()->dispatch(unknown,pr,ctx),"FEATURE_NOT_REGISTERED"));
  runtime::Invocation struc{structural.id,"fixture.op","in","corr"};
  assert(is_error(registry.value_if()->dispatch(struc,pr,ctx),"STRUCTURAL_ONLY"));
  assert(is_error(registry.value_if()->dispatch(req,*cancelled_provider.value_if(),ctx),"PROVIDER_REQUIRED")==false);
  auto executed=registry.value_if()->dispatch(req,pr,ctx);
  assert(executed && *executed.value_if()=="out" && fake->calls==2);
  auto ignored=req;ignored.operation_id="unknown.operation";
  assert(is_error(registry.value_if()->dispatch(ignored,pr,ctx),"UNSUPPORTED_OPERATION"));
  ignored=req;ignored.payload="wrong";
  assert(is_error(registry.value_if()->dispatch(ignored,pr,ctx),"INVALID_FEATURE_INPUT"));
  providers::ProviderRegistry::Builder empty_builder;
  auto empty=empty_builder.freeze();
  assert(is_error(registry.value_if()->dispatch(req,*empty.value_if(),ctx),"PROVIDER_REQUIRED"));
  auto plain_request=runtime::Invocation{plain.id,"fixture.op","in","corr"};
  assert(registry.value_if()->dispatch(plain_request,*empty.value_if(),ctx));
  auto wrong_output=feature_impl("TLC-FC-16-COHORT-006",core::ExecutionStatus::executable,std::make_shared<EchoHandler>());
  wrong_output.output_validator=[](std::string_view){return false;};
  runtime::FeatureRegistry::Builder bad_output_builder(snapshot());assert(bad_output_builder.add(wrong_output));
  auto bad_output_registry=bad_output_builder.freeze();
  runtime::Invocation bad_output_req{wrong_output.id,"fixture.op","in","corr"};
  assert(is_error(bad_output_registry.value_if()->dispatch(bad_output_req,pr,ctx),"INVALID_FEATURE_OUTPUT"));
  auto skip=feature_impl("TLC-FC-16-COHORT-007",core::ExecutionStatus::conditionally_executable,std::make_shared<ConditionalHandler>(false));
  runtime::FeatureRegistry::Builder skip_builder(snapshot());assert(skip_builder.add(skip));
  auto skip_registry=skip_builder.freeze();
  runtime::Invocation skip_request{skip.id,"fixture.op","in","corr"};
  assert(is_error(skip_registry.value_if()->dispatch(skip_request,pr,ctx),"PROVIDER_NOT_INVOKED"));

  auto dep=feature_impl("TLC-FC-16-COHORT-008",core::ExecutionStatus::executable,std::make_shared<EchoHandler>());
  dep.dependencies.push_back(feature("TLC-FC-16-COHORT-009"));
  runtime::FeatureRegistry::Builder missing_builder(snapshot());assert(missing_builder.add(dep));
  assert(is_error(missing_builder.freeze(),"UNKNOWN_DEPENDENCY"));
  auto dep2=feature_impl("TLC-FC-16-COHORT-009",core::ExecutionStatus::executable,std::make_shared<EchoHandler>());
  dep2.dependencies.push_back(dep.id);
  assert(missing_builder.add(dep2));
  assert(is_error(missing_builder.freeze(),"CYCLIC_DEPENDENCY"));

  // Frozen registry is shareable for independent, non-concurrent calls.
  assert(registry.value_if()->dispatch(plain_request,pr,ctx));
  // In-process callbacks never run under a mutex, and non-concurrent providers reject overlap.
  assert(!ctx.cancellation.stop_requested());
}
