#pragma once
#include <tllib/core/result.hpp>
#include <array>
#include <limits>
#include <string>
#include <string_view>
#include <utility>
namespace tllib::core {
class FeatureId {
 public:
  static Result<FeatureId> parse(std::string_view text) {
    if (!text.starts_with("TLC-FC-")) return error();
    text.remove_prefix(7);
    if (text.size() < 8 || !digit(text[0]) || !digit(text[1]) || text[2] != '-') return error();
    const auto sep = text.rfind('-');
    if (sep == std::string_view::npos || sep < 4 || sep + 4 != text.size() || text[sep-1] == '-' || text[3] < 'A' || text[3] > 'Z') return error();
    for (std::size_t i=3; i<sep; ++i) {
      const char c=text[i];
      if (!((c>='A' && c<='Z') || (c>='0' && c<='9') || (c=='-' && text[i-1]!='-'))) return error();
    }
    for (std::size_t i=sep+1; i<text.size(); ++i) if (!digit(text[i])) return error();
    return FeatureId("TLC-FC-"+std::string(text));
  }
  [[nodiscard]] const std::string& str() const noexcept { return value_; }
  friend bool operator==(const FeatureId&, const FeatureId&) = default;
 private:
  explicit FeatureId(std::string value):value_(std::move(value)){}
  static bool digit(char c) noexcept { return c>='0' && c<='9'; }
  static Error error() { return {ErrorCode::invalid_identifier,"Invalid TLC-FC identifier",{}, {}}; }
  std::string value_;
};
class DomainId {
 public:
  static Result<DomainId> parse(std::string_view text) {
    if (text.empty()) return Error{ErrorCode::invalid_identifier,"Empty domain identifier",{}, {}};
    bool dash=true;
    for(char c:text) {
      if(c=='-') { if(dash) return Error{ErrorCode::invalid_identifier,"Invalid separator",{}, {}}; dash=true; }
      else { if(!((c>='a'&&c<='z')||(c>='0'&&c<='9'))) return Error{ErrorCode::invalid_identifier,"Invalid domain character",{}, {}}; dash=false; }
    }
    if(dash) return Error{ErrorCode::invalid_identifier,"Trailing separator",{}, {}};
    return DomainId(std::string(text));
  }
  [[nodiscard]] const std::string& str() const noexcept { return value_; }
  friend bool operator==(const DomainId&, const DomainId&) = default;
 private:
  explicit DomainId(std::string value):value_(std::move(value)){}
  std::string value_;
};
struct Version {
  unsigned major{}, minor{}, patch{};
  static Result<Version> parse(std::string_view text) {
    std::array<unsigned,3> parts{};
    for (unsigned i=0;i<3;++i) {
      const auto dot=text.find('.');
      const auto piece=text.substr(0,dot);
      if(piece.empty() || (piece.size()>1 && piece[0]=='0')) return invalid("Invalid version");
      unsigned value=0;
      for(char c:piece) { if(c<'0'||c>'9'||value>(std::numeric_limits<unsigned>::max()-unsigned(c-'0'))/10) return invalid("Invalid version"); value=value*10+unsigned(c-'0'); }
      parts[i]=value;
      if(i<2) { if(dot==std::string_view::npos) return invalid("Invalid version"); text.remove_prefix(dot+1); }
      else if(dot!=std::string_view::npos) return invalid("Invalid version");
    }
    return Version{parts[0],parts[1],parts[2]};
  }
  [[nodiscard]] std::string str() const { return std::to_string(major)+"."+std::to_string(minor)+"."+std::to_string(patch); }
  friend bool operator==(const Version&, const Version&) = default;
};
class Fingerprint {
 public:
  static Result<Fingerprint> parse(std::string_view text) {
    if(text.size()!=40 && text.size()!=64) return Error{ErrorCode::invalid_identifier,"Fingerprint must be SHA-1 or SHA-256 hex",{}, {}};
    for(char c:text) if(!((c>='0'&&c<='9')||(c>='a'&&c<='f'))) return Error{ErrorCode::invalid_identifier,"Invalid fingerprint hex",{}, {}};
    return Fingerprint(std::string(text));
  }
  [[nodiscard]] const std::string& str() const noexcept {return value_;}
  friend bool operator==(const Fingerprint&,const Fingerprint&) = default;
 private:
  explicit Fingerprint(std::string value):value_(std::move(value)){}
  std::string value_;
};
enum class PackageStatus { draft, pilot, validated, finalized, deprecated, superseded };
enum class ScientificStatus { defined, partially_defined, preserved_unresolved, external_provider_required, not_applicable };
enum class ExecutionStatus { structural_only, executable, conditionally_executable, unsupported };
} // namespace tllib::core
