// voronoi_pruning.cpp
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include "utils.h"
#include "winding_number.h"
#include "connected_component.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;

bool are_adjacent(const int &idx_p1, const int &idx_p2, const std::pair<int, int> &range)
{
    // First verify that the two points are in the same range
    if (idx_p1 < range.first || idx_p1 > range.second)
    {
        return false;
    }
    if (idx_p2 < range.first || idx_p2 > range.second)
    {
        return false;
    }
    // Then check if they are adjacent
    // That is either the first and last point of the range
    if (idx_p1 == range.first && idx_p2 == range.second)
    {
        return true;
    }
    if (idx_p2 == range.first && idx_p1 == range.second)
    {
        return true;
    }
    // Or they are next to each other
    if (idx_p1 == idx_p2 + 1 || idx_p1 == idx_p2 - 1)
    {
        return true;
    }
    return false;
}

std::tuple<std::unordered_map<int, NodeInfo>, std::unordered_map<std::string, EdgeInfo>> voronoiPruning(
    const std::vector<std::pair<int, int>> &ridge_points,
    const std::vector<std::pair<int, int>> &ridge_vertices,
    const std::vector<std::pair<double, double>> &points,
    const std::vector<std::pair<double, double>> &vertices,
    const std::vector<std::vector<std::pair<double, double>>> &sample)
{
    std::vector<int> sample_size(sample.size(), 0);
    for (size_t i = 0; i < sample.size(); i++)
    {
        sample_size[i] = sample[i].size() - 1;
    }

    std::vector<int> cum_sample_size = cumSum(sample_size);

    std::vector<std::pair<int, int>> ranges(sample.size());
    for (size_t i = 0; i < sample.size(); i++)
    {
        if (i == 0)
        {
            ranges[i] = {0, cum_sample_size[i] - 1};
        }
        else
        {
            ranges[i] = {cum_sample_size[i - 1], cum_sample_size[i] - 1};
        }
    }

    std::unordered_map<int, NodeInfo> nodes;
    std::unordered_map<std::string, EdgeInfo> edges;

    for (size_t i = 0; i < ridge_points.size(); i++)
    {
        const std::pair<int, int> &pointidx = ridge_points[i];
        const std::pair<int, int> &vertexidx = ridge_vertices[i];

        int pointidx1 = pointidx.first;
        int pointidx2 = pointidx.second;
        int vertexidx1 = vertexidx.first;
        int vertexidx2 = vertexidx.second;

        bool skip = false;
        for (const std::pair<int, int> &range : ranges)
        {
            if (are_adjacent(pointidx1, pointidx2, range))
            {
                skip = true;
                break;
            }
        }
        if (skip)
        {
            continue;
        }

        const std::pair<double, double> &v1_pos = vertices[vertexidx1];
        const std::pair<double, double> &v2_pos = vertices[vertexidx2];

        // Check that both vertex indices are positive (not -1)
        // This is to ignore infinite segments as they can't be in the medial axis
        if (vertexidx1 >= 0 && vertexidx2 >= 0)
        {

            // Compute the object angle and add the edge
            std::pair<double, double> midpoint = {
                (v1_pos.first + v2_pos.first) / 2,
                (v1_pos.second + v2_pos.second) / 2};
            std::pair<double, double> v1 = {
                points[pointidx1].first - midpoint.first,
                points[pointidx1].second - midpoint.second};
            std::pair<double, double> v2 = {
                points[pointidx2].first - midpoint.first,
                points[pointidx2].second - midpoint.second};
            double object_angle = angleBetween(v1, v2) / 2;

            std::string edge = std::to_string(vertexidx1) + "-" + std::to_string(vertexidx2);
            edges[edge] = EdgeInfo{vertexidx1, vertexidx2, object_angle};

            // Add the vertices if not already added
            if (nodes.find(vertexidx1) == nodes.end())
            {
                double dist = distance(v1_pos, points[pointidx1]);
                nodes[vertexidx1] = NodeInfo{vertexidx1, v1_pos, dist, {vertexidx2}};
            }
            else
            {
                nodes[vertexidx1].connectedNodes.insert(vertexidx2);
            }

            if (nodes.find(vertexidx2) == nodes.end())
            {
                double dist = distance(v2_pos, points[pointidx1]);
                nodes[vertexidx2] = NodeInfo{vertexidx2, v2_pos, dist, {vertexidx1}};
            }
            else
            {
                nodes[vertexidx2].connectedNodes.insert(vertexidx1);
            }
        }
    }

    return {nodes, edges};
}

void medialAxisSelection(
    std::unordered_map<int, NodeInfo> &nodes,
    std::unordered_map<std::string, EdgeInfo> &edges,
    const std::vector<std::vector<std::pair<double, double>>> &sample)
{

    std::unordered_map<int, std::list<int>> connected_component = connectedComponent(nodes, edges);

    for (auto node_comp : connected_component)
    {
        std::pair<double, double> representative_p = nodes[node_comp.first].position;

        float w = 0;
        for (std::vector<std::pair<double, double>> curve_points : sample)
        {
            w += windingNumber(curve_points, representative_p);
        }

        // float error = round(w) - w; // Check that the winding number is close to an interger to make sure the curves are closed
        int w_ = (int)round(w);

        if (w_ % 2 == 0)
        {
            for (int node : node_comp.second)
            {
                std::unordered_set<int> connected_nodes = nodes[node].connectedNodes;
                for (int c : connected_nodes)
                {
                    nodes[c].connectedNodes.erase(node);

                    // Remove the edge from the edge list (try both names)
                    std::string e = std::to_string(node) + "-" + std::to_string(c);
                    if (edges.find(e) == edges.end())
                    {
                        e = std::to_string(c) + "-" + std::to_string(node);
                    }
                    edges.erase(e);
                }
                nodes.erase(node);
            }
        }
    }
}

std::tuple<std::unordered_map<int, NodeInfo>, std::unordered_map<std::string, EdgeInfo>> medialAxis(
    const std::vector<std::pair<int, int>> &ridge_points,
    const std::vector<std::pair<int, int>> &ridge_vertices,
    const std::vector<std::pair<double, double>> &points,
    const std::vector<std::pair<double, double>> &vertices,
    const std::vector<std::vector<std::pair<double, double>>> &sample)
{

    auto [nodes, edges] = voronoiPruning(ridge_points, ridge_vertices, points, vertices, sample);

    medialAxisSelection(nodes, edges, sample);

    return {nodes, edges};
}

PYBIND11_MODULE(voronoi_pruning, m)
{
    m.doc() = "A C++ fast implementation of Voronoi pruning to obtain the medial axis"; // optional module docstring

    py::class_<NodeInfo>(m, "NodeInfo")
        .def(py::init<int, std::pair<double, double>, double, std::unordered_set<int>>())
        .def_readwrite("idx", &NodeInfo::index)
        .def_readwrite("pos", &NodeInfo::position)
        .def_readwrite("dist", &NodeInfo::distance)
        .def_readwrite("connected", &NodeInfo::connectedNodes);

    py::class_<EdgeInfo>(m, "EdgeInfo")
        .def(py::init<int, int, double>())
        .def_readwrite("node1", &EdgeInfo::node1)
        .def_readwrite("node2", &EdgeInfo::node2)
        .def_readwrite("object_angle", &EdgeInfo::objectAngle);

    m.def("voronoiPruning", &voronoiPruning, "A function which computes the Voronoi pruning to obtain the medial axis",
          py::arg("ridge_points"), py::arg("ridge_vertices"), py::arg("points"), py::arg("vertices"), py::arg("sample"));

    m.def("medialAxis", &medialAxis, "A function which extracts the medial axis from the Voronoi diagram",
          py::arg("ridge_points"), py::arg("ridge_vertices"), py::arg("points"), py::arg("vertices"), py::arg("sample"));
}
