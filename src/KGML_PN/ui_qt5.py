import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from KGML_PN.pathway import Pathway
from matplotlib.patches import Rectangle, FancyArrow


class NetworkPlotWidget(QWidget):
    def __init__(self, parent=None):
        super(NetworkPlotWidget, self).__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

    def update_plot(self, pw: Pathway, G: bool = False) -> None:
        """ Updates the plot with the current token distribution. """
        self.ax.clear()
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
                self.ax.add_patch(Rectangle((x, y), w, h,
                                            facecolor='lightgrey',
                                            edgecolor=edgecolor))
                # Add knockout symbol.
                self.ax.plot([x, x + w], [y, y + h], color=edgecolor)
                self.ax.plot([x + w, x], [y, y + h], color=edgecolor)
            # Add normal nodes.
            if not node.knockout:
                edgecolor = 'hotpink' if node.tokens else 'black'
                linestyle = (0, (5, 1)) if node.tokens else 'solid'
                self.ax.add_patch(Rectangle((x, y), w, h,
                                            facecolor='lightblue',
                                            edgecolor=edgecolor,
                                            linewidth=1.5,
                                            linestyle=linestyle))
                self.ax.text(x + 0.4 * w, y + 0.5 * h,
                             node.name,
                             ha='center',
                             va='center',
                             fontsize=6)
                # Add token count.
                if node.tokens:
                    self.ax.text(x + 0.7 * w, y + 5,
                                 f'{node.tokens}',
                                 fontsize=7,
                                 color='black')
        # Draw groups around nodes.
        if G:
            for node in pw.groups.values():
                x, y, w, h = node.graphics.values()
                self.ax.add_patch(Rectangle(
                    (x - (0.1 * w), y - (0.45 * h)),
                    w * 1.25,
                    h * 1.35,
                    facecolor='none',
                    edgecolor='purple',
                    linewidth=1.5,
                    linestyle=(0, (5, 1))
                ))

                self.ax.text(x + 0.4 * w,
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
            self.ax.add_patch(FancyArrow(
                from_x, from_y, to_x - from_x, to_y - from_y,
                width=0.1,
                color=color,
                head_width=2,
                overhang=0.9,
                length_includes_head=True))
        legend_elements = [
            FancyArrow(0, 0, 0, 0,
                       width=0.5,
                       color=color,
                       label=relationship_type)
            for relationship_type, color in color_mappings.items()
        ]
        self.ax.legend(handles=legend_elements, loc='upper left', fontsize=7)
        self.ax.set_aspect('equal')
        self.ax.set_xlim(0, 1800)
        self.ax.set_ylim(100, 1200)
        self.ax.axis('off')
        self.ax.set_title('Petri Net Visualization')
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the central widget
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create a widget for the plotting area
        plotting_widget = NetworkPlotWidget()
        layout.addWidget(plotting_widget.canvas)

        # Create a horizontal layout for the buttons
        buttons_layout = QHBoxLayout()

        # Create buttons and add them to the layout
        button1 = QPushButton("Button 1")
        button2 = QPushButton("Button 2")
        button3 = QPushButton("Button 3")
        buttons_layout.addWidget(button1)
        buttons_layout.addWidget(button2)
        buttons_layout.addWidget(button3)

        # Add the buttons layout to the central layout
        layout.addLayout(buttons_layout)

        # Set the window properties
        self.setWindowTitle("Petri Net Application")
        self.setGeometry(100, 100, 800, 600)

        # Example usage to update the plot
        pw = Pathway("pathway.xml")  # Replace with your Pathway instance
        plotting_widget.update_plot(pw, G=False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
