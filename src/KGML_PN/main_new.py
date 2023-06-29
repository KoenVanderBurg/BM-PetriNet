import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from KGML_PN.pathway import Pathway
from KGML_PN.ui import update_plot
class NetworkPlotWidget(QWidget):
    def __init__(self):
        super(NetworkPlotWidget, self).__init__()

        # Create a Figure instance
        self.figure = Figure()

        # Create a FigureCanvas instance
        self.canvas = FigureCanvas(self.figure)

        # Create an axis
        self.ax = self.figure.add_subplot(111)

        # Set the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def update_plot(self, pw: Pathway, G: bool = False):
        self.ax.clear()
        update_plot(self.ax, pw, G)
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a horizontal layout for the central widget
        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        # Create a widget for the buttons
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_widget.setLayout(buttons_layout)

        # Create buttons and add them to the layout
        button1 = QPushButton("Next Frame")
        button2 = QPushButton("Show Groups")
        button3 = QPushButton("Remove Groups")
        button4 = QPushButton("Set Knockouts")
        buttons_layout.addWidget(button1)
        buttons_layout.addWidget(button2)
        buttons_layout.addWidget(button3)
        buttons_layout.addWidget(button4)

        # Create a widget for the plotting area
        plotting_widget = NetworkPlotWidget()

        # Add widgets to the horizontal layout
        layout.addWidget(buttons_widget)
        layout.addWidget(plotting_widget)
        layout.setStretch(0, 1)
        layout.setStretch(1, 4)

        # Set the window properties
        self.setWindowTitle("Petri Net Application")
        self.setGeometry(100, 100, 800, 600)

        # Connect button signals to slots
        button1.clicked.connect(self.next_frame)
        button2.clicked.connect(self.show_groups)
        button3.clicked.connect(self.remove_groups)
        button4.clicked.connect(self.set_knockouts)

        # Example usage to update the plot
        pw = Pathway("pathway.xml")  # Replace with your Pathway instance
        plotting_widget.update_plot(pw, G=False)

        self.plotting_widget = plotting_widget
        self.pw = pw
        self.G = False

        # Set the initial markings
        initial_markings = {
            60: 10,  # TLR1
            58: 3,   # TLR3
            64: 7,   # TLR4
            57: 2    # TLR5
        }
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
        knockouts = {
            'RAC1': 38,
            'TICAM2': 65
        }
        self.pw.set_knockouts(knockouts)
        self.plotting_widget.update_plot(self.pw, self.G)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
