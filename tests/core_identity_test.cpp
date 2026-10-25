#include <tllib/core/identity.hpp>
#include <cassert>
#include <string>

int main() {
  using namespace tllib::core;
  auto id = FeatureId::parse("TLC-FC-16-COHORT-002");
  assert(id && id.value_if()->str() == "TLC-FC-16-COHORT-002");
  assert(!FeatureId::parse("TLC-FC-16-cohort-002"));
  assert(!FeatureId::parse("TLC-FC-16-COHORT-2"));
  assert(!FeatureId::parse("TLC-FC-16-COHORT-002-extra"));
  assert(!FeatureId::parse(""));
  auto domain = DomainId::parse("low-data-architecture");
  assert(domain && domain.value_if()->str() == "low-data-architecture");
  assert(!DomainId::parse("Low--Data"));
  auto error = FeatureId::parse("invalid");
  assert(error.error_if() && error.error_if()->code == ErrorCode::invalid_identifier);
  Result<int> numeric(42);
  assert(numeric.value_if() && *numeric.value_if() == 42);
  Result<int> failed(Error{ErrorCode::invalid_domain, "bad", std::string("TLC-FC-16-COHORT-002"), {}});
  assert(!failed && failed.error_if()->feature_id.has_value());
}
