#!/bin/bash

# Save the root directory path
ROOT_DIR=$(pwd)

# Build vanishing_angle_cpp
cd src/SLDvec/skeleton/vanishing_angle_cpp
mkdir -p build && cd build                  # Create build directory    
cmake ..                                    # Configure with CMake
cmake --build . --config Release            # Build
cp *.so ../ 2>/dev/null || true             # Copy the built module to the root directory
cp Release/*.pyd ../ 2>/dev/null || true

# Build medial_axis_cpp
cd "$ROOT_DIR"                              # Return to root directory
cd src/SLDvec/skeleton/medial_axis_cpp
mkdir -p build && cd build                  # Create build directory   
cmake ..                                    # Configure with CMake  
cmake --build . --config Release            # Build
cp *.so ../ 2>/dev/null || true             # Copy the built module to the root directory
cp Release/*.pyd ../ 2>/dev/null || true