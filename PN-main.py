#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib.widgets import Button 
import random


def main() -> None:
    """ Entry point. """
    filename = 'pathway.xml'
    global PW, AX, FI
    PW = Pathway(filename)

    initial_marking = {
        60: 10,  # TLR1
        58: 3,   # TLR3
        64: 7,   # TLR4
        57: 2    # TLR5
    }

    PW.set_initial_marking(initial_marking)

    _, AX = plt.subplots()
    FI = 0

    # Create the next frame button to display each frame of the pathway.
    next_frame_button_ax = plt.axes([0.8, 0.02, 0.1, 0.05])
    next_frame_button = Button(next_frame_button_ax, 'Next Frame', color='lightgray', hovercolor='skyblue')
    next_frame_button.on_clicked(next_frame)

    # Create the make time-steps button to run 5 time-steps with a 5-second interval.
    make_time_steps_button_ax = plt.axes([0.6, 0.02, 0.18, 0.05])
    make_time_steps_button = Button(make_time_steps_button_ax, 'Make Time-Steps', color='lightgray', hovercolor='skyblue')
    make_time_steps_button.on_clicked(make_time_steps)


    # Create the plot for the pathway.
    update_plot()
    plt.show()

    # animation = FuncAnimation(fig, update_plot, fargs=(node_pairs,), frames=100, interval=200, blit = False)
    ## Get the starting nodes and their transition pairs (TLR) specific. 
    # starting_nodes = get_starting_nodes(pathway)
    # transition_pairs = get_transition_pairs(starting_nodes)    

class Pathway:
    def __init__(self, filename: str) -> None:
        """ Initialize the Pathway object from an KGML file. """
        
        assert os.path.exists(filename), \
            f'File {filename} does not exist in folder {os.getcwd()}'

        self.root = ET.parse(filename).getroot()
        self.name = self.root.get('name'),
        self.org = self.root.get('org'),
        self.number = self.root.get('number'),
        self.title = self.root.get('title'),
        self.length = len(self.root)
        self.nodes: list[Node] = []
        self.transitions: list[Transition] = []
        self.groups: list[Group] = []

        self.__add_nodes()
        self.__add_transitions()
        self.__add_groups()
        self.__create_node_pairs()
        return

    def __add_nodes(self) -> None:
        """ Add all the nodes in the pathway. """
        for entry in self.root.iter('entry'):
            # TODO: other types of entries exist, but are not used for now
            if entry.get('type') != 'gene':
                continue
            # initialize node object
            node = Node(
                node_type = entry.get('type'),
                name = entry.get('name'),
                node_id = int(entry.get('id')),
            )
            # parse graphics element
            graphics = entry.find('graphics')
            if graphics is None:
                print(f'No graphics found for node {node.name}')
                continue
            graphics_name: str = graphics.get('name', '')
            node.set_gene_name(graphics_name.split(', ')[0])
            node.set_graphics(
                x = float(graphics.get('x')) * 1.5,
                y = float(graphics.get('y')) * 1.5,
                width = float(graphics.get('width')) * 1.75,
                height = float(graphics.get('height')) * 1.25,
            )
            # store node in list
            self.nodes.append(node)
        return

    def __add_transitions(self) -> None:
        """ Add all the transitions in the pathway. """
        for transition in self.root.iter('relation'):
            sender = int(transition.get('entry1'))
            receiver = int(transition.get('entry2'))
            # non-valid transitions link to a node with name "undefined"
            # in this case, their IDs happen to be > 190
            # TODO: make this work on other KGML files as well
            if sender > 190 or receiver > 190:
                continue
            # very inefficient way to find the corresponding nodes
            for node in self.nodes:
                if node.id == sender:
                    node.next_nodes.append(receiver)
                if node.id == receiver:
                    node.prev_nodes.append(sender)
            # initialize transition object
            transition_object = Transition(
                entry1 = sender,
                entry2 = receiver,
                type = transition.get('subtype'),
            )
            # store transition in list
            self.transitions.append(transition_object)
        return
    
    def __add_groups(self) -> None:
        """ Add all the groups in the pathway. """
        for entry in self.root.iter('entry'):
            if entry.get('type') == 'group':
                group_object = Group(group_name=entry.get('name'))
                self.groups.append(group_object)
        return

    def transfer_tokens(self) -> None:
        transfer_info = []

        for node in self.nodes:
            # Check if the node has more than one next node and if it is not an inhibition transition
            if len(node.next_nodes) > 1 and not any(transition.type == 'inhibition' for transition in self.transitions if transition.entry1 == node.id):
                num_next_nodes = len(node.next_nodes)
                transferred_tokens = node.tokens

                if node.consume_token(transferred_tokens):
                    # Calculate the number of tokens to transfer to each next node and the remaining tokens to transfer to the last next node.
                    tokens_to_transfer = transferred_tokens // num_next_nodes
                    remaining_tokens = transferred_tokens % num_next_nodes

                    # Add the next nodes and the number of tokens to transfer to the transfer_info list.
                    for next_node_id in node.next_nodes[:-1]:
                        next_node = next((n for n in self.nodes if n.id == next_node_id), None)
                        if next_node is not None:
                            transfer_info.append((node, next_node, tokens_to_transfer))
                    
                    # Add the last next node and the number of tokens to transfer to the transfer_info list.
                    last_next_node_id = node.next_nodes[-1]
                    last_next_node = next((n for n in self.nodes if n.id == last_next_node_id), None)
                    if last_next_node is not None:
                        transfer_info.append((node, last_next_node, tokens_to_transfer + remaining_tokens))
           
            elif len(node.next_nodes) == 1:
                next_node_id = node.next_nodes[0]
                next_node = next((n for n in self.nodes if n.id == next_node_id), None)
                if next_node is not None:
                    relationship_type = None
                    for transition in self.transitions:
                        if transition.entry1 == node.id and transition.entry2 == next_node.id:
                            relationship_type = transition.type
                            break

                    if relationship_type in ['activation', 'expression', 'binding/association']:
                        transferred_tokens = node.tokens
                        if node.consume_token(transferred_tokens):
                            transfer_info.append((node, next_node, transferred_tokens))

        # for node, nnode, ttokens in transfer_info:
        #     print(f"{node.gene_name} ({node.id}) -> {nnode.gene_name} ({nnode.id}) ({ttokens})")

        # Shuffle the transfer_info list to randomize the firing order
        random.shuffle(transfer_info)

        print("New token distribution step: ")
        print("---------------------------------------------------------")

        # Perform the token transfers
        for node, next_node, transferred_tokens in transfer_info:
            next_node.add_token(transferred_tokens)
            if transferred_tokens > 0:
                # Print the token transfer information
                print(f" ({transferred_tokens}) tokens {node.gene_name} ({node.id}) -> {next_node.gene_name} ({next_node.id}), {next_node.gene_name} tokens: {next_node.tokens}, next nodes: {next_node.next_nodes}")

    def set_initial_marking(self, data: dict) -> None:
        """ Adds tokens to some nodes in the pathway. """
        for node in self.nodes:
            if node.id in data:
                node.add_token(data[node.id])
        return

    def __create_node_pairs(self) -> None:
        """ Create pairs of nodes that are connected. """
        pairs: dict = {}
        for node in self.nodes:
            current_id = node.id
            for prev_id in node.prev_nodes:
                # check if prev node exists in node list
                if prev_id in [n.id for n in self.nodes]:
                    pairs[(prev_id, current_id)] = True

            for next_id in node.next_nodes:
                # check if next node exists in node list
                if next_id in [n.id for n in self.nodes]:
                    # TODO: check if the group filter is necessary
                    pairs[(current_id, next_id)] = True
        self.node_pairs = pairs
        return


class Node:
    def __init__(self, node_type, name, node_id):
        self.type = node_type
        self.name = name
        self.gene_name = None
        self.id = node_id
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.tokens = 0
        self.next_nodes = []
        self.prev_nodes = []
    
    def set_gene_name(self, gene_name):
        self.gene_name = gene_name

    def set_graphics(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def add_token(self, count):
        self.tokens += count

    def consume_token(self, count):
        if self.tokens >= count:
            self.tokens -= count
            return True
        return False
    
    def __str__(self):
        return f"Id: {self.id} Node: {self.name} (Tokens: {self.tokens}, Gene: {self.gene_name}, prev: {self.prev_nodes}, next: {self.next_nodes})"

class Transition:
    def __init__(self, entry1, entry2, type):
        self.entry1 = entry1
        self.entry2 = entry2
        self.type = type

    def __str__(self): 
        return f"Transition: {self.entry1} -> {self.entry2} Type: {self.type}"

class Group:
    def __init__(self, group_name):
        self.name = group_name


def update_plot() -> None:
    """ Updates the plot with the current token distribution. """
    
    AX.clear()

    if FI != 0:
        PW.transfer_tokens()

    color_mappings = {
        'expression': 'blue',
        'activation': 'green',
        'phosphorylation': 'red',
        'binding/association': 'orange',
        'inhibition': 'purple'
    }

    for node in PW.nodes:
        if node.x is not None and node.y is not None and node.width is not None and node.height is not None:
            x = int(node.x)
            y = int(node.y)
            width = int(node.width)
            height = int(node.height)

            rect = plt.Rectangle((x, y), width, height, facecolor='lightblue', edgecolor='black')
            AX.add_patch(rect)
            AX.text(x + 0.4 * width, y + 0.5 * height, node.gene_name, ha='center', va='center', fontsize=6)
            if node.tokens > 0:
                AX.text(x + 0.7 * width, y + 5, f'{node.tokens}',  fontsize=7, color='red')
            else: 
                AX.text(x + 0.7 * width, y + 5, f'{node.tokens}',  fontsize=7, color='black')
            
            # add the frame counter to the plot area
            AX.text(0.5, 0.95, f'Frame: {FI}', transform=AX.transAxes, fontsize=10, verticalalignment='top', horizontalalignment='center')

            for pair in PW.node_pairs.keys():
                print(pair)
                if pair[0] == node.id:
                    start_x = x + 0.5 * width
                    start_y = y + 0.5 * height
                    for other_node in PW.nodes:
                        if other_node.id == pair[1]:
                            end_x = int(other_node.x) + 0.5 * int(other_node.width)
                            end_y = int(other_node.y) + 0.5 * int(other_node.height)
                            relationship_type = None
                            for transition in PW.transitions:
                                if transition.entry1 == pair[0] and transition.entry2 == pair[1]:
                                    relationship_type = transition.type
                                    break
                            print(relationship_type)
                            color = color_mappings.get(relationship_type, 'black')
                            AX.plot([start_x + 0.5 * width, end_x - 0.5 * width], [start_y, end_y], color=color)
                            AX.plot(start_x + 0.55 * width, start_y, 'go', markersize=5)
                            AX.plot(end_x - 0.55 * width, end_y, 'ro', markersize=5)

    legend_elements = [
        plt.Line2D([0], [0], color=color, lw=1, label=relationship_type)
        for relationship_type, color in color_mappings.items()
    ]
    AX.legend(handles=legend_elements, loc='upper left', fontsize=7)

    AX.set_aspect('equal')
    AX.set_xlim(0, 1800)
    AX.set_ylim(0, 1200)

    AX.set_title('Petri Net Visualization')
    plt.draw()
    return

def next_frame(event: any) -> None:
    global FI
    FI += 1
    if FI >= 100:
        FI = 0
    update_plot()


def make_time_steps(event):
    global FI
    for _ in range(5):
        FI += 1
        if FI >= 100:
            FI = 0
        update_plot()
        plt.pause(3)  # Pause for 5 seconds between each time-step
        plt.draw()


if __name__ == '__main__':
    main()
