#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Transition:
    """ A connection between two nodes/places. """

    def __init__(self, from_id: int, to_id: int, name: str) -> None:
        """
        ## Args
        - `int` from_id: id of the node the transition starts from.
            (xml source: relation -> entry1)
        - `int` to_id: id of the node the transition ends at.
            (xml source: relation -> entry2)
        - `str` name: name of the transition.
            (xml source: relation -> subtype -> name)
        """
        self.from_id = from_id
        self.to_id = to_id
        self.name = name        #NOTE: there is also a t-type, thus changed to prevent confusion further on. -@koenv at 31/05/2023, 09:37:36

    def __str__(self): 
        return f'Transition: {self.from_id} -> {self.to_id} Type: {self.type}'


"""
Transition types:
ECrel	enzyme-enzyme relation, indicating two enzymes catalyzing successive reaction steps
PPrel	protein-protein interaction, such as binding and modification
GErel	gene expression interaction, indicating relation of transcription factor and target gene product
PCrel	protein-compound interaction

"""