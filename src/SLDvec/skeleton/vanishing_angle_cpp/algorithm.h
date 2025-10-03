#ifndef ALGORITHM_H
#define ALGORITHM_H

#include <memory>
#include <vector>
#include <deque>
#include <iostream>
#include <cmath>
#include <algorithm>
#include "dynamic_tree.h"

/**
 * @brief Algorithm class for processing dynamic trees
 *
 * This class implements algorithms for analyzing and manipulating dynamic tree structures,
 * particularly focusing on calculating alpha values and shrinking trees based on specific criteria.
 */
class Algorithm
{
private:
    /**
     * @brief Shrinks the tree based on the given alpha value and edge
     *
     * @param input_tree The dynamic tree to be shrunk
     * @param alpha The alpha value used for shrinking
     * @param min_edge The edge with minimum alpha value
     */
    void shrink_tree(
        DynamicTree &input_tree,
        double alpha,
        std::shared_ptr<DynamicTreeEdge> min_edge);

public:
    // Attributes
    DynamicTree tree;               ///< The dynamic tree being processed
    std::vector<double> alpha_list; ///< List of alpha values calculated during execution

    /**
     * @brief Constructs an Algorithm object with a given dynamic tree
     *
     * @param current_tree The dynamic tree to initialize with
     */
    Algorithm(const DynamicTree &current_tree);

    /**
     * @brief Executes the main algorithm on the input tree
     *
     * This method processes the input tree and returns a list of alpha values
     * that represent different stages of tree transformation.
     *
     * @param input_tree The dynamic tree to execute the algorithm on
     * @return std::vector<double> List of calculated alpha values
     */
    std::vector<double> execute(DynamicTree &input_tree);
};

#endif // ALGORITHM_H