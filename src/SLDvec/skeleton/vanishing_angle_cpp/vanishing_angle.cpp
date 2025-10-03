#include <vector>
#include <iostream>
#include "algorithm.h"
#include "node_path_graph.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;

/**
 * @brief Compute vanishing angles for a medial axis
 *
 * This function processes a medial axis graph defined by points, edges, and angles
 * to compute vanishing angles that represent the significance of each edge.
 *
 * @param points Vector of 2D points representing node positions
 * @param edges Vector of integer pairs representing edge connections
 * @param angle Vector of angles corresponding to each edge
 * @return std::vector<float> Vector of vanishing angles for each edge
 */
std::vector<float> vanishingAngle(
    const std::vector<std::vector<double>> &points,
    const std::vector<std::vector<int>> &edges,
    const std::vector<double> &angle)
{

    NodePathGraph initial_graph = NodePathGraph(points, edges, angle);
    std::vector<NodePathGraph> components = initial_graph.to_components();

    for (NodePathGraph &component : components)
    {

        DynamicTree dynamic_tree = component.to_dynamic_tree_junction();
        Algorithm new_algo = Algorithm(dynamic_tree);
        new_algo.execute(dynamic_tree);

        for (std::shared_ptr<DynamicTreeNode> node : new_algo.tree.nodes)
        {
            if (node->path_index >= 0)
            {
                initial_graph.paths[node->path_index]->drop_threshold = node->drop_threshold;
            }
        }
    }

    std::vector<float> vanishing_angles;
    for (const std::shared_ptr<Path> &path : initial_graph.paths)
    {
        if (path->is_core)
        {
            vanishing_angles.push_back(1.0);
        }
        else
        {
            vanishing_angles.push_back(path->drop_threshold);
        }
    }
    return vanishing_angles;
}

PYBIND11_MODULE(vanishing_angle, m)
{
    m.doc() = "A C++ fast implementation of vanishing angle computation of medial axis.";

    m.def("vanishingAngle", &vanishingAngle,
          "Compute vanishing angles for edges in a medial axis graph\n\n"
          "Args:\n"
          "    points (List[List[float]]): List of 2D points representing node positions\n"
          "    edges (List[List[int]]): List of integer pairs representing edge connections\n"
          "    angle (List[float]): List of angles corresponding to each edge\n"
          "    timed (bool, optional): Enable timing measurements. Defaults to False\n\n"
          "Returns:\n"
          "    List[float]: List of vanishing angles for each edge",
          py::arg("points"),
          py::arg("edges"),
          py::arg("angle"));
}