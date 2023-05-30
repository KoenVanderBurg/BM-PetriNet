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

    global PW, AX, V
    PW = Pathway(args.filename)
    _, AX = plt.subplots()
    V = args.verbose

    initial_marking = {
        60: 10,  # TLR1
        58: 3,   # TLR3
        64: 7,   # TLR4
        57: 2    # TLR5
    }

    PW.set_initial_marking(initial_marking)

    next_frame_button = Button(plt.axes([0.8, 0.02, 0.1, 0.05]), 'Next Frame', color='lightgray', hovercolor='skyblue')
    next_frame_button.on_clicked(step)

    make_time_steps_button = Button(plt.axes([0.6, 0.02, 0.18, 0.05]), 'Make Time-Steps', color='lightgray', hovercolor='skyblue')
    make_time_steps_button.on_clicked(five_steps)

    update_plot(AX, PW)
    plt.show()

    return

def step(event: any) -> None:
    PW.step(V)
    update_plot(AX, PW)
    plt.draw()
    return

def five_steps(event: any) -> None:
    for _ in range(5):
        PW.step(V)
        update_plot(AX, PW)
        plt.pause(5)
        plt.draw()
    return


if __name__ == '__main__':
    main()
