#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Transition:
    """ A connection between two nodes/places. """

    def __init__(self, from_id: int, to_id: int, type: str) -> None:
        """
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
