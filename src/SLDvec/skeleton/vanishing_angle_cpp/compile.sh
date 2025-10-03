#!/bin/bash

# Compile the C++ code
python_module_ext=$(python -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))');
c++ -O3 -Wall -shared -std=c++17 -fPIC $(python3 -m pybind11 --includes) algorithm.cpp dynamic_tree_edge.cpp dynamic_tree_node.cpp dynamic_tree.cpp node_path_graph.cpp node.cpp vanishing_angle.cpp -o vanishing_angle$python_module_ext