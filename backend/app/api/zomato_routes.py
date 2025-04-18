from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.db.mongodb import MongoDB
import logging
from fastapi.responses import JSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)

def get_db():
    db = MongoDB()
    if not db.health_check():
        raise HTTPException(status_code=503, detail="Database unavailable")
    return db

class RestaurantQuery(BaseModel):
    cuisine: Optional[str] = None
    min_rating: Optional[float] = None
    location: Optional[str] = None
    limit: int = 10

@router.get("/restaurants")
async def get_restaurants(
    cuisine: Optional[str] = None,
    min_rating: Optional[float] = None,
    location: Optional[str] = None,
    limit: int = 10,
    db: MongoDB = Depends(get_db)
):
    try:
        import time
        start_time = time.time()
        
        filters = {}
        if cuisine:
            filters["cuisine"] = {"$regex": cuisine, "$options": "i"}
        if min_rating:
            filters["rating"] = {"$gte": min_rating}
        if location:
            filters["location"] = {"$regex": location, "$options": "i"}

        projection = {
            "_id": 0,
            "name": 1,
            "cuisine": 1,
            "rating": 1,
            "location": 1
        }

        results = await db.get_restaurants(filters, projection)
        if not results:
            return JSONResponse(
                content={"message": "No restaurants found"},
                status_code=404
            )
            
        query_time = time.time() - start_time
        logger.info(f"API request completed in {query_time:.2f}s")
        return results

    except HTTPException as e:
        if e.status_code == 504:
            logger.warning(f"Request timeout: {str(e)}")
            raise HTTPException(
                status_code=504,
                detail="Request timed out. Please try again with more specific filters."
            )
        raise
    except Exception as e:
        logger.error(f"Restaurant query failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch restaurants"
        )

@router.get("/cuisines")
async def get_cuisines(db: MongoDB = Depends(get_db)):
    try:
        import time
        start_time = time.time()
        
        results = await db.analyze_cuisines()
        query_time = time.time() - start_time
        logger.info(f"Cuisine analysis completed in {query_time:.2f}s")
        return results
        
    except HTTPException as e:
        if e.status_code == 504:
            logger.warning(f"Analysis timeout: {str(e)}")
            raise HTTPException(
                status_code=504,
                detail="Analysis timed out. Please try again with a smaller limit."
            )
        raise
    except Exception as e:
        logger.error(f"Cuisine analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze cuisines"
        )
