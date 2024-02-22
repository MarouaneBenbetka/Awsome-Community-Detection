import networkx as nx
import pandas as pd
import numpy as np
from manim import *

from typing import Hashable

"""

"""

class LouvainScene(Scene):
    # we need to store all the relevant data structures representing the state of our video
    def __init__(self, graph: nx.Graph, **kwargs):
        # this is the principal graph that we will be working on
        self.to_solve_graph = graph
        super().__init__(**kwargs)

    # create the graph and show it on the screen
    def animate_create_manim_graph(self, graph: nx.Graph):
        # take the networkx graph, convert it to manim graph
        # and return the manim graph

        # extract vertices and edges from the old graph
        vertices = graph.nodes
        edges = graph.edges

        manim_graph = Graph(vertices, edges)

        self.play(Create(manim_graph))
        self.wait()


    # determine the order of considering the nodes and show that on the screen
    def animate_graph_nodes_order(self, graph: Graph, ordered_nodes: List[Hashable]):
        node_order_texts = []

        for node, pos in graph.vertices.items():
            # find the order of the current node
            node_order_text = str(ordered_nodes.index(node))


            text = Text(node_order_text)
            text.next_to(pos, direction=DOWN)  # Adjust position of text relative to node
            self.add(text)

            # keep a reference on the text so that to remove it later
            node_order_texts.append(text)
        self.wait()

        # remove the texts from the screen
        for text in node_order_texts:
            self.remove(text)
            # there should be some waiting between removing the texts
            self.wait()

    # get the node as input and highlight the potential communities
    def animate_find_potential_communities(self, node, neighboring_nodes, potential_communities):
        # there should be a data structures out there representing the set of nodes
        # to take into consideratio
        # for each of the neighbors, find the community

        # the node and the text to get highlighted at the same time
        node_A: Mobject = None
        text_B: Mobject = None
        # TODO: consider retaking a look on this,
        # TODO: the exact happening of the process is to be determined
        self.play(
            node_A.animate.set_color(YELLOW),  # Highlight node A
            text_B.animate.set_color(YELLOW),  # Highlight text B
        )
        self.wait()

    # show the delta score for the choice
    def animate_evaluate_node_potential_communities(self, node, potential_communities):
        # TODO: also note that the scores are obtained from the outside
        # suppose that there is a table on which the potential communities are written=
        # for each community we write the delta score below it
        pass


    # change the label to the class with max modularity
    def animate_assign_to_community_max_modularity(self, node: Mobject, community):
        community_color = RED
        self.play(Animation(node.set_color, community_color))
        # self.play(Animate(node_A.set_color, RED), run_time=2)

    # highlight the nodes of the class with a certain community
    def animate_highlight_community_nodes(self, nodes, community):
        # Iterate through nodes and add the ones to highlight to the VGroup
        highlighted_nodes = VGroup() # this is the set of nodes to consider put into a view group
        manim_graph: Graph = None
        for node_key, node_obj in manim_graph.vertices.items():
            if node_key in node_obj:
                highlighted_nodes.add(node_obj)

        # Highlight nodes with animation
        self.play(highlighted_nodes.animate.set_color(YELLOW), run_time=2)

    # merge the nodes into a single node
    def animate_merge_same_community_nodes(self, manim_graph, nodes_from, node_to: Mobject):

        # get the position of the destination node
        node_to_position = node_to.get_coord()

        # Animate the transition of the nodes to the merged node
        for node_key in nodes_from:
            node_obj = manim_graph.vertices[node_key]
            self.play(node_obj.animate.move_to(node_to_position), run_time=1)

        self.wait()

    # highlight the edges whose one node at least is in community
    def animate_highlight_edges_concerning_communities(self, graph, nodes):
        pass
        # highlight the nodes in the community
    #

    # merge the edges into one edge
    def animate_merge_edges_to_one_edge(self):
        pass

    # just a setup function
    def setup(self):
        # consider generating the intermediate results necessary for visualization

        pass

    # the entire visualization will be done here
    def construct(self):
        self.animate_create_manim_graph(self.to_solve_graph)

