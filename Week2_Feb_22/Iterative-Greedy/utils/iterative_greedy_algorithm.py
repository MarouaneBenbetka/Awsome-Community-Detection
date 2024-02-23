import numpy as np
from utils.communities_network import modularity_matrix, modularity, filter_adj_matrix
from utils.visualization_animation import communities_to_frame
from tqdm.notebook import tqdm


def GCP(adj_matrix: np.ndarray) -> list:

    V = list(range(adj_matrix.shape[0]))

    v = np.random.choice(V)
    V.remove(v)

    K0 = [v]
    communities = [K0]
    nodes = [v]

    Mdb = -1

    while V:
        v = np.random.choice(V)
        nodes.append(v)

        Mdb = -1
        best_community = None
        best_community_index = -1

        new_adj_matrix = filter_adj_matrix(
            adj_matrix, nodes)

        for i, Ki in enumerate(communities):
            Ki_new = Ki + [v]

            new_communities = communities.copy()

            new_communities[i] = Ki_new

            Md = modularity(new_adj_matrix, new_communities)

            if Md > Mdb:
                Mdb = Md
                best_community = Ki_new
                best_community_index = i

        if len(nodes) > 1:
            new_adj_matrix = filter_adj_matrix(adj_matrix, nodes)
            Mdphi = modularity(new_adj_matrix, communities + [[v]])
        else:
            Mdphi = -1

        if Mdb > Mdphi:
            communities[best_community_index] = best_community
        else:

            Mdb = Mdphi
            Ki = [v]
            communities.append(Ki)

        V.remove(v)

    return communities, Mdb


def destruct(adj_matrix, communities, beta):

    nodes = list(range(adj_matrix.shape[0]))

    removed_nodes = np.random.choice(
        nodes, int(beta * len(nodes)), replace=False)

    filtered_communities = []
    for community in communities:

        new_community = [
            node for node in community if node not in removed_nodes]

        if new_community:
            filtered_communities.append(new_community)

    return removed_nodes, filtered_communities


def reconstruct(adj_matrix, communities, removed_nodes):

    # print("removed_nodes : " , removed_nodes)

    nodes = [node for node in list(
        range(adj_matrix.shape[0])) if node not in removed_nodes]

    Mdb = -1

    for node in removed_nodes:

        # print("Choosing Community for node : " , node)

        Mdb = -1
        best_community = None
        best_community_index = -1

        nodes.append(node)

        new_adj_matrix = filter_adj_matrix(adj_matrix, nodes)

        for i, Ki in enumerate(communities):
            Ki_new = Ki + [node]

            new_communities = communities.copy()
            new_communities[i] = Ki_new

            Md = modularity(new_adj_matrix, new_communities)

            if Md > Mdb:
                Mdb = Md
                best_community = Ki_new
                best_community_index = i

        Mdphi = modularity(new_adj_matrix, communities)

        # communities[best_community_index] = best_community

        if Mdb >= Mdphi:
            # print("Modularity : " , Mdb)
            communities[best_community_index] = best_community
            # print("Added to Community : " , best_community_index , " : " , best_community)
        else:
            # print("Modularity : " , Mdphi)
            Ki = [node]
            communities.append(Ki)
            Mdb = Mdphi
            # print("Added to new Community : " , Ki)

    return communities, Mdb


def IG(adj_matrix, nb_iterations=100, beta=.4):

    frames = []
    modularity_trace = []
    communities_trace = []

    # frames.append({'C': [i+1 for i in range(adj_matrix.shape[0])], 'Q': 0})

    communities, mod = GCP(adj_matrix)

    modularity_trace.append(mod)
    frames.append(communities_to_frame(adj_matrix.shape[0], communities, mod))
    communities_trace.append(communities)

    for i in tqdm(range(nb_iterations), desc="IG", total=nb_iterations):

        removed_nodes, filtered_communities = destruct(
            adj_matrix, communities, beta)

        new_communities, mod = reconstruct(
            adj_matrix, filtered_communities, removed_nodes)

        if modularity(adj_matrix, new_communities) > modularity(adj_matrix, communities):
            communities = new_communities
            modularity_trace.append(mod)
            communities_trace.append(communities)
            frames.append(communities_to_frame(
                adj_matrix.shape[0], communities, mod))

    return communities, modularity_trace, communities_trace, frames
