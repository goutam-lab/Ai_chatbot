import sys
import os
from pathlib import Path
import logging
from pymongo import ASCENDING, TEXT

# Get absolute path to project root
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import after path is set
try:
    from app.db.mongodb_service import MongoDBService
except ImportError as e:
    logging.error(f"Import failed: {str(e)}")
    logging.error(f"Python path: {sys.path}")
    raise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_indexes():
    try:
        db = MongoDBService()
        collection = db.db.restaurants
        
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
