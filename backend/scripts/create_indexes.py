from pymongo import ASCENDING, TEXT
from app.db.mongodb_service import MongoDBService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_indexes():
    try:
        db = MongoDBService()
        
        # Create indexes
        await db.db.restaurants.create_index([("cuisines", TEXT)])
        await db.db.restaurants.create_index([("location", TEXT)])
        await db.db.restaurants.create_index([("rate", ASCENDING)])
        
        logger.info("Successfully created MongoDB indexes")
    except Exception as e:
        logger.error(f"Failed to create indexes: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_indexes())
