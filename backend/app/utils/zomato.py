from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
db = client["zomato_db"]
collection = db["restaurants"]

# 🆕 Create indexes (run only once)
collection.create_index([("name", "text")])
collection.create_index([("location", "text")])
collection.create_index([("rating", -1)])
def verify_connection():
    try:
        return db.command('ping')['ok'] == 1
    except:
        return False

def search_restaurants(location: str):
    try:
        results = collection.find(
            {"location": {"$regex": location, "$options": "i"}},
            {"_id": 0, "name": 1, "rating": 1, "cuisines": 1, "location": 1}
        ).limit(5)
        return list(results)
    except Exception as e:
        return [{"error": str(e)}]

