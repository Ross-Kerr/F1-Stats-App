from tkinter import SE
import fastf1
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

class F1DataFetcher:
    def __init__(self, year, race_name, session_type='R'):
        """
        Initialize the F1DataFetcher class.
        :param year: Year of the race (e.g., 2024).
        :param race_name: Name of the race (e.g., "Bahrain").
        :param session_type: Type of the session (e.g., 'R' for race, 'Q' for qualifying).
        """
        self.year = year
        self.race_name = race_name
        self.session_type = session_type
        self.session = None
        self.laps = None
        self.driver_info = None
        self.weather_data = None

    def load_session_data(self, session_type):
        """
        Load the session data for the specified race and year.
        Fetch lap data, weather information, and driver data.
        """
        try:
            self.year = int(self.year) 
            # Load the session (e.g., 2024 Bahrain Grand Prix, Race session)
            self.session = fastf1.get_session(self.year, self.race_name, self.session_type)
            self.session.load()  # Load all data for the session

            # Extract lap data
            self.laps = self.session.laps
            logging.info(f"Laps data for {self.race_name} ({self.session_type} session) loaded successfully.")

            # Extract driver info
            self.driver_info = self.session.drivers
            logging.info(f"Driver data for {self.race_name} loaded successfully.")

            # Extract weather data
            self.weather_data = self.session.weather_data
            logging.info(f"Weather data for {self.race_name} loaded successfully.")

        except Exception as e:
            logging.error(f"Error loading session data: {e}")
            raise e  # Rethrow exception for further handling if needed

    def get_lap_data(self):
        """
        Returns lap data for all drivers.
        :return: DataFrame of lap data.
        """
        if self.laps is not None:
            return self.laps
        else:
            logging.error("Lap data is not available. Please load the session first.")
            return None

    def get_driver_info(self):
        """
        Returns driver information for the race.
        :return: DataFrame of driver information.
        """
        if self.driver_info is not None:
            return pd.DataFrame(self.driver_info)
        else:
            logging.error("Driver info is not available. Please load the session first.")
            return None

    def get_weather_data(self):
        """
        Returns weather data for the race.
        :return: DataFrame of weather information.
        """
        if self.weather_data is not None:
            return self.weather_data
        else:
            logging.error("Weather data is not available. Please load the session first.")
            return None

    def save_data_to_csv(self, file_name_prefix="race_data"):
        """
        Save lap data, driver info, and weather data to CSV files.
        :param file_name_prefix: Prefix for the filenames.
        """
        if self.laps is not None:
            self.laps.to_csv(f"{file_name_prefix}_laps_{self.race_name}_{self.session_type}.csv", index=False)
            logging.info("Lap data saved to CSV.")
        if self.driver_info is not None:
            driver_df = pd.DataFrame(self.driver_info)
            driver_df.to_csv(f"{file_name_prefix}_drivers_{self.race_name}_{self.session_type}.csv", index=False)
            logging.info("Driver data saved to CSV.")
        if self.weather_data is not None:
            self.weather_data.to_csv(f"{file_name_prefix}_weather_{self.race_name}_{self.session_type}.csv", index=False)
            logging.info("Weather data saved to CSV.")
        else:
            logging.warning("Weather data is not available to save.")
