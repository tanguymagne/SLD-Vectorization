// dynamic_tree_node.cpp
#include "dynamic_tree_edge.h"
#include "dynamic_tree_node.h"

DynamicTreeNode::DynamicTreeNode(const std::vector<double> &point, double r, double c) : point(point),
                                                                                         reward(r),
                                                                                         cost(c),
                                                                                         initial_cost(c),
                                                                                         visit_once(false),
                                                                                         is_old_node(false),
                                                                                         score(r),
                                                                                         total_cost(c),
                                                                                         index(-1),
                                                                                         path_index(-1),
                                                                                         drop_threshold(std::numeric_limits<double>::infinity())
{
}

void DynamicTreeNode::add_edge(const std::shared_ptr<DynamicTreeEdge> &edge)
{
    (this->edges).push_back(edge);
}

std::shared_ptr<DynamicTreeNode> DynamicTreeNode::get_other_node(const std::shared_ptr<DynamicTreeEdge> &edge) const
{
    return (this == edge->one.lock().get()) ? edge->other.lock() : edge->one.lock();
}

int DynamicTreeNode::get_unvisited_neighbor_count() const
{
    int count = 0;
    for (const std::weak_ptr<DynamicTreeEdge> &weak_edge : this->edges)
    {
        if (auto edge = weak_edge.lock())
        {
            if (!(this->get_other_node(edge)->visit_once))
            {
                count++;
            }
        }
    }
    return count;
}

std::shared_ptr<DynamicTreeEdge> DynamicTreeNode::get_edge(const std::shared_ptr<DynamicTreeNode> &other_node) const
{
    for (const std::weak_ptr<DynamicTreeEdge> &weak_edge : this->edges)
    {
        if (auto edge = weak_edge.lock())
        {
            if (this->get_other_node(edge) == other_node)
            {
                return edge;
            }
        }
    }
    std::cerr << "Error: edge not found" << std::endl;
    return nullptr;
}

void DynamicTreeNode::set_score()
{
    for (const std::weak_ptr<DynamicTreeEdge> &weak_edge : this->edges)
    {
        if (auto edge = weak_edge.lock())
        {
            std::shared_ptr<DynamicTreeNode> temp_node = this->get_other_node(edge);
            if (temp_node->visit_once)
            {
                edge->set_score(temp_node, temp_node->score);
                edge->set_cost(temp_node, temp_node->total_cost);
                this->score += temp_node->score;
                this->total_cost += temp_node->total_cost;
            }
        }
    }
}