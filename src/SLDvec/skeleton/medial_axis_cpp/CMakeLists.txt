cmake_minimum_required(VERSION 3.15)
project(voronoi_pruning)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Include pybind11 directly from Python package
execute_process(
    COMMAND "${Python_EXECUTABLE}" -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
find_package(pybind11 CONFIG REQUIRED PATHS "${pybind11_DIR}")

# Collect all source files
set(SOURCES
    voronoi_pruning.cpp
)

# Create the Python module
pybind11_add_module(voronoi_pruning ${SOURCES})

# Enable optimization flags
target_compile_options(voronoi_pruning PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/O2>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-O3>
)

# Include directories
target_include_directories(voronoi_pruning PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)