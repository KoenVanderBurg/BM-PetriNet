import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6 import QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from KGML_PN.pathway import Pathway
from KGML_PN.ui import update_plot


class NetworkPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def update_plot(self, pw: Pathway, G: bool = False):
        self.ax.clear()
        update_plot(self.ax, pw, G)
        self.canvas.draw()

        # Connect mouse press event to node selection
        self.canvas.mpl_connect('button_press_event', self.on_node_clicked)

    def on_node_clicked(self, event):
        if event.button == 1:  # Left mouse button
            if event.inaxes is not None:
                x, y = event.xdata, event.ydata
                node_info = self.ax.format_coord(x, y)
                print("Selected Node:", node_info)

                # TODO: instead of printing "selected node" use location to find gene.


class MainWindow(QMainWindow):
    """This class contains the code to create main UI in which the network and interactive buttons are defined. """

    def __init__(self):
        super().__init__()

        pathway = "pathway.xml"

        # Create the main widget.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Define the layout size.
        layout = QHBoxLayout(central_widget)

        buttons_widget = QWidget()
        buttons_layout = QGridLayout(buttons_widget)

        # Define various buttons in the UI.
        frame_button = QPushButton("Next Frame")
        show_g_button = QPushButton("Show Groups")
        rm_g_button = QPushButton("Remove Groups")
        knockout_button = QPushButton("Set Knockouts")
        buttons = [frame_button, show_g_button, rm_g_button, knockout_button]

        # Set the button
        button_font = QFont("Times New Roman", 10)
        for i, button in enumerate(buttons):
            button.setFont(button_font)
            button.setFixedSize(175, 100)
            buttons_layout.addWidget(button, i // 2, i % 2)
            button.setStyleSheet("background-color: #add8e6; border-radius: 10px; border: 2px solid #000000;")

        buttons_layout.setSpacing(20)
        buttons_layout.setRowStretch(2, 1)
        buttons_layout.setColumnStretch(1, 1)

        plotting_widget = NetworkPlotWidget()

        layout.addWidget(plotting_widget)
        layout.addWidget(buttons_widget)
        layout.setStretch(0, 4)
        layout.setStretch(1, 1)

        self.setWindowTitle(f"KGML-PN Simulation")
        self.showMaximized()

        frame_button.clicked.connect(self.next_frame)
        show_g_button.clicked.connect(self.show_groups)
        rm_g_button.clicked.connect(self.remove_groups)
        knockout_button.clicked.connect(self.set_knockouts)

        pw = Pathway(pathway)
        plotting_widget.update_plot(pw, G=False)

        self.plotting_widget = plotting_widget
        self.pw = pw
        self.G = False

        initial_markings = {60: 10, 58: 3, 64: 7, 57: 2}
        self.pw.set_initial_marking(initial_markings)
        self.plotting_widget.update_plot(self.pw, self.G)

    def next_frame(self):
        self.pw.step(verbose=True)
        self.plotting_widget.update_plot(self.pw, self.G)

    def show_groups(self):
        self.G = True
        self.plotting_widget.update_plot(self.pw, self.G)

    def remove_groups(self):
        self.G = False
        self.plotting_widget.update_plot(self.pw, self.G)

    def set_knockouts(self):
        knockouts = {'RAC1': 38, 'TICAM2': 65}
        self.pw.set_knockouts(knockouts)
        self.plotting_widget.update_plot(self.pw, self.G)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
