#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Internal imports
from KGML_PN.pathway import Pathway

# External imports
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow

def update_plot(ax: plt.Axes, pw: Pathway, set_groups : bool = False) -> None:
    """ 
    Updates the plot with the current token distribution.
    set_groups is used to view the different groupings of the network.   
    """

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
    # Draw the nodes found in the network. 
    for node in pw.nodes.values():
        x, y, w, h = node.graph_props.values()
        
        # Upon being set as knockout node, apply different visual.
        if node.knockout:
            edgecolor = 'red'
            ax.add_patch(Rectangle((x, y), w, h,
                         facecolor='lightgrey',
                         edgecolor=edgecolor))
            # Add knockout symbol.
            ax.plot([x, x+w], [y, y+h], color=edgecolor)
            ax.plot([x+w, x], [y, y+h], color=edgecolor)

        # Add normal (non-knockout) nodes.
        if not node.knockout: 
            edgecolor = 'hotpink' if node.tokens else 'black' # sets node edgecolor based on token amount. 
            linestyle = (0, (5,1)) if node.tokens else 'solid' # sets node edge linestyle based on token availiability. 
            ax.add_patch(Rectangle((x, y), w, h,
                            facecolor='lightblue',
                            edgecolor=edgecolor,
                            linewidth = 1.5,
                            linestyle = linestyle))
            
            # Sets the gene name in the node. 
            ax.text(x + 0.4 * w, y + 0.5 * h,
                    node.name,
                    ha='center',
                    va='center',
                    fontsize=6)
            
            # Add token count to the node.
            if node.tokens:
                ax.text(x + 0.7 * w, y + 5,
                        f'{node.tokens}',
                        fontsize=7,
                        color='black')
                
    # Draw groups around nodes.
    if set_groups:
        for group in pw.groups.values():
            x, y, w, h = group.graphics.values()
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
                    group.id,
                    ha='center',
                    va='center',
                    fontsize=7)
   
    # Plot the transitions between nodes.
    for transition in pw.transitions:

        # Get node objects involved with transition.
        from_node = pw.nodes[transition.from_id]
        to_node = pw.nodes[transition.to_id]
        
        # Retrieve graphical information from both nodes, and adjust for node width. 
        from_x, from_y, from_w, from_h = from_node.graph_props.values()
        to_x, to_y, to_w, to_h = to_node.graph_props.values()
        from_x += from_w
        from_y += from_h / 2
        to_y += to_h / 2

        # Add the color corresponding to the transition name. 
        color = color_mappings[transition.name]
        ax.add_patch(FancyArrow(
            from_x, from_y, to_x - from_x, to_y - from_y,
            width=0.1,
            color=color,
            head_width= 2,
            overhang= 0.9,
            length_includes_head=True))

    # Add the different transition types legenda.  
    legend_elements = [
        FancyArrow(0, 0, 0, 0, 
                width=0.5,
                color=color,
                label=relationship_type)
        for relationship_type, color in color_mappings.items()
    ]

    # Plotting the network inside the UI. 
    ax.legend(handles=legend_elements, loc='upper left', fontsize=7)
    ax.set_aspect('equal')
    ax.set_xlim(0, 1800)
    ax.set_ylim(100, 1200)
    ax.axis('off')
    ax.set_title('Petri Net Visualization')
    return