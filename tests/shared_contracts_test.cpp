#include <tllib/shared/contracts.hpp>
#include <cassert>
#include <string>
#include <type_traits>
#include <utility>
using namespace tllib;
int main() {
  auto fid=core::FeatureId::parse("TLC-FC-00-MASTER-005");
  assert(fid && fid.value_if()->str()=="TLC-FC-00-MASTER-005");
  assert(!core::FeatureId::parse("tlc-fc-00-master-005"));
  assert(!core::FeatureId::parse("TLC-FC-00--MASTER-005"));
  assert(!core::FeatureId::parse("TLC-FC-00-MASTER-5"));
  assert(core::FeatureId::parse("TLC-FC-00-MASTER--005")); // matches source JSON schema
  assert(core::parse_package_status("pilot") && !core::parse_package_status("random"));
  assert(core::parse_scientific_status("external_provider_required") && !core::parse_scientific_status("unknown"));
  assert(core::parse_execution_status("conditionally_executable") && !core::parse_execution_status("running"));
  assert(core::DomainId::parse("low-data-architecture"));
  assert(!core::DomainId::parse("Low--Data"));
  assert(core::Version::parse("1.0.0") && !core::Version::parse("01.0.0"));
  assert(core::Fingerprint::parse(std::string(40,'a')));
  assert(!core::Fingerprint::parse("ab1"));
  assert(shared::supported_version("1.0.0") && !shared::supported_version("2.0.0"));
  shared::ScientificReference ref{"maths/00-master/master.md",std::string("TLC-SO-MASTER-008"),std::string("3. Structure interne"),{}, {},shared::LineRange{41,47}};
  assert(shared::validate(ref));
  assert(!shared::validate(shared::ScientificReference{"../outside.md",{}, {}, {}, {}, {}}));
  assert(!shared::validate(shared::ScientificReference{"/absolute/source.yaml",{}, {}, {}, {}, {}}));
  assert(!shared::validate(shared::ScientificReference{"safe//bad",{}, {}, {}, {}, {}}));
  assert(!shared::validate(shared::ScientificReference{"safe/",{}, {}, {}, {}, {}}));
  assert(!shared::validate(shared::ScientificReference{"safe/./bad",{}, {}, {}, {}, {}}));
  assert(!shared::validate(shared::ScientificReference{"safe/file",{}, {}, {}, {},shared::LineRange{7,5}}));
  for(auto id:shared::contract_ids) assert(id.starts_with("TLC-HC-"));
  assert(shared::collection_kind("ordered_set") && !shared::collection_kind("vector"));
  shared::ReferenceCollection col; col.kind=shared::CollectionKind::ordered_set;col.ordering="preserved";col.duplicates="forbidden";col.members={ref};col.maximum=2;
  assert(shared::validate(col));
  col.members.push_back(ref);assert(!shared::validate(col));col.members.pop_back();
  // HC-RCOL-003: source order and duplicate-free identity references.
  shared::ReferenceCollection relation_refs;relation_refs.kind=shared::CollectionKind::ordered_set;
  relation_refs.ordering="preserved";relation_refs.duplicates="forbidden";
  relation_refs.members={std::string("TLC-SR-MASTER-007"),std::string("TLC-SR-MASTER-008")};
  assert(shared::validate(relation_refs));
  const auto serialized_refs=relation_refs.canonical();
  std::swap(relation_refs.members[0],relation_refs.members[1]);
  assert(shared::validate(relation_refs));assert(serialized_refs!=relation_refs.canonical());
  relation_refs.members.push_back(std::string("TLC-SR-MASTER-008"));
  assert(!shared::validate(relation_refs));
  shared::ReferenceCollection map_collection;map_collection.kind=shared::CollectionKind::ordered_map;
  map_collection.members={ref};map_collection.keys={"first"};map_collection.key_contract="opaque_key";
  assert(shared::validate(map_collection));
  map_collection.keys.push_back("extra");assert(!shared::validate(map_collection));
  shared::UnresolvedItem item{"UNR-001","scientific_unresolved",ref,"operation",shared::UnresolvedStatus::preserved_unresolved};
  assert(shared::validate(item));
  assert(!shared::unresolved_status("resolved_by_default"));
  shared::OpaqueValue opaque{"TLC-SO-MASTER-008",std::string("{\"unknown_field\":\"preserve\"}\0",29),ref,{}};
  assert(shared::validate(opaque));
  assert(!shared::validate(shared::OpaqueValue{"","{}",ref,{}}));
  const auto bytes=opaque.canonical();
  auto decoded=shared::wire::decode(bytes,"TLC-HC-OPAQUE-VALUE");
  assert(decoded && decoded.value_if()->size()==7 && (*decoded.value_if())[4]==opaque.payload);
  assert(!shared::wire::decode(bytes,"TLC-HC-FEATURE-ID"));
  assert(!shared::wire::decode("3:TLHC29:TLC-HC-OPAQUE-VALUE5:1.0.0","TLC-HC-OPAQUE-VALUE"));
  shared::wire::Writer bad("TLC-HC-FEATURE-ID");bad.add("TLC-FC-00-MASTER-005");
  auto pos=bad.data.find("1.0.0");bad.data.replace(pos,5,"2.0.0");
  auto unsupported=shared::wire::decode(bad.data,"TLC-HC-FEATURE-ID");
  assert(!unsupported && unsupported.error_if()->code==core::ErrorCode::unsupported_version);
  shared::StructuredError err{"MASTER_REFERENCE_SET_MISMATCH","invalid_input","reference set mismatch",fid.value_if()?std::optional<core::FeatureId>(*fid.value_if()):std::nullopt,
    shared::Recoverability::recoverable,shared::PublicResult::no_partial_result,shared::FailureAtomicity::no_observable_partial_result,{{"count","1"}}};
  assert(shared::validate(err));assert(err.canonical()==err.canonical());
  shared::Traceability tr;tr.categories[0].push_back(ref);assert(shared::validate(tr));
  assert(tr.resolves([](std::string_view p){return p=="maths/00-master/master.md";}));
  assert(!tr.resolves([](std::string_view){return false;}));
  tr.categories[0].push_back(ref);assert(!shared::validate(tr));tr.categories[0].pop_back();
  shared::DescriptorEnvelope envelope{*fid.value_if(),"declaration",{{"objects",col}},{item},{},tr};
  assert(shared::validate(envelope));
  auto result=shared::validate(envelope);assert(result && result.value_if()->canonical()==envelope.canonical());
  static_assert(std::is_same_v<decltype(std::declval<core::Result<shared::DescriptorEnvelope>&>().value_if()),const shared::DescriptorEnvelope*>);
  envelope.unresolved.push_back(item);assert(!shared::validate(envelope));
  assert(shared::wire::decode(ref.canonical(),"TLC-HC-SCIENTIFIC-REFERENCE"));
  assert(shared::wire::decode(col.canonical(),"TLC-HC-REFERENCE-COLLECTION"));
  assert(shared::wire::decode(item.canonical(),"TLC-HC-UNRESOLVED-ITEM"));
  assert(shared::wire::decode(err.canonical(),"TLC-HC-STRUCTURED-ERROR"));
  assert(shared::wire::decode(tr.canonical(),"TLC-HC-TRACEABILITY"));
  assert(shared::wire::decode(result.value_if()->canonical(),"TLC-HC-DESCRIPTOR-ENVELOPE"));
}
