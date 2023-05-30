#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kgmlpn.pathway import Pathway

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arrow
from matplotlib.widgets import Button

def update_plot(ax: plt.Axes, pw: Pathway) -> None:
    """ Updates the plot with the current token distribution. """

    ax.clear()

    color_mappings = {
        'expression': 'blue',
        'activation': 'green',
        'phosphorylation': 'red',
        'binding/association': 'orange',
        'inhibition': 'purple',
        'undefined': 'black',
    }

    for node in pw.nodes.values():
        x, y, w, h = node.graph_props.values()

        edgecolor = 'red' if node.tokens else 'black'
        ax.add_patch(Rectangle((x, y), w, h, facecolor='lightblue', edgecolor=edgecolor))
        ax.text(x + 0.4 * w, y + 0.5 * h, node.name, ha='center', va='center', fontsize=6)
        if node.tokens:
            ax.text(x + 0.7 * w, y + 5, f'{node.tokens}',  fontsize=7, color='black')

    for transition in pw.transitions:
        from_node = pw.nodes[transition.from_id]
        to_node = pw.nodes[transition.to_id]
        from_x, from_y, from_w, from_h = from_node.graph_props.values()
        to_x, to_y, to_w, to_h = to_node.graph_props.values()
        from_x += from_w
        from_y += from_h / 2
        to_y += to_h / 2
        color = color_mappings[transition.type]
        ax.add_patch(Arrow(from_x, from_y, to_x - from_x, to_y - from_y, width=0.5, color=color))

    legend_elements = [
        Arrow(0, 0, 0, 0, width=0.5, color=color, label=relationship_type)
        for relationship_type, color in color_mappings.items()
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=7)

    ax.set_aspect('equal')
    ax.set_xlim(0, 1800)
    ax.set_ylim(0, 1200)
    ax.set_title('Petri Net Visualization')

    return