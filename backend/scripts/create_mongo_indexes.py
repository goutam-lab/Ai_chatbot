import sys
import os
from pathlib import Path
import logging
from pymongo import ASCENDING, TEXT

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

from app.db.mongodb_service import MongoDBService

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
