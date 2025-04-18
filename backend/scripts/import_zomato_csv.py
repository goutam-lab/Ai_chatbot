import csv
import os
import sys
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

# Increase CSV field size limit to handle larger fields
csv.field_size_limit(10**7)  # Set to 10MB or any value appropriate for your data

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))

def import_data():
    try:
        # Use absolute path
        csv_path = Path("C:/college/omnivio-data/zomato.csv")
        print(f"Looking for CSV at: {csv_path}")
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found at {csv_path}")

        db = client["zomato_db"]
        collection = db["restaurants"]
        collection.delete_many({})

        with open(csv_path, 'r', encoding='latin1') as f:
            reader = csv.DictReader(f)
            batch = list(reader)
            collection.insert_many(batch)
            print(f"✅ Success! Imported {len(batch)} records")

        print("Sample document:", collection.find_one())

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    import_data()
