// connected_component.h
#ifndef CONNECTED_COMPONENT_H
#define CONNECTED_COMPONENT_H

#include <unordered_map>
#include <vector>
#include <unordered_set>
#include <list>
#include <iostream>
#include "utils.h"

/**
 * @brief Helper function to find the root parent of a node in the disjoint set
 * @details Recursively finds and returns the root parent of a node while performing
 *          path compression for optimization.
 *
 * @param parent Reference to unordered map storing parent relationships
 * @param x Node index whose root parent needs to be found
 * @return int Index of the root parent
 */
inline int merge(std::unordered_map<int, int> &parent, int x)
{
    if (parent[x] == x)
    {
        return x;
    }
    return merge(parent, parent[x]);
}

/**
 * @brief Identifies all connected components in an undirected graph
 * @details Implementation based on union-find algorithm with path compression.
 *          Source: https://www.geeksforgeeks.org/connected-components-in-an-undirected-graph/
 *
 * @param nodes Reference to unordered map containing node information keyed by node index
 * @param edges Reference to unordered map containing edge information keyed by edge identifier
 * @return std::unordered_map<int, std::list<int>> Map of component parent indices to lists of node indices in that component
 */
std::unordered_map<int, std::list<int>> connectedComponent(std::unordered_map<int, NodeInfo> &nodes, std::unordered_map<std::string, EdgeInfo> &edges)
{
    std::unordered_map<int, int> parent;
    for (auto const &[idx, node] : nodes)
    {
        parent[idx] = idx;
    }

    // Loop to set parent of each nodes
    for (auto const &[key, edge] : edges)
    {
        parent[merge(parent, edge.node1)] = merge(parent, edge.node2);
    }

    // Loop to merge all component
    for (auto const &[idx, node] : nodes)
    {
        parent[idx] = merge(parent, parent[idx]);
    }

    // map to store the parent and the different connected component
    std::unordered_map<int, std::list<int>> connected_component;
    for (auto const &[idx, node] : nodes)
    {
        connected_component[parent[idx]].push_back(idx);
    }

    return connected_component;
}

#endif // CONNECTED_COMPONENT_H