#pragma once

#include <tllib/core/result.hpp>
#include <tllib/shared/contracts.hpp>

#include <array>
#include <charconv>
#include <cstddef>
#include <optional>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace tllib::domains::message {

// TLC-FC-07-MESSAGE-002 is structural_only: no oracle, truth value or transport.
struct PreexistenceEvidence {
  std::string feature_id;
  std::string object_id;
  shared::ScientificReference source_reference;
  shared::OpaqueValue opaque_statement;
  shared::Traceability provenance;
  std::string candidate_status;
  bool evaluation_requested{false};
};

namespace detail {

inline constexpr std::array<std::string_view, 13> kEvidencePaths{
    "maths/07-message/message.md",
    "registry/math-contracts/TLC-FC-07-MESSAGE-002/contract.yaml",
    "registry/ir/TLC-FC-07-MESSAGE-002/ir.yaml",
    "registry/optimized-ir/message/TLC-FC-07-MESSAGE-002/ir.yaml",
    "registry/algorithms/message/TLC-FC-07-MESSAGE-002/algorithm.yaml",
    "registry/test-plans/TLC-FC-07-MESSAGE-002/test-plan.yaml",
    "registry/oracles/message/TLC-FC-07-MESSAGE-002/oracle.yaml",
    "registry/domain-finalization/message/feature-status.yaml",
    "registry/domain-finalization/message/module-specification.yaml",
    "registry/domain-finalization/message/patterns.yaml",
    "registry/domain-finalization/message/implementation-tasks.yaml",
    "registry/domain-finalization/message/decision-required.yaml",
    "registry/domain-finalization/message/manifest.yaml",
};

inline constexpr std::array<std::size_t, 8> kEvidenceCounts{1, 1, 1, 1, 1, 1, 1, 6};

inline bool valid_provenance(const shared::Traceability& trace,
                             const shared::ScientificReference& source) {
  if (trace.validate())
    return false;
  std::size_t expected = 0;
  for (std::size_t category = 0; category < kEvidenceCounts.size(); ++category) {
    const auto& refs = trace.categories[category];
    if (refs.size() != kEvidenceCounts[category])
      return false;
    for (const auto& ref : refs) {
      if (ref.source_path != kEvidencePaths[expected++])
        return false;
    }
  }
  const auto& first = trace.categories[0].front();
  return first.source_path == source.source_path && first.section == source.section &&
         first.subsection == source.subsection && first.line_range == source.line_range;
}

inline bool parse_count(std::string_view field, std::size_t& output) {
  if (field.empty() || (field.size() > 1 && field.front() == '0'))
    return false;
  const auto [end, code] = std::from_chars(field.data(), field.data() + field.size(), output);
  return code == std::errc{} && end == field.data() + field.size();
}

inline bool read_optional(const std::vector<std::string>& fields, std::size_t& pos,
                          std::optional<std::string>& result) {
  if (pos >= fields.size())
    return false;
  const auto& present = fields[pos++];
  if (present == "0") {
    result.reset();
    return true;
  }
  if (present != "1" || pos >= fields.size())
    return false;
  result = fields[pos++];
  return true;
}

inline core::Result<shared::ScientificReference> read_reference(std::string_view bytes) {
  const auto decoded = shared::wire::decode(bytes, "TLC-HC-SCIENTIFIC-REFERENCE");
  if (!decoded)
    return *decoded.error_if();
  const auto& fields = *decoded.value_if();
  if (fields.size() < 8)
    return core::invalid("Truncated scientific reference");
  std::size_t pos = 3;
  shared::ScientificReference result;
  result.source_path = fields[pos++];
  if (!read_optional(fields, pos, result.object_id) ||
      !read_optional(fields, pos, result.section) ||
      !read_optional(fields, pos, result.subsection) || pos >= fields.size()) {
    return core::invalid("Malformed scientific reference");
  }
  const auto has_range = fields[pos++];
  if (has_range == "1") {
    if (fields.size() - pos < 2)
      return core::invalid("Truncated source range");
    std::size_t start = 0;
    std::size_t end = 0;
    if (!parse_count(fields[pos++], start) || !parse_count(fields[pos++], end))
      return core::invalid("Invalid source range");
    result.line_range = shared::LineRange{start, end};
  } else if (has_range != "0") {
    return core::invalid("Invalid source range marker");
  }
  if (!read_optional(fields, pos, result.source_commit) || pos != fields.size() ||
      result.validate() || result.canonical() != bytes) {
    return core::invalid("Invalid scientific reference");
  }
  return result;
}

inline core::Result<shared::OpaqueValue> read_opaque(std::string_view bytes) {
  const auto decoded = shared::wire::decode(bytes, "TLC-HC-OPAQUE-VALUE");
  if (!decoded)
    return *decoded.error_if();
  const auto& fields = *decoded.value_if();
  if (fields.size() < 7)
    return core::invalid("Truncated opaque evidence");
  shared::OpaqueValue result;
  result.semantic_type_id = fields[3];
  result.payload = fields[4];
  auto source = read_reference(fields[5]);
  if (!source)
    return *source.error_if();
  result.source_reference = std::move(*source.value_if());
  std::size_t pos = 6;
  if (!read_optional(fields, pos, result.encoding) || pos != fields.size() || result.validate() ||
      result.canonical() != bytes) {
    return core::invalid("Invalid opaque evidence");
  }
  return result;
}

inline core::Result<shared::Traceability> read_traceability(std::string_view bytes) {
  const auto decoded = shared::wire::decode(bytes, "TLC-HC-TRACEABILITY");
  if (!decoded)
    return *decoded.error_if();
  const auto& fields = *decoded.value_if();
  std::size_t pos = 3;
  shared::Traceability result;
  for (auto& refs : result.categories) {
    std::size_t count = 0;
    if (pos >= fields.size() || !parse_count(fields[pos++], count) || count > fields.size() - pos) {
      return core::invalid("Invalid traceability collection size");
    }
    for (std::size_t i = 0; i < count; ++i) {
      auto reference = read_reference(fields[pos++]);
      if (!reference)
        return *reference.error_if();
      refs.push_back(std::move(*reference.value_if()));
    }
  }
  if (pos != fields.size() || result.validate() || result.canonical() != bytes) {
    return core::invalid("Invalid traceability");
  }
  return result;
}

inline core::Error evidence_error(std::string code, std::string message, bool unsupported = false) {
  return {unsupported ? core::ErrorCode::unavailable_capability : core::ErrorCode::invalid_argument,
          std::move(message),
          "TLC-FC-07-MESSAGE-002",
          {},
          {{"category", unsupported ? "unsupported_operation" : "invalid_input"},
           {"recoverability", unsupported ? "non_retryable" : "recoverable"},
           {"public_result", "no_partial_result"},
           {"failure_atomicity", "no_observable_partial_result"}},
          std::move(code)};
}

} // namespace detail

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

  // Internal, lossless structural encoding. No canonical wire format is prescribed.
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

  [[nodiscard]] static core::Result<UnevaluatedPreexistenceClaim> from_wire(std::string_view bytes);

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
  if (evidence.evaluation_requested) {
    return detail::evidence_error("OracleEvaluationRequested",
                                  "Scientific oracle evaluation is not supported", true);
  }
  const auto& source = evidence.source_reference;
  const bool authoritative_source =
      source.source_path == "maths/07-message/message.md" &&
      source.section == std::optional<std::string>("Nature du Message fondamental") &&
      source.subsection == std::optional<std::string>("Préexistence du Message") &&
      source.line_range == std::optional<shared::LineRange>(shared::LineRange{58, 60});

  if (evidence.feature_id != UnevaluatedPreexistenceClaim::feature_id() ||
      evidence.object_id != "TLC-SO-MESSAGE-013" ||
      (source.object_id && *source.object_id != evidence.object_id) || !authoritative_source ||
      source.validate() || evidence.opaque_statement.validate() ||
      evidence.opaque_statement.source_reference != source ||
      evidence.candidate_status != "unevaluated_candidate" ||
      !detail::valid_provenance(evidence.provenance, source)) {
    return detail::evidence_error("MissingPreexistenceEvidence",
                                  "Source evidence, identity or traceability is incomplete");
  }
  return UnevaluatedPreexistenceClaim(std::move(evidence));
}

inline core::Result<UnevaluatedPreexistenceClaim>
UnevaluatedPreexistenceClaim::from_wire(std::string_view bytes) {
  auto malformed = []() -> core::Result<UnevaluatedPreexistenceClaim> {
    return detail::evidence_error("MissingPreexistenceEvidence",
                                  "Invalid serialized preexistence evidence");
  };
  const auto decoded = shared::wire::decode(bytes, feature_id());
  if (!decoded)
    return malformed();
  const auto& fields = *decoded.value_if();
  if (fields.size() != 11 || fields[3] != representation() || fields[10] != verification_status()) {
    return malformed();
  }

  auto source = detail::read_reference(fields[6]);
  auto opaque = detail::read_opaque(fields[7]);
  auto provenance = detail::read_traceability(fields[8]);
  if (!source || !opaque || !provenance)
    return malformed();
  PreexistenceEvidence evidence{fields[4],
                                fields[5],
                                std::move(*source.value_if()),
                                std::move(*opaque.value_if()),
                                std::move(*provenance.value_if()),
                                fields[9],
                                false};
  auto result = register_message_preexistence_claim(std::move(evidence));
  if (!result || result.value_if()->canonical() != bytes)
    return malformed();
  return result;
}

} // namespace tllib::domains::message
