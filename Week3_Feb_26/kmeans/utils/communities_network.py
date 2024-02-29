import numpy as np
from itertools import combinations
from sklearn import metrics
import community as community_louvain
import networkx as nx


def modularity_matrix(adj_matrix: np.ndarray) -> np.ndarray:
    """
    Calculates the modularity matrix for a given adjacency matrix.

    Parameters:
        adj_matrix (np.ndarray): The adjacency matrix of the network.

    Returns:
        np.ndarray: The modularity matrix.
    """
    k_i = np.expand_dims(adj_matrix.sum(axis=1), axis=1)
    k_j = k_i.T
    norm = 1 / k_i.sum()
    K = norm * np.matmul(k_i, k_j)

    return norm * (adj_matrix - K)


def modularity(adj_matrix: np.ndarray, communities: list) -> float:
    """
    Calculates the modularity of a network given the adjacency matrix and a list of communities.

    Parameters:
        adj_matrix (np.ndarray): The adjacency matrix of the network.
        communities (list): A list of communities, where each community is represented as a list of node indices.

    Returns:
        float: The modularity value of the network.

    Raises:
        None

    """
    k_i = np.expand_dims(adj_matrix.sum(axis=1), axis=1)
    k_j = k_i.T

    weights_sum = k_i.sum()

    # if the nodes aren't linked we return the worst modularity
    if weights_sum == 0:
        return -1

    norm = 1 / weights_sum
    K = norm * np.matmul(k_i, k_j)  # (ki * kj) / 2m
    mod_matrix = norm * (adj_matrix - K)  # ( 1/2m ) *  Aij - (ki * kj) / 2m

    C = np.zeros_like(mod_matrix)

    for community in communities:
        if len(community) <= 1:
            continue
        for i, j in combinations(community, 2):
            C[i, j] = 1.0
            C[j, i] = 1.0

    return np.tril(np.multiply(mod_matrix, C), 0).sum()


def filter_adj_matrix(adj_matrix: np.ndarray, V: list) -> np.ndarray:
    """
    Filters the adjacency matrix by keeping only the nodes in V.

    Parameters:
        adj_matrix (np.ndarray): The adjacency matrix representing the network.
        V (list): The list of nodes to keep in the filtered adjacency matrix.

    Returns:
        np.ndarray: The filtered adjacency matrix.
    """
    new_adj_matrix = adj_matrix.copy()

    for i in range(new_adj_matrix.shape[0]):
        if i not in V:
            new_adj_matrix[i, :] = 0
            new_adj_matrix[:, i] = 0

    return new_adj_matrix


def communities_to_labels(G, communities: list, original_nodes) -> list:
    """
    Converts a list of communities into a list of node labels with their corresponding community index.

    Parameters:
    G (networkx.Graph): The input graph.
    communities (list): A list of communities, where each community is represented as a list of node indices.

    Returns:
    list: A list of tuples, where each tuple contains a node label and its corresponding community index.
          The list is sorted in ascending order of node labels.
    """

    res = []

    for index, community in enumerate(communities):
        for node in community:
            res.append((original_nodes[node], index+1))

    return sorted(res)


def calc_nmi(true_labels: list, pred_labels: list) -> float:
    """
    Calculates the Normalized Mutual Information (NMI) between true labels and predicted labels.

    Args:
        true_labels (list): A list of tuples containing node and true label pairs.
        pred_labels (list): A list of tuples containing node and predicted label pairs.

    Returns:
        float: The NMI score between true labels and predicted labels.
    """
    true_labels = [label for _, label in true_labels]
    pred_labels = [label for _, label in pred_labels]

    return metrics.normalized_mutual_info_score(true_labels, pred_labels)


def generation_transformation_dict(G, nodes: list) -> dict:
    """
    Generates a transformation dictionary that maps indices to nodes.

    Args:
        G (networkx.Graph): The input graph.
        nodes (list): A list of nodes.

    Returns:
        dict: A dictionary that maps indices to nodes.
    """
    dic = {}
    for i, node in enumerate(nodes):
        dic[i] = node

    return dic


def adjacency_to_sets(adj_matrix):
    return [set(np.nonzero(row)[0]) for row in adj_matrix]


def calculate_jaccard_similarity(adj_matrix):
    sets_list = adjacency_to_sets(adj_matrix)
    n = len(sets_list)  # Number of nodes
    # Initialize similarity matrix with zeros
    similarity_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i, n):
            intersection = len(sets_list[i].intersection(sets_list[j]))
            union = len(sets_list[i].union(sets_list[j]))
            similarity = intersection / union if union != 0 else 0
            similarity_matrix[i][j] = similarity_matrix[j][i] = similarity

    return similarity_matrix


def calculate_Q_Sim(S: np.ndarray, communities: list) -> float:
    """
    Calculates the similarity-based modularity of a network given the similarity matrix and a list of communities.

    Parameters:
        S (np.ndarray): The similarity matrix of the network.
        C (list): A list of communities, where each community is represented as a list of node indices.

    Returns:
        float: The similarity-based modularity value of the network.

    Raises:
        None
    """

    k_i = np.expand_dims(S.sum(axis=1), axis=1)
    k_j = k_i.T

    weights_sum = k_i.sum()

    # if the nodes aren't linked we return the worst modularity
    if weights_sum == 0:
        return -1

    norm = 1 / weights_sum
    K = norm * np.matmul(k_i, k_j)  # (ki * kj) / 2m
    mod_matrix = norm * (S - K)  # ( 1/2m ) *  Aij - (ki * kj) / 2m

    C = np.zeros_like(mod_matrix)

    for community in communities:
        if len(community) <= 1:
            continue
        for i, j in combinations(community, 2):
            C[i, j] = 1.0
            C[j, i] = 1.0

    return np.tril(np.multiply(mod_matrix, C), 0).sum()


def louvain(G: nx.Graph) -> list:

    partition = community_louvain.best_partition(G)
    modularity = community_louvain.modularity(partition, G)

    return partition, modularity
