
import networkx as nx
import numpy as np
from scipy.linalg import eigh
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


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

    nb_edges = len(nodes) * (len(nodes) - 1)   # cause it's a complete graph

    return sum_distances / nb_edges


def fitness_function(adj_matrix: np.ndarray, nodes: list, alpha=.9, beta=1.1) -> float:
    """
    This function calculates the fitness function for a given subgraph defined by the nodes.
    It returns the number of edges inside the subgraph divided by the sum of edges inside and coming out of the subgraph.
    """

    subgraph = adj_matrix[nodes][:, nodes]

    num_edges_inside = np.count_nonzero(np.triu(subgraph))

    unused_nodes = [node for node in list(
        range(adj_matrix.shape[0])) if node not in nodes]

    num_edges_outside = np.count_nonzero(adj_matrix[nodes][:, unused_nodes])

    return num_edges_inside / (num_edges_inside**alpha + num_edges_outside**beta)


def find_cliques(G: nx.Graph, adj_matrix: np.ndarray) -> list:
    """
    This function takes a graph G and returns a list of all cliques in the graph.
    """

    range(1, 10)

    cliques_generator = nx.find_cliques(G)

    res = []
    for clique in cliques_generator:
        if len(clique) > 2:
            res.append({
                "nodes": clique,
                "weight": average_weight(adj_matrix, clique)
            })

    return res


def filter_matrix(matrix: np.ndarray, V: list) -> np.ndarray:
    """
    Filters the adjacency matrix by keeping only the nodes in V.

    Parameters:
        matrix (np.ndarray): The adjacency matrix representing the network.
        V (list): The list of nodes to keep in the filtered adjacency matrix.

    Returns:
        np.ndarray: The filtered adjacency matrix.
    """
    new_matrix = matrix.copy()

    for i in range(new_matrix.shape[0]):
        if i not in V:
            new_matrix[i, :] = 0
            new_matrix[:, i] = 0

    return new_matrix


def local_expension(G: nx.Graph, D: np.ndarray, k=2):
    """
    This function takes a graph G and returns a list of k initial seeds.
    """

    adj_matrix = nx.to_numpy_array(G)

    initial_seeds = []

    cliques = find_cliques(G, adj_matrix)

    cliques_sorted = sorted(cliques, key=lambda x: x["weight"], reverse=True)

    unselected_nodes = set(G.nodes())

    skip_nodes = []

    M = 0
    while M < k and cliques_sorted:

        max_degree_node = max(unselected_nodes, key=lambda node:  G.degree(
            node) * int(node not in skip_nodes))

        chosen_clique = None
        chosen_clique_index = -1
        for i, clique in enumerate(cliques_sorted):
            if max_degree_node in clique["nodes"]:
                chosen_clique_index = i
                chosen_clique = clique["nodes"]
                break

        if not chosen_clique:
            skip_nodes.append(max_degree_node)

        cliques_sorted.pop(chosen_clique_index)

        clique_distance_matrix = D[chosen_clique][:, chosen_clique]

        sum_of_distances = np.sum(clique_distance_matrix, axis=1)

        centroid = chosen_clique[np.argmin(sum_of_distances)]

        fitness_value = fitness_function(adj_matrix, chosen_clique)

        for node in unselected_nodes:
            if node not in chosen_clique:
                fitness = fitness_function(
                    adj_matrix, chosen_clique + [node])

                if fitness > fitness_value:
                    fitness_value = fitness
                    chosen_clique.append(node)

        initial_seeds.append(centroid)

        unselected_nodes.difference_update(chosen_clique)

        M += 1

    if M < k:

        for _ in range(k-M):

            if not unselected_nodes:
                raise ValueError("No more nodes to select , k is too large")

            max_distance_seed = max(
                unselected_nodes, key=lambda node: np.sum(D[initial_seeds][:, node]))

            initial_seeds.append(max_distance_seed)

            unselected_nodes.remove(max_distance_seed)
            M += 1

    return initial_seeds


def PCA_reduction(D: np.ndarray, epsilon=10e-4) -> np.ndarray:
    """
    This function takes a distance matrix D and returns the reduced matrix using PCA.
    """

    pca = PCA()
    X = pca.fit_transform(D)

    eigenvalues = pca.explained_variance_
    positive_indices = np.where(eigenvalues > epsilon)[0]

    X_transformed = X[:, positive_indices]

    return X_transformed


def kmeans_clustering(X: np.ndarray, K: int, initial_seeds: np.ndarray) -> np.ndarray:
    """
    This function takes a matrix X and the number of clusters K and returns the cluster indices.
    """

    kmeans = KMeans(n_clusters=K, random_state=0, init=initial_seeds).fit(X)

    comm_dict = {}
    for i, label in enumerate(kmeans.labels_):
        comm_dict[label] = comm_dict.get(label, []) + [i]

    communities = list(comm_dict.values())
    return communities, kmeans.labels_


def calculate_modularity(G: nx.Graph, communities: list) -> float:

    return nx.community.modularity(G, communities)


def local_expansion_kmeans(G: nx.Graph, A: np.ndarray, Kmin: int, Kmax: int) -> list:
    """
    This function implements the local expansion k-means algorithm.
    It takes a weighted adjacency matrix A, minimum number of clusters Kmin, and maximum number of clusters Kmax.
    It returns the community set Cmax.
    """

    # Calculate the similarity matrix S using the weighted adjacency matrix A
    S = similarity_matrix(A)

    # Calculate the distance matrix D using S
    D = distance_matrix(S)

    D_transformed = PCA_reduction(D)

    Cmax = []
    Qmax = 0
    Kbest = Kmin

    for K in range(Kmin, Kmax + 1):

        try:
            initial_seeds = local_expension(G, D, K)
            communities, labels = kmeans_clustering(
                D_transformed, K, D_transformed[initial_seeds])

            # Calculate the similarity-based modularity Qs
            Qs = calculate_modularity(G, communities)

            if Qs > Qmax:
                Qmax = Qs
                Cmax = communities
                Kbest = K
        except Exception as e:
            print(e)
            print("K : ", K, " is too large")
            break

    return Cmax, Qmax, Kbest
