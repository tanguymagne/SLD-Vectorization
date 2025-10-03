// utils.h
#ifndef UTILS_H
#define UTILS_H

#include <vector>
#include <cmath>
#include <algorithm>
#include <tuple>
#include <unordered_set>

/**
 * @brief Stores information about a node in a graph structure
 *
 * Contains the node's index, position in 2D space, distance to the shape outline value,
 * and a set of connected node indices.
 */
struct NodeInfo
{
    int index;                              ///< Index identifier of the node
    std::pair<double, double> position;     ///< 2D position coordinates (x, y)
    double distance;                        ///< Distance value associated with the node
    std::unordered_set<int> connectedNodes; ///< Set of indices of connected nodes
};

/**
 * @brief Stores information about an edge between two nodes
 *
 * Contains the indices of the two connected nodes and the angle
 * form by the vectors from the midpoint to the shape outline.
 */
struct EdgeInfo
{
    int node1;          ///< Index of the first node
    int node2;          ///< Index of the second node
    double objectAngle; ///< Angle of the object associated with this edge
};

/**
 * @brief Normalize a given 2D vector
 *
 * @param p Input vector as a pair of coordinates (x, y)
 * @return std::pair<double, double> Normalized vector with magnitude 1
 */
inline std::pair<double, double> normalizeVector(const std::pair<double, double> &p)
{
    double norm = std::hypot(p.first, p.second);
    return {p.first / norm, p.second / norm};
}

/**
 * @brief Calculates the angle between two 2D vectors
 *
 * @param vec1 First vector as a pair of coordinates (x, y)
 * @param vec2 Second vector as a pair of coordinates (x, y)
 * @return double Angle between the vectors in radians [0, π]
 */
inline double angleBetween(const std::pair<double, double> &vec1, const std::pair<double, double> &vec2)
{
    std::pair<double, double> normalizedVec1 = normalizeVector(vec1);
    std::pair<double, double> normalizedVec2 = normalizeVector(vec2);
    double dotProduct = normalizedVec1.first * normalizedVec2.first + normalizedVec1.second * normalizedVec2.second;
    dotProduct = std::clamp(dotProduct, -1.0, 1.0);
    return std::acos(dotProduct);
}

/**
 * @brief Calculates the Euclidean distance between two points in 2D space
 *
 * @param p1 First point as a pair of coordinates (x, y)
 * @param p2 Second point as a pair of coordinates (x, y)
 * @return double Euclidean distance between the points
 */
inline double distance(const std::pair<double, double> &p1, const std::pair<double, double> &p2)
{
    return std::hypot(p1.first - p2.first, p1.second - p2.second);
}

/**
 * @brief Calculates the cumulative sum of a vector of integers
 *
 * @param v Input vector of integers
 * @return std::vector<int> Vector containing cumulative sums where each element
 *         is the sum of all previous elements including itself
 */
inline std::vector<int> cumSum(const std::vector<int> &v)
{
    std::vector<int> res;
    res.reserve(v.size());
    res.push_back(v[0]);
    for (size_t i = 1; i < v.size(); i++)
    {
        res.push_back(res[i - 1] + v[i]);
    }
    return res;
}

#endif // UTILS_H