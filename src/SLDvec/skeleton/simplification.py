from typing import List, Optional

import networkx as nx

from SLDvec.utils.networkx import (
    BranchInfo,
    find_Y_foot_direction,
    get_all_branches_info,
    merge_branch,
)


def get_target_merge_node(nodes_branch_info: List[BranchInfo], G: nx.Graph) -> Optional[BranchInfo]:
    """Return the branch to follow to merge a node, or None if the node should not be merged.

    Args:
        nodes_branch_info (List[BranchInfo]): A list of BranchInfo objects. Each object contains
            informations about a branch going out of a node.

        G (nx.Graph): The graph to analyze.

    Raises:
        ValueError: If multiple branches have the same distance to the border of the shape, or if
            multiple branches lead to the same target and it is not possible to decide which one to
            follow.

    Returns:
        Optional[BranchInfo]: The BranchInfo object of the branch to follow, or None if the node
            should not be merged because it is connected to a single neighbor node.
    """
    # If one of the branches ends with a degree 1 node, and one branch is a loop or the direction of
    # the Y foot is toward that degree 1 node, the function returns None as this degree 3 node is
    # probably a node traversed twice and should not be merged.
    if any([1 == x.endbranch_n_neighbors for x in nodes_branch_info]):
        degree_3_node_of_interest = nodes_branch_info[0].branch[0]
        y_foot_direction = find_Y_foot_direction(G, degree_3_node_of_interest)
        y_foot_branch_direction = [
            branch_info
            for branch_info in nodes_branch_info
            if branch_info.branch[1] == y_foot_direction
        ][0]
        number_neighbor_y_foot_direction = y_foot_branch_direction.endbranch_n_neighbors
        loop_branch = y_foot_branch_direction.branch[0] == y_foot_branch_direction.branch[-1]
        if number_neighbor_y_foot_direction == 1 or loop_branch:
            return None

    # Find the maximum of the minimum distance to the shape outline among the three branches
    max_distance = max(x.min_distance_along_branch for x in nodes_branch_info)

    argmax = [
        i
        for i in range(len(nodes_branch_info))
        if nodes_branch_info[i].min_distance_along_branch == max_distance
    ]
    # Note: In theorie, there could be multiple branches witht the same maximum distance to the
    # shape outline. However in practice, this does not happen because the shape is created using
    # potrace so it is not regular and the distance to the shape outline is always different.
    argmax = argmax[0]

    # Return the branch that achieves the maximum distance to the shape outline
    return nodes_branch_info[argmax]


def merge_3_neighbords_node(G_: nx.Graph) -> nx.Graph:
    """Merge the 3 neighbors nodes of the graph that are artifacts of the medial axis computation.

    Args:
        G_ (nx.Graph): The graph to simplify.
        verbose (bool, optional): Wheter to print the merged node. Defaults to False.

    Raises:
        NotImplementedError: If there is a node with more than 3 neighbors.
        Warning: If there is more than two 3 neighbors node left with a merge target that is not
            None, after merging all other node.

    Returns:
        nx.Graph: A copy of the original graph with the 3 neighbors nodes merged.
    """
    G = G_.copy()

    # For each node with 3 neighbors, get the information about the branches and the target to merge
    merge_node_along_branch_dict = {}
    for node in G.nodes():
        if G.degree(node) == 3:
            node_info = get_all_branches_info(G, node)
            merge_node_along_branch_dict[node] = get_target_merge_node(node_info, G)

    # Merge the pairs of nodes that match (i.e. they are both the target of each other)
    already_merged = []
    for node, branch_to_merge in merge_node_along_branch_dict.items():
        if node in already_merged or branch_to_merge is None:
            continue
        merge_target = branch_to_merge.branch[-1]

        if (
            merge_target in merge_node_along_branch_dict
            and merge_node_along_branch_dict[merge_target] is not None
            and merge_node_along_branch_dict[merge_target].branch[-1] == node
        ):
            merge_branch(G, branch_to_merge.branch)
            already_merged.append(node)
            already_merged.append(merge_target)

    for node in already_merged:
        merge_node_along_branch_dict.pop(node)

    # Then consider the remaining nodes that have a not None target
    remaining_node_not_none_target = [
        k for k, v in merge_node_along_branch_dict.items() if v is not None
    ]

    # First merge the nodes for which the target is also a not None target
    remaining_node_not_merged = []
    for n in remaining_node_not_none_target:
        if (
            merge_node_along_branch_dict[n].branch[-1] in remaining_node_not_none_target
            and merge_node_along_branch_dict[n].branch[-1]
            in G.nodes  # Check that the target node is still in the graph
            and n in G.nodes  # Check that the node to merge is still in the graph
        ):
            merge_branch(G, merge_node_along_branch_dict[n].branch)
            merge_node_along_branch_dict.pop(n)
        else:
            remaining_node_not_merged.append(n)

    for n in remaining_node_not_merged:
        if any([x not in G.nodes() for x in merge_node_along_branch_dict[n].branch]):
            # This node or the target node has been merged with another node
            # This node can't be merged, and is thus skipped
            continue
        if merge_node_along_branch_dict[n].endbranch_n_neighbors != 1:
            merge_branch(G, merge_node_along_branch_dict[n].branch)
            merge_node_along_branch_dict.pop(n)

    return G
