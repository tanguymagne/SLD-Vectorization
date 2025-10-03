#!/bin/bash

# Compile the C++ code
python_module_ext=$(python -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))');
c++ -O3 -Wall -shared -std=c++17 -fPIC $(python3 -m pybind11 --includes) voronoi_pruning.cpp -o voronoi_pruning$python_module_ext