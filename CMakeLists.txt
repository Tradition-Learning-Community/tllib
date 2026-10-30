cmake_minimum_required(VERSION 3.27)
project(tllib VERSION 0.1.0 LANGUAGES CXX)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
include(CTest)

add_library(tllib_core INTERFACE)
add_library(tllib::core ALIAS tllib_core)
target_compile_features(tllib_core INTERFACE cxx_std_20)
target_include_directories(tllib_core INTERFACE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)
set_target_properties(tllib_core PROPERTIES EXPORT_NAME core)

install(TARGETS tllib_core EXPORT tllibTargets)
install(DIRECTORY include/tllib DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(EXPORT tllibTargets NAMESPACE tllib:: DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/tllib)
configure_package_config_file(cmake/tllibConfig.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/tllibConfig.cmake
  INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/tllib)
write_basic_package_version_file(${CMAKE_CURRENT_BINARY_DIR}/tllibConfigVersion.cmake
  VERSION ${PROJECT_VERSION} COMPATIBILITY SameMajorVersion)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/tllibConfig.cmake
  ${CMAKE_CURRENT_BINARY_DIR}/tllibConfigVersion.cmake
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/tllib)

if(BUILD_TESTING)
  add_executable(tllib_array_view_test tests/array_view_test.cpp)
  target_link_libraries(tllib_array_view_test PRIVATE tllib::core)
  if(MSVC)
    target_compile_options(tllib_array_view_test PRIVATE /W4 /WX)
  else()
    target_compile_options(tllib_array_view_test PRIVATE -Wall -Wextra -Wpedantic -Werror)
  endif()
  add_test(NAME tllib_array_view_test COMMAND tllib_array_view_test)
  find_package(Threads REQUIRED)
  add_executable(tllib_build_smoke tests/build_smoke.cpp)
  target_link_libraries(tllib_build_smoke PRIVATE tllib::core)
  if(MSVC)
    target_compile_options(tllib_build_smoke PRIVATE /W4 /WX)
  else()
    target_compile_options(tllib_build_smoke PRIVATE -Wall -Wextra -Wpedantic -Werror)
  endif()
  add_test(NAME tllib_build_smoke COMMAND tllib_build_smoke)
  add_executable(tllib_core_identity_test tests/core_identity_test.cpp)
  target_link_libraries(tllib_core_identity_test PRIVATE tllib::core)
  if(MSVC)
    target_compile_options(tllib_core_identity_test PRIVATE /W4 /WX)
  else()
    target_compile_options(tllib_core_identity_test PRIVATE -Wall -Wextra -Wpedantic -Werror)
  endif()
  add_test(NAME tllib_core_identity_test COMMAND tllib_core_identity_test)
  add_executable(tllib_shared_contracts_test tests/shared_contracts_test.cpp)
  target_link_libraries(tllib_shared_contracts_test PRIVATE tllib::core)
  if(MSVC)
    target_compile_options(tllib_shared_contracts_test PRIVATE /W4 /WX)
  else()
    target_compile_options(tllib_shared_contracts_test PRIVATE -Wall -Wextra -Wpedantic -Werror)
  endif()
  add_test(NAME tllib_shared_contracts_test COMMAND tllib_shared_contracts_test)
  add_executable(tllib_runtime_provider_test tests/runtime_provider_test.cpp)
  target_link_libraries(tllib_runtime_provider_test PRIVATE tllib::core Threads::Threads)
  if(MSVC)
    target_compile_options(tllib_runtime_provider_test PRIVATE /W4 /WX)
  else()
    target_compile_options(tllib_runtime_provider_test PRIVATE -Wall -Wextra -Wpedantic -Werror)
  endif()
  add_test(NAME tllib_runtime_provider_test COMMAND tllib_runtime_provider_test)
endif()

# Narrow CPython provider port bridge. No nanobind/pybind11 decision (#256).
option(TLLIB_BUILD_PYTHON_PROVIDER_BRIDGE "Build opt-in Python provider adapter" OFF)
if(TLLIB_BUILD_PYTHON_PROVIDER_BRIDGE)
  find_package(Python3 3.9 REQUIRED COMPONENTS Interpreter Development.Module)
  Python3_add_library(_native MODULE bindings/python/native/provider_bridge.cpp WITH_SOABI)
  target_link_libraries(_native PRIVATE tllib::core Python3::Module)
  target_compile_features(_native PRIVATE cxx_std_20)
  target_compile_definitions(_native PRIVATE TLLIB_PACKAGE_VERSION="\"${PROJECT_VERSION}\"")
  if(MSVC)
    target_compile_options(_native PRIVATE /W4 /WX)
  else()
    target_compile_options(_native PRIVATE -Wall -Wextra -Wpedantic -Werror)
  endif()
  set_target_properties(_native PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/python/tllib")
  install(TARGETS _native LIBRARY DESTINATION tllib RUNTIME DESTINATION tllib)
  install(FILES
    "${CMAKE_CURRENT_SOURCE_DIR}/bindings/python/tllib/__init__.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/bindings/python/tllib/__init__.pyi"
    "${CMAKE_CURRENT_SOURCE_DIR}/bindings/python/tllib/py.typed"
    DESTINATION tllib)
  file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/python/tllib")
  foreach(_file IN ITEMS __init__.py __init__.pyi py.typed)
    configure_file(
      "${CMAKE_CURRENT_SOURCE_DIR}/bindings/python/tllib/${_file}"
      "${CMAKE_CURRENT_BINARY_DIR}/python/tllib/${_file}" COPYONLY)
  endforeach()
  if(BUILD_TESTING)
    add_test(NAME tllib_python_provider_bridge
      COMMAND "${Python3_EXECUTABLE}" -m unittest discover
        -s "${CMAKE_CURRENT_SOURCE_DIR}/tests/python"
        -p "test_provider_bridge.py" -v)
    set_tests_properties(tllib_python_provider_bridge PROPERTIES
      ENVIRONMENT "PYTHONPATH=${CMAKE_CURRENT_BINARY_DIR}/python")
  endif()
endif()
