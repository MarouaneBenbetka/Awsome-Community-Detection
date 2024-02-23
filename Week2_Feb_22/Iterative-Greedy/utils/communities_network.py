import numpy as np
from itertools import combinations
from sklearn import metrics


def modularity_matrix(adj_matrix: np.ndarray) -> np.ndarray:
    k_i = np.expand_dims(adj_matrix.sum(axis=1), axis=1)
    k_j = k_i.T
    norm = 1 / k_i.sum()
    K = norm * np.matmul(k_i, k_j)

    return norm * (adj_matrix - K)


def modularity(adj_matrix: np.ndarray, communities: list) -> float:

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


def filter_adj_matrix(adj_matrix, V):
    # keep only the nodes in V

    new_adj_matrix = adj_matrix.copy()

    for i in range(new_adj_matrix.shape[0]):
        if i not in V:
            new_adj_matrix[i, :] = 0
            new_adj_matrix[:, i] = 0

    return new_adj_matrix


def communities_to_labels(G, communities):
    dic = {}
    for i, node in enumerate(G.nodes()):
        dic[i] = node

    res = []

    for index, community in enumerate(communities):
        for node in community:
            res.append((dic[node], index+1))

    return sorted(res)


def calc_nmi(true_labels, pred_labels):
    true_labels = [label for node, label in true_labels]
    pred_labels = [label for node, label in pred_labels]

    return metrics.normalized_mutual_info_score(true_labels, pred_labels, average_method='min')


def generation_transformation_dict(G, nodes):
    dic = {}
    for i, node in enumerate(nodes):
        dic[i] = node

    return dic
