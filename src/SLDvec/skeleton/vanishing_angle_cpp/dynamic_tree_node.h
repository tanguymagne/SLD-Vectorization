// dynamic_tree_node.h
#ifndef DYNAMICTREENODE_H
#define DYNAMICTREENODE_H

#include <vector>
#include <memory>
#include <limits>
#include <cmath>
#include <iostream>
#include <map>
#include "dynamic_tree_edge.h"

class DynamicTreeEdge; // Forward declaration

/**
 * @brief A class representing a node in a dynamic tree structure
 *
 * The DynamicTreeNode class maintains information about a point in space along with
 * its properties such as rewards, costs, and connections to other nodes in the tree.
 */
class DynamicTreeNode
{
public:
    // Attributes
    std::vector<double> point;                         ///< Coordinates of the node in space
    double reward;                                     ///< Reward value associated with the node
    double cost;                                       ///< Current cost value of the node
    double initial_cost;                               ///< Initial cost value of the node
    bool visit_once;                                   ///< Flag indicating if node has been visited
    bool is_old_node;                                  ///< Flag indicating if this is an old node
    double score;                                      ///< Current score of the node
    double total_cost;                                 ///< Total accumulated cost at this node
    std::vector<std::weak_ptr<DynamicTreeEdge>> edges; ///< Collection of edges connected to this node
    int index;                                         ///< Index of this node in the node collection
    int path_index;                                    ///< Index of this node in the path
    double drop_threshold;                             ///< Threshold value for node dropping

    /**
     * @brief Constructs a new DynamicTreeNode object
     *
     * @param point Vector containing the coordinates of the node
     * @param r Initial reward value
     * @param c Initial cost value
     */
    DynamicTreeNode(const std::vector<double> &point, double r, double c);

    /**
     * @brief Adds an edge to this node's collection
     *
     * @param edge Shared pointer to the edge to be added
     */
    void add_edge(const std::shared_ptr<DynamicTreeEdge> &edge);

    /**
     * @brief Gets the node on the other side of the specified edge
     *
     * @param edge Shared pointer to the edge to follow
     * @return std::shared_ptr<DynamicTreeNode> Pointer to the connected node
     */
    std::shared_ptr<DynamicTreeNode> get_other_node(const std::shared_ptr<DynamicTreeEdge> &edge) const;

    /**
     * @brief Counts the number of unvisited neighboring nodes
     *
     * @return int Number of unvisited neighbors
     */
    int get_unvisited_neighbor_count() const;

    /**
     * @brief Gets the edge connecting this node to another specified node
     *
     * @param other_node Shared pointer to the node to find the edge to
     * @return std::shared_ptr<DynamicTreeEdge> Pointer to the connecting edge, or nullptr if not found
     */
    std::shared_ptr<DynamicTreeEdge> get_edge(const std::shared_ptr<DynamicTreeNode> &other_node) const;

    /**
     * @brief Updates the score of this node based on its visited neighbors
     *
     * Calculates and updates the score and total cost by considering all
     * visited neighboring nodes.
     */
    void set_score();
};

#endif // DYNAMICTREENODE_H