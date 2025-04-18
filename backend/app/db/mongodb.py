from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Dict, List, Optional
from fastapi import HTTPException
import os
from dotenv import load_dotenv
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
logger = logging.getLogger(__name__)

class MongoDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_connection()
        return cls._instance
        
    def init_connection(self):
        self.client = MongoClient(
            os.getenv("MONGODB_URI"),
            maxPoolSize=100,
            minPoolSize=10,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000
        )
        self.db = self.client[os.getenv("MONGODB_NAME", "zomato")]
        self.create_indexes()
        
    def create_indexes(self):
        try:
            self.db.restaurants.create_index([("location", "text")])
            self.db.restaurants.create_index([("cuisine", 1)])
            self.db.restaurants.create_index([("rating", -1)])
        except PyMongoError as e:
            logger.error(f"Index creation failed: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_restaurants(self, filters: Optional[Dict] = None, projection: Optional[Dict] = None) -> List[Dict]:
        """Fetch restaurants with optimized query"""
        try:
            import time
            start_time = time.time()
            result = list(self.db.restaurants.find(
                filters or {},
                projection or {},
                max_time_ms=15000  # Increased from 5s to 15s
            ))
            query_time = time.time() - start_time
            logger.info(f"Restaurant query executed in {query_time:.2f}s")
            return result
        except PyMongoError as e:
            if "operation exceeded time limit" in str(e):
                logger.warning(f"Query timeout: {e}")
                raise HTTPException(
                    status_code=504,
                    detail="Database query timeout"
                )
            logger.error(f"Query failed: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))        
    async def analyze_cuisines(self, limit: int = 10) -> List[Dict]:
        """Optimized cuisine analysis"""
        pipeline = [
            {"$unwind": "$cuisine"},
            {"$group": {"_id": "$cuisine", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {"$project": {"_id": 0, "cuisine": "$_id", "count": 1}}
        ]
        try:
            import time
            start_time = time.time()
            result = list(self.db.restaurants.aggregate(
                pipeline,
                allowDiskUse=True,
                maxTimeMS=20000  # Increased from 10s to 20s
            ))
            query_time = time.time() - start_time
            logger.info(f"Cuisine analysis executed in {query_time:.2f}s")
            return result
        except PyMongoError as e:
            if "operation exceeded time limit" in str(e):
                logger.warning(f"Aggregation timeout: {e}")
                raise HTTPException(
                    status_code=504,
                    detail="Database aggregation timeout"
                )
            logger.error(f"Aggregation failed: {e}")
            raise

    def health_check(self) -> bool:
        """Check database connection health"""
        try:
            return self.db.command('ping')['ok'] == 1
        except PyMongoError:
            return False
