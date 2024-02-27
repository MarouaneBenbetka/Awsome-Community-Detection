
import networkx as nx
import numpy as np
from scipy.linalg import eigh
from sklearn.preprocessing import StandardScaler


def similarity_matrix(A: np.ndarray) -> np.ndarray:
    """
    This function takes an adjacency matrix A and returns the similarity matrix S.
    """
    # Calculate the Similarity Matrix S
    S = np.dot(A, A.T)
    return S


def distance_matrix(S: np.ndarray) -> np.ndarray:
    """
    This function takes a similarity matrix S and returns the distance matrix D.
    """
    # Define the Distance Matrix D

    D = np.sqrt(np.add.outer(np.diag(S), np.diag(S)) - 2 * S)
    return D


def average_weight(dist_matrix: np.ndarray, nodes: list) -> float:
    """
    This function takes a distance matrix D and a list of nodes and returns the average weight of the nodes.
    specific for complete graphs
    """

    filtered_dist_matrix = dist_matrix[nodes][:, nodes]

    sum_distances = np.sum(filtered_dist_matrix)  # sum of distances
    nb_edges = len(nodes) * (len(nodes) - 1)  # cause it's a complete graph

    return sum_distances / nb_edges


def fitness_function(adj_matrix: np.ndarray, nodes: list, alpha=.9, beta=1.1) -> float:
    """
    This function calculates the fitness function for a given subgraph defined by the nodes.
    It returns the number of edges inside the subgraph divided by the sum of edges inside and coming out of the subgraph.
    """

    subgraph = adj_matrix[nodes][:, nodes]

    num_edges_inside = np.count_nonzero(subgraph) // 2

    unused_nodes = [node for node in list(
        range(adj_matrix.shape[0])) if node not in nodes]

    num_edges_outside = np.count_nonzero(adj_matrix[nodes][:, unused_nodes])

    print("Kin :", num_edges_inside)
    print("Kout :", num_edges_outside)

    return num_edges_inside / num_edges_inside**alpha + num_edges_outside**beta


def find_cliques(G: nx.Graph) -> list:
    """
    This function takes a graph G and returns a list of all cliques in the graph.
    """
    return list(nx.find_cliques(G))
