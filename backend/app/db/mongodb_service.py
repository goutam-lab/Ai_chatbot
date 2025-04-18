from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from fastapi import HTTPException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(override=True)

class MongoDBService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_connection()
        return cls._instance
    
    def init_connection(self):
        """Initialize MongoDB connection with detailed error handling"""
        try:
            # Get MongoDB configuration
            mongodb_uri = os.getenv("MONGODB_URI")
            mongodb_name = os.getenv("MONGODB_NAME")
            
            if not mongodb_uri or not mongodb_name:
                raise ValueError("MongoDB configuration is missing in environment variables")
            
            logger.info(f"Connecting to MongoDB at {mongodb_uri}")
            
            # Initialize MongoDB client with timeout
            self.client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,  # 5 seconds timeout
                connectTimeoutMS=10000  # 10 seconds connection timeout
            )
            
            # Test the connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Set up database
            self.db = self.client[mongodb_name]
            
            # Verify the restaurants collection exists
            if "restaurants" not in self.db.list_collection_names():
                logger.warning("Restaurants collection not found in database")
                raise HTTPException(
                    status_code=500,
                    detail="Restaurants collection not found in database"
                )
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to connect to MongoDB. Please ensure MongoDB is running and accessible."
            )
        except ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB server selection timeout: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="MongoDB server is not responding. Please check if MongoDB is running."
            )
        except Exception as e:
            logger.error(f"Unexpected error during MongoDB initialization: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize MongoDB: {str(e)}"
            )

    async def get_restaurants(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Fetch restaurants with optional filters"""
        try:
            collection = self.db.restaurants
            cursor = collection.find(filters or {})
            return list(cursor)
        except Exception as e:
            logger.error(f"Error fetching restaurants: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch restaurants: {str(e)}"
            )

    async def analyze_cuisines(self) -> List[Dict]:
        """Analyze cuisine distribution"""
        try:
            pipeline = [
                {"$unwind": "$cuisines"},
                {"$group": {"_id": "$cuisines", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            return list(self.db.restaurants.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error analyzing cuisines: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to analyze cuisines: {str(e)}"
            )

    def get_restaurant_stats(self) -> Dict:
        """Get basic restaurant statistics"""
        try:
            cursor = self.db.restaurants.aggregate([
                {"$group": {
                    "_id": None,
                    "total_restaurants": {"$sum": 1},
                    "avg_rating": {"$avg": "$Aggregate rating"}
                }}
            ])
            return cursor.next()
        except Exception as e:
            print(f"Error getting restaurant stats: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error fetching restaurant statistics"
            )

    def get_relevant_restaurants(self, query: str) -> List[Dict]:
        """Fetch restaurants relevant to the user's query"""
        try:
            # Basic keyword matching - can be enhanced based on specific needs
            filters = {
                "$or": [
                    {"Restaurant Name": {"$regex": query, "$options": "i"}},
                    {"Cuisines": {"$regex": query, "$options": "i"}},
                    {"Address": {"$regex": query, "$options": "i"}}
                ]
            }
            return list(self.db.restaurants.find(filters).limit(5))
        except Exception as e:
            print(f"Error fetching relevant restaurants: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error fetching relevant restaurants"
            )

    async def get_top_restaurants_by_area(self, area: str, limit: int = 10) -> List[Dict]:
        """Get top-rated restaurants in a specific area"""
        try:
            # Create a case-insensitive regex pattern for the area
            area_pattern = {"$regex": f".*{area}.*", "$options": "i"}
            
            # Query to find restaurants in the specified area
            query = {"location": area_pattern}
            
            # Projection to include only the fields we need
            projection = {
                "name": 1,
                "rate": 1,
                "cuisines": 1,
                "address": 1,
                "approx_cost(for two people)": 1,
                "_id": 0
            }
            
            # Execute the query with sorting by rating
            cursor = self.db.restaurants.find(
                query,
                projection
            ).sort("rate", -1).limit(limit)
            
            return list(cursor)
        except Exception as e:
            logger.error(f"Error searching restaurants by area: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to search restaurants: {str(e)}"
            )
