import sys
import fastf1 as ff1
import fastf1.plotting
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QComboBox, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class F1TireStrategyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1 Race Data Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.tyre_canvas = FigureCanvas(plt.figure())
        self.position_canvas = FigureCanvas(plt.figure())
        self.race_selector = QComboBox()
        self.load_button = QPushButton("Load Data")
        self.plot_tyre_button = QPushButton("Plot Tyre Strategy")
        self.plot_position_button = QPushButton("Plot Position Changes")

        self.race_selector.addItems([
            "Bahrain", "Saudi Arabia", "Australia", "Japan", "China", "Miami", "Imola", "Monaco", "Canada", "Spain", "Austria", "Great Britain", "Hungary", "Belgium", "Netherlands", "Italy", "Singapore", "USA", "Mexico", "Brazil", "Las Vegas", "Qatar", "Abu Dhabi"
        ])
        
        self.load_button.clicked.connect(self.load_data)
        self.plot_tyre_button.clicked.connect(self.plot_tyre_strategy)
        self.plot_position_button.clicked.connect(self.plot_position_changes)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select a Grand Prix:"))
        layout.addWidget(self.race_selector)
        layout.addWidget(self.load_button)
        layout.addWidget(self.plot_tyre_button)
        layout.addWidget(self.tyre_canvas)
        layout.addWidget(self.plot_position_button)
        layout.addWidget(self.position_canvas)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.session = None
        self.stints = None
        self.drivers = None
    
    def load_data(self):
        selected_race = self.race_selector.currentText()
        self.session = ff1.get_session(2024, selected_race, 'R')
        self.session.load()
        laps = self.session.laps
        self.drivers = [self.session.get_driver(driver)['Abbreviation'] for driver in self.session.drivers]
        self.stints = laps[["Driver", "Stint", "Compound", "LapNumber"]].groupby(["Driver", "Stint", "Compound"]).count().reset_index()
        self.stints = self.stints.rename(columns={"LapNumber": "StintLength"})
        print(f"Data Loaded Successfully for {selected_race}!")
    
    def plot_tyre_strategy(self):
        if self.session is None or self.stints is None:
            print("Please load data first!")
            return
        
        fig, ax = plt.subplots(figsize=(6, 10))
        
        for driver in self.drivers:
            driver_stints = self.stints.loc[self.stints["Driver"] == driver]
            previous_stint_end = 0  # Reset for each driver
            for _, row in driver_stints.iterrows():
                compound_color = fastf1.plotting.get_compound_color(row["Compound"], session=self.session)
                ax.barh(driver, width=row["StintLength"], left=previous_stint_end, color=compound_color, edgecolor="black")
                previous_stint_end += row["StintLength"]
        
        ax.set_title(f"2024 {self.race_selector.currentText()} Grand Prix Strategies")
        ax.set_xlabel("Lap Number")
        ax.invert_yaxis()
        self.tyre_canvas.figure.clf()
        self.tyre_canvas.figure = fig
        self.tyre_canvas.draw()
        print("Tyre Strategy Plot Generated Successfully!")
    
    def plot_position_changes(self):
        if self.session is None:
            print("Please load data first!")
            return
        
        fig, ax = plt.subplots(figsize=(8, 4.9))
        
        for drv in self.session.drivers:
            drv_laps = self.session.laps.pick_drivers(drv)
            abb = drv_laps['Driver'].iloc[0]
            style = fastf1.plotting.get_driver_style(identifier=abb, style=['color', 'linestyle'], session=self.session)
            ax.plot(drv_laps['LapNumber'], drv_laps['Position'], label=abb, **style)
        
        ax.set_ylim([20.5, 0.5])
        ax.set_yticks([1, 5, 10, 15, 20])
        ax.set_xlabel('Lap')
        ax.set_ylabel('Position')
        ax.legend(bbox_to_anchor=(1.0, 1.02))
        plt.tight_layout()
        
        self.position_canvas.figure.clf()
        self.position_canvas.figure = fig
        self.position_canvas.draw()
        print("Position Changes Plot Generated Successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = F1TireStrategyApp()
    mainWin.show()
    sys.exit(app.exec_())
