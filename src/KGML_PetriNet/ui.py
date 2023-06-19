#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Internal imports
from KGML_PetriNet.pathway import Pathway

# External imports
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow


def update_plot(ax: plt.Axes, pw: Pathway, G : bool = False) -> None:
    """ Updates the plot with the current token distribution. """

    ax.clear()

    color_mappings = {
        'expression': 'blue',
        'activation': 'green',
        'phosphorylation': 'red',
        'binding/association': 'orange',
        'inhibition': 'purple',
        'dephosphorylation': 'brown',
        'indirect effect': 'pink',
        'compound': 'yellow',
        'undefined': 'black',
    }

    # Draw nodes.
    for node in pw.nodes.values():
        x, y, w, h = node.graph_props.values()
        
        # Add knockout nodes.
        if node.knockout:
            edgecolor = 'red'
            ax.add_patch(Rectangle((x, y), w, h,
                         facecolor='lightgrey',
                         edgecolor=edgecolor))
            # Add knockout symbol.
            ax.plot([x, x+w], [y, y+h], color=edgecolor)
            ax.plot([x+w, x], [y, y+h], color=edgecolor)

        # Add normal nodes.
        if not node.knockout: 
            edgecolor = 'hotpink' if node.tokens else 'black'
            linestyle = (0, (5,1)) if node.tokens else 'solid'

            ax.add_patch(Rectangle((x, y), w, h,
                            facecolor='lightblue',
                            edgecolor=edgecolor,
                            linewidth = 1.5,
                            linestyle = linestyle))

            ax.text(x + 0.4 * w, y + 0.5 * h,
                    node.name,
                    ha='center',
                    va='center',
                    fontsize=6)

            # Add token count.
            if node.tokens:
                ax.text(x + 0.7 * w, y + 5,
                        f'{node.tokens}',
                        fontsize=7,
                        color='black')

    # Draw groups around nodes. . 
    if G:
        for node in pw.groups.values():
            x, y, w, h = node.graphics.values()
            ax.add_patch(Rectangle(
                        (x - (0.1 * w), y - (0.45 * h)),
                        w * 1.25, 
                        h * 1.35 , 
                        facecolor='none', 
                        edgecolor= 'purple',
                        linewidth= 1.5,
                        linestyle= (0, (5,1)) 
                        ))
                        
            ax.text(x + 0.4 * w, 
                    y + 1.1 * h, 
                    node.id,
                    ha='center',
                    va='center',
                    fontsize=7)


    for transition in pw.transitions:
        from_node = pw.nodes[transition.from_id]
        to_node = pw.nodes[transition.to_id]
        from_x, from_y, from_w, from_h = from_node.graph_props.values()
        to_x, to_y, to_w, to_h = to_node.graph_props.values()
        from_x += from_w
        from_y += from_h / 2
        to_y += to_h / 2
        color = color_mappings[transition.name]
        ax.add_patch(FancyArrow(
            from_x, from_y, to_x - from_x, to_y - from_y,
            width=0.1,
            color=color,
            head_width= 2,
            overhang= 0.9,
            length_includes_head=True))

    legend_elements = [
        FancyArrow(0, 0, 0, 0, 
                width=0.5,
                color=color,
                label=relationship_type)
        for relationship_type, color in color_mappings.items()
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=7)

    ax.set_aspect('equal')
    ax.set_xlim(0, 1800)
    ax.set_ylim(100, 1200)
    ax.axis('off')
    ax.set_title('Petri Net Visualization')

    return
