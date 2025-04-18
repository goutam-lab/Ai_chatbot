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

async def setup_indexes():
    try:
        db = MongoDBService()
        collection = db.db.restaurants
        
        # Get existing indexes
        existing_indexes = await collection.index_information()
        
        # Create compound text index if none exists
        if not any('text' in str(idx) for idx in existing_indexes.values()):
            await collection.create_index([
                ("cuisines", TEXT), 
                ("location", TEXT)
            ], name="restaurant_text_search")
            logger.info("Created compound text index")
        else:
            logger.info("Text index already exists")
            
        # Create rating index if it doesn't exist
        if "rate_1" not in existing_indexes:
            await collection.create_index([("rate", ASCENDING)])
            logger.info("Created rating index")
        else:
            logger.info("Rating index already exists")
            
    except Exception as e:
        logger.error(f"Index setup failed: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_indexes())
