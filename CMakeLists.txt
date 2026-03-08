cmake_minimum_required(VERSION 3.23)
project(cugrep LANGUAGES CXX CUDA)

# Force C++20 — libcudf headers require 'requires' keyword
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CUDA_STANDARD 20)
set(CMAKE_CUDA_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE Release)

find_package(CUDAToolkit REQUIRED)

find_package(cudf REQUIRED HINTS
    "/usr/local/lib/python3.12/dist-packages/libcudf/lib64/cmake/cudf"
    "/usr/local/lib/cmake/cudf"
)

find_library(KVIKIO_LIB kvikio
    HINTS
        "/usr/local/lib/python3.12/dist-packages/libkvikio/lib64"
        "/usr/local/lib/python3.12/dist-packages/libcudf/lib64"
        "/usr/local/lib"
)
message(STATUS "kvikio: ${KVIKIO_LIB}")

add_executable(cugrep
    src/main.cpp
    src/cugrep.cpp
    src/gpu_matcher.cu
    src/file_reader.cpp
)

target_include_directories(cugrep PRIVATE include/)

# Explicitly set C++20 on the target as well (belt + suspenders)
target_compile_features(cugrep PRIVATE cxx_std_20)

target_compile_options(cugrep PRIVATE
    $<$<COMPILE_LANGUAGE:CXX>:-std=c++20>
    $<$<COMPILE_LANGUAGE:CUDA>:-std=c++20>
)

target_link_libraries(cugrep PRIVATE
    cudf::cudf
    CUDA::cudart
    ${KVIKIO_LIB}
)

set_target_properties(cugrep PROPERTIES
    CUDA_SEPARABLE_COMPILATION ON
    CUDA_ARCHITECTURES "75"
)
