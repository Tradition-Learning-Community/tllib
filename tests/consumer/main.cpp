#include <tllib/build_info.hpp>
#include <tllib/core/identity.hpp>
#include <tllib/generated/feature_metadata.hpp>
#include <tllib/shared/contracts.hpp>
int main() {
  auto id=tllib::core::FeatureId::parse("TLC-FC-00-MASTER-005");
  if(!id || tllib::foundation_status.empty())return 1;
  tllib::shared::ScientificReference ref{"maths/00-master/master.md",{}, {}, {}, {}, {}};
  auto validated=tllib::shared::validate(ref);
  if(!validated)return 2;
  auto roundtrip=tllib::shared::wire::roundtrip(ref.canonical(),"TLC-HC-SCIENTIFIC-REFERENCE");
  if(!roundtrip || *roundtrip.value_if()!=ref.canonical())return 3;
  if(tllib::generated::features.empty())return 4;
  for(const auto& item:tllib::generated::features)
    if(item.feature_id=="TLC-FC-00-MASTER-005" && item.execution_status=="structural_only")return 0;
  return 5;
}
