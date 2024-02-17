import numpy as np
import pandas as pd

import networkx as nx
import matplotlib.pyplot as plt
import pickle


class TeamDataSource(object):
    def __init__(self, id, data_path):
        self.id = id
        self.data_path = data_path

class StudentGraphGenerator(object):

    def __init__(self, student_list_data_source):
        self.student_list_data_source = student_list_data_source
        self.data_sources = set()
        self.collaborations_list = []

        self.generated_binary_graph = None
        self.generated_weighted_graph = None
        
    def _generate_collaborations_list(self):
        # generate the global list of collaborations
        
        for data_source in self.data_sources:
            data_source_path = data_source.data_path
            
            with open(data_source_path, 'r') as f:
                lines = list(map(lambda x: x.strip(),f.readlines()))
                lines = list(filter(lambda x: len(x) > 0, lines))
                
                # extract the team from each line and add it to the global variable collaborations_list
                for line in lines:
                    members = line.split(',')
                    self.collaborations_list.append(members.copy())
        return self.collaborations_list
            
    def consider_team_data_source(self, id, teams_data_source):
        
        data_source = TeamDataSource(id, teams_data_source)
        self.data_sources.add(data_source)
    
    def print_data_sources(self):
        for data_source in self.data_sources:
            print("DataSource(id: {}, source: {})".format(data_source.id, data_source.data_path))
    
    def _generate_individuals_binary_collaborations(self):
        def _generate_binary_collaborations(team):
            lista = []
            for i in range(len(team) - 1):
                    for j in range(i+1, len(team)):
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

    def draw_graph_binary(self):
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
        plt.show()

    def draw_graph_weighted(self):
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
        plt.show()

    
    def export_binary_graph(self, export_path):
        name:str = export_path
        if not name.endswith('.pkl'):
            name += '.pkl'

        with open(name, 'wb') as file:
            # Serialize and write the object to the file
            pickle.dump(self.generated_binary_graph, file)

    def export_weighted_graph(self, export_path):
        name:str = export_path
        if not name.endswith('.pkl'):
            name += '.pkl'

        with open(name, 'wb') as file:
            # Serialize and write the object to the file
            pickle.dump(self.generated_weighted_graph, file)

