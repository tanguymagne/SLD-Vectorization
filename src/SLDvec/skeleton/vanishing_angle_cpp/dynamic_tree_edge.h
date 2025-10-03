// dynamic_tree_edge.h
#ifndef DYNAMICTREEEDGE_H
#define DYNAMICTREEEDGE_H

#include <limits>
#include <memory>
#include "dynamic_tree_node.h"

class DynamicTreeNode; // Forward declaration

/**
 * @brief A class representing an edge in a dynamic tree structure
 *
 * The DynamicTreeEdge class maintains information about connections between nodes
 * in a dynamic tree, including directional scores and costs between connected nodes.
 */
class DynamicTreeEdge
{
public:
    // Attributes
    std::weak_ptr<DynamicTreeNode> one;   ///< Weak pointer to the first node of the edge
    std::weak_ptr<DynamicTreeNode> other; ///< Weak pointer to the second node of the edge
    double one_to_other_score;            ///< Score value from first node to second node
    double one_to_other_cost;             ///< Cost value from first node to second node
    double other_to_one_score;            ///< Score value from second node to first node
    double other_to_one_cost;             ///< Cost value from second node to first node

    /**
     * @brief Constructs a new DynamicTreeEdge object
     *
     * @param one Shared pointer to the first node
     * @param other Shared pointer to the second node
     */
    DynamicTreeEdge(const std::shared_ptr<DynamicTreeNode> &one,
                    const std::shared_ptr<DynamicTreeNode> &other);

    /**
     * @brief Sets the score for the edge in the direction from the specified node
     *
     * @param node The node from which the score direction is considered
     * @param score The score value to set
     */
    void set_score(const std::shared_ptr<DynamicTreeNode> &node, double score);

    /**
     * @brief Sets the cost for the edge in the direction from the specified node
     *
     * @param node The node from which the cost direction is considered
     * @param cost The cost value to set
     */
    void set_cost(const std::shared_ptr<DynamicTreeNode> &node, double cost);

    /**
     * @brief Gets the node at the other end of the edge
     *
     * @param node The reference node
     * @return std::shared_ptr<DynamicTreeNode> Pointer to the other connected node
     */
    std::shared_ptr<DynamicTreeNode> get_other_node(const std::shared_ptr<DynamicTreeNode> &node) const;
};

#endif // DYNAMICTREEEDGE_H