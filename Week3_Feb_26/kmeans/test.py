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
    # Calculate the number of edges inside the subgraph
    num_edges_inside = np.sum(adj_matrix[nodes][:, nodes])

    # Calculate the number of edges coming out of the subgraph
    num_edges_outside = np.sum(adj_matrix[:, nodes]) - num_edges_inside

    # Calculate the fitness value
    return num_edges_inside / num_edges_inside**alpha + num_edges_outside**beta


def find_cliques(G: nx.Graph) -> list:
    """
    This function takes a graph G and returns a list of all cliques in the graph.
    """
    return list(nx.find_cliques(G))


def local_expension(G: nx.Graph, k):
    """
    This function takes a graph G and returns a list of k initial seeds.
    """

    adj_matrix = nx.to_numpy_array(G)
    S = similarity_matrix(adj_matrix)
    D = distance_matrix(S)

    initial_seeds = []

    cliques = find_cliques(G)

    # TODO : optimize this
    cliques_with_weights = [(clique, average_weight(D, clique))
                            for clique in cliques]

    cliques_sorted = sorted(cliques_with_weights,
                            key=lambda x: x[1], reverse=True)

    unselected_nodes = set(G.nodes())
    M = 0
    while M < k and cliques_sorted: \

        max_degree_node = max(unselected_nodes, key=lambda x: G.degree(x))
        node_cliques = [clique for clique,
                        _ in cliques_sorted if max_degree_node in clique]

        if not node_cliques:
            break

        chosen_clique = node_cliques[0]

        # TODO :
        # delete the chosen_clique from the list of cliques_sorted

        centrality = nx.degree_centrality(G).get(max_degree_node, 0)
        initial_seeds.append(chosen_clique)
        unselected_nodes.difference_update(chosen_clique)

        M += 1
    return initial_seeds


def local_expansion_kmeans(A: np.ndarray, Kmin: int, Kmax: int) -> list:
    """
    This function implements the local expansion k-means algorithm.
    It takes a weighted adjacency matrix A, minimum number of clusters Kmin, and maximum number of clusters Kmax.
    It returns the community set Cmax.
    """

    # Calculate the similarity matrix S using the weighted adjacency matrix A
    S = np.dot(A, A.T)

    # Calculate the distance matrix D using S
    D = np.sqrt(np.add.outer(np.diag(S), np.diag(S)) - 2 * S)

    # Mapping all nodes of the complex network into p-dimensional Euclidean space with PCA
    pca = PCA(n_components=2)
    X = pca.fit_transform(D)

    Cmax = []
    Qmax = 0

    for K in range(Kmin, Kmax + 1):
        # Select K initial seeds using the local expansion strategy (Algorithm 1)
        initial_seeds = local_expension(G, K)

        # Identify K communities C1, C2, ..., CK with k-means algorithm
        kmeans = KMeans(n_clusters=K, random_state=0).fit(X)
        communities = kmeans.labels_

        # Calculate the similarity-based modularity Qs
        Qs = calculate_modularity(communities, S)

        if Qs > Qmax:
            Qmax = Qs
            Cmax = communities

    return Cmax


def calculate_modularity(communities: np.ndarray, S: np.ndarray) -> float:
    """
    This function calculates the similarity-based modularity Qs given the communities and similarity matrix S.
    """
    n = len(communities)
    Qs = 0

    for i in range(n):
        for j in range(n):
            if communities[i] == communities[j]:
                Qs += S[i, j] - (np.sum(S[i, :]) * np.sum(S[j, :])) / np.sum(S)

    return Qs


# Example usage

adj_matrix = np.array([
    [0, 1, 1, 0, 0],
    [1, 0, 1, 0, 0],
    [1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1],
    [0, 0, 0, 1, 0],
])

Kmin = 2
Kmax = 4

Cmax = local_expansion_kmeans(adj_matrix, Kmin, Kmax)
print("Community Set Cmax:", Cmax)


# Define a sample weighted adjacency matrix A
A = np.array([[0, 1, 0.5, 0],
              [1, 0, 1, 0.5],
              [0.5, 1, 0, 1],
              [0, 0.5, 1, 0]])

# Calculate the Similarity Matrix S
S = np.dot(A, A.T)

# Define the Distance Matrix D
D = np.sqrt(np.add.outer(np.diag(S), np.diag(S)) - 2 * S)

# Perform PCA via Spectral Decomposition on the Centered Distance Matrix
# Center D since PCA assumes centered data
D_centered = D - np.mean(D, axis=0)
eigenvalues, eigenvectors = eigh(D_centered)

# Select the top p eigenvectors. Let's choose p=2 for 2D visualization
p = 2
top_p_eigenvectors = eigenvectors[:, -p:]

# Print the calculated matrices and the PCA result
S, D, top_p_eigenvectors


def find_initial_seeds(G, K):
    # Ensure K initial seeds
    initial_seeds = []

    # Detect all complete subgraphs (cliques) in the complex network
    cliques = list(nx.find_cliques(G))
    print(type(cliques))
    print(cliques)
    # Calculate the average weight of all detected subgraphs
    cliques_with_avg_weight = []
    for clique in cliques:
        weights = [G[u][v]['weight'] for u, v in zip(clique[:-1], clique[1:])]
        print(weights)
        avg_weight = np.mean(weights) if weights else 0
        cliques_with_avg_weight.append((clique, avg_weight))

    # Sort subgraphs according to the average weight in descending order
    cliques_sorted = sorted(cliques_with_avg_weight,
                            key=lambda x: x[1], reverse=True)

    # Mark nodes as unselected initially
    unselected_nodes = set(G.nodes())

    M = 0
    while M < K and cliques_sorted:
        # Find the node with maximum degree among unselected nodes
        max_degree_node = max(unselected_nodes, key=lambda x: G.degree(x))

        # Identify all complete subgraphs the chosen node belongs to
        node_cliques = [clique for clique,
                        _ in cliques_sorted if max_degree_node in clique]

        # Choose the unmarked complete subgraph with the maximum average weight
        if not node_cliques:
            break
        chosen_clique = max(node_cliques, key=lambda clique: next(
            (avg_weight for c, avg_weight in cliques_with_avg_weight if c == clique), 0))

        # Calculate centrality (this could be various forms of centrality; here we use degree centrality for simplicity)
        centrality = nx.degree_centrality(G).get(max_degree_node, 0)

        # Initiate the group with the chosen complete subgraph
        # This step could involve expanding the group based on local density, which is not detailed here.
        # For simplicity, we consider the chosen clique itself as the initial seed.
        initial_seeds.append(chosen_clique)

        # Mark all the selected nodes
        unselected_nodes.difference_update(chosen_clique)

        M += 1

    # If M < K, choose the remaining seeds as specified (not implemented here)
    # This could involve selecting nodes that are far away from the chosen seeds, based on some metric.

    return initial_seeds


# Example usage


adj_matrix = np.array([
    [0, 1, 1, 0, 0],
    [1, 0, 1, 0, 0],
    [1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1],
    [0, 0, 0, 1, 0],

])
G = nx.from_numpy_array(adj_matrix)
# Add edges and weights to G as per your complex network
# G.add_edge(node1, node2, weight=...)

# Set K, the number of initial seeds desired
K = 3

# Find initial seeds
initial_seeds = find_initial_seeds(G, K)
print("Initial Seeds:", initial_seeds)
