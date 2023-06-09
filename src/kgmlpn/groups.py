#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Group:
    """A node which represents a complex of 2 or more gene nodes """

    def __init__(self, id: int, name: str, graphics: dict, group_nodes : dict) -> None:
        """
        ## Args
        - `int` id: unique identifier of (node) group
            (xml source: entry -> id)
        - `str` name: name of the group
            (xml source: entry -> name)
         - `dict` graphics: dictionary containing the graphical properties of the node.
            (xml source: entry -> graphics -> x, y, width, height)
        - `dict`nodes: dictionary containing nodes of group.         
        
        """
        self.id = id
        self.name = name
        self.graphics = graphics
        self.group_nodes = group_nodes

        return


    def __str__(self):
        return f'Group id: {self.id},  (Nodes: {self.nodes})'