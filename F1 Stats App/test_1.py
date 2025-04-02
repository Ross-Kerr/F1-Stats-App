# Test script for F1DataFetcher, F1MongoDBHandler, and F1StatsApp

# Test F1DataFetcher
from F1DataFetcher import F1DataFetcher
from F1MongoDBHandler import F1MongoDBHandler
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Test F1DataFetcher
logging.info("Testing F1DataFetcher...")
f1_fetcher = F1DataFetcher(2024, "Bahrain")  # Example year and race
f1_fetcher.load_session_data(session_type='R')  # 'R' for Race session
laps_data = f1_fetcher.get_lap_data()
logging.info(f"Laps Data: {laps_data}")

# Test F1MongoDBHandler
logging.info("Testing F1MongoDBHandler...")
db_handler = F1MongoDBHandler()

# Insert some sample lap data
sample_lap_data = {
    "year": 2024,
    "race": "Bahrain",
    "lap_number": 1,
    "driver": "VER",
    "lap_time": "1:31.345",
}
db_handler.insert_data([sample_lap_data])

# Retrieve the inserted data
retrieved_data = db_handler.get_data({"year": 2024, "race": "Bahrain"})
logging.info(f"Retrieved Data: {retrieved_data}")

# Test F1StatsApp (GUI)
logging.info("Testing F1StatsApp GUI...")

# Create the Tkinter root window and the app instance
import tkinter as tk
from F1_Stats_App import F1StatsApp

root = tk.Tk()  # Create root window for Tkinter
app = F1StatsApp(root)  # Create an instance of F1StatsApp

# Run the Tkinter app
root.mainloop()
