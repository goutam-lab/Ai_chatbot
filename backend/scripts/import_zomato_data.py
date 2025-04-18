import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

try:
    import pandas as pd
    USE_PANDAS = True
except ImportError:
    USE_PANDAS = False
    import csv

load_dotenv()

def import_zomato_data():
    # Load CSV
    csv_path = Path(r"C:\Users\gouta\OneDrive\Desktop\omnivio-3\backend\data\zomato.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Zomato CSV not found at {csv_path}")

    # Connect to MongoDB
    client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
    db = client[os.getenv("MONGODB_NAME", "zomato_db")]
    collection = db["restaurants"]
    
    # Clear existing data
    collection.delete_many({})

    if USE_PANDAS:
        # Using pandas
        df = pd.read_csv(csv_path, encoding="latin1")
        data = df.to_dict("records")
    else:
        # Using standard csv module
        with open(csv_path, 'r', encoding='latin1') as f:
            reader = csv.DictReader(f)
            data = list(reader)

    # Insert data
    result = collection.insert_many(data)
    print(f"✅ Successfully inserted {len(result.inserted_ids)} records")
    print(f"📊 Sample document: {collection.find_one()}")

if __name__ == "__main__":
    if not USE_PANDAS:
        print("⚠️ pandas not found, using slower csv module")
    import_zomato_data()
