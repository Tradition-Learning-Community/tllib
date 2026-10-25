#include <tllib/build_info.hpp>
#include <tllib/core/identity.hpp>
#include <tllib/shared/contracts.hpp>
int main() {
  auto id=tllib::core::FeatureId::parse("TLC-FC-00-MASTER-005");
  if(!id || tllib::foundation_status.empty())return 1;
  tllib::shared::ScientificReference ref{"maths/00-master/master.md",{}, {}, {}, {}, {}};
  auto validated=tllib::shared::validate(ref);
  if(!validated)return 2;
  auto roundtrip=tllib::shared::wire::roundtrip(ref.canonical(),"TLC-HC-SCIENTIFIC-REFERENCE");
  return roundtrip && *roundtrip.value_if()==ref.canonical()?0:3;
}
