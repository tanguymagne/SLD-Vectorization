#include "node_path_graph.h"
#include <iostream>

/**
 * @brief Calculate 2D Euclidean distance between two points
 *
 * @param p1 First point as vector of doubles
 * @param p2 Second point as vector of doubles
 * @return double Distance between the points
 */
double dist2D(const std::vector<double> &p1, const std::vector<double> &p2)
{
    return hypot(p1[0] - p2[0], p1[1] - p2[1]);
}

NodePathGraph::NodePathGraph()
{
    this->nodes = std::vector<std::shared_ptr<Node>>();
    this->paths = std::vector<std::shared_ptr<Path>>();
}

NodePathGraph::NodePathGraph(
    const std::vector<std::vector<double>> &points,
    const std::vector<std::vector<int>> &edges,
    const std::vector<double> &angle)
{
    // Creates the nodes
    for (size_t pi = 0; pi < points.size(); pi++)
    {
        std::shared_ptr<Node> new_node = std::make_shared<Node>(points[pi]);
        new_node->index = pi;
        this->nodes.push_back(new_node);
    }

    // Creates the edges
    for (size_t ei = 0; ei < edges.size(); ei++)
    {
        std::vector<int> edge = edges[ei];
        double theta = angle[ei];
        int pid1 = edge[0];
        int pid2 = edge[1];

        double l = dist2D(points[pid1], points[pid2]);
        std::shared_ptr<Node> node1 = this->nodes[pid1];
        std::shared_ptr<Node> node2 = this->nodes[pid2];
        std::shared_ptr<Path> new_path = std::make_shared<Path>(node1, node2, l, theta);

        node1->add_path(new_path);
        node2->add_path(new_path);
        this->paths.push_back(new_path);

        new_path->path_index = this->paths.size() - 1;
    }

    this->burn();
}

void NodePathGraph::burn()
{
    std::vector<std::shared_ptr<Node>> degree_ones = this->get_degree_ones();
    std::deque<std::shared_ptr<Node>> queue;

    for (const std::shared_ptr<Node> &node : degree_ones)
    {
        queue.push_back(node);
    }

    while (!queue.empty())
    {
        std::shared_ptr<Node> target_node = queue.front();
        queue.pop_front();

        std::shared_ptr<Path> path = target_node->get_one_path();
        if (path == nullptr)
        {
            continue;
        }

        path->is_core = false;
        std::shared_ptr<Node> next_node = target_node->get_next(path);
        next_node->remove_path(path);
        if (next_node->is_iso())
        {
            queue.push_back(next_node);
        }
    }

    this->reset_paths();
}

std::vector<std::shared_ptr<Node>> NodePathGraph::get_degree_ones() const
{
    std::vector<std::shared_ptr<Node>> degree_ones;
    for (const std::shared_ptr<Node> &node : this->nodes)
    {
        if (node->is_iso())
        {
            degree_ones.push_back(node);
        }
    }
    return degree_ones;
}

void NodePathGraph::reset_paths()
{
    for (const std::shared_ptr<Path> &path : this->paths)
    {
        path->one.lock()->add_path(path);
        path->other.lock()->add_path(path);
    }
}

std::vector<NodePathGraph> NodePathGraph::to_components()
{
    std::vector<NodePathGraph> graph_list;

    for (const std::shared_ptr<Node> &node : this->nodes)
    {
        if (!node->taken)
        {
            NodePathGraph curr_graph;

            std::deque<std::shared_ptr<Node>> queue;
            queue.push_back(node);
            node->taken = true;

            std::vector<std::shared_ptr<Node>> old_node_list;
            std::vector<std::shared_ptr<Node>> new_node_list;
            std::vector<std::shared_ptr<Path>> old_path_list;

            // BFS to find all connected components
            while (!queue.empty())
            {
                std::shared_ptr<Node> curr_node = queue.front();
                queue.pop_front();
                old_node_list.push_back(curr_node);

                std::shared_ptr<Node> new_node = std::make_shared<Node>(curr_node->point);
                new_node->index = curr_node->index;
                new_node_list.push_back(new_node);

                curr_graph.nodes.push_back(new_node);

                // Spread to the neighbors
                for (const std::weak_ptr<Path> &weak_path : curr_node->paths)
                {
                    if (std::shared_ptr<Path> path = weak_path.lock())
                    {
                        std::shared_ptr<Node> next_node = curr_node->get_next(path);

                        if (!next_node->taken)
                        {
                            queue.push_back(next_node);
                            next_node->taken = true;
                            old_path_list.push_back(path);
                        }
                    }
                }
            }

            for (const std::shared_ptr<Path> &old_path : old_path_list)
            {
                std::shared_ptr<Node> old_node_one = old_path->one.lock();
                std::shared_ptr<Node> old_node_other = old_path->other.lock();

                int one_index = std::distance(old_node_list.begin(),
                                              std::find(old_node_list.begin(), old_node_list.end(), old_node_one));
                int other_index = std::distance(old_node_list.begin(),
                                                std::find(old_node_list.begin(), old_node_list.end(), old_node_other));

                std::shared_ptr<Node> new_node_one = new_node_list[one_index];
                std::shared_ptr<Node> new_node_other = new_node_list[other_index];

                std::shared_ptr<Path> new_path = std::make_shared<Path>(
                    new_node_one, new_node_other, old_path->length, old_path->theta);
                new_path->path_index = old_path->path_index;

                new_node_one->add_path(new_path);
                new_node_other->add_path(new_path);

                curr_graph.paths.push_back(new_path);
            }

            curr_graph.burn();
            graph_list.push_back(curr_graph);
        }
    }
    return graph_list;
}

DynamicTree NodePathGraph::to_dynamic_tree_junction()
{
    double total_reward = 0.0;
    double min_cost = std::numeric_limits<double>::infinity();

    DynamicTree dynamic_tree = DynamicTree();

    for (const std::shared_ptr<Node> &node : this->nodes)
    {
        node->is_core = false;
    }

    std::vector<std::shared_ptr<Node>> core_nodes;
    double core_node_x = 0;
    double core_node_y = 0;

    for (const std::shared_ptr<Path> &path : this->paths)
    {
        total_reward += sin(path->theta) * path->length;
        min_cost = std::min(min_cost, path->length);
        if (path->is_core)
        {
            path->one.lock()->is_core = true;
            path->other.lock()->is_core = true;

            path->tree_node_index = 0;
        }
    }

    for (const std::shared_ptr<Node> &node : this->nodes)
    {
        if (node->is_core)
        {
            core_nodes.push_back(node);
            core_node_x += node->point[0];
            core_node_y += node->point[1];
        }
    }

    std::shared_ptr<DynamicTreeNode> core_node = nullptr;
    if (!core_nodes.empty())
    {
        std::shared_ptr<DynamicTreeNode> core_node = std::make_shared<DynamicTreeNode>(
            std::vector<double>{core_node_x / core_nodes.size(), core_node_y / core_nodes.size()},
            total_reward,
            min_cost);
        dynamic_tree.add_node(core_node);
        core_node->path_index = -2;
    }

    std::unordered_map<std::shared_ptr<Path>, std::shared_ptr<DynamicTreeNode>> path_to_node;

    for (const std::shared_ptr<Path> &path : this->paths)
    {
        if (!(path->is_core))
        {
            std::shared_ptr<DynamicTreeNode> new_node = std::make_shared<DynamicTreeNode>(
                path->mid_point(),
                sin(path->theta) * path->length,
                path->length);

            if (path->length == 0)
            {
                std::cout << "Error: path length is 0" << std::endl;
            }

            dynamic_tree.add_node(new_node);

            new_node->path_index = path->path_index;
            path->tree_node_index = new_node->index;
            path_to_node[path] = new_node;
        }
    }

    for (const std::shared_ptr<Node> &node : this->nodes)
    {
        std::vector<std::shared_ptr<Path>> non_core_path;
        int core_count = 0;
        for (const std::weak_ptr<Path> &weak_path : node->paths)
        {
            if (std::shared_ptr<Path> path = weak_path.lock())
            {
                if (!path->is_core)
                {
                    non_core_path.push_back(path);
                }
                else
                {
                    core_count++;
                }
            }
        }

        if (core_count != 0 && non_core_path.size() < 1)
        {
            continue;
        }
        else if (core_count != 0 && non_core_path.size() == 1)
        {
            std::shared_ptr<Path> path = non_core_path[0];
            std::shared_ptr<DynamicTreeEdge> new_edge = std::make_shared<DynamicTreeEdge>(
                path_to_node[path],
                core_node);
            dynamic_tree.add_edge(new_edge);
        }
        else if (core_count != 0 && non_core_path.size() > 1)
        {
            std::shared_ptr<DynamicTreeNode> junction_node = std::make_shared<DynamicTreeNode>(
                node->point,
                0,
                0);
            dynamic_tree.add_node(junction_node);

            std::shared_ptr<DynamicTreeEdge> new_edge = std::make_shared<DynamicTreeEdge>(
                junction_node,
                core_node);
            dynamic_tree.add_edge(new_edge);

            for (const std::shared_ptr<Path> &path : non_core_path)
            {
                std::shared_ptr<DynamicTreeEdge> new_edge = std::make_shared<DynamicTreeEdge>(
                    path_to_node[path],
                    junction_node);
                dynamic_tree.add_edge(new_edge);
            }
        }
        else if (core_count == 0 && non_core_path.size() <= 1)
        {
            continue;
        }
        else if (core_count == 0 && non_core_path.size() == 2)
        {
            std::shared_ptr<Path> path1 = non_core_path[0];
            std::shared_ptr<Path> path2 = non_core_path[1];
            std::shared_ptr<DynamicTreeEdge> new_edge = std::make_shared<DynamicTreeEdge>(
                path_to_node[path1],
                path_to_node[path2]);
            dynamic_tree.add_edge(new_edge);
        }
        else if (core_count == 0 && non_core_path.size() > 2)
        {
            std::shared_ptr<DynamicTreeNode> junction_node = std::make_shared<DynamicTreeNode>(
                node->point,
                0,
                0);
            dynamic_tree.add_node(junction_node);

            for (const std::shared_ptr<Path> &path : non_core_path)
            {
                std::shared_ptr<DynamicTreeEdge> new_edge = std::make_shared<DynamicTreeEdge>(
                    junction_node,
                    path_to_node[path]);
                dynamic_tree.add_edge(new_edge);
            }
        }
    }
    return dynamic_tree;
}