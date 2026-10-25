cmake_minimum_required(VERSION 3.27)
project(tllib VERSION 0.0.0 LANGUAGES CXX)

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
endif()
