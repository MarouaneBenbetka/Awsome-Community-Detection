
import networkx as nx
import numpy as np
from scipy.linalg import eigh
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from utils.communities_network import calculate_Q_Sim
from sklearn.preprocessing import StandardScaler
import math


def similarity_matrix(A: np.ndarray) -> np.ndarray:
    """
    This function takes an adjacency matrix A and returns the similarity matrix S.
    """
    # Calculate the Similarity Matrix S
    S = np.dot(A, A.T)
    return S


def distance_matrix2(similarity_matrix):
    """
    Converts an unnormalized similarity matrix to a distance matrix.
    This function first normalizes the similarity scores based on the maximum value found in the matrix.

    Parameters:
    similarity_matrix (numpy.ndarray): A square matrix containing unnormalized similarity scores.

    Returns:
    numpy.ndarray: A square matrix containing distance scores.
    """
    # Validate the input matrix is square
    if similarity_matrix.shape[0] != similarity_matrix.shape[1]:
        raise ValueError("The similarity matrix must be square.")

    # Normalize similarity scores by the maximum score in the matrix
    max_similarity = np.max(similarity_matrix, axis=1)
    normalized_similarity = similarity_matrix / max_similarity

    # scaler = StandardScaler()
    # normalized_similarity = scaler.fit_transform(similarity_matrix)

    # Convert normalized similarity to distance
    distance_matrix = 1 - normalized_similarity

    # Ensure the diagonal elements are 0 (distance from an element to itself)
    # np.fill_diagonal(distance_matrix, 0)

    return distance_matrix


def standard_scale(matrix):
    """
    Standardizes the given matrix by applying standard scaling.

    Parameters:
    matrix (numpy.ndarray): The input matrix to be standardized.

    Returns:
    numpy.ndarray: The standardized matrix.

    """
    # Calculate mean and standard deviation for each column
    mean_values = np.mean(matrix, axis=0)
    std_dev_values = np.std(matrix, axis=0)

    # Apply standard scaling
    scaled_matrix = (matrix - mean_values) / std_dev_values

    return scaled_matrix


def distance_matrix(S: np.ndarray) -> np.ndarray:
    """
    This function takes a similarity matrix S and returns the distance matrix D.
    """
    # Define the Distance Matrix D
    n = S.shape[0]

    D = np.zeros(S.shape)

    for i in range(n):
        for j in range(n):
            D[i, j] = math.sqrt(S[i, i] + S[j, j] - 2*S[i, j])

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


def local_expension(G: nx.Graph, D: np.ndarray, k=2, alpha=.9, beta=1.1):
    """
    This function takes a graph G and returns a list of k initial seeds.
    """

    adj_matrix = nx.to_numpy_array(G)
    initial_seeds = []

    # find all complete subgraphs of size 3 or more in the graph
    cliques = find_cliques(G, D)

    # sort the cliques by their weight
    cliques_sorted = sorted(cliques, key=lambda x: x["weight"], reverse=True)

    # get the unselected nodes
    unselected_nodes = set(G.nodes())
    skip_nodes = []

    M = 0
    while M < k and cliques_sorted:

        # get the node with the maximum degree
        max_degree_node = max(unselected_nodes, key=lambda node:  G.degree(
            node) * int(node not in skip_nodes))

        chosen_clique = None
        chosen_clique_index = -1
        # get the clique that contains the node with the maximum degree
        for i, clique in enumerate(cliques_sorted):
            if max_degree_node in clique["nodes"]:
                chosen_clique_index = i
                chosen_clique = clique["nodes"]
                break

        # if the node with the maximum degree is not in any clique we skip it in next iteration
        if not chosen_clique:
            skip_nodes.append(max_degree_node)
            continue

        cliques_sorted.pop(chosen_clique_index)

        # sort the nodes in the clique by their distance to the other nodes in the clique
        condidat_nodes_in_order = sorted(
            unselected_nodes, key=lambda node: min(D[node, target_node] for target_node in chosen_clique))

        # get the initial fitness value of the chosen clique
        fitness_value = fitness_function(adj_matrix, chosen_clique)

        # add the nodes that maximizes the fitness function to the chosen clique
        for node in condidat_nodes_in_order:
            if node not in chosen_clique:
                fitness = fitness_function(
                    adj_matrix, chosen_clique + [node], alpha, beta)

                if fitness >= fitness_value:
                    fitness_value = fitness
                    chosen_clique.append(node)

        # get the subgraph of the chosen clique
        H = G.subgraph(chosen_clique)

        # get the closeness centrality of the subgraph
        closeness_centrality_subgraph = nx.closeness_centrality(H)

        # get the node with the maximum closeness centrality as a seed
        centroid = max(
            closeness_centrality_subgraph, key=closeness_centrality_subgraph.get)

        # add the centroid to the initial seeds
        initial_seeds.append(centroid)

        # remove the nodes in the chosen clique from the unselected nodes
        unselected_nodes.difference_update(chosen_clique)

        # remove the treeted nodes from the cliques list
        new_cliques = []
        for clique in cliques_sorted:
            clique["nodes"] = [node for node in clique["nodes"]
                               if node in unselected_nodes]
            clique["weight"] = average_weight(adj_matrix, clique["nodes"])

            if len(clique["nodes"]) > 2:
                new_cliques.append(clique)

        # sort the new cliques according to their weight
        cliques_sorted = sorted(
            new_cliques, key=lambda x: x["weight"], reverse=True)

        M += 1

    # if the number of initial seeds is less than k we add the nodes with the maximum distance to the initial seeds
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

    pca = PCA(n_components=.90)
    X = pca.fit_transform(D)

    # positive_indices = np.where(eigenvalues > epsilon)[0]

    return X


def kmeans_clustering(X: np.ndarray, K: int, initial_seeds: np.ndarray) -> np.ndarray:
    """
    This function takes a matrix X and the number of clusters K and returns the cluster indices.
    """

    if len(initial_seeds):
        kmeans = KMeans(n_clusters=K, random_state=0,
                        init=initial_seeds).fit(X)
    else:
        kmeans = KMeans(n_clusters=K, random_state=0, init="k-means++").fit(X)

    comm_dict = {}
    for i, label in enumerate(kmeans.labels_):
        comm_dict[label] = comm_dict.get(label, []) + [i]

    communities = list(comm_dict.values())

    return communities, kmeans.labels_


def calculate_modularity(G: nx.Graph, communities: list) -> float:
    return nx.community.modularity(G, communities)


def local_expansion_kmeans(G: nx.Graph, A: np.ndarray, Kmin: int, Kmax: int, metric="Mod", alpha=.9, beta=1.1) -> list:
    """
    This function implements the local expansion k-means algorithm.
    It takes a weighted adjacency matrix A, minimum number of clusters Kmin, and maximum number of clusters Kmax.
    It returns the community set Cmax.
    """

    # Calculate the similarity matrix S using the weighted adjacency matrix A
    S = similarity_matrix(A)

    # Calculate the distance matrix D using S
    D = distance_matrix2(S)

    D_transformed = PCA_reduction(D)

    Cmax = []
    Qmax = -1
    Kbest = Kmin
    labelsBest = []
    trace = []

    Mod = -1
    Modsim = -1

    # iterate from Kmin to Kmax to find the best number of clusters accoriding to the choosed matrix either Mod or QSim
    for K in range(Kmin, Kmax + 1):
        try:

            # get the initial seeds using the local expansion algorithm
            initial_seeds = local_expension(G, D, K, alpha, beta)

            # apply the kmeans clustering algorithm
            communities, labels = kmeans_clustering(
                D_transformed, K, D_transformed[initial_seeds])

            # Calculate the similarity-based modularity or Modularity according to the choosed metric
            if metric == "Mod":
                Qs = calculate_modularity(G, communities)
                Mod = Qs
                Modsim = calculate_Q_Sim(A, communities)
            elif metric == "QSim":
                Qs = calculate_Q_Sim(A, communities)
                Mod = calculate_modularity(G, communities)
                Modsim = Qs

            # just for printing the trace
            trace += [{"communities": communities, "K": K,
                       "Modularity": calculate_modularity(G, communities), "Similarity-Based Modularity": Modsim, "labels": Mod}]

            # choose the best number of clusters according to the choosed metric K
            if Qs > Qmax:
                Qmax = Qs
                Cmax = communities
                Kbest = K
                labelsBest = labels
        except Exception as e:
            print(e)
            break

    return Cmax, Qmax, Kbest, labelsBest, trace


def kmeans_random(G: nx.Graph, A: np.ndarray, Kmin: int, Kmax: int, metric="Mod") -> list:
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
    Qmax = -1
    Kbest = Kmin
    labelsBest = []

    trace = []

    for K in range(Kmin, Kmax + 1):

        try:
            communities, labels = kmeans_clustering(
                D_transformed, K, [])

            # Calculate the similarity-based modularity Qs

            if metric == "Mod":
                Qs = calculate_modularity(G, communities)
            elif metric == "QSim":
                Qs = calculate_Q_Sim(S, communities)

            trace += [{"communities": communities, "K": K,
                       "Modularity": Qs, "labels": labels}]

            if Qs > Qmax:
                Qmax = Qs
                Cmax = communities
                Kbest = K
                labelsBest = labels
        except Exception as e:
            break

    return Cmax, Qmax, Kbest, labelsBest, trace
