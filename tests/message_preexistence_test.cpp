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
  provenance.categories[0].push_back(source);
  return {"TLC-FC-07-MESSAGE-002",
          "TLC-SO-MESSAGE-013",
          source,
          opaque,
          provenance,
          "unevaluated_candidate",
          false};
}

bool has_error(const tllib::core::Result<UnevaluatedPreexistenceClaim>& result,
               std::string_view code) {
  return !result && result.error_if() && result.error_if()->stable_code &&
         *result.error_if()->stable_code == code && !result.value_if();
}

} // namespace

int main() {
  // MSG-002-A01/A04/A05/A08: no oracle, no truth value, exact opaque preservation.
  auto input = evidence();
  const auto initial_source = input.source_reference;
  const auto initial_statement = input.opaque_statement.canonical();
  const auto initial_traceability = input.provenance.canonical();
  auto result = register_message_preexistence_claim(input);
  assert(result);
  const auto& claim = *result.value_if();
  assert(claim.feature_id() == "TLC-FC-07-MESSAGE-002");
  assert(claim.representation() == "unevaluated_claim");
  assert(claim.verification_status() == "unavailable_without_oracle");
  assert(claim.candidate_status() == "unevaluated_candidate");
  assert(claim.evidence().source_reference == initial_source);
  assert(claim.evidence().opaque_statement.canonical() == initial_statement);
  assert(claim.evidence().provenance.canonical() == initial_traceability);
  assert(claim.evidence().opaque_statement.payload == std::string("opaque\0payload", 14));

  // MSG-002-A06: determinism for structurally identical source evidence.
  const auto same = register_message_preexistence_claim(evidence());
  assert(same && *same.value_if() == claim && same.value_if()->canonical() == claim.canonical());
  const auto encoded =
      tllib::shared::wire::roundtrip(claim.canonical(), UnevaluatedPreexistenceClaim::feature_id());
  assert(encoded && *encoded.value_if() == claim.canonical());

  // MSG-002-A02: reject absent, changed or invalid source evidence atomically.
  auto missing = evidence();
  missing.object_id.clear();
  assert(has_error(register_message_preexistence_claim(missing), "MissingPreexistenceEvidence"));
  missing = evidence();
  missing.feature_id = "TLC-FC-07-MESSAGE-001";
  assert(has_error(register_message_preexistence_claim(missing), "MissingPreexistenceEvidence"));
  missing = evidence();
  missing.object_id = "TLC-SO-MESSAGE-014";
  assert(has_error(register_message_preexistence_claim(missing), "MissingPreexistenceEvidence"));
  missing = evidence();
  missing.source_reference.line_range = tllib::shared::LineRange{58, 61};
  assert(has_error(register_message_preexistence_claim(missing), "MissingPreexistenceEvidence"));
  missing = evidence();
  missing.source_reference.subsection = "Autre sous-section";
  assert(has_error(register_message_preexistence_claim(missing), "MissingPreexistenceEvidence"));
  missing = evidence();
  missing.source_reference.source_path = "maths/07-message/other.md";
  assert(has_error(register_message_preexistence_claim(missing), "MissingPreexistenceEvidence"));
  missing = evidence();
  missing.source_reference.line_range.reset();
  assert(has_error(register_message_preexistence_claim(missing), "MissingPreexistenceEvidence"));
  missing = evidence();
  missing.source_reference.line_range = tllib::shared::LineRange{20, 10};
  assert(has_error(register_message_preexistence_claim(missing), "MissingPreexistenceEvidence"));
  missing = evidence();
  missing.opaque_statement.semantic_type_id.clear();
  assert(has_error(register_message_preexistence_claim(missing), "MissingPreexistenceEvidence"));
  missing = evidence();
  missing.candidate_status = "verified";
  assert(has_error(register_message_preexistence_claim(missing), "MissingPreexistenceEvidence"));

  // MSG-002-A03: explicitly reject any attempted oracle evaluation.
  auto invalid_request = evidence();
  invalid_request.evaluation_requested = true;
  assert(
      has_error(register_message_preexistence_claim(invalid_request), "OracleEvaluationRequested"));

  // The claim exposes only structural evidence; callers cannot mutate it.
  static_assert(
      std::is_same_v<decltype(std::declval<const UnevaluatedPreexistenceClaim&>().evidence()),
                     const PreexistenceEvidence&>);
}
