#ifndef NODE_PATH_GRAPH_H
#define NODE_PATH_GRAPH_H

#include <vector>
#include <memory>
#include <deque>
#include <cmath>
#include <unordered_map>
#include "node.h"
#include "path.h"
#include "dynamic_tree.h"
#include "dynamic_tree_node.h"
#include "dynamic_tree_edge.h"

/**
 * @brief A graph structure composed of nodes and paths
 *
 * This class represents a graph where vertices are represented by Node objects
 * and edges are represented by Path objects. The graph can be manipulated
 * and transformed into different representations.
 */
class NodePathGraph
{
public:
    std::vector<std::shared_ptr<Node>> nodes; ///< Collection of nodes in the graph
    std::vector<std::shared_ptr<Path>> paths; ///< Collection of paths connecting the nodes

    /**
     * @brief Default constructor
     */
    NodePathGraph();

    /**
     * @brief Constructs a graph from points, edges, and angles
     *
     * @param points Vector of 2D points representing node positions
     * @param edges Vector of integer pairs representing node connections
     * @param angle Vector of angles corresponding to each edge
     */
    NodePathGraph(
        const std::vector<std::vector<double>> &points,
        const std::vector<std::vector<int>> &edges,
        const std::vector<double> &angle);

    /**
     * @brief Marks non-core paths in the graph
     *
     * This method identifies and marks paths that are not part of the core
     * structure of the graph.
     */
    void burn();

    /**
     * @brief Gets nodes with degree one
     *
     * @return Vector of nodes that have exactly one connection
     */
    std::vector<std::shared_ptr<Node>> get_degree_ones() const;

    /**
     * @brief Resets all paths in the graph
     *
     * Reestablishes connections between nodes and paths to their original state.
     */
    void reset_paths();

    /**
     * @brief Splits the graph into connected components
     *
     * @return Vector of NodePathGraph objects, each representing a connected component
     */
    std::vector<NodePathGraph> to_components();

    /**
     * @brief Converts the graph to a dynamic tree structure with junctions
     *
     * @return DynamicTree representation of the graph
     */
    DynamicTree to_dynamic_tree_junction();
};

#endif // NODE_PATH_GRAPH_H