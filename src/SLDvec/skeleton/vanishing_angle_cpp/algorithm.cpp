#include "algorithm.h"

Algorithm::Algorithm(const DynamicTree &current_tree) : tree(current_tree)
{
    tree = current_tree.duplicate();
    alpha_list.push_back(0.0);
}

std::vector<double> Algorithm::execute(DynamicTree &input_tree)
{
    double total_score = 0.0;
    double total_cost = 0.0;

    for (std::shared_ptr<DynamicTreeNode> node : input_tree.nodes)
    {
        node->score = node->reward;
        node->total_cost = node->cost;
        node->visit_once = false;

        total_score += node->reward;
        total_cost += node->cost;
    }

    for (std::shared_ptr<DynamicTreeEdge> edge : input_tree.edges)
    {
        edge->one_to_other_score = std::numeric_limits<double>::quiet_NaN();
        edge->one_to_other_cost = std::numeric_limits<double>::quiet_NaN();
        edge->other_to_one_score = std::numeric_limits<double>::quiet_NaN();
        edge->other_to_one_cost = std::numeric_limits<double>::quiet_NaN();
    }

    std::vector<std::shared_ptr<DynamicTreeNode>> leaves = input_tree.get_leaves();
    std::vector<std::shared_ptr<DynamicTreeNode>> temp_leaves = leaves;

    while (!leaves.empty())
    {
        temp_leaves = leaves;

        for (std::shared_ptr<DynamicTreeNode> leaf : leaves)
        {
            leaf->set_score();
        }

        for (std::shared_ptr<DynamicTreeNode> leaf : leaves)
        {
            leaf->visit_once = true;
        }

        leaves = input_tree.get_leaves();
    }

    // Corner case of ending with one node
    if (temp_leaves.size() == 1)
    {
        std::shared_ptr<DynamicTreeNode> temp_node = temp_leaves[0];
        for (std::weak_ptr<DynamicTreeEdge> weak_edge : temp_node->edges)
        {
            if (std::shared_ptr<DynamicTreeEdge> edge = weak_edge.lock())
            {
                if (temp_node == edge->one.lock())
                {
                    edge->other_to_one_score = edge->other.lock()->score;
                    edge->other_to_one_cost = edge->other.lock()->total_cost;
                }
                else
                {
                    edge->one_to_other_score = edge->one.lock()->score;
                    edge->one_to_other_cost = edge->one.lock()->total_cost;
                }
            }
        }
    }
    if (temp_leaves.size() == 2)
    {
        std::shared_ptr<DynamicTreeNode> node1 = temp_leaves[0];
        std::shared_ptr<DynamicTreeNode> node2 = temp_leaves[1];

        for (std::weak_ptr<DynamicTreeEdge> weak_edge : node1->edges)
        {
            if (std::shared_ptr<DynamicTreeEdge> edge = weak_edge.lock())
            {
                if (edge->get_other_node(node1) == node2)
                {
                    edge->one_to_other_score = edge->one.lock()->score;
                    edge->one_to_other_cost = edge->one.lock()->total_cost;
                }
            }
        }
    }

    double min_alpha = std::numeric_limits<double>::infinity();
    std::shared_ptr<DynamicTreeEdge> min_edge = nullptr;

    for (std::shared_ptr<DynamicTreeEdge> edge : input_tree.edges)
    {
        if (std::isnan(edge->one_to_other_score) && std::isnan(edge->other_to_one_score))
        {
            std::cerr << "Error: edges score not set, this should not happen" << std::endl;
        }
        else if (std::isnan(edge->one_to_other_score))
        {
            edge->one_to_other_score = total_score - edge->other_to_one_score;
            edge->one_to_other_cost = total_cost - edge->other_to_one_cost;
        }
        else if (std::isnan(edge->other_to_one_score))
        {
            edge->other_to_one_score = total_score - edge->one_to_other_score;
            edge->other_to_one_cost = total_cost - edge->one_to_other_cost;
        }

        // Find the minimum alpha and corresponding edge
        if (edge->one_to_other_cost != 0 && min_alpha > edge->one_to_other_score / edge->one_to_other_cost)
        {
            min_alpha = edge->one_to_other_score / edge->one_to_other_cost;
            min_edge = edge;
        }

        if (edge->other_to_one_cost != 0 && min_alpha > edge->other_to_one_score / edge->other_to_one_cost)
        {
            min_alpha = edge->other_to_one_score / edge->other_to_one_cost;
            min_edge = edge;
        }
    }

    if (!min_edge)
    {
        return this->alpha_list;
    }

    this->alpha_list.push_back(min_alpha + this->alpha_list.back());
    this->shrink_tree(input_tree, min_alpha, min_edge);

    int iter_count = 1;
    while (!(input_tree.edges.empty()))
    {
        iter_count++;
        min_alpha = std::numeric_limits<double>::infinity();
        min_edge = nullptr;

        for (std::shared_ptr<DynamicTreeEdge> edge : input_tree.edges)
        {
            if (edge->one_to_other_cost != 0 && min_alpha > edge->one_to_other_score / edge->one_to_other_cost)
            {
                min_alpha = edge->one_to_other_score / edge->one_to_other_cost;
                min_edge = edge;
            }

            if (edge->other_to_one_cost != 0 && min_alpha > edge->other_to_one_score / edge->other_to_one_cost)
            {
                min_alpha = edge->other_to_one_score / edge->other_to_one_cost;
                min_edge = edge;
            }
        }

        if (min_edge == nullptr)
        {
            break;
        }

        this->alpha_list.push_back(min_alpha + this->alpha_list.back());
        this->shrink_tree(input_tree, min_alpha, min_edge);
    }

    return this->alpha_list;
}

void Algorithm::shrink_tree(
    DynamicTree &input_tree,
    double alpha,
    std::shared_ptr<DynamicTreeEdge> min_edge)
{
    double total_alpha = this->alpha_list.back();
    std::deque<std::shared_ptr<DynamicTreeNode>> queue;
    double min_edge_cost = 0.0;
    std::shared_ptr<DynamicTreeNode> safe_node = nullptr;

    if (min_edge->one_to_other_cost != 0 && alpha == (min_edge->one_to_other_score / min_edge->one_to_other_cost))
    {
        safe_node = min_edge->other.lock();
        queue.push_back(min_edge->one.lock());
        min_edge_cost = min_edge->one_to_other_cost;
    }
    else if (min_edge->other_to_one_cost != 0 && alpha == (min_edge->other_to_one_score / min_edge->other_to_one_cost))
    {
        safe_node = min_edge->one.lock();
        queue.push_back(min_edge->other.lock());
        min_edge_cost = min_edge->other_to_one_cost;
    }
    else
    {
        std::cerr << "Error: min_edge is not a valid edge" << std::endl;
    }

    while (!queue.empty())
    {
        std::shared_ptr<DynamicTreeNode> curr_node = queue.front();
        queue.pop_front();

        for (std::weak_ptr<DynamicTreeEdge> &weak_edge : curr_node->edges)
        {
            if (std::shared_ptr<DynamicTreeEdge> edge = weak_edge.lock())
            {
                auto it = std::find(input_tree.edges.begin(), input_tree.edges.end(), edge);

                if (it != input_tree.edges.end())
                {
                    input_tree.edges.erase(it);
                }

                std::shared_ptr<DynamicTreeNode> other_node = curr_node->get_other_node(edge);

                if (other_node != safe_node)
                {
                    queue.push_back(other_node);
                }

                auto other_edge_it = std::find_if(
                    other_node->edges.begin(),
                    other_node->edges.end(),
                    [&edge](const std::weak_ptr<DynamicTreeEdge> &e)
                    {
                        return e.lock() == edge;
                    });
                if (other_edge_it != other_node->edges.end())
                {
                    other_node->edges.erase(other_edge_it);
                }
            }
        }

        curr_node->edges.clear();
        auto it_curr_node = std::find(input_tree.nodes.begin(), input_tree.nodes.end(), curr_node);
        if (it_curr_node != input_tree.nodes.end())
        {
            input_tree.nodes.erase(it_curr_node);
        }
        this->tree.nodes[curr_node->index]->drop_threshold = total_alpha;
    }

    for (std::shared_ptr<DynamicTreeEdge> &edge : input_tree.edges)
    {
        edge->one_to_other_score -= alpha * edge->one_to_other_cost;
        edge->other_to_one_score -= alpha * edge->other_to_one_cost;
    }

    std::deque<std::pair<std::shared_ptr<DynamicTreeEdge>, std::shared_ptr<DynamicTreeNode>>> edge_queue;

    for (std::weak_ptr<DynamicTreeEdge> &weak_edge : safe_node->edges)
    {
        if (std::shared_ptr<DynamicTreeEdge> edge = weak_edge.lock())
        {
            edge_queue.push_back({edge, safe_node});
        }
    }

    while (!edge_queue.empty())
    {
        auto [curr_edge, curr_node] = edge_queue.front();
        edge_queue.pop_front();

        if (curr_node == curr_edge->one.lock())
        {
            curr_edge->one_to_other_cost -= min_edge_cost;
            if (curr_edge->one_to_other_cost < 0)
            {
                curr_edge->one_to_other_cost = 0;
            }
        }
        else if (curr_node == curr_edge->other.lock())
        {
            curr_edge->other_to_one_cost -= min_edge_cost;
            if (curr_edge->other_to_one_cost < 0)
            {
                curr_edge->other_to_one_cost = 0;
            }
        }
        else
        {
            std::cerr << "Error: curr_node is not in curr_edge" << std::endl;
        }

        std::shared_ptr<DynamicTreeNode> next_node = curr_edge->get_other_node(curr_node);

        for (std::weak_ptr<DynamicTreeEdge> &weak_next_edge : next_node->edges)
        {
            if (std::shared_ptr<DynamicTreeEdge> next_edge = weak_next_edge.lock())
            {
                if (next_edge != curr_edge)
                {
                    edge_queue.push_back({next_edge, next_node});
                }
            }
        }
    }
}