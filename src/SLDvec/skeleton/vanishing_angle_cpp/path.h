#ifndef PATH_H
#define PATH_H

#include <memory>
#include <vector>
#include "node.h"

/**
 * @brief A class representing a path between two nodes in a graph
 *
 * The Path class maintains information about a connection between two nodes,
 * including its length, angle, and various properties related to path optimization
 * and solution tracking.
 */
class Path
{
public:
    // The attributes
    std::weak_ptr<Node> one;   ///< Weak pointer to the first node of the path
    std::weak_ptr<Node> other; ///< Weak pointer to the second node of the path
    double length;             ///< Length of the path between the nodes
    double theta;              ///< Angle (theta) of the path
    bool is_core;              ///< Flag indicating if this is a core path
    bool in_sol;               ///< Flag indicating if this path is in the solution
    int tree_node_index;       ///< Index of this path in the tree node structure
    int path_index;            ///< Index of this path in the path collection
    double drop_threshold;     ///< Threshold value for path dropping

    /**
     * @brief Constructs a new Path object
     *
     * @param one Shared pointer to the first node
     * @param other Shared pointer to the second node
     * @param l Length of the path
     * @param angle Angle (theta) of the path
     */
    Path(const std::shared_ptr<Node> &one, const std::shared_ptr<Node> &other, double l, double angle) : one(one),
                                                                                                         other(other),
                                                                                                         length(l),
                                                                                                         theta(angle),
                                                                                                         is_core(true),
                                                                                                         in_sol(false),
                                                                                                         tree_node_index(-1),
                                                                                                         path_index(-1),
                                                                                                         drop_threshold(0)
    {
    }

    /**
     * @brief Calculates the midpoint of the path
     *
     * @return std::vector<double> A vector containing the x and y coordinates of the midpoint.
     *         Returns an empty vector if either node pointer is invalid.
     */
    std::vector<double> mid_point() const
    {
        std::shared_ptr<Node> one_ = this->one.lock();
        std::shared_ptr<Node> other_ = this->other.lock();

        if (one_ && other_)
        {
            return {
                (one_->point[0] + other_->point[0]) / 2,
                (one_->point[1] + other_->point[1]) / 2};
        }
        return {};
    }
};

#endif // PATH_H