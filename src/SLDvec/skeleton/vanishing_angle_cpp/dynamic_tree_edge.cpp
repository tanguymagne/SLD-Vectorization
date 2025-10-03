// dynamic_tree_edge.cpp
#include "dynamic_tree_edge.h"
#include "dynamic_tree_node.h"

DynamicTreeEdge::DynamicTreeEdge(const std::shared_ptr<DynamicTreeNode> &one,
                                 const std::shared_ptr<DynamicTreeNode> &other) : one(one),
                                                                                  other(other),
                                                                                  one_to_other_score(std::numeric_limits<double>::quiet_NaN()),
                                                                                  one_to_other_cost(std::numeric_limits<double>::quiet_NaN()),
                                                                                  other_to_one_score(std::numeric_limits<double>::quiet_NaN()),
                                                                                  other_to_one_cost(std::numeric_limits<double>::quiet_NaN())
{
}

void DynamicTreeEdge::set_score(const std::shared_ptr<DynamicTreeNode> &node, double score)
{
    if (node == this->one.lock())
    {
        this->one_to_other_score = score;
    }
    else
    {
        this->other_to_one_score = score;
    }
}

void DynamicTreeEdge::set_cost(const std::shared_ptr<DynamicTreeNode> &node, double cost)
{
    if (node == this->one.lock())
    {
        this->one_to_other_cost = cost;
    }
    else
    {
        this->other_to_one_cost = cost;
    }
}

std::shared_ptr<DynamicTreeNode> DynamicTreeEdge::get_other_node(const std::shared_ptr<DynamicTreeNode> &node) const
{
    return (node == this->one.lock()) ? this->other.lock() : this->one.lock();
}