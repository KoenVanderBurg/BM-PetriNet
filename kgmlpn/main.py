#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from kgmlpn.pathway import Pathway
from kgmlpn.ui import update_plot

import matplotlib.pyplot as plt
from matplotlib.widgets import Button 


def main() -> None:
    """ Entry point. """
    
    parser = argparse.ArgumentParser(description='Visualize a KEGG pathway as a Petri Net.')
    parser.add_argument('filename', type=str, help='Path to the KEGG pathway xml file.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print additional information.')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 0.0.1')
    args = parser.parse_args()

    global PW, AX, V, G
    PW = Pathway(args.filename)
    _, AX = plt.subplots()
    V = args.verbose
    G = False

    initial_marking = {
        60: 10,  # TLR1
        58: 3,   # TLR3
        64: 7,   # TLR4
        57: 2    # TLR5
    }

    PW.set_initial_marking(initial_marking)

    # Add buttons to the plot
    next_frame_button = Button(plt.axes([0.8, 0.02, 0.10, 0.05]), 'Next Frame', color='lightgray', hovercolor='skyblue')
    next_frame_button.on_clicked(step)

    make_grouping_button = Button(plt.axes([0.3, 0.02, 0.10, 0.05]), 'Show groups', color='lightgray', hovercolor='skyblue')
    make_grouping_button.on_clicked(plot_grouping)

    make_rm_grouping_button = Button(plt.axes([0.2, 0.02, 0.10, 0.05]), 'Remove groups', color='lightgray', hovercolor='skyblue')
    make_rm_grouping_button.on_clicked(remove_grouping)

    update_plot(AX, PW, G)
    plt.show()

    return

def step(event: any) -> None:
    PW.step(V)
    update_plot(AX, PW, G)
    plt.draw()
    return

def plot_grouping(event: any) -> None:
    global G 
    G = True
    update_plot (AX, PW, G)
    plt.draw()

def remove_grouping(event: any) -> None:
    global G
    G = False
    update_plot (AX, PW, G)
    plt.draw()

if __name__ == '__main__':
    main()
