# V1 — Official platform qualification and future targets (#260)

**Policy in force 2026-10-30.** A platform is promoted only when an
actual build, test run, CMake external-consumer install and native Python
wheel import have passed on its OS/architecture/interpreter. A GitHub
runner is **evidence for its tested image**, not proof of a minimum compiler
version or all future releases. `tllib` is at pre-1.0 foundation stage,
not a scientific V1 release.

| Level now | Environment | C++ / Python | Evidence and limits |
| --- | --- | --- | --- |
| **Tier 1 foundation** | Linux Ubuntu 24.04 x86-64 | runner GCC C++20, CPython 3.12 | Existing native CTest, external CMake consumer, wheel and provider/buffer/parity tests successful in PR #274–#279; exact toolchain emitted by future CI jobs |
| **Candidate only; NOT qualified** | Windows x86-64 | VS 2022 MSVC, CPython 3.12–3.14 | No native tests/wheel proof |
| **Candidate only; NOT qualified** | macOS arm64 | AppleClang, CPython 3.12–3.14 | No native tests/wheel proof |
| **Candidate only; NOT qualified** | Linux aarch64, macOS x86-64 | GCC/Clang or AppleClang | No native tests/wheel proof |
| **Experimental, no support** | musl, Windows arm64, GPU, CPython free-threaded, PyPy, abi3/abi3t | To be individually qualified | Unsupported |

No tested minimum C++ compiler version is inferred from an `ubuntu-latest`
image. Target minima GCC 13+, Clang 17+, VS 2022 17.8+, AppleClang 15+
are **design candidates** until native/packaging tests qualify them.

The wheel currently declares `requires-python >=3.12,<3.13`; a later
Python interpreter is NOT implicitly supported by its upstream release.
The general C++ bridge can compile under other environments, but that
is not wheel support. For future V1 release, qualify CPython 3.13 and
3.14, Windows and macOS before promotion. EOL interpreters are not
promoted by inertia. `abi3`, `abi3t`, subinterpreters and free-threading
remain experimental.

**CI scope:** PR fast Linux x86-64; native CMake consumer and ASan/UBSan
when code changes; Python wheel on same Tier 1 foundation;
pinned specs validation on tooling changes. No expensive Cartesian
matrix per PR. Nightly / release expansion belongs to #243/#11 and
cannot claim results not observed.

**Change control:** New tiers require published compilation, CTest,
consumer install, wheel import, callback/lifetime tests, platform
versions, ABI boundaries and release note via ADR-009/#14. Retiring
support requires a dated deprecation and migration guide.
