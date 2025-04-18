import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path}")

try:
    from app.main import app
    print("Successfully imported app.main")
    
    from app.db.mongodb_service import MongoDBService
    print("Successfully imported MongoDBService")
    
    print("\nAll imports successful!")
except ImportError as e:
    print(f"\nImport error: {str(e)}")
    sys.exit(1) 