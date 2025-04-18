import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.mongodb_service import MongoDBService
from app.services.openai_service import get_assistant_response

client = TestClient(app)

def test_restaurant_search_flow():
    # Test message
    test_message = "Top restaurants in Andheri"
    
    # Make request to chat endpoint
    response = client.post(
        "/api/chat",
        json={"message": test_message}
    )
    
    # Verify response status
    assert response.status_code == 200
    
    # Get response data
    data = response.json()
    
    # Verify response structure
    assert "response" in data
    
    # Print the response for manual verification
    print("\nTest Results:")
    print(f"Input Message: {test_message}")
    print(f"Assistant Response: {data['response']}")
    
    # Additional verification steps
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0
    
    # Check if response contains restaurant information
    # (This is a basic check - actual content will vary)
    assert any(keyword in data["response"].lower() 
              for keyword in ["restaurant", "rating", "cuisine", "address"])

if __name__ == "__main__":
    # Run the test
    test_restaurant_search_flow() 