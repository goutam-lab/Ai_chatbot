import asyncio
from app.services.openai_service import get_assistant_response
from app.db.mongodb_service import MongoDBService

async def test_complete_flow():
    # Initialize MongoDB service
    db_service = MongoDBService()
    
    # Test message
    test_message = "Top restaurants in Andheri"
    print(f"\nTesting with message: '{test_message}'\n")
    
    try:
        # Step 1: Get assistant response
        print("1. Sending message to OpenAI Assistant...")
        response = await get_assistant_response(test_message)
        
        # Step 2: Print the response
        print("\n2. Received response from Assistant:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        # Step 3: Verify MongoDB data
        print("\n3. Verifying MongoDB data...")
        restaurants = db_service.get_top_restaurants_by_area("Andheri")
        print(f"Found {len(restaurants)} restaurants in Andheri")
        
        if restaurants:
            print("\nSample restaurant data:")
            for i, restaurant in enumerate(restaurants[:3], 1):
                print(f"\nRestaurant {i}:")
                print(f"Name: {restaurant.get('Restaurant Name', 'Unknown')}")
                print(f"Rating: {restaurant.get('Aggregate rating', 'N/A')}")
                print(f"Cuisine: {restaurant.get('Cuisines', 'Unknown')}")
                print(f"Address: {restaurant.get('Address', 'Unknown')}")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_complete_flow()) 