#pragma once

#include <tllib/core/result.hpp>
#include <tllib/shared/contracts.hpp>

#include <string>
#include <string_view>
#include <utility>

namespace tllib::domains::message {

// TLC-FC-07-MESSAGE-002: a structural claim, never a scientific oracle.
// Input data is owned by the result; opaque bytes and references are not interpreted.
struct PreexistenceEvidence {
  std::string feature_id;
  std::string object_id;
  shared::ScientificReference source_reference;
  shared::OpaqueValue opaque_statement;
  shared::Traceability provenance;
  std::string candidate_status;
  bool evaluation_requested{false};
};

class UnevaluatedPreexistenceClaim final {
public:
  [[nodiscard]] static constexpr std::string_view feature_id() noexcept {
    return "TLC-FC-07-MESSAGE-002";
  }
  [[nodiscard]] static constexpr std::string_view verification_status() noexcept {
    return "unavailable_without_oracle";
  }
  [[nodiscard]] static constexpr std::string_view representation() noexcept {
    return "unevaluated_claim";
  }

  [[nodiscard]] const PreexistenceEvidence& evidence() const noexcept {
    return evidence_;
  }
  [[nodiscard]] std::string_view candidate_status() const noexcept {
    return evidence_.candidate_status;
  }

  // Lossless structural encoding; not a transport format or a scientific evaluation.
  [[nodiscard]] std::string canonical() const {
    shared::wire::Writer writer(feature_id());
    writer.add(representation());
    writer.add(evidence_.feature_id);
    writer.add(evidence_.object_id);
    writer.add(evidence_.source_reference.canonical());
    writer.add(evidence_.opaque_statement.canonical());
    writer.add(evidence_.provenance.canonical());
    writer.add(evidence_.candidate_status);
    writer.add(verification_status());
    return writer.data;
  }

  [[nodiscard]] bool operator==(const UnevaluatedPreexistenceClaim& other) const {
    return canonical() == other.canonical();
  }

private:
  explicit UnevaluatedPreexistenceClaim(PreexistenceEvidence evidence)
      : evidence_(std::move(evidence)) {}

  friend core::Result<UnevaluatedPreexistenceClaim>
  register_message_preexistence_claim(PreexistenceEvidence evidence);

  PreexistenceEvidence evidence_;
};

[[nodiscard]] inline core::Result<UnevaluatedPreexistenceClaim>
register_message_preexistence_claim(PreexistenceEvidence evidence) {
  auto fail = [](std::string stable_code,
                 std::string message) -> core::Result<UnevaluatedPreexistenceClaim> {
    return core::Error{core::ErrorCode::invalid_argument,
                       std::move(message),
                       std::string(UnevaluatedPreexistenceClaim::feature_id()),
                       {},
                       {},
                       std::move(stable_code)};
  };

  if (evidence.evaluation_requested) {
    return fail("OracleEvaluationRequested",
                "Scientific evaluation is unavailable for the preexistence claim");
  }

  // Match the authoritative source location in the pinned feature traceability.
  // This validates a scientific citation; it does not interpret its statement.
  const auto& ref = evidence.source_reference;
  const bool authoritative_source =
      ref.source_path == "maths/07-message/message.md" &&
      ref.section == std::optional<std::string>("Nature du Message fondamental") &&
      ref.subsection == std::optional<std::string>("Préexistence du Message") &&
      ref.line_range == std::optional<shared::LineRange>(shared::LineRange{58, 60});

  if (evidence.feature_id != UnevaluatedPreexistenceClaim::feature_id() ||
      evidence.object_id != "TLC-SO-MESSAGE-013" ||
      (evidence.source_reference.object_id &&
       *evidence.source_reference.object_id != evidence.object_id) ||
      !authoritative_source || evidence.source_reference.validate() ||
      evidence.opaque_statement.validate() || evidence.provenance.validate() ||
      evidence.candidate_status != "unevaluated_candidate") {
    return fail("MissingPreexistenceEvidence",
                "Required preexistence identity, source range or evidence is missing or invalid");
  }

  return UnevaluatedPreexistenceClaim(std::move(evidence));
}

} // namespace tllib::domains::message
