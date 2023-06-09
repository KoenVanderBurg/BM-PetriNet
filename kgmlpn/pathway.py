#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
from xml.etree import ElementTree

from kgmlpn.node import Node
from kgmlpn.transition import Transition
from kgmlpn.groups import Group


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
        self.groups = {}

        self.nodes = self.extract_nodes(root)
        self.transitions = self.extract_transitions(root)
        self.update_node_connections()
        self.groups = self.extract_groups(root)
        
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
            #TODO: other types of entries exist, but are not used for now  NOTE:(yes groups, but they are not nodes, they are collections of nodes) -@koenv at 31/05/2023, 09:37:36
            if entry.get('type') in ['map', 'group']: continue
            graphics = entry.find('graphics')
            node = Node(
                id = int(entry.get('id')),
                kegg_id = entry.get('name'),
                type = entry.get('type'),
                name = graphics.get('name', '').split(', ')[0], #NOTE: this is a bit of a hack since it is not full name, but it works for now -@koenv at 31/05/2023, 09:37:36
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
    def extract_groups(root: ElementTree.Element) -> dict[int, Group]:
        """Parses the root of KGML file and extracts group nodes"""
        
        groups = {}
        for entry in root.iter('entry'):
            if entry.get('type') != 'group': continue
            graphics = entry.find('graphics')
            group_nodes = {}
            for component in entry.find('component'):
                component_id = int(component.get('id'))
                group_nodes.update({component_id: component_id})

            group = Group(
                id = int(entry.get('id')),
                name = entry.get('name'),
                group_nodes = group_nodes,
                graphics = dict(
                    x = float(graphics.get('x')) * 1.5,
                    y = float(graphics.get('y')) * 1.5,
                    w = float(graphics.get('width')) * 1.75,
                    h = float(graphics.get('height')) * 1.25,
                )
            )
            groups.update({group.id: group})

        return groups

    @staticmethod
    def extract_transitions(root: ElementTree.Element) -> set[Transition]:
        """ Parses the root of the KGML file and extracts all transitions. """

        transitions = set()
        for relation in root.iter('relation'):
            from_id = int(relation.get('entry1'))
            to_id = int(relation.get('entry2'))
            # non-valid transitions link to a group with name "undefined" -> not sure about handling this. 
            # in this case, their IDs happen to be > 190  #HACK:  it works for now -@koenv at 31/05/2023, 09:37:36

            if from_id > 190 or to_id > 190:
                continue
            # initialize transition object
            transition = Transition(
                from_id = from_id,
                to_id = to_id,
                name = subtype.get('name') if (subtype:=relation.find('subtype')) is not None else 'undefined'
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
        """ The ids of all nodes that have at least one token. """

        return {node.id for node in self.nodes.values() if node.tokens > 0}

    def step(self, verbose: bool = False) -> None:
        """ Fires all possible transition. """

        if verbose: print('-' * 80); self.print_state()

        buffer = self.buffer_template.copy()

        for node_id in self.active_nodes:
            node = self.nodes[node_id]
            if not node.outgoing: continue

            # calculate the number of tokens to distribute (one version of token distribution). 
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
