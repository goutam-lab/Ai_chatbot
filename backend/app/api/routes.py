from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from app.db.mongodb_service import MongoDBService
from app.services.openai_service import get_assistant_response
import asyncio
from concurrent.futures import TimeoutError as ConcurrentTimeoutError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Initializing routes.py router")  # Debug output
router = APIRouter()
db = MongoDBService()  # Use MongoDBService instead of MongoDB
print(f"Router initialized: {router}")  # Debug output

# Explicitly include the router in __all__ for proper import
__all__ = ["router"]

class ChatRequest(BaseModel):
    message: str
    is_data_query: Optional[bool] = False

@router.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"Received chat request: {request.message}")
    try:
        # Set timeout for the entire operation (increased from 15 to 30 seconds)
        try:
            if request.is_data_query or any(word in request.message.lower() 
                                          for word in ['restaurant', 'zomato', 'cuisine', 'rating']):
                # Handle Zomato data queries with increased timeout (30 seconds)
                response = await asyncio.wait_for(
                    handle_zomato_query(request.message),
                    timeout=60.0 #increased from 30 to 60 seconds
                )
                return {"response": response}
                
            # Directly check for food/restaurant related queries
            needs_db = any(word in request.message.lower() 
                         for word in ['food', 'restaurant', 'cuisine', 'dine', 'eat', 'menu'])
            
            if needs_db:
                # Get data from database with increased timeout (30 seconds)
                db_data = await asyncio.wait_for(
                    handle_zomato_query(request.message),
                    timeout=60.0 #increased from 30 to 60 seconds
                )
                # Get final response with context
                response = await asyncio.wait_for(
                    get_assistant_response(
                        f"User query: {request.message}\n"
                        f"Database results: {db_data}\n"
                        "Generate a helpful response using this data"
                    ),
                    timeout=60.0 #increased from 30 to 60 seconds
                )
            else:
                # Get direct response
                response = await asyncio.wait_for(
                    get_assistant_response(request.message),
                    timeout=60.0 #increased from 30 to 60 seconds
                )

            return {
                "response": response,
                "source": "database" if needs_db else "assistant"
            }
            
        except ConcurrentTimeoutError:
            logger.error("Request timed out")
            return JSONResponse(
                status_code=504,
                content={
                    "error": "timeout",
                    "message": "Your request took too long. Please try again with a simpler query."
                }
            )
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "server_error",
                "message": f"Error processing request: {str(e)}"
            }
        )

@router.get("/restaurants")
async def get_restaurants(
    cuisine: Optional[str] = None,
    min_rating: Optional[float] = None,
    limit: int = 10
):
    """Get restaurants with optional filters"""
    try:
        filters = {}
        if cuisine:
            filters["cuisines"] = {"$regex": cuisine, "$options": "i"}
        if min_rating:
            filters["rate"] = {"$gte": min_rating}
            
        restaurants = await db.get_restaurants(filters)
        return restaurants[:limit]
    except Exception as e:
        logger.error(f"Error fetching restaurants: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch restaurants: {str(e)}"
        )

@router.get("/analytics/cuisines")
async def get_cuisine_analytics():
    """Get cuisine distribution analytics"""
    try:
        return await db.analyze_cuisines()
    except Exception as e:
        logger.error(f"Error analyzing cuisines: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze cuisines: {str(e)}"
        )

@router.get("/analytics/ratings")
async def get_rating_analytics():
    """Get rating distribution analytics"""
    pipeline = [
        {"$group": {
            "_id": {"$floor": "$rating"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    return await db.restaurants.aggregate(pipeline)

async def handle_zomato_query(query: str) -> str:
    """Process Zomato dataset queries with increased timeout handling"""
    query = query.lower()
    
    try:
        if "cuisine" in query:
            results = await db.analyze_cuisines()
            return f"Top cuisines: {', '.join([f'{x['_id']} ({x['count']})' for x in results[:5]])}"
        
        if "rating" in query or "best" in query:
            top_rated = await db.get_restaurants(
                {"rate": {"$gte": 4.5}}
            )
            return f"Top rated restaurants: {', '.join([x['name'] for x in top_rated[:5]])}"
        
        return "I can analyze Zomato restaurant data. Ask about cuisines, ratings or restaurants."
    except Exception as e:
        logger.error(f"Error handling Zomato query: {str(e)}", exc_info=True)
        return f"Error processing your query: {str(e)}"
