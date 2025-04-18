import os
import requests
import time
import asyncio
import json
from dotenv import load_dotenv
from fastapi import HTTPException
from app.services.assistant_tools import (
    search_restaurants_by_area,
    search_restaurants_by_cuisine,
    restaurant_search_by_area_tool,
    restaurant_search_by_cuisine_tool
)

# Load environment variables from .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
print(f"Loading .env from absolute path: {env_path}")
if not os.path.exists(env_path):
    raise FileNotFoundError(f".env file not found at: {env_path}")
load_dotenv(env_path, override=True)

# Load API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print(f"Error: OPENAI_API_KEY not found in environment variables (loaded from: {env_path})")
    raise ValueError("OpenAI API key not found in environment variables")

print(f"OpenAI API Key loaded successfully from: {env_path}")
# OpenAI API configuration
OPENAI_API_URL = "https://api.openai.com/v1"
OPENAI_HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "OpenAI-Beta": "assistants=v2",
    "Content-Type": "application/json"
}

# Other env variables
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_NAME = os.getenv("MONGODB_NAME")

# Main OpenAI service class
class OpenAIService:
    def __init__(self):
        try:
            print("Initializing OpenAI Service...")
            self.assistant_id = self.initialize_assistant()
            print("OpenAI Service initialized successfully")
        except Exception as e:
            print(f"Error in OpenAIService initialization: {str(e)}")
            raise

    def initialize_assistant(self):
        try:
            print("Starting assistant initialization...")

            # Check if we have an existing assistant ID
            if ASSISTANT_ID:
                try:
                    # Verify the assistant exists
                    response = requests.get(
                        f"{OPENAI_API_URL}/assistants/{ASSISTANT_ID}",
                        headers=OPENAI_HEADERS
                    )
                    if response.status_code == 200:
                        print(f"Using existing assistant: {ASSISTANT_ID}")
                        return ASSISTANT_ID
                    print(f"Existing assistant not found or invalid: {response.text}")
                except Exception as e:
                    print(f"Error checking existing assistant: {str(e)}")

            print("Creating new assistant...")
            assistant_data = {
                "name": "Restaurant Search Assistant",
                "instructions": """
                    You are a restaurant search assistant specialized in finding dining options.
                    When users ask about restaurants:
                    1. ALWAYS use the appropriate search tool based on their query
                    2. For location-only queries ("restaurants in X"), use search_restaurants_by_area
                    3. For cuisine-only queries ("Italian restaurants"), use search_restaurants_by_cuisine
                    4. For combined queries ("Italian in X"), use search_restaurants_by_cuisine with location parameter
                    5. Format responses with: Name, Rating, Cuisine, Address, Price Range
                    6. If no results found, say "No restaurants found matching your criteria"
                    7. NEVER invent restaurant information
                """,
                "tools": [restaurant_search_by_area_tool, restaurant_search_by_cuisine_tool],
                "model": "gpt-4"
            }
            
            response = requests.post(
                f"{OPENAI_API_URL}/assistants",
                headers=OPENAI_HEADERS,
                json=assistant_data
            )
            
            if response.status_code == 200:
                assistant = response.json()
                print(f"Assistant created successfully with ID: {assistant['id']}")
                os.environ["OPENAI_ASSISTANT_ID"] = assistant['id']
                return assistant['id']
            else:
                raise Exception(f"Failed to create assistant: {response.text}")

        except Exception as e:
            print(f"Error in assistant initialization: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error initializing OpenAI assistant: {str(e)}"
            )

    async def get_assistant_response(self, user_message: str, db_context: str = None) -> str:
        try:
            print(f"Processing message: {user_message[:100]}...")

            # Create thread
            thread_response = requests.post(
                f"{OPENAI_API_URL}/threads",
                headers=OPENAI_HEADERS
            )
            if thread_response.status_code != 200:
                raise Exception(f"Failed to create thread: {thread_response.text}")
            thread = thread_response.json()
            thread_id = thread['id']

            # Add message to thread
            message_response = requests.post(
                f"{OPENAI_API_URL}/threads/{thread_id}/messages",
                headers=OPENAI_HEADERS,
                json={
                    "role": "user",
                    "content": user_message
                }
            )
            if message_response.status_code != 200:
                raise Exception(f"Failed to add message: {message_response.text}")

            # Create run
            run_response = requests.post(
                f"{OPENAI_API_URL}/threads/{thread_id}/runs",
                headers=OPENAI_HEADERS,
                json={
                    "assistant_id": self.assistant_id
                }
            )
            if run_response.status_code != 200:
                raise Exception(f"Failed to create run: {run_response.text}")
            run = run_response.json()
            run_id = run['id']

            # Wait for run to complete (up to 30s)
            start_time = time.time()
            while True:
                if time.time() - start_time > 30:
                    raise HTTPException(
                        status_code=504,
                        detail={
                            "error": "timeout",
                            "message": "The request took too long. Please try again with a more specific query.",
                            "retryable": True
                        }
                    )

                run_status_response = requests.get(
                    f"{OPENAI_API_URL}/threads/{thread_id}/runs/{run_id}",
                    headers=OPENAI_HEADERS
                )
                if run_status_response.status_code != 200:
                    raise Exception(f"Failed to get run status: {run_status_response.text}")
                run = run_status_response.json()

                if run['status'] == "requires_action":
                    print("Assistant requires action - handling tool calls")
                    tool_calls = run['required_action']['submit_tool_outputs']['tool_calls']
                    tool_outputs = []

                    for tool_call in tool_calls:
                        if tool_call['function']['name'] == "search_restaurants_by_area":
                            print(f"Calling area search with args: {tool_call['function']['arguments']}")
                            args = json.loads(tool_call['function']['arguments'])
                            area = args.get("area")
                            results = await search_restaurants_by_area(area)
                            print(f"Area search returned {len(results)} restaurants")
                            tool_outputs.append({
                                "tool_call_id": tool_call['id'],
                                "output": json.dumps(results)
                            })
                        elif tool_call['function']['name'] == "search_restaurants_by_cuisine":
                            print(f"Calling cuisine search with args: {tool_call['function']['arguments']}")
                            args = json.loads(tool_call['function']['arguments'])
                            cuisine = args.get("cuisine")
                            location = args.get("location")
                            results = await search_restaurants_by_cuisine(cuisine, location)
                            print(f"Cuisine search returned {len(results)} restaurants")
                            tool_outputs.append({
                                "tool_call_id": tool_call['id'],
                                "output": json.dumps(results)
                            })

                    submit_response = requests.post(
                        f"{OPENAI_API_URL}/threads/{thread_id}/runs/{run_id}/submit_tool_outputs",
                        headers=OPENAI_HEADERS,
                        json={
                            "tool_outputs": tool_outputs
                        }
                    )
                    if submit_response.status_code != 200:
                        raise Exception(f"Failed to submit tool outputs: {submit_response.text}")
                    continue

                if run['status'] == "completed":
                    break
                elif run['status'] in ["failed", "cancelled", "expired"]:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Assistant run failed with status: {run['status']}"
                    )

                await asyncio.sleep(1)

            # Get assistant response
            messages_response = requests.get(
                f"{OPENAI_API_URL}/threads/{thread_id}/messages",
                headers=OPENAI_HEADERS
            )
            if messages_response.status_code != 200:
                raise Exception(f"Failed to get messages: {messages_response.text}")
            
            messages = messages_response.json()['data']
            assistant_message = next(
                (msg['content'][0]['text']['value'] for msg in messages if msg['role'] == "assistant"),
                "Sorry, I couldn't generate a response."
            )

            return assistant_message

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing request: {str(e)}"
            )

# Initialize the service once
try:
    print("Creating OpenAI service instance...")
    openai_service = OpenAIService()
    print("OpenAI service instance created successfully")
except Exception as e:
    print(f"Failed to create OpenAI service instance: {str(e)}")
    raise

# Export async function for reuse
async def get_assistant_response(user_message: str, db_context: str = None) -> str:
    return await openai_service.get_assistant_response(user_message, db_context)
