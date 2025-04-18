from typing import List, Dict, Optional
from app.db.mongodb_service import MongoDBService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_service = MongoDBService()

async def search_restaurants_by_area(location: str) -> List[Dict]:
    """
    Search for top-rated restaurants in a specific location.
    
    Args:
        location (str): The location to search for restaurants in
        
    Returns:
        List[Dict]: List of restaurant information including name, rating, and address
    """
    if not location:
        logger.warning("No location provided for restaurant search")
        return []

    try:
        logger.info(f"Searching for restaurants in location: {location}")
        restaurants = await db_service.get_top_restaurants_by_area(location)
        logger.info(f"Found {len(restaurants)} restaurants in {location}")
        
        # Format the response for the assistant
        formatted_restaurants = []
        for restaurant in restaurants:
            formatted_restaurants.append({
                "name": restaurant.get("name", "Unknown"),
                "rating": restaurant.get("rate", "N/A"),
                "cuisine": restaurant.get("cuisines", "Unknown"),
                "address": restaurant.get("address", "Unknown"),
                "price_range": restaurant.get("approx_cost(for two people)", "N/A")
            })
        
        if not formatted_restaurants:
            logger.info(f"No restaurants found in {location}")
            return []

        return formatted_restaurants
    except Exception as e:
        logger.error(f"Error in search_restaurants_by_area: {str(e)}")
        return []

async def search_restaurants_by_cuisine(cuisine: str, location: Optional[str] = None) -> List[Dict]:
    """
    Search for top-rated restaurants by cuisine type and optional location.
    
    Args:
        cuisine (str): The cuisine type to search for
        location (str): Optional location to filter by
        
    Returns:
        List[Dict]: List of restaurant information including name, rating, and address
    """
    if not cuisine:
        logger.warning("No cuisine type provided for restaurant search")
        return []

    try:
        # Build the query
        query = {"cuisines": {"$regex": cuisine, "$options": "i"}}
        if location:
            query["location"] = {"$regex": f".*{location}.*", "$options": "i"}
            logger.info(f"Searching for {cuisine} restaurants in {location}")
        else:
            logger.info(f"Searching for {cuisine} restaurants in all locations")

        # Get restaurants sorted by rating
        restaurants = await db_service.get_restaurants(query)
        if not restaurants:
            logger.info(f"No {cuisine} restaurants found")
            return []

        logger.info(f"Found {len(restaurants)} {cuisine} restaurants")
        
        # Format the response for the assistant
        formatted_restaurants = []
        for restaurant in restaurants:
            formatted_restaurants.append({
                "name": restaurant.get("name", "Unknown"),
                "rating": restaurant.get("rate", "N/A"),
                "cuisine": restaurant.get("cuisines", "Unknown"),
                "address": restaurant.get("address", "Unknown"),
                "price_range": restaurant.get("approx_cost(for two people)", "N/A")
            })
        
        return formatted_restaurants[:10]  # Return top 10 restaurants
    except Exception as e:
        logger.error(f"Error in search_restaurants_by_cuisine: {str(e)}")
        return []

# Tool definitions for OpenAI Assistant
restaurant_search_by_area_tool = {
    "type": "function",
    "function": {
        "name": "search_restaurants_by_area",
        "description": "Search for top-rated restaurants in a specific area. Returns a list of restaurants with their names, ratings, cuisines, and addresses. Use this tool whenever a user asks about restaurants in a specific location.",
        "parameters": {
            "type": "object",
            "properties": {
                "area": {
                    "type": "string",
                    "description": "The area to search for restaurants in (e.g., 'Andheri', 'Bandra', etc.). Extract this from the user's query."
                }
            },
            "required": ["area"]
        }
    }
}

restaurant_search_by_cuisine_tool = {
    "type": "function",
    "function": {
        "name": "search_restaurants_by_cuisine",
        "description": "Search for top-rated restaurants by cuisine type. Returns a list of restaurants with their names, ratings, locations, and price ranges. Use when user asks for specific cuisine types.",
        "parameters": {
            "type": "object",
            "properties": {
                "cuisine": {
                    "type": "string",
                    "description": "The cuisine type to search for (e.g., 'Italian', 'Chinese', etc.)"
                },
                "location": {
                    "type": "string",
                    "description": "Optional location to filter by"
                }
            },
            "required": ["cuisine"]
        }
    }
}
