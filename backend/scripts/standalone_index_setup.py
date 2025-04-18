import sys
import os
import logging
from pymongo import MongoClient, ASCENDING, TEXT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_indexes():
    try:
        # Connect directly to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['omnivio']  # Replace with your actual DB name
        collection = db['restaurants']
        
        # Get existing indexes
        existing_indexes = collection.index_information()
        logger.info(f"Existing indexes: {existing_indexes.keys()}")
        
        # Create compound text index if none exists
        if not any('text' in str(idx) for idx in existing_indexes.values()):
            collection.create_index([
                ("cuisines", TEXT), 
                ("location", TEXT)
            ], name="restaurant_text_search")
            logger.info("Created compound text index")
        else:
            logger.info("Text index already exists")
            
        # Create rating index if needed
        if "rate_1" not in existing_indexes:
            collection.create_index([("rate", ASCENDING)])
            logger.info("Created rating index")
        else:
            logger.info("Rating index already exists")
            
        return True
    except Exception as e:
        logger.error(f"Index setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    if setup_indexes():
        logger.info("Index setup completed successfully")
        sys.exit(0)
    else:
        logger.error("Index setup failed")
        sys.exit(1)
