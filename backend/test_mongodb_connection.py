import asyncio
from app.db.mongodb_service import MongoDBService

async def test_connection():
    print("Testing MongoDB connection...")
    try:
        db = MongoDBService()
        # Test getting restaurant count
        count = await db.get_restaurants({})
        print(f"Found {len(count)} restaurants in database")
        
        # Test getting Italian restaurants
        italian = await db.get_restaurants({"cuisines": {"$regex": "Italian", "$options": "i"}})
        print(f"Found {len(italian)} Italian restaurants")
        
        # Test Banashankari restaurants
        banashankari = await db.get_restaurants({"location": {"$regex": "Banashankari", "$options": "i"}})
        print(f"Found {len(banashankari)} restaurants in Banashankari")
        
    except Exception as e:
        print(f"MongoDB test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_connection())
