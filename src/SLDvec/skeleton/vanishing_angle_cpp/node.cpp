#include "node.h"
#include "path.h"

Node::Node(const std::vector<double> &point) : point(point),
                                               is_core(true),
                                               index(-1),
                                               taken(false),
                                               bt(0),
                                               radius(0)
{
}

double Node::et() const
{
    return this->bt + this->radius;
}

std::shared_ptr<Path> Node::get_one_path() const
{
    if (!this->paths.empty())
    {
        return this->paths.begin()->lock();
    }
    return nullptr;
}

void Node::add_path(const std::shared_ptr<Path> &path)
{
    std::vector<std::weak_ptr<Path>>::iterator it = std::find_if(
        this->paths.begin(),
        this->paths.end(),
        [&](const std::weak_ptr<Path> &p)
        {
            return p.lock() == path;
        });
    if (it == this->paths.end())
    {
        this->paths.push_back(path);
    }
}

void Node::remove_path(const std::shared_ptr<Path> &path)
{
    std::vector<std::weak_ptr<Path>>::iterator it = std::find_if(
        this->paths.begin(),
        this->paths.end(),
        [&](const std::weak_ptr<Path> &p)
        {
            return p.lock() == path;
        });
    if (it != this->paths.end())
    {
        this->paths.erase(it);
    }
}

bool Node::is_iso() const
{
    return this->paths.size() == 1;
}

std::shared_ptr<Node> Node::get_next(const std::shared_ptr<Path> &path) const
{
    return (path->one.lock().get() == this) ? path->other.lock() : path->one.lock();
}