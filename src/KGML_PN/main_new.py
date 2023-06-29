import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, QLabel, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from KGML_PN.pathway import Pathway
from KGML_PN.ui import update_plot

# Widget for displaying the network plot
class NetworkPlotWidget(QWidget):
    def __init__(self):
        super(NetworkPlotWidget, self).__init__()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def update_plot(self, pw: Pathway, G: bool = False):
        self.ax.clear()
        update_plot(self.ax, pw, G)
        self.canvas.draw()

# Main application window
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create horizontal layout for the central widget
        layout = QHBoxLayout(central_widget)

        # Create widget for buttons
        buttons_widget = QWidget()
        buttons_layout = QGridLayout(buttons_widget)

        # Create buttons and add them to the layout
        frame_button = QPushButton("Next Frame")
        show_g_button = QPushButton("Show Groups")
        rm_g_button = QPushButton("Remove Groups")
        knockout_button = QPushButton("Set Knockouts")
        buttons = [frame_button, knockout_button, show_g_button, rm_g_button]

        # Set button font and size
        button_font = QFont("Times", 10, QFont.Bold)
        for i, button in enumerate(buttons):
            button.setFont(button_font)
            button.setFixedSize(175, 100)
            buttons_layout.addWidget(button, i // 2, i % 2)

        # Set button layout properties
        buttons_layout.setSpacing(20)
        buttons_layout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

        # Create widget for the plotting area
        plotting_widget = NetworkPlotWidget()

        # Add widgets to the horizontal layout
        layout.addWidget(plotting_widget)
        layout.addWidget(buttons_widget)
        layout.setStretch(0, 4)
        layout.setStretch(1, 1)

        # Set window properties
        self.setWindowTitle("Petri Net Application")
        # maximize the window
        self.showMaximized()


        # Connect button signals to slots
        frame_button.clicked.connect(self.next_frame)
        show_g_button.clicked.connect(self.show_groups)
        rm_g_button.clicked.connect(self.remove_groups)
        knockout_button.clicked.connect(self.set_knockouts)

        # Example usage to update the plot
        pw = Pathway("pathway.xml")
        plotting_widget.update_plot(pw, G=False)

        # Store references to widgets and variables
        self.plotting_widget = plotting_widget
        self.pw = pw
        self.G = False

        # Set the initial markings
        initial_markings = {60: 10, 58: 3, 64: 7, 57: 2} # id : count tokens
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
    sys.exit(app.exec_())
