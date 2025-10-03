// dynamic_tree.cpp
#include "dynamic_tree.h"

DynamicTree::DynamicTree(
    const std::vector<std::vector<double>> &points,
    std::vector<std::vector<int>> &edge_index,
    std::vector<double> &reward_list,
    std::vector<double> &cost_list)
{
    // Create the nodes
    for (size_t i = 0; i < points.size(); i++)
    {
        std::shared_ptr<DynamicTreeNode> new_node = std::make_shared<DynamicTreeNode>(points[i], reward_list[i], cost_list[i]);
        this->nodes.push_back(new_node);
    }

    // Create the edges
    for (size_t i = 0; i < edge_index.size(); i++)
    {
        int first_index = edge_index[i][0];
        int second_index = edge_index[i][1];
        std::shared_ptr<DynamicTreeEdge> new_edge = std::make_shared<DynamicTreeEdge>(this->nodes[first_index], this->nodes[second_index]);
        this->edges.push_back(new_edge);

        this->nodes[first_index]->add_edge(new_edge);
        this->nodes[second_index]->add_edge(new_edge);
    }
}

DynamicTree::DynamicTree()
{
    nodes = std::vector<std::shared_ptr<DynamicTreeNode>>();
    edges = std::vector<std::shared_ptr<DynamicTreeEdge>>();
}

DynamicTree DynamicTree::duplicate() const
{
    DynamicTree new_tree;

    for (const std::shared_ptr<DynamicTreeNode> &node : this->nodes)
    {
        std::shared_ptr<DynamicTreeNode> new_node = std::make_shared<DynamicTreeNode>(node->point, node->reward, node->cost);
        new_tree.add_node(new_node);
        new_node->path_index = node->path_index;
    }

    for (const std::shared_ptr<DynamicTreeEdge> &edge : this->edges)
    {
        std::shared_ptr<DynamicTreeEdge> new_edge = std::make_shared<DynamicTreeEdge>(
            new_tree.nodes[edge->one.lock()->index],
            new_tree.nodes[edge->other.lock()->index]);
        new_tree.add_edge(new_edge);
    }

    return new_tree;
}

std::vector<std::shared_ptr<DynamicTreeNode>> DynamicTree::get_leaves() const
{
    std::vector<std::shared_ptr<DynamicTreeNode>> leaves;

    for (const std::shared_ptr<DynamicTreeNode> &node : this->nodes)
    {
        if (node->visit_once)
        {
            continue;
        }
        if (node->get_unvisited_neighbor_count() < 2)
        {
            leaves.push_back(node);
        }
    }

    return leaves;
}

void DynamicTree::add_node(std::shared_ptr<DynamicTreeNode> node)
{
    node->index = this->nodes.size();
    this->nodes.push_back(std::move(node));
}

void DynamicTree::add_edge(std::shared_ptr<DynamicTreeEdge> edge)
{
    edge->one.lock()->add_edge(edge);
    edge->other.lock()->add_edge(edge);
    this->edges.push_back(std::move(edge));
}

void DynamicTree::describe() const
{
    std::cout << "There are " << this->nodes.size() << " nodes" << std::endl;
    std::cout << "There are " << this->edges.size() << " edges" << std::endl;
}

bool DynamicTree::has_edge(const std::shared_ptr<DynamicTreeEdge> &edge) const
{
    std::vector<double> point1 = edge->one.lock()->point;
    std::vector<double> point2 = edge->other.lock()->point;
    for (const std::shared_ptr<DynamicTreeEdge> &e : this->edges)
    {
        if ((e->one.lock()->point[0] == point1[0] && e->one.lock()->point[1] == point1[1] &&
             e->other.lock()->point[0] == point2[0] && e->other.lock()->point[1] == point2[1]) ||
            (e->one.lock()->point[0] == point2[0] && e->one.lock()->point[1] == point2[1] &&
             e->other.lock()->point[0] == point1[0] && e->other.lock()->point[1] == point1[1]))
        {
            return true;
        }
    }
    return false;
}

std::string DynamicTree::to_string() const
{
    std::string str = "";
    for (const std::shared_ptr<DynamicTreeNode> &node : this->nodes)
    {
        std::string p_str = std::to_string(node->point[0]) + ", " + std::to_string(node->point[1]);
        str += "Node: " + p_str + "'s reward is " + std::to_string(node->reward) + "\n";
        str += "Node: " + p_str + "'s cost is " + std::to_string(node->cost) + "\n";
    }
    return str;
}