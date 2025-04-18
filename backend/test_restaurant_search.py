import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))
from app.services.openai_service import get_assistant_response

async def test_search():
    queries = [
        "Find Italian restaurants in Banashankari",
        "Show me Chinese restaurants",
        "What restaurants are there in Koramangala?"
    ]
    
    for query in queries:
        print(f"\nTesting query: '{query}'")
        try:
            response = await get_assistant_response(query)
            print("Response:", response)
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_search())
