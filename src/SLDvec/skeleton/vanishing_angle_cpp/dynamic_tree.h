// dynamic_tree.h
#ifndef DYNAMICTREE_H
#define DYNAMICTREE_H

#include <vector>
#include <iostream>
#include <memory>
#include "dynamic_tree_edge.h"
#include "dynamic_tree_node.h"

/**
 * @brief A class representing a dynamic tree structure
 *
 * The DynamicTree class manages a collection of nodes and edges that form
 * a dynamic tree structure, providing methods for tree manipulation and analysis.
 */
class DynamicTree
{
public:
    std::vector<std::shared_ptr<DynamicTreeNode>> nodes; ///< Collection of nodes in the tree
    std::vector<std::shared_ptr<DynamicTreeEdge>> edges; ///< Collection of edges in the tree

    /**
     * @brief Constructs a new DynamicTree with specified nodes and edges
     *
     * @param points Vector of point coordinates for each node
     * @param edge_index Vector of index pairs defining edge connections
     * @param reward_list Vector of reward values for each node
     * @param cost_list Vector of cost values for each node
     */
    DynamicTree(
        const std::vector<std::vector<double>> &points,
        std::vector<std::vector<int>> &edge_index,
        std::vector<double> &reward_list,
        std::vector<double> &cost_list);

    /**
     * @brief Constructs an empty DynamicTree
     */
    DynamicTree();

    /**
     * @brief Creates a deep copy of the current tree
     *
     * @return DynamicTree A new tree with copied nodes and edges
     */
    DynamicTree duplicate() const;

    /**
     * @brief Gets all leaf nodes in the tree
     *
     * A leaf node is defined as an unvisited node with fewer than 2 unvisited neighbors.
     *
     * @return std::vector<std::shared_ptr<DynamicTreeNode>> Vector of leaf nodes
     */
    std::vector<std::shared_ptr<DynamicTreeNode>> get_leaves() const;

    /**
     * @brief Adds a node to the tree
     *
     * @param node Shared pointer to the node to be added
     */
    void add_node(std::shared_ptr<DynamicTreeNode> node);

    /**
     * @brief Adds an edge to the tree
     *
     * @param edge Shared pointer to the edge to be added
     */
    void add_edge(std::shared_ptr<DynamicTreeEdge> edge);

    /**
     * @brief Prints a description of the tree structure
     */
    void describe() const;

    /**
     * @brief Checks if a specific edge exists in the tree
     *
     * @param edge Shared pointer to the edge to check
     * @return bool True if the edge exists, false otherwise
     */
    bool has_edge(const std::shared_ptr<DynamicTreeEdge> &edge) const;

    /**
     * @brief Generates a string representation of the tree
     *
     * @return std::string Detailed string description of all nodes and their properties
     */
    std::string to_string() const;
};

#endif // DYNAMICTREE_H