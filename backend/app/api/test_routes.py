print("Loading test_routes.py")
from fastapi import APIRouter, HTTPException
from app.db.mongodb import MongoDB
from app.services.openai_service import get_assistant_response

print("Creating APIRouter instance")
router = APIRouter()
print(f"Router created: {router}")
db = MongoDB()

print(f"Current router routes: {router.routes}")
@router.get("/test-services")
async def test_services():
    print(f"After route definition - Current router routes: {router.routes}")
    """Test all service connections"""
    try:
        # Test MongoDB
        await db.client.admin.command('ping')
        
        # Test OpenAI
        test_response = await get_assistant_response("test")
        
        return {
            "status": "success",
            "mongo": "connected",
            "openai": "connected"
        }
    except Exception as e:
        import traceback
        print(f"Service test failed: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Service test failed: {str(e)}"
        )
