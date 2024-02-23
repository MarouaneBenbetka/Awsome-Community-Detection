import networkx as nx
import pandas as pd


class Action(object):
    def __init__(
            self, node, source_community, destination_community, value,
            save_actions=False 
                ):
        self.node = node
        self.source_community = source_community
        self.destination_community = destination_community
        self.value = value
        self.save_actions = save_actions
        self.actions = None

    def print_action(self):
        print(
            'node: {}, source: {}, destination: {}, value: {}'.format(
                self.node,
                self.source_community,
                self.destination_community,
                self.value
            )
        )


"""
- The louvain algorithm passes with two phases:
- phase 1: 
    - there is a certain ordering of nodes based on which the node movement gain is determined
    - Follow the order, and do the following: 
        - for each node, evaluate all the possible movements and choose the one that gives the highest modularity score
            - STEP 1: evaluate all the possible movements: see the neighboring nodes communities, build the action and its value
                    - add the action to the list of possible actions
            - STEP 2: among the possible actions, choose the one with the highest modularity gain
                    - if two actions have the same modularity, just choose one of them based on a certain predefined criteria           
        - do the same with the remaining nodes
        - this step is assumed to converge because we apply the reassignment action one time only for each node


- PHASE 2: 
    - reduce the nodes put in the same community to one node
    - relaunch the algorithm
"""


class LouvainMachine(object):
    def __init__(self, graph: nx.Graph):
        self.graph = nx.Graph()
        self.graph_history = []
        self.action_history = []
        # initial values for the communities
        # fill the nodes in the new graph initially
        self.graph.add_nodes_from(graph.nodes)

        # for each node in the graph, assign a community name
        # and a people community
        # note that there are some nodes that will not be present
        # as keys representing their people
        # initially, every node represents itself
        for node in graph.nodes:
            self.graph._node[node] = dict()
            self.graph._node[node]['community'] = node
            self.graph._node[node]['people_nodes'] = [node]

        # extract the edges from the previous graph
        # and add them to the newly created graph
        for edge in graph.edges:
            a, b = edge
            self.graph.add_edges_from([(a, b, {'weight': 1})])

        # todo: consider taking a look on this
        # compute the constant m for the graph
        self.m = len(self.graph.edges)
        self.graph_history.append(self.graph.copy())

    def order_nodes(self):
        # RETURN LIST OF REFERENCES TO THE NODES TO BE CONSIDERED IN THIS ORDER
        # see the current graph with the current node labels and determine the order
        # this phase happends only one time in the first phase of the louvain pass
        # return a list of nodes in the order in which they should be considerd
        # the HEURISTIC can be introduced here
        return self.graph.nodes

    def print_graph(self):
        for node in self.graph.nodes:
            print(node)

        for edge in self.graph.edges:
            print(edge)

    def print_status(self):
        # show the current status of the internal variables
        # show the graph nodes
        # show the graph edges
        # show the properties of the nodes
        # show the edges data as well
        print("Solver State:")
        print('Nodes:')
        print(self.graph.nodes)
        print('_________________________________________')
        print('Edges:')
        print(self.graph.edges)
        print('_________________________________________')
        print('Node attributes:')
        print(self.graph._node)
        print('_________________________________________')
        print('Edge data')
        for e in self.graph.edges:
            print('edge: {}, attributes: {}'.format(e, self.graph.get_edge_data(*e)))
        print('------------------End of Status------------------')

    def modularity_gain(self, action):
        pass
        # based on the formula given in the paper, compute the modularity gain of the current graph
        # given the action parameter

    def modularity_score(self):
        # compute the modularity of the graph
        return 0

    @staticmethod
    def graph_status(g):
        print("Solver State:")
        print('Nodes:')
        print(g.nodes)
        print('_________________________________________')
        print('Edges:')
        print(g.edges)
        print('_________________________________________')
        print('Node attributes:')
        print(g._node)
        print('_________________________________________')
        print('Edge data')
        for e in g.edges:
            print('edge: {}, attributes: {}'.format(e, g.get_edge_data(*e)))
        print('------------------End of Status------------------')

    def forward_louvain(self):

        # assign community maximizing delta gain for each node
        # improvement: True if the node-community assignment produced positive delta gain
        improvement = self.louvain_assign()

        if not improvement:
            return False

        # if there is improvement, proceed with the reduction phase
        g = self.louvain_reduce()

        # if the graph is not reduced
        if len(g.nodes) == len(self.graph.nodes):
            return False

        self.graph = g
        self.graph_history.append(self.graph.copy())
        # tell there is improvement
        return True

    def solve_communities(self):
        # TODO: consider adding other control parameters such as the pass count
        # or any other stop criteria

        improvement = self.forward_louvain()

        # consider doing something here
        while improvement:
            improvement = self.forward_louvain()

    def compute_delta_q(self, node, community):
        # ki_in:

        # m: the edge count in the entire graph
        # sum_weights: sum of the weights in the same community
        sum_weights_internal = 0
        ki_in = 0

        # ki is the sum of weights of edges incident to the current node
        ki = 0

        for a, b in self.graph.edges:
            # if a and b are in community: add c to sum_weights
            a_community = self.graph._node[a]['community']
            b_community = self.graph._node[b]['community']
            c = self.graph.get_edge_data(a, b)['weight']
            # print(c)
            if a_community == community and b_community == community:
                sum_weights_internal += 2 * c

            if a == node and b_community == community or b == node and a_community == community:
                ki_in += c

            if a == node or b == node:
                ki += c
        # compute the value of ki_in
        # TODO: retake a look here

        # delta q: (ki_in / m) - (ki * degree of the class) / (2*m**2)
        delta_q = (ki_in / self.m) - (sum_weights_internal * ki) / (2 * self.m ** 2)
        return delta_q

    def neighbor_communities(self, node):
        neighbor_communities = set()
        node_neighbors = list(nx.neighbors(self.graph, node))

        # print('=============')
        for neighbor in node_neighbors:
            neighbor_communities.add(self.graph._node[neighbor]['community'])

        return list(neighbor_communities)

    def louvain_assign_possible_actions(self, node):

        neighbor_communities = self.neighbor_communities(node)

        actions = []
        print('neighbor communities', neighbor_communities)
        for community in neighbor_communities:  # the candidate communities
            # compute delta gain
            delta_q = self.compute_delta_q(node, community)

            action = Action(
                node,
                self.graph._node[node]['community'],
                community,
                delta_q
            )
            actions.append(action)

        return actions

    def apply_action(self, action: Action):
        # source = action.source_community
        destination = action.destination_community
        # value = action.value
        node = action.node
        self.graph._node[node]['community'] = destination

    def louvain_assign(self):
        # this is the first phase of the louvain algorithm
        # the expected result is the graph with the new labels for the nodes
        ordered_nodes = self.order_nodes()
        # m = sum(list(map(lambda x: self.graph.get_edge_data(x[0], x[1])['weight'], self.graph.edges)))

        # printing the content of the dict
        improvement = False
        phase_actions = []
        for node in ordered_nodes:
            actions = self.louvain_assign_possible_actions(node)

            action_max = None
            if len(actions) > 0:
                action_max = max(actions, key=lambda action: action.value)

                phase_actions.append((actions.copy(), action_max))
                if action_max.value > 0:
                    action_max.print_action()
                    self.apply_action(action_max)
                    print('choosing maximum action >>>>', end='')
                    action_max.print_action()
                    improvement = True
                    continue

            print('no action is chosen')
        self.action_history.append(phase_actions)
        return improvement

    def louvain_reduce(self):
        # generate a new graph, based on the current communities

        g = nx.Graph()
        print(g)
        # generating the new graph nodes
        community_nodes_dict = dict()
        for node in self.graph.nodes:
            current_community = self.graph._node[node]['community']

            if current_community in community_nodes_dict:
                community_nodes_dict[current_community].extend(
                    self.graph._node[node]['people_nodes']
                )
            else:
                community_nodes_dict[current_community] = []
                (
                    community_nodes_dict[current_community].extend
                        (
                        self.graph._node[node]['people_nodes']
                    )
                )
        g.add_nodes_from(list(community_nodes_dict.keys()))

        for n in g.nodes:
            g._node[n] = dict()
            g._node[n]['community'] = n
            g._node[n]['people_nodes'] = community_nodes_dict[n]
        print(g._node)

        # generate edges of the graph
        new_edges_dict = {}
        for n1, n2 in self.graph.edges:
            # here here
            # a: community of the node n1
            # b: community of the node n2
            a = self.graph._node[n1]['community']
            b = self.graph._node[n2]['community']

            c = self.graph.get_edge_data(n1, n2, 'weight')

            if (a, b) in new_edges_dict:
                new_edges_dict[(a, b)] += c['weight']
            elif (b, a) in new_edges_dict:
                new_edges_dict[(b, a)] += c['weight']
            else:
                new_edges_dict[(a, b)] = c['weight']
            # g.add_edge((self.graph._node[a]['community'], self.graph._node[b]['community']))

        print('adding edges from necessary')
        for key, value in new_edges_dict.items():
            # we should consider adding the des between the communities not the edges themselves
            a, b = key

            g.add_edges_from([(a, b, {'weight': value})])

        return g.copy()

    @staticmethod
    def display_graph_table(g: nx.Graph, display_fn, title=''):

        # 1. print the table of nodes
        # each node will have a name, a set of people nodes

        peoples_nodes = [g._node[node]['people_nodes'] for node in g.nodes]
        communities = [g._node[node]['community'] for node in g.nodes]
        df_nodes = pd.DataFrame.from_dict(
            {
                'nodes': list(map(lambda x: str(x), g.nodes)),
                'community': communities,
                'people_nodes': peoples_nodes
            }
        )
        ids = [(i + 1) for i in range(len(g.edges))]
        nodes_a = [a for a, b in g.edges]
        nodes_b = [b for a, b in g.edges]

        weights = [g.get_edge_data(u, v)['weight'] for u, v in g.edges]
        df_edges = pd.DataFrame.from_dict(
            {
                'edges': ids,
                'node_a': nodes_a,
                'node_b': nodes_b,
                'weight': weights
            }
        )

        print('--------------------------{}--------------------------'.format(title))
        display_fn(df_nodes)
        display_fn(df_edges)
        print('_______________________________________________________________________________________________________')
        # display a table of edges, each edge will have its weight

    @staticmethod
    def display_graph_actions(actions: 'List[Action]', max_action: Action, display_fn):
        # construct a data frame for actions:
        action_sources = [a.source_community for a in actions]
        action_destinations = [a.destination_community for a in actions]
        action_nodes = [a.node for a in actions]
        action_values = [a.value for a in actions]

        actions_df = pd.DataFrame.from_dict({
            'nodes': action_nodes,
            'source community': action_sources,
            'destination community': action_destinations,
            'mod gain': action_values

        })

        display_fn(actions_df)

    @staticmethod
    def display_graph_phase_actions(phase_actions, display_fn, phase=''):
        pass
        # phase actions is a list of tuples
        # each tuple has the following format (list of node actions, max action)
        for node_actions, max_action in phase_actions:
            # construct the data frame for the current node
            nodes = [a.node for a in node_actions]
            sources = [a.source_community for a in node_actions]
            destinations = [a.destination_community for a in node_actions]
            values = [a.value for a in node_actions]

            # build the data frame to display
            node_actions_df = pd.DataFrame.from_dict({
                'node': nodes,
                'source': sources,
                'destination': destinations,
                'value': values
            })
            print('---------------Possible actions for node {} in phase {}---------------'.format(
                nodes[0], phase
            ))
            display_fn(node_actions_df)
            # the above four lists are related to the same node
            # among these, we will choose one that maximizes modularity gain
            print('the action among the previous actions that maximizes modularity gain is:')
            max_action.print_action()
            # display the possible actions for the node alongside the max action
        print('----------------------------------------------------------------')
        print('displayed possible actions for all the nodes in phase: {}'.format(phase))
        print('----------------------------------------------------------------')

    def display_graph_history_tables(self, display_fn):
        # for i, g in zip(range(1, len(self.graph_history)), self.graph_history[1:]):
        for i, g, a in zip(range(len(self.graph_history)), self.graph_history, self.action_history):
            print('')
            self.display_graph_table(g, lambda x: display_fn(x), title='Graph in the phase: {}'.format(i + 1))
            # self.display_graph_actions(actions, max_action, lambda x: display_fn(x))
            self.display_graph_phase_actions(a, phase=i + 1, display_fn=display_fn)
            print('')

    def map_to_true_labels_space(self, nodes, true_labels):
        community_nodes = dict()
        for n in self.nodes:
            community_nodes[n] = self.graph._node['people_nodes']
        
        predicted_communities = [values for i, values in community_nodes.items()]
        
        true_communities_dict = dict()

        # construct true communities
        for node, label in zip(nodes, true_labels):
            if label in true_communities_dict:
                true_communities_dict[label].append(node)
            else:
                true_communities_dict[label] = [node,]
        
        true_communities = [values for i, values in true_communities_dict.items()]

        # compute the nmi from true_communities
        

    def compute_modularity(self):
        partition = {node: self.graph.nodes[node]['community'] for node in self.graph.nodes()}
        modularity = nx.community.modularity(partition, self.graph) 
        return modularity