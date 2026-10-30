# Development quality gates — #249

Small C++20 native build (no downloads by CMake):

```sh
cmake -S . -B build/native -DBUILD_TESTING=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build/native --parallel 2
ctest --test-dir build/native --output-on-failure
```

Formatting and lint prerequisites: `clang-format 18.1.8`, `ruff 0.14.1`,
`clang-tidy-18` (or distro equivalent). Changed-line gate:

```sh
python3 tools/quality_check.py --base HEAD^
clang-tidy-18 -p build/native -checks=-*,clang-analyzer-* -warnings-as-errors=* tests/build_smoke.cpp
```

Policy: `.clang-format` is authoritative for C++ files; `ruff.toml`
for Python. Added Python files undergo formatter and lint; edited Python
files undergo lint; changed C++ line ranges undergo clang-format checking.
This permits migration without a giant cosmetic reformat of legacy code.
Do not add blanket suppression of errors: fix the precise defect.
Future domain code follows these same rules.

`-Wall -Wextra -Wpedantic -Werror` apply to **our targets**, `/W4 /WX`
on MSVC. Dependencies never inherit these flags. The native core is header
only, and CTest/standard-library assertions are the selected framework:
no new GoogleTest download or duplicated test harness.

Existing categories: unit (identity, ArrayView, shared contracts),
integration (providers, callbacks, CMake consumer, wheel),
structural conformance (pinned specs), negative tests and C++/Python parity.
No scientific execution claims. Local tests are runnable without GitHub.
