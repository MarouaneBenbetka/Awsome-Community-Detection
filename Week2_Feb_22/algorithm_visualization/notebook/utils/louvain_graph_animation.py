from manim import *
import networkx as nx

"""
We consider giving some explanation about what the functioning of thjs part will be like
In the first place, we have already established the infrastructure to geneate the different 
actions that are taken during the Louvain passes

The Louvain Algorithm generally goes like the following:

    1. Assignment Phase: 
        a. Determine a certain order of nodes: (default order in this case)
        b. for each node, evaluate potential communities
        c. select the community assignment with maximum modularity gain
    2. Reduction phase: 
        a. for each community, highlight the nodes with the same community
        b. Merge the highlighted nodes into a single node in a new graph that will be displayed on the right side
        c. For each two of the new communities, highlight the concerned edges in the old graph
        d. merge the selected edges into a single edge between the communities in the new graph
    
    For each of the previously mentioned actions, we define a scene, alongside its inputs and expected outputs
    
    We should learn more about the manim Graph Library
"""

"""
class MyParameterizedScene(Scene):
    def __init__(self, param1, param2, **kwargs):
        self.param1 = param1
        self.param2 = param2
        super().__init__(**kwargs)

    def construct(self):
        # Example animation using parameters
        square = Square()
        square.move_to(LEFT * self.param1)
        circle = Circle()
        circle.move_to(RIGHT * self.param2)
        self.play(Create(square), Create(circle))
        self.wait(2)
"""
# actually, it turned out that we will use a single scene to manage the entire staff
# let's just go with this approach, if we discover a new way to do that, then there will
# getting the old verson of code to work with the newer one


class CreateGraphScene(Scene):

    def __init__(self, graph: nx.Graph, **kwargs):
        vertices = graph.nodes
        edges = graph.edges

        manim_graph = Graph(vertices, edges, vertex_type=Dot, vertex_config={2: {"fill_color": BLACK}})
        self.manim_graph = manim_graph
        super().__init__(**kwargs)

    def construct(self):
        # create the graph and show it on the screen
        self.play(Create(self.manim_graph))
        self.wait()


class OrderGraphNodesScene(Scene):
    """
    This concerns the first step of the first phase
    Inputs: takes a graph in the input
    Outputs: return the ordered nodes:
    TODO: consider elaborating more on this
    """

    def __init__(self, graph: nx.Graph):
        # TODO: consider taking a look on this
        # determine the order of the graph nodes
        Scene.__init__(self)

        # create the graph of manim

    def construct(self):
        pass

    def construct(self):
        # for each node associate a small lable with text representing the order
        # in which the node will be considered
        pass


class FindPotentialCommunitiesScene(Scene):

    def __init__(self, graph, node):
        pass

    def construct(self):
        # for the passed node, show potential communities into a side list
        # we might need some design skills in this phase
        pass


class EvaluateNodePotentialCommunities(Scene):

    def __init__(self, node, communities):
        pass

    def construct(self):
        # For each community, evaluate the score,
        # This logic seems to be complex, consider dividing the problem if necessary
        pass
    Scene


class AssignToClassMaxModularityScene(Scene):
    """
    This is related to the step C of the first phase
    """

    def __init__(self, node, community):
        # we can represent communities with colors or numbers
        pass

    def construct(self):
        pass


class HighlightCommunityNodesScene(Scene):
    """"
    def __init__(self, param1, param2, **kwargs):
        self.param1 = param1
        self.param2 = param2
        super().__init__(**kwargs)
        """

    def __init__(self, nodes, graph: Graph, **kwargs):
        self.nodes_to_highlight = nodes
        self.graph = graph
        super().__init__(**kwargs)

    def construct(self):
        # change color of the first node
        first_key = list(self.graph.vertices.keys())[0]
        self.graph.vertices[first_key].add_updater(lambda o: o.set_color(DARK_BROWN))
        self.wait()


class MergeSameCommunityNodesScene(Scene):
    """
    This relates to the phase B of the second phase
    """

    def __init__(self, community, nodes):
        pass

    def construct(self):
        # construct a new node form the previous nodes having the same community

        pass


class HighlightEdgesConcerningCommunities(Scene):

    def __init__(self):
        pass

    def construct(self):
        # highlight in (bold) the edges related to some communities
        pass


class MergeEdgesToOneEdgeScene(Scene):

    def __init__(self):
        pass

    def construct(self):
        # merge the edges into one edge with the weight being the sum of the weights
        pass
