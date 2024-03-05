def local_expension(G: nx.Graph, D: np.ndarray, k=2):
    """
    This function takes a graph G and returns a list of k initial seeds.
    """

    adj_matrix = nx.to_numpy_array(G)
    initial_seeds = []

    cliques = find_cliques(G, D)
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

        fitness_value = fitness_function(adj_matrix, chosen_clique)

        condidat_nodes_in_order = sorted(
            unselected_nodes, key=lambda node: min(D[node, target_node] for target_node in unselected_nodes))

        for node in condidat_nodes_in_order:
            if node not in chosen_clique:
                fitness = fitness_function(
                    adj_matrix, chosen_clique + [node])

                if fitness >= fitness_value:
                    fitness_value = fitness
                    chosen_clique.append(node)

        H = G.subgraph(chosen_clique)
        closeness_centrality_subgraph = nx.closeness_centrality(H)
        centroid = max(
            closeness_centrality_subgraph, key=closeness_centrality_subgraph.get)

        initial_seeds.append(centroid)
        unselected_nodes.difference_update(chosen_clique)

        new_cliques = []
        for cliques in cliques_sorted:
            cliques["nodes"] = [node for node in cliques["nodes"]
                                if node in unselected_nodes]
            cliques["weight"] = average_weight(adj_matrix, cliques["nodes"])
            if len(cliques["nodes"]) > 2:
                new_cliques.append(cliques)

        cliques_sorted = sorted(
            new_cliques, key=lambda x: x["weight"], reverse=True)

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