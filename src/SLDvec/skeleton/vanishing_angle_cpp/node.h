#ifndef NODE_H
#define NODE_H

#include <vector>
#include <limits>
#include <memory>
#include <algorithm>

class Path; // Forward declaration

/**
 * @brief A class representing a node in a graph structure
 *
 * The Node class maintains information about a point in space along with its
 * connections and various properties used in path optimization algorithms.
 */
class Node
{
public:
    std::vector<double> point;              ///< Coordinates of the node in space
    bool is_core;                           ///< Flag indicating if this is a core node
    std::vector<std::weak_ptr<Path>> paths; ///< Collection of paths connected to this node
    int index;                              ///< Index of this node in the node collection
    bool taken;                             ///< Flag indicating if this node has been processed
    double bt;                              ///< Beginning time value for the node
    double radius;                          ///< Radius value used in calculations

    /**
     * @brief Constructs a new Node object
     *
     * @param point Vector containing the coordinates of the node
     */
    Node(const std::vector<double> &point);

    /**
     * @brief Calculates the end time (et) for the node
     *
     * @return double The end time value (bt + radius)
     */
    double et() const;

    /**
     * @brief Gets one path connected to this node
     *
     * @return std::shared_ptr<Path> Pointer to the first path, or nullptr if no paths exist
     */
    std::shared_ptr<Path> get_one_path() const;

    /**
     * @brief Adds a path to this node's collection
     *
     * @param path Shared pointer to the path to be added
     */
    void add_path(const std::shared_ptr<Path> &path);

    /**
     * @brief Removes a path from this node's collection
     *
     * @param path Shared pointer to the path to be removed
     */
    void remove_path(const std::shared_ptr<Path> &path);

    /**
     * @brief Checks if this node is isolated (has only one connection)
     *
     * @return bool True if the node has exactly one path, false otherwise
     */
    bool is_iso() const;

    /**
     * @brief Gets the node at the other end of the given path
     *
     * @param path Shared pointer to the path to follow
     * @return std::shared_ptr<Node> Pointer to the connected node
     */
    std::shared_ptr<Node> get_next(const std::shared_ptr<Path> &path) const;
};

#endif // NODE_H