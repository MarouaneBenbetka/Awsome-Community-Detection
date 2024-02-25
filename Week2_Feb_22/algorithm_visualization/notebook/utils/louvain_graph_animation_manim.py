import networkx as nx
import pandas as pd
import numpy as np
from manim import *
# from louvain4 import Action, LouvainMachine
from utils.louvain4 import Action, LouvainMachine
from typing import Hashable, Tuple

"""

"""

class LouvainScene(Scene):
    # we need to store all the relevant data structures representing the state of our video
    def __init__(self, graph: nx.Graph, **kwargs):
        # this is the principal graph that we will be working on
        self.to_solve_graph = graph
        
        self.community_color_mapping = None
        self.node_vertex_mapping = None
        self.nx_community_manim_community_mapping = None
        self.louvain_machine = None
        self.mobject_store = dict()

        self.node_color_store = dict()

        self.status_text = None
        self.status_table = None
        super().__init__(**kwargs)

    def consider_louvain_machine(self, louvain_machine: LouvainMachine):
        self.louvain_machine = louvain_machine
        self.to_solve_graph = louvain_machine.graph_history[0]

    @staticmethod
    def constant_graph():
        g = Graph([1, 2, 3, 'a'], [(1, 2), (1, 3), (2, 3), (1, 'a')])

        return g

        
    @staticmethod
    def object_to_color(obj):
        # Compute hash value of the object
        hash_value = hash(obj)
        
        # Convert hash value to a 6-digit hexadecimal color code
        color_code = "#{:06x}".format(hash_value & 0xFFFFFF)
        
        return color_code

    def _color_manim_graph_nodes(self, vertices, colors, animate=False): 
        
        if type(colors) != list:
            colors = [colors] * len(vertices)
        
        # compute the runtime
        run_time = 1 if animate else 0

        for c, v in zip(colors, vertices):
            self.play(v.animate.set_fill_color(c), run_time=run_time)

    def generate_status_table(self, node: str, possible_actions: List[Tuple[str, float]]):
        # This method generates the status table with the specified title and columns

        # Create data for the table
        table_data = [["Destination Community", "Gain in Modularity"]]
        for destination_community, modularity_gain in possible_actions:
            table_data.append([str(destination_community), str(modularity_gain)])

        # Create the table
        self.status_table = Table(table_data)
        self.status_table_title = Text(f"Possible actions for {node} node")
        self.status_table.move_to([3.5, 0, 0])
        # Calculate the position of the table and title
        table_height = len(table_data) * 0.5  # Assuming each row height is 0.5
        table_width = max(len(row) for row in table_data) * 1.5  # Assuming each column width is 1.5
        title_height = 1  # Assuming title height is 1

        # Position the title and table in the right half of the scene
        self.status_table_title.to_edge(UP)
        self.status_table.next_to(self.status_table_title, DOWN)
        self.status_table_title.shift((self.camera.frame_width - table_width / 4) * RIGHT)
        # self.status_table.shift((self.camera.frame_width - table_width / 4) * RIGHT)
        self.status_table.scale(0.4)
        # Add the title and table to the scene
        self.add(self.status_table_title, self.status_table)


    def update_status_table(self, possible_actions: List[Tuple[str, float]]):
        # This method updates the content of the status table
        if self.status_table is not None:
            # Create updated data for the table
            table_data = [["Destination Community", "Gain in Modularity"]]
            for destination_community, modularity_gain in possible_actions:
                table_data.append([str(destination_community), str(modularity_gain)])

            # Update the table with new data
            self.status_table.data = table_data

    def highlight_selected_row(self, row_index: int):
        """
        Highlight the selected row in the table by changing its background color to yellow.
        
        Parameters:
            row_index (int): Index of the row to be highlighted.
        """
        if self.status_table is not None:
            # Check if the row_index is valid
            if 0 <= row_index < len(self.status_table.data):
                # Iterate through each cell in the selected row and change its background color to yellow
                for cell in self.status_table.data[row_index]:
                    cell.set_color(YELLOW)  # Assuming YELLOW is defined somewhere in your code



    def _build_manim_graph(self):
        COLORS = [RED, GREEN, BLUE, ORANGE, YELLOW, GREY_BROWN] # here is the def. of the colors
        
        nx_graph = self.to_solve_graph
        
        
        # extract nodes and vertices from the old graph
        vertices = nx_graph.nodes
        labels = {i: str(i) for i in vertices}
        color_mapping = {i: COLORS[j%len(COLORS)] for i, j in zip(vertices, range(len(vertices)))}
        
        # TODO: we might consider removing the inequality if necessary
        # the lbrary might have an automated handling for loop edges 
        edges = [(a, b) for a, b in nx_graph.edges if a != b]
        print('the edges')
        print(edges)
        graph = Graph(vertices, edges, layout='circular', layout_scale=3, labels=labels)
        
        # self.animate_color_nodes
        self.manim_graph = graph

        self.node_vertex_mapping = {i: j for i, j in zip(self.to_solve_graph.nodes, vertices)}
        self.nx_community_manim_community_mapping = {
            self.to_solve_graph._node[i]['community']: j for i, j in zip(self.to_solve_graph.nodes, self.manim_graph.vertices)
        }

        self.community_color_mapping = \
            {self.to_solve_graph._node[i]['community']: self.object_to_color(i) for i in self.to_solve_graph.nodes}
        self.node_color_store = color_mapping
        return self.manim_graph
    
    def _compute_left_side_center(self):
        # compute the center of the left side
        return [0, 0, 0]

    # # create the graph and show it on the screen
    # def animate_create_manim_graph(self, graph: nx.Graph):
    #     # take the networkx graph, convert it to manim graph
    #     # and return the manim graph

    #     # extract vertices and edges from the old graph
    #     self.add(self.manim_graph)
    #     # self.status_text.animate()
    #     self.play(Create(self.manim_graph))
        
    #     # TODO: we mgith consider removing this as well
    #     # self.wait()
    def animate_create_manim_graph(self, graph: nx.Graph):
        # Take the networkx graph, convert it to manim graph
        # and display the manim graph on the left half of the screen

        # Extract vertices and edges from the old graph
        self.add(self.manim_graph)

        # Calculate the position of the graph
        graph_width = 6  # Assuming a width of 6 units for the graph
        graph_height = 4  # Assuming a height of 4 units for the graph

        # Position the graph on the left half of the screen
        self.manim_graph.scale(0.6)

        # move to the center of the left side
        left_side_center = self._compute_left_side_center()
        self.manim_graph.move_to([-3, 0, 0])

        # Play the animation to create the graph
        self.play(Create(self.manim_graph))



    def _move_order_text_to_target_node(self, text, manim_node):
        HALF_UNIT = 0.5
        self.play(Create(text), subcaption_duration=0.1)
        text.generate_target()
        text.target.move_to(manim_node.get_center() + \
                             HALF_UNIT * self._compute_node_average_incoming_edge_direction(manim_node))
        self.play(MoveToTarget(text))

    def _compute_node_average_incoming_edge_direction(self, manim_node):
        
        sum_incoming_edge_direction = manim_node.get_center()
        count = 0
        for a, b in self.manim_graph.edges:
            na = self.manim_graph.vertices[a]
            nb = self.manim_graph.vertices[b]
            
            # na: is the first node of the graph
            # nb: is the second node of the graph
            if na == nb: # if the edge is recursive, do not take it into consideration 
                continue

            if manim_node == na: # 
                delta_direction = nb.get_center() - na.get_center()
                sum_incoming_edge_direction += delta_direction
                count += 1
                
            elif manim_node == nb: 
                delta_direction =na.get_center() - nb.get_center()
                sum_incoming_edge_direction += delta_direction
                count += 1
                
        MINUS_ONE = -1
        # if the degree of the node is not zero
        print(count)
        if count > 0:
            average_incoming_edge_direction = sum_incoming_edge_direction / count
            normalized_average_incoming_edge_direction = \
                MINUS_ONE * average_incoming_edge_direction /  np.linalg.norm(average_incoming_edge_direction)
            return normalized_average_incoming_edge_direction
        
        return RIGHT

    def _animate_manim_cluster_to_vertex(self, manim_cluster, target_vertex):
        animations = []
        for manim_vertex in manim_cluster:
            manim_vertex.generate_target()
            manim_vertex.target.move_to(target_vertex.get_center())
            animations.append(MoveToTarget(manim_vertex))
        
        return animations

    def _delete_nodes(self, nodes):
        vertices = self._get_manim_vertex_keys_from_nodes(nodes)

        for vertex in vertices:
            self.manim_graph._remove_vertex(vertex)
    
    def _add_edges(self, edges):
        aa, bb = zip(*edges)
        aa_manim = self._get_manim_vertex_keys_from_nodes(aa)
        bb_manim = self._get_manim_vertex_keys_from_nodes(bb)
        to_add_edges = list(zip(aa_manim, bb_manim))

        for edge in to_add_edges:
            self.manim_graph._add_edge(edge)

    def animate_reduce_nodes_to_nodes(self, clusters, nodes):
        clusters_nodes_flattened = []
        for cluster in clusters:
            for node in cluster:
                clusters_nodes_flattened.append(node)
        
        to_delete_nodes = [node for node in clusters_nodes_flattened if node not in nodes]

        manim_clusters = [self._get_manim_vertices_from_nodes(cluster) for cluster in clusters]
        manim_representative_nodes = self._get_manim_vertices_from_nodes(nodes)
        
        
        to_add_edges = []

            # get all the neighbors of the cluster nodes
        for cluster, rep in zip(clusters, nodes):
            for n in cluster:
                current_node_neighbors = nx.neighbors(self.to_solve_graph, n)
                for neighbor in current_node_neighbors:
                    to_add_edges.append((rep, neighbor))
        
        # we add the edges from the representative node
        # to the nodes connected with the deleted nodes
        
        

        # animate vertices to vertex
        animations = []
        for cluster, representative in zip(manim_clusters, manim_representative_nodes):
            if representative in cluster: 
                cluster.remove(representative)
                pass

            animations.append(self._animate_manim_cluster_to_vertex(cluster, representative))




        # we can play all the actions in a sequential manner
        # or we can do it in parallel
        flattened_animations = []
        for i in animations:
            for j in i:
                flattened_animations.append(j)
        if len(flattened_animations) > 0:
            self.play(*flattened_animations)
            self._delete_nodes(to_delete_nodes)
            self._add_edges(to_add_edges) 
               

    
    def _create_texts_for_ordered_nodes(self, ordered_nodes):
        nodes_text_dict = dict()

        for i, n in zip(range(len(ordered_nodes)), ordered_nodes):
            # create the text for displaying
            current_order_string = str(i + 1)
            current_text = Text(current_order_string, font_size=36, color=RED)
            nodes_text_dict[n] = current_text

        return nodes_text_dict
    # determine the order of considering the nodes and show that on the screen
    def animate_graph_nodes_order(self, ordered_nodes: List[Hashable]):

        
        node_text_dict = self._create_texts_for_ordered_nodes(ordered_nodes)
        
        # show the texts in the order given by the list
        for n in ordered_nodes:
            # show the text corresponding to the node n
            current_text = node_text_dict[n]
            current_manim_node = self.manim_graph.vertices[n]
            # move the text to the corresponding target node
            self._move_order_text_to_target_node(current_text, current_manim_node)

    def get_manim_graph_node_fill_color(self, node):
        manim_vertex = self.node_vertex_mapping[node]
        manim_vertex_fill_color = self.manim_graph.vertices[manim_vertex].get_fill_color()
        return manim_vertex_fill_color
        
    def get_manim_graph_node_label(self, node):
        manim_vertex = self.node_vertex_mapping[node]
        manim_vertex_fill_color = self.manim_graph.vertices[manim_vertex]
        return manim_vertex_fill_color
        

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
        
        # TODO: we might consider removing this comment as well
        # self.wait()

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
        
    def _highlight_manim_graph_nodes(self, nodes, highlight_colors=YELLOW):
        print('called highlighting nodes:', nodes)
        
        if not highlight_colors is list:
            highlight_colors = [highlight_colors] * len(nodes)
        print('passed at least one time from here')
        print(self.node_vertex_mapping)
        
        print('type(nodes)=', type(nodes[0]))
        print(type(list(self.node_vertex_mapping.keys())[0]))
        print('nodes', nodes)
        print('self.node_vertex_mapping', self.node_vertex_mapping)
        print('type(self.node_vertex_mapping)', type(self.node_vertex_mapping))
        print('self.manim_graph.vertices', self.manim_graph.vertices)

        # vertices = [self.manim_graph.vertices[self.node_vertex_mapping[node]] for node in nodes]
        vertices = self._get_manim_vertices_from_nodes(nodes)
        # vertices = [self.node_vertex_mapping[node] for node in nodes]
        
        print(vertices)
        

        for vertex in vertices:
            vertex.save_state()

        # self.manim_graph.vertices[node].set_fill(highlight_color)
        # highlight all the vertices
        self.play(
            *[FadeToColor(vertex, highlight_colors[i]) for vertex, i in zip(vertices, range(len(vertices)))],
            *[ScaleInPlace(vertex, 1.2) for vertex in vertices]
            )
        
        # self.play(*[FocusOn(vertex)])
        
        # recover the initial state of each of the vertices
        self.play(*[Restore(vertex) for vertex in vertices])
    
    def _get_manim_vertices_from_nodes(self, nodes):

        print('called with', nodes)
        print('called on', self.manim_graph.vertices)
        manim_vertex_keys = [self.node_vertex_mapping[node] for node in nodes]
        return [self.manim_graph.vertices[vertex] for vertex in manim_vertex_keys]

    def _get_manim_vertex_keys_from_nodes(self, nodes):
        manim_vertex_keys = [self.node_vertex_mapping[node] for node in nodes]
        return manim_vertex_keys
    def animate_associate_texts_to_vertices(self, nodes, text_strings, font_size=36):
        ONE_UNIT = 1
        manim_vertices = self._get_manim_vertices_from_nodes(nodes)
        manim_texts = [Text(t, font_size=font_size) for t in text_strings]
        for text, vertex in zip(manim_texts, manim_vertices):
            text.move_to(vertex.get_center() + 1.25 * self._compute_node_average_incoming_edge_direction(vertex))
        show_text_in_front_vertices_animations = [FadeIn(text) for text in manim_texts]
        self.play(*show_text_in_front_vertices_animations)


    def animate_highlight_community_nodes(self, communities):
        # Iterate through nodes and add the ones to highlight to the VGroup
        # from the nx graph, get the community nodes 
        # nodes in the old graph
        highlighted_community_nodes = [node for node in self.to_solve_graph.nodes if \
                            self.to_solve_graph._node[node]['community'] in communities]

        # the vertices to highlight 
        highlighted_community_manim_nodes = [self.node_vertex_mapping[node] for node in highlighted_community_nodes]

        # highlight the vertices and recover states
        self._highlight_manim_graph_nodes(highlighted_community_manim_nodes, highlight_colors=RED)
        
    def animate_highlight_nodes(self, nodes, highlight_colors=RED):
        highlighted_community_manim_nodes = [self.node_vertex_mapping[node] for node in nodes]
        self._highlight_manim_graph_nodes(highlighted_community_manim_nodes, highlight_colors)

    def animate_color_nodes(self, nodes, colors):

        # colored_manim_vertices = [self.node_vertex_mapping[node] for node in nodes]
        colored_manim_vertices = self._get_manim_vertices_from_nodes(nodes)
        self._color_manim_graph_nodes(colored_manim_vertices, colors=colors, animate=True)

    def set_color_nodes(self, nodes, colors):
        colored_manim_vertices = self._get_manim_vertices_from_nodes(nodes)
        colored_manim_vertex_keys = self._get_manim_vertex_keys_from_nodes(nodes)
        for key, color in zip(colored_manim_vertex_keys, colors):
            self.manim_graph.vertices[key].set_color(color)
            
            
            
        # self._color_manim_graph_nodes(colored_manim_vertices, colors=colors, animate=False)

    def animate_assign_nodes_to_communities(self, nodes_parition, communities):
        # nodes partition: is a list of lists
        # communities: the label representing the community, it could be an integer for example

        assert len(nodes_parition) == len(communities)
        community_colors = [self.community_color_mapping[community] for community in communities]
        animations = []
        
        for cluster, color in zip(nodes_parition, community_colors):
            cluster_vertices = self._get_manim_vertices_from_nodes(cluster)
            
            for vertex in cluster_vertices:
                vertex.set_fill(color)
            




    # merge the nodes into a single node
    def animate_merge_same_community_nodes(self, manim_graph, nodes_from, node_to: Mobject):

        # get the position of the destination node
        node_to_position = node_to.get_coord()

        # Animate the transition of the nodes to the merged node
        for node_key in nodes_from:
            node_obj = manim_graph.vertices[node_key]
            self.play(node_obj.animate.move_to(node_to_position), run_time=1)

        self.wait()

    def animate_repalce_graph(self, new_graph):
        # keep reference to the old graph and the new graph
        self.to_solve_graph = new_graph
        self.old_graph = self.manim_graph

        # animate the transformation
        self._build_manim_graph()

        self.remove(self.old_graph)
        self.manim_graph.scale(0.5)
        self.manim_graph.move_to([3.5, 0, 0])
        self.play(TransformFromCopy(self.old_graph, self.manim_graph))
        

    # highlight the edges whose one node at least is in community
    def animate_highlight_edges_concerning_communities(self, graph, nodes):
        pass
        # highlight the nodes in the community
    #

    # merge the edges into one edge
    def animate_merge_edges_to_one_edge(self):
        pass
    

    def update_status_text(self, new_text: str):
        # This method updates the status text displayed on the screen
        if "status_text" in self.mobject_store:
            status_text_obj = self.mobject_store["status_text"]
            status_text_obj.become(Text(new_text))

    def remove_status_table(self):
        # This method removes the status table from the scene
        if self.status_table is not None:
            self.remove(self.status_table)
            self.remove(self.status_table_title)  # Also remove the title if it exists
            self.status_table = None  # Reset the status table object

    def setup_status_text(self):
        # setup the text and put it in the mobject store
        self.status_text = Text('status text')
        self.status_text.to_edge(UP)
        self.mobject_store['status_text'] = self.status_text
        self.play(FadeIn(self.status_text))
    
    # just a setup function
    def setup(self):
        # consider generating the intermediate results necessary for visualization
        # self.status_text = Text("status text")
        # self.status_text.target.generate_target()
        
        # self.setup_status_text()
        self._build_manim_graph()
        self.animate_create_manim_graph(self.to_solve_graph)
        nodes = self.to_solve_graph.nodes
        node_colors = [self.node_color_store[node] for node in nodes]
        self.set_color_nodes(nodes, node_colors)

    def setup_node_colors(self):
        # change the color of the current nodes to the suitable color
        current_nodes = self.to_solve_graph.nodes
        current_colors = [self.node_color_store[node] for node in current_nodes]
        self.set_color_nodes(current_nodes, current_colors)
        pass


    def animate_assign_phase(self, phase_actions):
        # the actions_history is a list of phase_actions
        # each of phase_actions is a list of tuples
        # each tuple has a list of possible actions on node and the action that maximizes the gain
        # Here: 
        # the received actions is a list of tuples,
        # each tuple has a list of possible actions on a node and a max actions
        # actions contains all the actions related to all the nodes
        # TODO: this might change later
        for i, node in zip(range(len(phase_actions)), self.to_solve_graph.nodes):
            max_action: Action
            node_actions: List[Action]
            # print('the node is here')
            # print(node)
            

            # TODO: note here
            # print(phase_actions)
            node_actions, max_action = phase_actions[i]

            
            # ---> show the actions table
            possible_actions = [(a.destination_community, a.value) for a in node_actions]
            self.generate_status_table(str(node), possible_actions)

            candidates = []
            for action in node_actions: 
                candidates.append(action.destination_community)
            candidates = list(set(candidates))

            # HIGHLIGHT THE NODES CONNECTED TO THE CURRENT NODE
            self.play(
                FocusOn(*self._get_manim_vertices_from_nodes([node])),
                ScaleInPlace(*self._get_manim_vertices_from_nodes([node]), 1.3)
                )
            self.wait()
            self.animate_highlight_nodes(candidates, highlight_colors=BLUE)
            # self.wait()

            self.wait()
            # target node
            target_node = max_action.node
            
            self.animate_highlight_nodes([target_node], highlight_colors=BLUE)
            
            # TODO: consider adding something here to highlight the rows of the table
            # self.highlight_status_table_target_rows()
            self.wait()
            # get the color of the target node
            target_node_color = self.node_color_store[target_node]
            self.set_color_nodes([node], [target_node_color])

            self.remove_status_table()
        





    def animate_reduce_phase(self, new_graph):
        # get the new graph from the graph history and replace it directly
        self.animate_repalce_graph(new_graph=new_graph)
        
        

    # the entire visualization will be done here
    def construct(self):
        # 
        if self.louvain_machine is None:
            raise ValueError('self.louvain_machine is None. Consider setting it to a non None value')
        # we will see the history of the graphs
        # create the graph to visualize
        # self._build_manim_graph()
        
        # shoe the graph with animations
        # THE CODE BEFORE STARTS HERE
        # self.animate_create_manim_graph(self.to_solve_graph)
        
        # TODO: we might need to uncomment this
        # self.wait()

        # # show the order in which to consider the nodes
        # self.animate_graph_nodes_order(self.to_solve_graph.nodes)
        # self.animate_highlight_community_nodes([1, 2, 3])

        # self.animate_associate_texts_to_vertices([1, 2, 3], [f'hello {i}' for i in range(1, 4)])
        # self.animate_reduce_nodes_to_nodes([[1, 2]], [3])
        
        # self.animate_repalce_graph(self.to_solve_graph)

        # THE CODE ENDS HERE
        print(f'len(graph history): {len(self.louvain_machine.graph_history)}')
        print(f'len(actions history): {len(self.louvain_machine.action_history)}')
        for i in range(0, len(self.louvain_machine.graph_history)-1):
            current_new_graph = self.louvain_machine.graph_history[i+1]
            current_actions = self.louvain_machine.action_history[i]
            # current_actions contains all the possible actions in the first phase
            # of the current pass
            
            self.setup_node_colors()
            self.animate_assign_phase(current_actions)

            # TODO: we might consider uncommenting this
            # self.wait()
            self.animate_reduce_phase(current_new_graph)
        # pass