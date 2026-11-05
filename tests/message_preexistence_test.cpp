#include <tllib/domains/message/preexistence.hpp>

#include <cassert>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>

using tllib::domains::message::PreexistenceEvidence;
using tllib::domains::message::register_message_preexistence_claim;
using tllib::domains::message::UnevaluatedPreexistenceClaim;

namespace {

template <class T>
constexpr bool has_truth_value = requires(const T& value) { value.truth_value(); };
template <class T>
constexpr bool has_executable_oracle = requires(const T& value) { value.executable_oracle(); };

PreexistenceEvidence evidence() {
  tllib::shared::ScientificReference source{"maths/07-message/message.md",
                                            std::string("TLC-SO-MESSAGE-013"),
                                            std::string("Nature du Message fondamental"),
                                            std::string("Préexistence du Message"),
                                            {},
                                            tllib::shared::LineRange{58, 60}};
  tllib::shared::OpaqueValue opaque{
      "TLC-SO-MESSAGE-013", std::string("opaque\0payload", 14), source, {}};
  tllib::shared::Traceability provenance;
  std::size_t index = 0;
  for (std::size_t category = 0; category < tllib::domains::message::detail::kEvidenceCounts.size();
       ++category) {
    for (std::size_t i = 0; i < tllib::domains::message::detail::kEvidenceCounts[category]; ++i) {
      auto ref = source;
      ref.source_path = tllib::domains::message::detail::kEvidencePaths[index++];
      if (category != 0) {
        ref.object_id.reset();
        ref.section.reset();
        ref.subsection.reset();
        ref.line_range.reset();
      }
      provenance.categories[category].push_back(std::move(ref));
    }
  }
  assert(index == tllib::domains::message::detail::kEvidencePaths.size());
  return {"TLC-FC-07-MESSAGE-002",
          "TLC-SO-MESSAGE-013",
          source,
          opaque,
          provenance,
          "unevaluated_candidate",
          false};
}

bool has_error(const tllib::core::Result<UnevaluatedPreexistenceClaim>& result,
               std::string_view expected, bool unsupported = false) {
  if (result || result.value_if() || !result.error_if())
    return false;
  const auto& err = *result.error_if();
  const auto category = err.context.find("category");
  const auto recoverability = err.context.find("recoverability");
  const auto public_result = err.context.find("public_result");
  const auto atomicity = err.context.find("failure_atomicity");
  return err.stable_code && *err.stable_code == expected &&
         err.feature_id == std::optional<std::string>("TLC-FC-07-MESSAGE-002") &&
         err.code == (unsupported ? tllib::core::ErrorCode::unavailable_capability
                                  : tllib::core::ErrorCode::invalid_argument) &&
         category != err.context.end() &&
         category->second == (unsupported ? "unsupported_operation" : "invalid_input") &&
         recoverability != err.context.end() &&
         recoverability->second == (unsupported ? "non_retryable" : "recoverable") &&
         public_result != err.context.end() && public_result->second == "no_partial_result" &&
         atomicity != err.context.end() && atomicity->second == "no_observable_partial_result";
}

std::string with_replacement(std::string_view encoded, std::size_t index,
                             std::string_view replacement) {
  const auto fields =
      tllib::shared::wire::decode(encoded, UnevaluatedPreexistenceClaim::feature_id());
  assert(fields);
  tllib::shared::wire::Writer writer(UnevaluatedPreexistenceClaim::feature_id());
  for (std::size_t i = 3; i < fields.value_if()->size(); ++i) {
    writer.add(i == index ? replacement : std::string_view((*fields.value_if())[i]));
  }
  return writer.data;
}

} // namespace

int main() {
  // MSG-002-A01, A04, A05, A08: structural success, unchanged evidence, no oracle.
  auto input = evidence();
  const auto original_source = input.source_reference;
  const auto original_opaque = input.opaque_statement.canonical();
  const auto original_trace = input.provenance.canonical();
  auto result = register_message_preexistence_claim(input);
  assert(result);
  const auto& claim = *result.value_if();
  assert(claim.feature_id() == "TLC-FC-07-MESSAGE-002");
  assert(claim.representation() == "unevaluated_claim");
  assert(claim.verification_status() == "unavailable_without_oracle");
  assert(claim.candidate_status() == "unevaluated_candidate");
  assert(claim.evidence().object_id == "TLC-SO-MESSAGE-013");
  assert(claim.evidence().source_reference == original_source);
  assert(claim.evidence().opaque_statement.canonical() == original_opaque);
  assert(claim.evidence().provenance.canonical() == original_trace);
  assert(claim.evidence().opaque_statement.payload == std::string("opaque\0payload", 14));
  // Shared descriptor contract: identity, reference, provenance and unresolved status.
  const auto envelope = claim.descriptor();
  assert(envelope);
  assert(envelope.value_if()->feature_id.str() == "TLC-FC-07-MESSAGE-002");
  assert(envelope.value_if()->representation == "unevaluated_claim");
  assert(envelope.value_if()->package_status == tllib::core::PackageStatus::finalized);
  assert(envelope.value_if()->scientific_status ==
         tllib::core::ScientificStatus::external_provider_required);
  assert(envelope.value_if()->execution_status == tllib::core::ExecutionStatus::structural_only);
  assert(envelope.value_if()->references.size() == 1);
  assert(envelope.value_if()->references.at("evidence").members.size() == 1);
  assert(std::get<tllib::shared::ScientificReference>(
             envelope.value_if()->references.at("evidence").members.front()) == original_source);
  assert(envelope.value_if()->provenance.canonical() == original_trace);
  assert(envelope.value_if()->unresolved.empty());
  assert(envelope.value_if()->dependencies.empty());
  assert(tllib::shared::validate(*envelope.value_if()));
  assert(tllib::domains::message::detail::valid_provenance(claim.evidence().provenance,
                                                           claim.evidence().source_reference));
  static_assert(!has_truth_value<UnevaluatedPreexistenceClaim>);
  static_assert(!has_executable_oracle<UnevaluatedPreexistenceClaim>);
  static_assert(
      std::is_same_v<decltype(std::declval<const UnevaluatedPreexistenceClaim&>().evidence()),
                     const PreexistenceEvidence&>);

  // MSG-002-A06: structurally identical evidence produces identical results.
  auto same = register_message_preexistence_claim(evidence());
  assert(same && *same.value_if() == claim && same.value_if()->canonical() == claim.canonical());

  // MSG-002-A07: actual typed reconstruction, including all metadata and opaque bytes.
  auto restored = UnevaluatedPreexistenceClaim::from_wire(claim.canonical());
  assert(restored && *restored.value_if() == claim);
  assert(restored.value_if()->evidence().provenance.canonical() == original_trace);
  assert(restored.value_if()->evidence().source_reference == original_source);
  assert(restored.value_if()->evidence().opaque_statement.canonical() == original_opaque);
  assert(restored.value_if()->verification_status() == "unavailable_without_oracle");

  auto rich = evidence();
  rich.source_reference.source_commit = std::string(40, 'a');
  rich.opaque_statement.source_reference = rich.source_reference;
  rich.opaque_statement.encoding = "uninterpreted";
  rich.opaque_statement.payload = std::string("\0\xFF\0opaque", 9);
  rich.provenance.categories[0][0].source_commit = rich.source_reference.source_commit;
  rich.provenance.categories[3][0].source_commit = std::string(40, 'f');
  auto rich_result = register_message_preexistence_claim(rich);
  assert(rich_result);
  auto rich_copy = UnevaluatedPreexistenceClaim::from_wire(rich_result.value_if()->canonical());
  assert(rich_copy && *rich_copy.value_if() == *rich_result.value_if());
  assert(rich_copy.value_if()->evidence().opaque_statement.payload ==
         rich.opaque_statement.payload);
  assert(rich_copy.value_if()->evidence().opaque_statement.encoding ==
         rich.opaque_statement.encoding);
  assert(rich_copy.value_if()->evidence().source_reference.source_commit ==
         rich.source_reference.source_commit);

  const auto original_wire = claim.canonical();
  assert(has_error(
      UnevaluatedPreexistenceClaim::from_wire(original_wire.substr(0, original_wire.size() - 1)),
      "MissingPreexistenceEvidence"));
  assert(has_error(
      UnevaluatedPreexistenceClaim::from_wire(with_replacement(original_wire, 10, "available")),
      "MissingPreexistenceEvidence"));
  assert(has_error(
      UnevaluatedPreexistenceClaim::from_wire(with_replacement(original_wire, 9, "verified")),
      "MissingPreexistenceEvidence"));
  assert(has_error(UnevaluatedPreexistenceClaim::from_wire(
                       with_replacement(original_wire, 3, "evaluated_claim")),
                   "MissingPreexistenceEvidence"));

  // MSG-002-A02: no partial success when identity, source or provenance is invalid.
  auto invalid = evidence();
  invalid.object_id.clear();
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));
  invalid = evidence();
  invalid.feature_id = "TLC-FC-07-MESSAGE-001";
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));
  invalid = evidence();
  invalid.object_id = "TLC-SO-MESSAGE-014";
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));
  invalid = evidence();
  invalid.source_reference.line_range.reset();
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));
  invalid = evidence();
  invalid.source_reference.line_range = tllib::shared::LineRange{58, 61};
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));
  invalid = evidence();
  invalid.source_reference.source_path = "maths/07-message/other.md";
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));
  invalid = evidence();
  invalid.source_reference.subsection = "Other subsection";
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));
  invalid = evidence();
  invalid.source_reference.object_id = "TLC-SO-MESSAGE-014";
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));
  invalid = evidence();
  invalid.opaque_statement.source_reference.line_range = tllib::shared::LineRange{59, 60};
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));
  invalid = evidence();
  invalid.opaque_statement.semantic_type_id.clear();
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));
  invalid = evidence();
  invalid.provenance.categories[6].clear();
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));
  invalid = evidence();
  invalid.provenance.categories[7][0].source_path = "other.yaml";
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));
  invalid = evidence();
  invalid.provenance.categories[7].push_back(invalid.provenance.categories[7].front());
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));
  invalid = evidence();
  invalid.candidate_status = "verified";
  assert(has_error(register_message_preexistence_claim(invalid), "MissingPreexistenceEvidence"));

  // MSG-002-A03: no truth-value or oracle request may succeed.
  invalid = evidence();
  invalid.evaluation_requested = true;
  assert(
      has_error(register_message_preexistence_claim(invalid), "OracleEvaluationRequested", true));
}
