import tkinter as tk
from tkinter import ttk
import logging
import fastf1
import pandas as pd
from F1MongoDBHandler import F1MongoDBHandler  # Assuming this file is available
from F1DataFetcher import F1DataFetcher  # Assuming this file is available

# Set up logging
logging.basicConfig(level=logging.INFO)

class F1StatsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("F1 Stats Application")

        # Create instances of F1DataFetcher and F1MongoDBHandler
        self.db_handler = F1MongoDBHandler()

        # Frame to hold all the widgets
        self.frame = ttk.Frame(self.root)
        self.frame.grid(row=0, column=0, padx=10, pady=10)

        # Year selection dropdown
        self.year_label = ttk.Label(self.frame, text="Select Year:")
        self.year_label.grid(row=0, column=0, sticky='w', pady=5)
        self.year_combobox = ttk.Combobox(self.frame, values=[2024, 2023, 2022, 2021, 2020], state="readonly")
        self.year_combobox.grid(row=0, column=1, pady=5)

        # Hardcoded list of races for the race dropdown
        self.race_label = ttk.Label(self.frame, text="Select Race:")
        self.race_label.grid(row=1, column=0, sticky='w', pady=5)
        
        # Hardcoding the race options
        self.race_combobox = ttk.Combobox(self.frame, state="readonly")
        self.race_combobox['values'] = [
            "Bahrain", "Saudi Arabia", "Australia", "China", "Miami", "Monaco", 
            "Azerbaijan", "Canada", "Austria", "Britain", "Hungary", "Belgium", 
            "Netherlands", "Italy", "Singapore", "Japan", "USA", "Mexico", 
            "Brazil", "Abu Dhabi"
        ]
        self.race_combobox.grid(row=1, column=1, pady=5)

        # Session type selection (Race or Qualifying)
        self.session_label = ttk.Label(self.frame, text="Select Session Type:")
        self.session_label.grid(row=2, column=0, sticky='w', pady=5)
        self.session_combobox = ttk.Combobox(self.frame, values=["Race", "Qualifying"], state="readonly")
        self.session_combobox.grid(row=2, column=1, pady=5)

        # Button to begin fetching and loading data
        self.fetch_button = ttk.Button(self.frame, text="Fetch and Load Data", command=self.fetch_and_load_data)
        self.fetch_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Populate the race dropdown based on the selected year
        self.year_combobox.bind("<<ComboboxSelected>>", self.update_race_dropdown)

        # Frame for displaying status or messages
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.grid(row=1, column=0, padx=10, pady=10)

        self.status_label = ttk.Label(self.status_frame, text="Status: Waiting for input...")
        self.status_label.grid(row=0, column=0, pady=5)

        # Initialize selected year and race variables
        self.selected_year = None
        self.selected_race = None

    def update_race_dropdown(self, event):
        """
        Update the race dropdown based on the selected year.
        """
        self.selected_year = self.year_combobox.get()
        logging.info(f"Selected year: {self.selected_year}")
        # Optionally, filter races based on the year if needed

    def fetch_and_load_data(self):
        # Get the selected year, race, and session type
        selected_year = self.year_combobox.get()
        selected_race = self.race_combobox.get()
        session_type = self.session_combobox.get()[0]  # Get the first letter of the session type

        logging.info(f"Fetching data for {selected_race} {selected_year} ({session_type} session)")
        

        # Initialize F1DataFetcher with selected parameters
        data_fetcher = F1DataFetcher(year=selected_year, race_name=selected_race, session_type=session_type)

        try:
            # Load the session data (this will also fetch laps, driver, and weather data)
            data_fetcher.load_session_data(session_type)
            laps_data = data_fetcher.get_lap_data()  # Get the lap data after loading the session
        
            # If there's no lap data, log a warning
            if laps_data is None or laps_data.empty:
                logging.warning("No lap data found for this session.")
                return
        
            # Clean the data (pass the race_name along)
            cleaned_data = self.db_handler.clean_data(laps_data, selected_race)

            # Insert the cleaned data into MongoDB
            self.db_handler.insert_data(cleaned_data)
        
            logging.info(f"Successfully fetched and stored data for {selected_race} ({session_type} session)")

        except Exception as e:
            logging.error(f"Error fetching or storing data: {e}")



# Main Tkinter setup
if __name__ == "__main__":
    root = tk.Tk()
    app = F1StatsApp(root)
    root.mainloop()
