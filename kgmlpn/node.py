#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Node:
    """ A node representation in a KEGG pathway, in a Petri Net this would be called a place. """

    def __init__(self, id: int, kegg_id: str, type: str, name: str, graph_props: dict) -> None:
        """
        ## Args
        - `int` id: unique identifier of the node.
            (xml source: entry -> id)
        - `str` kegg_id: unique kegg identifier of the node.
            (xml source: entry -> name)
        - `str` type: type of the node.
            (xml source: entry -> type)
        - `str` name: name of the node.
            (xml source: entry -> graphics -> name)
        - `dict` graph_props: dictionary containing the graphical properties of the node.
            (xml source: entry -> graphics -> x, y, width, height)
        """
        self.id = id
        self.kegg_id = kegg_id
        self.type = type
        self.name = name
        self.graph_props = graph_props

        self.tokens = 0
        self.outgoing: set[int] = set()
        self.incoming: set[int] = set()
        self.knockout = False
        return

    def update_tokens(self, n: int) -> None:
        """ Updates the number of tokens in the node. """

        assert self.tokens + n >= 0, \
            f'Node {self.id} has {self.tokens} tokens and cannot be updated by {n} tokens.'
        
        self.tokens += n
        return

    def __str__(self):
        return f'Id: {self.id} Node: {self.name} (Tokens: {self.tokens}, Gene: {self.name}, In: {self.incoming}, Out: {self.outgoing})'
