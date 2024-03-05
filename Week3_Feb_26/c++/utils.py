
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
            continue

        cliques_sorted.pop(chosen_clique_index)
        clique_distance_matrix = D[chosen_clique][:, chosen_clique]
        # sum_of_distances = np.sum(clique_distance_matrix, axis=1)

        # Extract the subgraph

        # centroid = chosen_clique[np.argmin(sum_of_distances)]

        fitness_value = fitness_function(adj_matrix, chosen_clique)
        # assign a class to the nodes in the unselected_nodes

        for node in unselected_nodes:
            if node not in chosen_clique:
                fitness = fitness_function(
                    adj_matrix, chosen_clique + [node])

                if fitness >= fitness_value:
                    fitness_value = fitness
                    chosen_clique.append(node)

        # this is all about finding the node to consider as
        # the centroid
        # we choose the node tha maximizes the closeness centrality
        # or minimizes the sum of distances

        H = G.subgraph(chosen_clique)
        closeness_centrality_subgraph = nx.closeness_centrality(H)
        centroid = max(
            closeness_centrality_subgraph, key=closeness_centrality_subgraph.get)

        # we have found the node with the previous requirements

        # add the node to the list of centroids
        initial_seeds.append(centroid)

        # we remove all the nodes alredy assigned to a cluster
        # from the initial list of nodes
        unselected_nodes.difference_update(chosen_clique)


        new_cliques = []
        for cliques in cliques_sorted:
            # a node can be in multiple cliques
            # if a node is processed based on its belonging to a certain high priority clique
            # then all the cliques with lower priority should get rid of
            # the already processed node

            cliques["nodes"] = [node for node in cliques["nodes"]
                                if node in unselected_nodes]

            # for each reconstructed clique, compute the average weight
            # do not take into consideration the nodes that
            # are already removed
            cliques["weight"] = average_weight(adj_matrix, cliques["nodes"])

            # keep only >= 3-k cliques
            if len(cliques["nodes"]) > 2:
                new_cliques.append(cliques)

        # resort the cliques based on the nodes and weights
        cliques_sorted = sorted(
            new_cliques, key=lambda x: x["weight"], reverse=True)

        # move to the next iteration
        M += 1

    if M < k: # if the number of detected cliques is less
        # than the number of desired clusters k

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

    pca = PCA(n_components=0.99)
    X = pca.fit_transform(D)

    # eigenvalues = pca.explained_variance_
    # positive_indices = np.where(eigenvalues > epsilon)[0]

    # decompose the matrix into U alpha U-1
    U, V, U1 =  np.linalg.svd(D)
    values = []
    vectors = []
    # iterave on the eigenvalues of the matrix (the diagonal of the matrix V)
    # if the eigenvalue is greater than 0, take it with its corresponding vector
    for i, v in zip(range(len(np.diag(V), np.diag(V)))):
        if v > 0:
            # add the vector to the list
            vectors.append(U[:, i].T)
            values.append(v)

    # construct the P matrix:
    P = np.array([vector for vector in vectors]).T

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


def local_expansion_kmeans(G: nx.Graph, A: np.ndarray, Kmin: int, Kmax: int, metric="Mod") -> list:
    """
    This function implements the local expansion k-means algorithm.
    It takes a weighted adjacency matrix A, minimum number of clusters Kmin,
    and maximum number of clusters Kmax.
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

    for K in range(Kmin, Kmax + 1):
        try:
            initial_seeds = local_expension(G, D, K)

            communities, labels = kmeans_clustering(
                D, K, D[initial_seeds])

            # communities, labels = kmeans_clustering(
            #     D_transformed, K, D_transformed[initial_seeds])

            # Calculate the similarity-based modularity Qs

            if metric == "Mod":
                Qs = calculate_modularity(G, communities)
            elif metric == "QSim":
                Qs = calculate_Q_Sim(A, communities)

            # trace += [{"communities": communities, "K": K,
            #            "Modularity": Qs, "labels": labels}]

            if Qs > Qmax:
                Qmax = Qs
                Cmax = communities
                Kbest = K
                labelsBest = labels
        except Exception as e:

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
