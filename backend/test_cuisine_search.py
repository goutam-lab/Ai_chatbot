import asyncio
from app.services.openai_service import get_assistant_response

async def test_cuisine_search():
    # Test 1: Cuisine with location
    print("\n=== Testing: Italian restaurants in Bangalore ===")
    response = await get_assistant_response("Find me Italian restaurants in Bangalore")
    print("Response:", response)
    
    # Test 2: Cuisine without location
    print("\n=== Testing: Italian restaurants ===")
    response = await get_assistant_response("Find me Italian restaurants")
    print("Response:", response)
    
    # Test 3: Specific cuisine in Banashankari
    print("\n=== Testing: Italian restaurants in Banashankari ===")
    response = await get_assistant_response("Find me Italian restaurants in Banashankari")
    print("Response:", response)

if __name__ == "__main__":
    asyncio.run(test_cuisine_search())
