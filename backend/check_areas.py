import asyncio
from app.db.mongodb_service import MongoDBService

async def check_areas():
    db = MongoDBService()
    areas = await db.get_distinct_areas()
    print("Available restaurant areas:", areas)

if __name__ == "__main__":
    asyncio.run(check_areas())
