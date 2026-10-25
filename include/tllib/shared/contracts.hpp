#pragma once
#include <tllib/core/identity.hpp>
#include <algorithm>
#include <array>
#include <cstddef>
#include <functional>
#include <limits>
#include <map>
#include <optional>
#include <set>
#include <string>
#include <string_view>
#include <utility>
#include <vector>
namespace tllib::shared {
using core::Error;
using core::Result;
using core::invalid;
inline constexpr std::string_view contract_version="1.0.0";
inline constexpr std::array<std::string_view,8> contract_ids={
  "TLC-HC-FEATURE-ID","TLC-HC-SCIENTIFIC-REFERENCE","TLC-HC-REFERENCE-COLLECTION",
  "TLC-HC-UNRESOLVED-ITEM","TLC-HC-OPAQUE-VALUE","TLC-HC-STRUCTURED-ERROR",
  "TLC-HC-TRACEABILITY","TLC-HC-DESCRIPTOR-ENVELOPE"};
// Dependency indices follow contract_ids. Forbids hidden cross-domain cycles.
inline constexpr std::array<unsigned,8> dependency_masks={0,0,1u<<1,1u<<1,1u<<1,1u<<0,1u<<1,
  (1u<<0)|(1u<<2)|(1u<<3)|(1u<<6)};
constexpr bool dependencies_acyclic() {
  for(unsigned start=0;start<8;++start) {
    unsigned visited=0,front=dependency_masks[start];
    while(front) {
      if(front & (1u<<start))return false;
      const unsigned new_bits=front & ~visited;
      if(!new_bits)break;
      visited|=new_bits;front=0;
      for(unsigned i=0;i<8;++i)if(new_bits & (1u<<i))front|=dependency_masks[i];
    }
  }
  return true;
}
static_assert(dependencies_acyclic());
inline bool supported_version(std::string_view version) noexcept {return version==contract_version;}
namespace wire {
// Canonical length-prefixed binary wire representation. Binary fields are uninterpreted.
struct Writer {
  std::string data;
  explicit Writer(std::string_view contract) { add("TLHC"); add(contract); add(contract_version); }
  void add(std::string_view field) { data+=std::to_string(field.size()); data+=':'; data.append(field.data(),field.size()); }
  void add(std::size_t value) {add(std::to_string(value));}
  void optional(const std::optional<std::string>& value) {add(value?"1":"0"); if(value) add(*value);}
  template<class T> void sequence(const std::vector<T>& values) {add(values.size()); for(const auto& value:values) add(value.canonical());}
};
inline Result<std::vector<std::string>> decode(std::string_view bytes, std::string_view expected_contract) {
  std::vector<std::string> fields;
  while(!bytes.empty()) {
    const auto split=bytes.find(':');
    if(split==std::string_view::npos || split==0 || split>19 || (split>1 && bytes[0]=='0')) return invalid("Invalid canonical length");
    std::size_t size=0;
    for(std::size_t i=0;i<split;++i) {
      const char c=bytes[i];
      if(c<'0'||c>'9'||size>(std::numeric_limits<std::size_t>::max()-std::size_t(c-'0'))/10) return invalid("Invalid canonical length");
      size=size*10+std::size_t(c-'0');
    }
    bytes.remove_prefix(split+1);
    if(size>bytes.size()) return invalid("Truncated canonical field");
    fields.emplace_back(bytes.substr(0,size));
    bytes.remove_prefix(size);
  }
  if(fields.size()<3 || fields[0]!="TLHC" || fields[1]!=expected_contract) return invalid("Unexpected wire contract");
  if(!supported_version(fields[2])) return Error{core::ErrorCode::unsupported_version,"Unsupported shared contract version",{}, {}};
  return fields;
}
} // namespace wire
inline bool relative_path(std::string_view path) {
  if(path.empty() || path.back()=='/' || path.front()=='/' || path.front()=='\\' || path.find('\\')!=std::string_view::npos || path.find(':')!=std::string_view::npos) return false;
  while(!path.empty()) {
    const auto slash=path.find('/'); const auto part=path.substr(0,slash);
    if(part.empty() || part=="." || part=="..") return false;
    if(slash==std::string_view::npos) break;
    path.remove_prefix(slash+1);
  }
  return true;
}
struct LineRange { std::size_t start{},end{}; friend bool operator==(const LineRange&,const LineRange&)=default; };
struct ScientificReference {
  std::string source_path;
  std::optional<std::string> object_id,section,subsection,source_commit;
  std::optional<LineRange> line_range;
  [[nodiscard]] std::optional<Error> validate() const {
    if(!relative_path(source_path)) return invalid("Unsafe repository source path");
    if(line_range && (line_range->start==0 || line_range->end<line_range->start)) return invalid("Invalid inclusive line range");
    return {};
  }
  [[nodiscard]] std::string canonical() const {
    wire::Writer w("TLC-HC-SCIENTIFIC-REFERENCE");
    w.add(source_path);w.optional(object_id);w.optional(section);w.optional(subsection);
    w.add(line_range?"1":"0");if(line_range){w.add(line_range->start);w.add(line_range->end);}
    w.optional(source_commit);return w.data;
  }
  friend bool operator==(const ScientificReference&,const ScientificReference&)=default;
};
enum class CollectionKind {scalar,optional,sequence,set,ordered_set,multiset,map,ordered_map};
inline Result<CollectionKind> collection_kind(std::string_view text) {
  constexpr std::array<std::string_view,8> names={"scalar","optional","sequence","set","ordered_set","multiset","map","ordered_map"};
  for(std::size_t i=0;i<names.size();++i) if(text==names[i]) return static_cast<CollectionKind>(i);
  return invalid("Unknown collection kind");
}
inline std::string_view name(CollectionKind kind) {
  constexpr std::array<std::string_view,8> names={"scalar","optional","sequence","set","ordered_set","multiset","map","ordered_map"};
  return names[static_cast<std::size_t>(kind)];
}
struct ReferenceCollection {
  CollectionKind kind{CollectionKind::sequence};
  std::vector<ScientificReference> members;
  std::vector<std::string> keys; // map/ordered_map entry keys, in member order
  std::size_t minimum{0};
  std::optional<std::size_t> maximum;
  std::string membership{"open"},ordering{"not_constrained"},duplicates{"implementation_defined"};
  std::optional<std::string> key_contract,value_contract;
  [[nodiscard]] std::optional<Error> validate() const {
    if(static_cast<std::size_t>(kind)>=8) return invalid("Unknown collection kind");
    if(maximum && *maximum<minimum) return invalid("Invalid cardinality interval");
    if(members.size()<minimum || (maximum && members.size()>*maximum)) return invalid("Cardinality violation");
    if((kind==CollectionKind::scalar && members.size()!=1) || (kind==CollectionKind::optional && members.size()>1)) return invalid("Scalar/optional cardinality violation");
    const bool mapping=(kind==CollectionKind::map || kind==CollectionKind::ordered_map);
    if(mapping && (!key_contract || keys.size()!=members.size())) return invalid("Map requires matching keys and declared key contract");
    if(!mapping && !keys.empty()) return invalid("Non-map cannot contain entry keys");
    if(mapping){std::set<std::string> seen_keys;for(const auto& key:keys)if(key.empty() || !seen_keys.insert(key).second)return invalid("Invalid/duplicate map key");}
    constexpr std::array<std::string_view,4> memberships={"exact","constrained","open","not_applicable"};
    constexpr std::array<std::string_view,5> orderings={"required","preserved","implementation_defined","not_constrained","not_applicable"};
    constexpr std::array<std::string_view,5> duplications={"forbidden","allowed","significant","implementation_defined","not_applicable"};
    auto in=[](std::string_view value,const auto& values){return std::find(values.begin(),values.end(),value)!=values.end();};
    if(!in(membership,memberships) || !in(ordering,orderings) || !in(duplicates,duplications))return invalid("Invalid collection semantics");
    for(const auto& m:members) if(auto e=m.validate()) return e;
    if(kind==CollectionKind::set || kind==CollectionKind::ordered_set || duplicates=="forbidden") {
      std::set<std::string> seen;
      for(const auto& m:members) if(!seen.insert(m.canonical()).second) return invalid("Duplicate reference");
    }
    return {};
  }
  [[nodiscard]] std::string canonical() const {
    wire::Writer w("TLC-HC-REFERENCE-COLLECTION");w.add(name(kind));w.add(minimum);
    w.add(maximum?"1":"0");if(maximum)w.add(*maximum);
    w.add(membership);w.add(ordering);w.add(duplicates);w.optional(key_contract);w.optional(value_contract);
    w.add(keys.size());for(const auto& key:keys)w.add(key);w.sequence(members);return w.data;
  }
};
enum class UnresolvedStatus {preserved_unresolved,external_provider_required};
inline Result<UnresolvedStatus> unresolved_status(std::string_view text) {
  if(text=="preserved_unresolved")return UnresolvedStatus::preserved_unresolved;
  if(text=="external_provider_required")return UnresolvedStatus::external_provider_required;
  return invalid("Invalid unresolved status");
}
struct UnresolvedItem {
  std::string unresolved_id,classification;
  ScientificReference source_reference;
  std::string blocking_scope;
  UnresolvedStatus status{UnresolvedStatus::preserved_unresolved};
  [[nodiscard]] std::optional<Error> validate() const {
    if(unresolved_id.empty() || classification.empty() || blocking_scope.empty() || static_cast<unsigned>(status)>1) return invalid("Incomplete unresolved item");
    return source_reference.validate();
  }
  [[nodiscard]] std::string canonical() const {
    wire::Writer w("TLC-HC-UNRESOLVED-ITEM");w.add(unresolved_id);w.add(classification);w.add(source_reference.canonical());
    w.add(blocking_scope);w.add(status==UnresolvedStatus::preserved_unresolved?"preserved_unresolved":"external_provider_required");return w.data;
  }
};
struct OpaqueValue {
  std::string semantic_type_id;
  std::string payload; // Uninterpreted binary or structured bytes, including unknown fields.
  ScientificReference source_reference;
  std::optional<std::string> encoding;
  [[nodiscard]] std::optional<Error> validate() const {
    if(semantic_type_id.empty())return invalid("Missing semantic type identity");
    return source_reference.validate();
  }
  [[nodiscard]] std::string canonical() const {
    wire::Writer w("TLC-HC-OPAQUE-VALUE");w.add(semantic_type_id);w.add(payload);w.add(source_reference.canonical());w.optional(encoding);return w.data;
  }
};
enum class Recoverability {recoverable,retryable,non_retryable,implementation_defined,not_applicable};
enum class PublicResult {error_only,no_partial_result,partial_result_allowed,implementation_defined};
enum class FailureAtomicity {no_observable_partial_result,basic,not_constrained,implementation_defined,not_applicable};
struct StructuredError {
  std::string code,category,condition;
  std::optional<core::FeatureId> feature_id;
  Recoverability recoverability{Recoverability::implementation_defined};
  PublicResult public_result{PublicResult::no_partial_result};
  FailureAtomicity failure_atomicity{FailureAtomicity::no_observable_partial_result};
  std::map<std::string,std::string> context; // deterministic key order, diagnostic only
  [[nodiscard]] std::optional<Error> validate() const {
    if(code.empty() || category.empty() || condition.empty() || static_cast<unsigned>(recoverability)>4 ||
       static_cast<unsigned>(public_result)>3 || static_cast<unsigned>(failure_atomicity)>4) return invalid("Incomplete structured error");
    return {};
  }
  [[nodiscard]] std::string canonical() const {
    wire::Writer w("TLC-HC-STRUCTURED-ERROR");w.add(code);w.add(category);w.add(condition);
    w.add(feature_id?"1":"0");if(feature_id)w.add(feature_id->str());
    w.add(static_cast<std::size_t>(recoverability));w.add(static_cast<std::size_t>(public_result));w.add(static_cast<std::size_t>(failure_atomicity));
    w.add(context.size());for(const auto&[key,value]:context){w.add(key);w.add(value);}
    w.add("implementation_defined");return w.data;
  }
};
struct Traceability {
  std::array<std::vector<ScientificReference>,8> categories;
  static constexpr std::array<std::string_view,8> names={"scientific_sources","mathematical_contracts","source_irs","finalized_irs","algorithm_specifications","test_plans","acceptance_oracles","scientific_decisions"};
  [[nodiscard]] std::optional<Error> validate() const {
    for(const auto& refs:categories){
      std::set<std::string> seen;
      for(const auto& ref:refs){if(auto e=ref.validate())return e;if(!seen.insert(ref.canonical()).second)return invalid("Duplicate traceability reference");}
    }
    return {};
  }
  [[nodiscard]] bool resolves(const std::function<bool(std::string_view)>& resolver) const {
    if(validate())return false;
    for(const auto& refs:categories)for(const auto& ref:refs)if(!resolver(ref.source_path))return false;
    return true;
  }
  [[nodiscard]] std::string canonical() const {
    wire::Writer w("TLC-HC-TRACEABILITY");for(const auto& refs:categories)w.sequence(refs);return w.data;
  }
};
struct DescriptorEnvelope {
  core::FeatureId feature_id;
  std::string representation;
  std::map<std::string,ReferenceCollection> references;
  std::vector<UnresolvedItem> unresolved;
  std::vector<std::string> dependencies;
  Traceability provenance;
  core::ScientificStatus scientific_status{core::ScientificStatus::partially_defined};
  core::ExecutionStatus execution_status{core::ExecutionStatus::structural_only};
  [[nodiscard]] std::optional<Error> validate() const {
    if(representation.empty())return invalid("Missing representation");
    if(static_cast<unsigned>(scientific_status)>4 || static_cast<unsigned>(execution_status)>3)return invalid("Invalid descriptor status");
    for(const auto& [label,collection]:references){if(label.empty())return invalid("Empty reference label");if(auto e=collection.validate())return e;}
    std::set<std::string> seen;
    for(const auto& item:unresolved){if(auto e=item.validate())return e;if(!seen.insert(item.unresolved_id).second)return invalid("Duplicate unresolved identity");}
    seen.clear();for(const auto& dependency:dependencies)if(dependency.empty() || !seen.insert(dependency).second)return invalid("Duplicate/empty dependency");
    return provenance.validate();
  }
  [[nodiscard]] std::string canonical() const {
    wire::Writer w("TLC-HC-DESCRIPTOR-ENVELOPE");w.add(feature_id.str());w.add(representation);
    w.add(references.size());for(const auto& [key,value]:references){w.add(key);w.add(value.canonical());}
    w.sequence(unresolved);w.add(dependencies.size());for(const auto& d:dependencies)w.add(d);
    w.add(provenance.canonical());w.add(static_cast<std::size_t>(scientific_status));w.add(static_cast<std::size_t>(execution_status));return w.data;
  }
};
template<class T> [[nodiscard]] Result<T> validate(T value) {
  if(auto err=value.validate()) return *err;
  return value;
}
} // namespace tllib::shared
