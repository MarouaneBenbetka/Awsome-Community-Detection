from manim import *


class GraphScene(Scene):

    def construct(self):
        # Create two nodes
        node1 = Circle(color=BLUE).shift(LEFT)
        node2 = Dot(color=BLUE).shift(RIGHT)

        # Create an edge between nodes
        edge = Line(node1.get_center(), node2.get_center())

        # Add nodes and edge to the scene
        self.add(node1, node2, edge)

        # Add labels to the nodes
        label1 = Tex("Node 1").next_to(node1, UP)
        label2 = Tex("Node 2").next_to(node2, UP)

        self.add(label1, label2)

        # Show the graph
        self.wait()