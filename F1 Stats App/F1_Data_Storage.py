from pymongo import MongoClient
import pandas as pd
import fastf1 as ff1

class F1DataStorage:
    def __init__(self, db_name="F1Database", collection_name="race_data"):
        """
        Initialize MongoDB connection.
        """
        self.client = MongoClient("mongodb://localhost:27017/")  # Connect to MongoDB
        self.db = self.client[db_name]  # Select Database
        self.collection = self.db[collection_name]  # Select Collection

    def store_race_data(self, df):
        """
        Store race data in MongoDB as JSON documents.
        """
        json_data = df.to_dict(orient="records")  # Convert DataFrame to JSON
        self.collection.insert_many(json_data)  # Insert JSON data into MongoDB
        print("Race data successfully stored in MongoDB!")

    def retrieve_race_data(self):
        """
        Retrieve race data from MongoDB and return it as a pandas DataFrame.
        """
        retrieved_data = list(self.collection.find({}, {"_id": 0}))  # Exclude MongoDB's default `_id` field
        df = pd.DataFrame(retrieved_data)  # Convert JSON data back to DataFrame
        return df

# Example usage:
if __name__ == "__main__":
    storage = F1DataStorage()  # Initialize storage handler
    
    # Load an example race session (Bahrain 2024)
    session = ff1.get_session(2024, "Bahrain", "R")
    session.load()
    laps = session.laps  # Extract lap data
    
    storage.store_race_data(laps)  # Store data in MongoDB
    retrieved_df = storage.retrieve_race_data()  # Retrieve stored data
    print(retrieved_df.head())  # Display retrieved data
