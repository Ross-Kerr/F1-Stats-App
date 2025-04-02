import pymongo
import pandas as pd
import logging

# Set up logging for the application
logging.basicConfig(level=logging.INFO)

class F1MongoDBHandler:
    def __init__(self, db_name='F1App', collection_name='race_data'):
        """
        Initialize the MongoDB Handler class.
        :param db_name: Name of the MongoDB database (default: 'F1App').
        :param collection_name: Name of the collection to store the data (default: 'race_data').
        """
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")  # Connect to the MongoDB server
        self.db = self.client[db_name]  # Connect to the database
        self.collection = self.db[collection_name]  # Specify the collection to interact with
        
    def convert_pandas_types(self, data):
        """
        Convert Pandas Timedelta, Timestamp, and NaT values into serializable formats for MongoDB.
        :param data: Dictionary with data to be converted.
        :return: Cleaned dictionary with serializable types.
        """
        for key, value in data.items():
            if isinstance(value, pd.Timestamp):
                data[key] = value.isoformat()  # Convert Timestamp to ISO format string
            elif isinstance(value, pd.Timedelta):
                data[key] = value.total_seconds()  # Convert Timedelta to seconds (float)
            elif pd.isna(value):  # Convert NaT (Not a Time) to None
                data[key] = None
        return data

    def clean_data(self, df, race_name):
        """
        Clean and sanitize the data before inserting it into MongoDB.
        :param race_name: Name of the race (e.g., "Bahrain").
        """
        # Adjust the required columns based on what is available
        required_columns = ['Driver', 'LapTime', 'LapNumber']  # Ensure these columns exist

        # Ensure required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise KeyError(f"Missing required columns. Found columns: {df.columns}. Missing columns: {missing_columns}")

        # Add 'race_name' if missing (you might get this from session or pass it manually)
        if 'race_name' not in df.columns:
            df['race_name'] = race_name  # Now it gets passed from the calling code

        # Drop rows with missing essential data (including 'race_name', 'Driver', 'LapNumber')
        df.dropna(subset=required_columns + ['race_name'], inplace=True)

        # Convert DataFrame to a list of dictionaries
        data_dict = df.to_dict(orient="records")

        # Check if any dictionary contains None for 'race_name', 'Driver', or 'LapNumber'
        for row in data_dict:
            if row.get('race_name') is None or row.get('Driver') is None or row.get('LapNumber') is None:
                logging.error(f"Invalid data found (missing 'race_name', 'Driver', or 'LapNumber'): {row}")
                continue  # Skip invalid rows

        # Convert Pandas-specific types into MongoDB-friendly formats
        clean_data_dict = [self.convert_pandas_types(row) for row in data_dict]

        return clean_data_dict






    def insert_data(self, data):
        """
        Insert cleaned data into MongoDB collection (avoiding duplicates).
        :param data: List of dictionaries containing lap data.
        """
        if not data or not isinstance(data, list):  
            logging.warning("No valid data provided for insertion.")
            return

        # Convert list of dictionaries into a Pandas DataFrame
        df = pd.DataFrame(data)

        # If there is no data to insert, log a warning and return
        if df.empty:
            logging.warning("No data to insert into the database.")
            return

        # Rename columns to match expected MongoDB schema
        expected_columns = {'driver': 'Driver', 'lap_time': 'LapTime', 'lap_number': 'LapNumber'}
        df.rename(columns=expected_columns, inplace=True)

        # Convert DataFrame to list of dictionaries for MongoDB insertion
        data_dict = df.to_dict(orient="records")

        # Clean data to remove any invalid or incomplete records
        clean_data_dict = [self.convert_pandas_types(row) for row in data_dict]

        # Remove records where any of the required fields are missing
        required_fields = ['race_name', 'Driver', 'LapNumber']
        clean_data_dict = [record for record in clean_data_dict if all(record.get(field) for field in required_fields)]

        # If no valid data remains, log and return
        if not clean_data_dict:
            logging.warning("No valid records to insert (some records have missing fields).")
            return

        # Insert data, using 'upsert' to avoid duplicates
        for record in clean_data_dict:
            race_name = record.get("race_name")
            driver = record.get("Driver")
            lap_number = record.get("LapNumber")

            if race_name is None or driver is None or lap_number is None:
                logging.error(f"Skipping record with missing required fields: {record}")
                continue  # Skip this record if any required field is missing

            try:
                # Check if a record already exists for the same race_name, driver, and lap_number
                existing_record = self.collection.find_one({
                    "race_name": race_name,
                    "Driver": driver,
                    "LapNumber": lap_number
                })

                if existing_record:
                    # Update existing record
                    self.collection.update_one(
                        {"_id": existing_record["_id"]},  
                        {"$set": record}  
                    )
                    logging.info(f"Updated record: {record}")
                else:
                    # Insert new record
                    self.collection.insert_one(record)
                    logging.info(f"Inserted new record: {record}")

            except Exception as e:
                logging.error(f"Error inserting/updating data into MongoDB: {e}")





    def update_data(self, query, new_values):
        """
        Update data in MongoDB based on a query.
        :param query: Dictionary specifying which documents to update.
        :param new_values: Dictionary with the updated values.
        """
        try:
            update_result = self.collection.update_many(query, {"$set": new_values})
            logging.info("%d documents updated.", update_result.modified_count)
        except Exception as e:
            logging.error(f"Error updating data: {e}")

    def delete_data(self, query):
        """
        Delete data from MongoDB based on a query.
        :param query: Dictionary specifying which documents to delete.
        """
        try:
            delete_result = self.collection.delete_many(query)
            logging.info("%d documents deleted.", delete_result.deleted_count)
        except Exception as e:
            logging.error(f"Error deleting data: {e}")
