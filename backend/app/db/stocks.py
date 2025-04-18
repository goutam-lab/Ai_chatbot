"""Stock data database operations"""
from typing import Optional, Dict
import asyncio
from datetime import datetime

# Example implementation - replace with your actual database connection
async def get_stock_data(symbol: str) -> Optional[Dict]:
    """Get stock data from database"""
    # This would connect to your actual database
    # For now returning example data
    example_data = {
        "AAPL": {
            "symbol": "AAPL",
            "price": 185.64,
            "change": +1.23,
            "timestamp": datetime.now().isoformat()
        },
        "MSFT": {
            "symbol": "MSFT",
            "price": 402.56,
            "change": -0.45,
            "timestamp": datetime.now().isoformat()
        },
        "GOOGL": {
            "symbol": "GOOGL",
            "price": 142.37,
            "change": +2.11,
            "timestamp": datetime.now().isoformat()
        }
    }
    return example_data.get(symbol.upper())

async def get_all_stocks() -> Dict[str, Dict]:
    """Get all available stock data"""
    return {
        "AAPL": await get_stock_data("AAPL"),
        "MSFT": await get_stock_data("MSFT"),
        "GOOGL": await get_stock_data("GOOGL")
    }
