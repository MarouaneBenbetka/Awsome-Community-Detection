import networkx as nx
import matplotlib.pyplot as plt
import pickle
import pandas as pd
from typing import List


class TeamDataSource(object):
    def __init__(self, uid, data_path):
        self.id = uid
        self.data_path = data_path


class StudentGraphGenerator(object):

    def __init__(self, student_list_data_source):
        self.student_list_data_source = student_list_data_source
        self.data_sources = set()
        self.collaborations_list = []
        self.constraints = []
        self.generated_binary_graph = None
        self.generated_weighted_graph = None

    def _generate_collaborations_list(self):
        # generate the global list of collaborations

        for data_source in self.data_sources:
            data_source_path = data_source.data_path

            with open(data_source_path, 'r') as f:
                lines = list(map(lambda x: x.strip(), f.readlines()))
                lines = list(filter(lambda x: len(x) > 0, lines))

                # extract the team from each line and add it to the global variable collaborations_list
                for line in lines:
                    members = line.split(',')
                    self.collaborations_list.append(members.copy())
        return self.collaborations_list

    def consider_team_data_source(self, id, teams_data_source):

        data_source = TeamDataSource(id, teams_data_source)
        self.data_sources.add(data_source)

    def consider_constraint(self, member_list):
        self.constraints = member_list

    def print_data_sources(self):
        for data_source in self.data_sources:
            print("DataSource(id: {}, source: {})".format(data_source.id, data_source.data_path))

    def _generate_individuals_binary_collaborations(self):
        def _generate_binary_collaborations(team):
            lista = []
            for i in range(len(team) - 1):
                for j in range(i + 1, len(team)):
                    collaboration = (team[i], team[j])
                    lista.append(collaboration)

            return lista.copy()

        individuals = set()
        binary_collaborations_list = []

        # Preprocessing phase,
        # get the data in a format ready for exploitation

        for team in self.collaborations_list:
            # team is a list of members
            # extract individuals of the team
            for m in team:
                individuals.add(m)

            # extract all relations existing within the team
            current_colaborations = _generate_binary_collaborations(team)
            binary_collaborations_list.extend(current_colaborations.copy())

        # consider constraints:
        if len(self.constraints) > 0:

            # do the filtering on individuals
            new_individuals = set()
            new_collaborations_binary = []
            for ind in individuals:
                if ind in self.constraints:
                    new_individuals.add(ind)

            # do the filtering on collaborations
            for col in binary_collaborations_list:
                if col[0] in self.constraints and col[1] in self.constraints:
                    new_collaborations_binary.append(col)
            individuals = new_individuals
            binary_collaborations_list = new_collaborations_binary

        return individuals, binary_collaborations_list

    def _generate_graph_binary(self):
        individuals, binary_collaborations_list = \
            self._generate_individuals_binary_collaborations()

        # Graph construction phase
        # generate the final results

        g = nx.Graph()
        g.add_nodes_from(list(individuals))
        g.add_edges_from(list(binary_collaborations_list))

        self.generated_binary_graph = g.copy()
        return g

    def _generate_graph_weighted(self):
        def _generate_weighted_collaboration(binary_collaborations):
            weighted_collaborations_dict = dict()
            for bc in binary_collaborations:
                a, b = bc[0], bc[1]
                if (a, b) in weighted_collaborations_dict:
                    weighted_collaborations_dict[(a, b)] += 1
                elif (b, a) in weighted_collaborations_dict:
                    weighted_collaborations_dict[(b, a)] += 1
                else:
                    weighted_collaborations_dict[bc] = 1
            return weighted_collaborations_dict

        individuals, binary_collaborations_list = \
            self._generate_individuals_binary_collaborations()

        # preprocessing of binary relations to get weighted results
        # edge_attributes = [(1, 2, {'weight': 3.0}), (2, 3, {'weight': 5.0})]
        # each node with be a tuple of three elements (nodeA, nodeB, dict)
        weighted_collaborations = _generate_weighted_collaboration(binary_collaborations_list)

        edges = []
        for key, value in weighted_collaborations.items():
            edges.append((key[0], key[1], {"weight": value}))

        # Graph construction phase
        # generate the final results
        g = nx.Graph()
        g.add_nodes_from(list(individuals))
        g.add_edges_from(list(edges))
        self.generated_weighted_graph = g.copy()
        return g

    def generate_graph(self, mode='binary'):
        # consider the existence or absence of the edge
        MODE_BINARY = 'binary'

        # consider the existence or absence of the edge with weight as well 
        MODE_WEIGHTED = 'weighted'

        MODE_VALUES = [MODE_BINARY, MODE_WEIGHTED]
        assert mode in MODE_VALUES, "Mode must be either '{MODE_BINARY}' or '{MODE_WEIGHTED}'"

        # transform the data sources to a local variable

        if mode == MODE_BINARY:
            # generate the graph in binary mode
            self._generate_graph_binary()
        else:
            # generate the graph with weighted mode
            self._generate_graph_weighted()

    def draw_graph_binary(self, save_option=False, save_path=None):
        plt.figure(figsize=(12, 7))

        nx.draw(
            self.generated_binary_graph,
            with_labels=True,
            alpha=0.9,
            pos=nx.spring_layout(self.generated_binary_graph, k=0.9),
            node_color='skyblue',
            node_size=2000,
            font_size=8,
            font_color='black',
            font_weight='bold',
            edge_color='red', width=1
        )

        # Show the plot
        plt.title("Graph Visualization")

        # THE SAVE OPTION        
        if save_option and save_path != None:
            plt.savefig(save_path)

        plt.show()

    def draw_graph_weighted(self, save_option=False, save_path=None):
        plt.figure(figsize=(12, 7))

        nx.draw(
            self.generated_binary_graph,
            with_labels=True,
            pos=nx.spring_layout(self.generated_binary_graph, k=0.9),
            node_color='skyblue',
            node_size=1000,
            font_size=12,
            font_color='black',
            font_weight='bold',
            edge_color='red', width=1
        )

        # Show the plot
        plt.title("Graph Visualization")

        # THE SAVE OPTION        
        if save_option and save_path != None:
            plt.savefig(save_path)

        plt.show()

    def export_binary_graph(self, export_path):
        name: str = export_path
        if not name.endswith('.pkl'):
            name += '.pkl'

        with open(name, 'wb') as file:
            # Serialize and write the object to the file
            pickle.dump(self.generated_binary_graph, file)

    def export_weighted_graph(self, export_path):
        name: str = export_path
        if not name.endswith('.pkl'):
            name += '.pkl'

        with open(name, 'wb') as file:
            # Serialize and write the object to the file
            pickle.dump(self.generated_weighted_graph, file)


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


class Action(object):
    def __init__(self, node, source_community, destination_community, value):
        self.node = node
        self.source_community = source_community
        self.destination_community = destination_community
        self.value = value

    def print_action(self):
        print(
            'node: {}, source: {}, destination: {}, value: {}'.format(
                self.node,
                self.source_community,
                self.destination_community,
                self.value
            )
        )


class LouvainMachine(object):
    def __init__(self, graph: nx.Graph):
        self.graph = nx.Graph()
        self.graph_history = []
        self.action_history = []
        # initial values for the communities
        # fill the nodes in the new graph initially
        self.graph.add_nodes_from(graph.nodes)

        # for each node in the graph, assign a community name
        # and a prople community
        # note that there are some nodes that will not be present
        # as keys representing their people
        # initially, every node represents itself
        for node in graph.nodes:
            self.graph._node[node] = dict()
            self.graph._node[node]['community'] = node
            self.graph._node[node]['people_nodes'] = [node]

        # print the nodes to make sure that they are created
        print('>> Called constructor LouvainMachine: created graph with nodes:')
        print(self.graph.nodes)
        print(self.graph._node)
        print('---------------------------------------------------------------')

        # extract the edges from the previous graph
        # and add them to the newly created graph
        for edge in graph.edges:
            a, b = edge
            self.graph.add_edges_from([(a, b, {'weight': 1})])

            # self.graph.add_edge(a, b, 1)
        # print the edges to make sure that they are created
        print('created graph with edges:')
        print(self.graph.edges)
        print('---------------------------------------------------------------')
        # todo: consider taking a look on this
        self.m = len(self.graph.edges)
        self.graph_history.append(self.graph.copy())

        self.improvement = True

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
        # consider the current graph with the current labels, and compute the modularity score
        # compute the global modularity score of the current graph
        node_count = len(self.graph.nodes)

        # for each node, compute the number of neighboring nodes
        nodes_neighbor_count = {}
        Q = 0
        for node in self.graph.nodes:
            for neighbor in nx.neighbors(self.graph, node):
                Q += 1 - (() / ())

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

        improvement = self.louvain_assign()
        print('called louvain_assign, got the following value for improvement: ', improvement)

        if not improvement:
            return False

        # self.graph_history.append(self.graph.copy())
        # if there is improvement, proceed with the reduction phase
        g = self.louvain_reduce()

        if len(g.nodes) == len(self.graph.nodes):
            return False

        self.graph = g
        # print("showing the returned graph")
        # self.graph_status(g)
        # print('status after updating self.graph')
        # self.print_status()
        self.graph_history.append(self.graph.copy())
        return True

    def solve_communities(self):
        # TODO: consider adding other control parameters such as the pass count
        # or any other stop criteria

        improvement = self.forward_louvain()

        # consider doing something here
        while improvement:
            improvement = self.forward_louvain()

        # invoke the two phases of louvain algorithm stated below
        # consider adding some parameters to control tracking the history and all things related to that

    def apply_action(self, action: Action):
        source = action.source_community
        destination = action.destination_community
        value = action.value
        node = action.node
        # TODO: the problem is coming from here, consider removing all the elements, not only the
        # TODO: node having the same name
        # self.graph._node[source]['people_nodes'].remove(node)
        # self.graph._node[destination]['people_nodes'].append(node)
        # self.graph._node[destination]['people_nodes'].extend(self.graph._node[node]['people_nodes'])
        self.graph._node[node]['community'] = destination
        # TODO: consider doing more thing here
        # TODO: consider writing all the data structures involved
        # and update each one of them individually so that waste no info

    def louvain_assign(self):
        # this is the first phase of the louvain algorithm
        # the expected result is the graph with the new labels for the nodes
        ordered_nodes = self.order_nodes()
        # m = sum(list(map(lambda x: self.graph.get_edge_data(x[0], x[1])['weight'], self.graph.edges)))

        # printing the content of the dict
        improvement = False
        phase_actions = []
        for node in ordered_nodes:

            # get the set of neighboring communities
            neighbor_communities = set()
            node_neighbors = list(nx.neighbors(self.graph, node))

            print('=============')
            for neighbor in node_neighbors:
                neighbor_communities.add(self.graph._node[neighbor]['community'])
                # neighbor_communities.add(self.graph.)
            # if self.graph._node[node]['community'] in neighbor_communities:
            #     neighbor_communities.remove(self.graph._node[node]['community'])

            # here we  have the set of possible new communities READY
            actions = []
            neighbor_communities = list(neighbor_communities)
            print('neighbor communities', neighbor_communities)
            for community in neighbor_communities:  # the candidate communities
                # compute value

                # ki_in: the number of node neighbors in the same class

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
                action = Action(
                    node,
                    self.graph._node[node]['community'],
                    community,
                    delta_q
                )
                actions.append(action)
                # the end of the evaluation shoudl be here

            # choose the action that maximizes the delta q
            # print('possible actions:')
            # print(actions)

            # print('the set of possible actions in the current phase:')
            # for a in actions:
            #     a.print_action()
            # print('-----------------------------------------------------')

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
            # print(f'the community of {node} is {current_community}')
            # community_nodes_dict[current_community].append('4445')
            if current_community in community_nodes_dict:
                print('before:')
                print(community_nodes_dict[current_community])
                # community_nodes_dict[current_community].append(node)
                community_nodes_dict[current_community].extend(
                    self.graph._node[node]['people_nodes']
                )
                print('after:')
                print(community_nodes_dict[current_community])

            else:
                community_nodes_dict[current_community] = []
                community_nodes_dict[current_community].extend(
                    self.graph._node[node]['people_nodes']
                )
        # print('the dict')
        # print(community_nodes_dict)
        # remove the keys that have no value from the dict
        # to_remove = []
        # for key, value in community_nodes_dict.items():
        #     if value == {}:
        #         to_remove.append(key)
        # for key in to_remove:
        #     del community_nodes_dict[key]
        # print('keys', list(community_nodes_dict.keys()))
        g.add_nodes_from(list(community_nodes_dict.keys()))
        # print('nodesss')
        # print(g.nodes)
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

            # print('(a, b) = ({}, {})'.format(a, b))
            g.add_edges_from([(a, b, {'weight': value})])

        # self.graph_status(g=g)
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
        print('______________________________________________________________')
        # display a table of edges, each edge will have its weight

    @staticmethod
    def display_graph_actions(actions: List['Action'], max_action: Action, display_fn):
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
        print('displayed possible actions for all the nodes in phase: {}'.format(phase))
        print('----------------------------------------------------------------')

    def display_graph_history_tables(self, display_fn):
        # for i, g in zip(range(1, len(self.graph_history)), self.graph_history[1:]):
        for i, g, a in zip(range(len(self.graph_history)), self.graph_history, self.action_history):
            # LouvainMachine.display_graph_table(g, display_fn)
            # actions, max_action = a
            # a represents phase actions
            # print('got value for a: ', a)
            print('')
            self.display_graph_table(g, lambda x: display_fn(x), title='Graph in the phase: {}'.format(i + 1))
            # self.display_graph_actions(actions, max_action, lambda x: display_fn(x))
            self.display_graph_phase_actions(a, phase=i + 1, display_fn=display_fn)
            print('')
