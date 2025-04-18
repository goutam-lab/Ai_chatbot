from app.db.mongodb_service import MongoDBService
import sys
import os

def test_mongodb_connection():
    print("Testing MongoDB connection...")
    try:
        # Initialize MongoDB service
        db_service = MongoDBService()
        
        # Try to get some data
        restaurants = db_service.get_top_restaurants_by_area("Andheri")
        print(f"\nFound {len(restaurants)} restaurants in Andheri")
        
        if restaurants:
            print("\nSample restaurant data:")
            for i, restaurant in enumerate(restaurants[:3], 1):
                print(f"\nRestaurant {i}:")
                print(f"Name: {restaurant.get('Restaurant Name', 'Unknown')}")
                print(f"Rating: {restaurant.get('Aggregate rating', 'N/A')}")
                print(f"Cuisine: {restaurant.get('Cuisines', 'Unknown')}")
                print(f"Address: {restaurant.get('Address', 'Unknown')}")
        else:
            print("No restaurants found. Make sure your database is populated.")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Add the parent directory to Python path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_mongodb_connection() 