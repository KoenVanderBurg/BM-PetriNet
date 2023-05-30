#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from xml.etree import ElementTree
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arrow
from matplotlib.widgets import Button 
import random


def main() -> None:
    """ Entry point. """
    filename = 'pathway.xml'
    global PW, AX
    PW = Pathway(filename)

    initial_marking = {
        60: 10,  # TLR1
        58: 3,   # TLR3
        64: 7,   # TLR4
        57: 2    # TLR5
    }

    PW.set_initial_marking(initial_marking)

    _, AX = plt.subplots()

    next_frame_button = Button(plt.axes([0.8, 0.02, 0.1, 0.05]), 'Next Frame', color='lightgray', hovercolor='skyblue')
    next_frame_button.on_clicked(next_frame)

    make_time_steps_button = Button(plt.axes([0.6, 0.02, 0.18, 0.05]), 'Make Time-Steps', color='lightgray', hovercolor='skyblue')
    make_time_steps_button.on_clicked(make_time_steps)

    update_plot()
    plt.show()

    return


class Node:
    def __init__(self, id: int, kegg_handle: str, type: str, name: str, graph_props: dict) -> None:
        """ Instantiates a Node object.

        ## Args
        - `int` id: unique identifier of the node
            (xml source: entry > id)
        - `str` kegg_handle: non-unique kegg identifier of the node
            (xml source: entry > name)
        - `str` type: type of the node
            (xml source: entry > type)
        - `str` name: name of the node
            (xml source: entry > graphics > name)
        - `dict` graph_props: dictionary containing the graphical properties of the node
            (xml source: entry > graphics > x, y, width, height)
        """
        self.id = id
        self.kegg_handle = kegg_handle
        self.type = type
        self.name = name
        self.graph_props = graph_props

        self.tokens = 0
        self.outgoing: set[int] = set()
        self.incoming: set[int] = set()
        return

    def update_tokens(self, n: int) -> None:
        """ Updates the number of tokens in the node. """
        assert self.tokens + n >= 0, \
            f'Node {self.id} has {self.tokens} tokens and cannot be updated by {n} tokens.'
        self.tokens += n
        return

    def __str__(self):
        return f'Id: {self.id} Node: {self.name} (Tokens: {self.tokens}, Gene: {self.name}, In: {self.incoming}, Out: {self.outgoing})'

    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other: 'Node'):
        return self.id == other.id
    
    def __ne__(self, other: 'Node'):
        return not self.__eq__(other)
    
    def __repr__(self) -> str:
        return f'Node({self.id}, {self.kegg_handle}, {self.type}, {self.name}, {self.gp})'

class Transition:
    def __init__(self, from_id: int, to_id: int, type: str) -> None:
        """ Instantiates a Transition object.

        ## Args
        - `int` from_id: id of the node the transition starts from
            (xml source: relation > entry1)
        - `int` to_id: id of the node the transition ends at
            (xml source: relation > entry2)
        - `str` type: type of the transition
            (xml source: relation > subtype > name)
        """
        self.from_id = from_id
        self.to_id = to_id
        self.type = type

    def __str__(self): 
        return f'Transition: {self.from_id} -> {self.to_id} Type: {self.type}'

class Pathway:

    def __init__(self, filename: str) -> None:
        """ Initialize the Pathway object from an KGML file. """
        
        assert os.path.exists(filename), \
            f'File {filename} does not exist in folder {os.getcwd()}'

        root = ElementTree.parse(filename).getroot()
        self.name = root.get('name'),
        self.org = root.get('org'),
        self.number = root.get('number'),
        self.title = root.get('title'),
        self.length = len(root)
        self.nodes = {}
        self.transitions = set()

        self.nodes = self.extract_nodes(root)
        self.transitions = self.extract_transitions(root)
        self.update_node_connections()

        self.buffer_template = {node_id: 0 for node_id in self.nodes.keys()}
        self.steps_taken = 0
        return

    def set_initial_marking(self, marking: dict[int, int]) -> None:
        """ Adds tokens to some nodes in the pathway. """
        for node_id, num_tokens in marking.items():
            self.nodes[node_id].update_tokens(num_tokens)
        return

    @staticmethod
    def extract_nodes(root: ElementTree.Element) -> dict[int, Node]:
        """ Parses the root of the KGML file and extracts all nodes. """
        nodes = {}
        for entry in root.iter('entry'):
            # TODO: other types of entries exist, but are not used for now
            if entry.get('type') != 'gene': continue
            graphics = entry.find('graphics')
            node = Node(
                id = int(entry.get('id')),
                kegg_handle = entry.get('name'),
                type = entry.get('type'),
                name = graphics.get('name', '').split(', ')[0],
                graph_props = dict(
                    x = float(graphics.get('x')) * 1.5,
                    y = float(graphics.get('y')) * 1.5,
                    w = float(graphics.get('width')) * 1.75,
                    h = float(graphics.get('height')) * 1.25,
                )
            )
            nodes.update({node.id: node})
        return nodes

    @staticmethod
    def extract_transitions(root: ElementTree.Element) -> set[Transition]:
        """ Parses the root of the KGML file and extracts all transitions. """
        transitions = set()
        for relation in root.iter('relation'):
            from_id = int(relation.get('entry1'))
            to_id = int(relation.get('entry2'))
            # non-valid transitions link to a node with name "undefined"
            # in this case, their IDs happen to be > 190
            # TODO: make this work on other KGML files as well
            if from_id > 190 or to_id > 190:
                continue
            # initialize transition object
            transition = Transition(
                from_id = from_id,
                to_id = to_id,
                type = subtype.get('name') if (subtype:=relation.find('subtype')) is not None else 'undefined'
            )
            # store transition object
            transitions.add(transition)
        return transitions

    def update_node_connections(self) -> None:
        """ Updates the incoming and outgoing connections of all nodes. """
        for transition in self.transitions:
            self.nodes[transition.from_id].outgoing.add(transition.to_id)
            self.nodes[transition.to_id].incoming.add(transition.from_id)
        return

    @property
    def active_nodes(self) -> set[int]:
        """ Returns the ids of all nodes that have at least one token. """
        return {node.id for node in self.nodes.values() if node.tokens > 0}

    def step(self, verbose: bool = False) -> None:
        """ Fires all possible transition. """

        if verbose: print('-' * 80); self.print_state()

        buffer = self.buffer_template.copy()

        for node_id in self.active_nodes:
            node = self.nodes[node_id]
            if not node.outgoing: continue
            num_next_nodes = len(node.outgoing)
            baseline = node.tokens // num_next_nodes
            remainder = node.tokens % num_next_nodes

            # distribute the baseline tokens
            for next_node_id in node.outgoing:
                buffer[next_node_id] += baseline
            # then we randomly distribute the remainder
            for _ in range(remainder):
                next_node_id = random.choice(list(node.outgoing))
                buffer[next_node_id] += 1
            # finally, we remove all tokens from the current node
            buffer[node_id] -= node.tokens

        # execute the instructions in the buffer
        for node_id, num_tokens in buffer.items():
            if num_tokens: self.nodes[node_id].update_tokens(num_tokens)

        if verbose: self.print_state()

        self.steps_taken += 1
        return

    def print_state(self) -> None:
        """ Prints the current state of the pathway. """
        print(', '.join([f'{self.nodes[nid].name} ({self.nodes[nid].tokens})' for nid in self.active_nodes]))
        return

def update_plot() -> None:
    """ Updates the plot with the current token distribution. """
    
    AX.clear()

    color_mappings = {
        'expression': 'blue',
        'activation': 'green',
        'phosphorylation': 'red',
        'binding/association': 'orange',
        'inhibition': 'purple',
        'undefined': 'black',
    }

    for node in PW.nodes.values():
        x, y, w, h = node.graph_props.values()

        edgecolor = 'red' if node.tokens else 'black'
        AX.add_patch(Rectangle((x, y), w, h, facecolor='lightblue', edgecolor=edgecolor))
        AX.text(x + 0.4 * w, y + 0.5 * h, node.name, ha='center', va='center', fontsize=6)
        if node.tokens:
            AX.text(x + 0.7 * w, y + 5, f'{node.tokens}',  fontsize=7, color='black')

    for transition in PW.transitions:
        from_node = PW.nodes[transition.from_id]
        to_node = PW.nodes[transition.to_id]
        from_x, from_y, from_w, from_h = from_node.graph_props.values()
        to_x, to_y, to_w, to_h = to_node.graph_props.values()
        from_x += from_w
        from_y += from_h / 2
        to_y += to_h / 2
        color = color_mappings[transition.type]
        AX.add_patch(Arrow(from_x, from_y, to_x - from_x, to_y - from_y, width=0.5, color=color))

    legend_elements = [
        Arrow(0, 0, 0, 0, width=0.5, color=color, label=relationship_type)
        for relationship_type, color in color_mappings.items()
    ]
    AX.legend(handles=legend_elements, loc='upper left', fontsize=7)

    AX.set_aspect('equal')
    AX.set_xlim(0, 1800)
    AX.set_ylim(0, 1200)
    AX.set_title('Petri Net Visualization')

    return

def next_frame(event: any) -> None:
    PW.step()
    update_plot()
    plt.draw()
    return

def make_time_steps(event: any) -> None:
    for _ in range(5):
        PW.step()
        update_plot()
        plt.pause(5)
        plt.draw()
    return


if __name__ == '__main__':
    main()
