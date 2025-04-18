from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
print("Attempting to import routers...")
from app.api import zomato_routes, routes, test_routes
print(f"Successfully imported: zomato_routes={zomato_routes}, routes={routes}, test_routes={test_routes}")
from app.db.mongodb_service import MongoDBService

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
mongodb_service = MongoDBService()

# Include routers
app.include_router(zomato_routes.router, prefix="/api/zomato")
print(f"Including routes router: {routes.router}")  # Debug output
app.include_router(routes.router, prefix="/api")
print("Routes router included successfully")  # Debug output
app.include_router(test_routes.router, prefix="/api")
print("Test routes router included successfully")  # Debug output

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
