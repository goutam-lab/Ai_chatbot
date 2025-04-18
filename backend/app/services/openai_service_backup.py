import os
import openai
import time
import asyncio
import json
from dotenv import load_dotenv
from fastapi import HTTPException
from app.services.assistant_tools import search_restaurants_by_area, restaurant_search_tool

# Load environment variables first
load_dotenv(override=True)

# Get environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in environment variables")
    raise ValueError("OpenAI API key not found in environment variables")

print("OpenAI API Key loaded successfully")
openai.api_key = api_key

ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_NAME = os.getenv("MONGODB_NAME")

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
            # Delete existing assistant if it exists
            try:
                if ASSISTANT_ID:
                    print(f"Deleting existing assistant: {ASSISTANT_ID}")
                    openai.Assistant.delete(ASSISTANT_ID)
            except Exception as e:
                print(f"Error deleting existing assistant: {str(e)}")
                # Continue even if deletion fails

            print("Creating new assistant...")
            # Create a new assistant with proper configuration
            assistant = openai.Assistant.create(
                name="Restaurant Search Assistant",
                instructions="""You are a helpful restaurant assistant that can search for restaurants in specific areas.
                When a user asks about restaurants in an area, you MUST use the search_restaurants_by_area tool to find relevant restaurants.
                Always extract the area name from the user's query and use it with the tool.
                Format the response in a user-friendly way, including restaurant names, ratings, cuisines, and addresses.
                If no restaurants are found, inform the user politely.
                DO NOT make up restaurant information - only use data from the search_restaurants_by_area tool.""",
                tools=[restaurant_search_tool],
                model="gpt-4"
            )
            
            print(f"Assistant created successfully with ID: {assistant.id}")
            # Update the ASSISTANT_ID in the environment
            os.environ["OPENAI_ASSISTANT_ID"] = assistant.id
            
            return assistant.id
        except Exception as e:
            print(f"Error in assistant initialization: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error initializing OpenAI assistant: {str(e)}"
            )

    async def get_assistant_response(self, user_message: str, db_context: str = None) -> str:
        try:
            print(f"Processing message: {user_message[:100]}...")

            # Create thread and post message
            thread = openai.Thread.create()
            openai.Thread.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_message,
            )

            # Start assistant run
            run = openai.Thread.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id,
            )

            # Wait for completion with timeout
            start_time = time.time()
            while True:
                if time.time() - start_time > 30:  # 30 second timeout
                    raise HTTPException(
                        status_code=504,
                        detail={
                            "error": "timeout",
                            "message": "The request took too long. Please try again with a more specific query.",
                            "retryable": True
                        }
                    )
                    
                run = openai.Thread.runs.retrieve(
                    thread_id=thread.id, 
                    run_id=run.id
                )
                
                if run.status == "requires_action":
                    print("Assistant requires action - handling tool calls")
                    # Handle tool calls
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    tool_outputs = []
                    
                    for tool_call in tool_calls:
                        if tool_call.function.name == "search_restaurants_by_area":
                            print(f"Calling search_restaurants_by_area with arguments: {tool_call.function.arguments}")
                            # Extract area from the function arguments
                            args = json.loads(tool_call.function.arguments)
                            area = args.get("area")
                            
                            # Call the tool function
                            results = search_restaurants_by_area(area)
                            print(f"Tool returned {len(results)} restaurants")
                            
                            # Submit the tool output
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps(results)
                            })
                    
                    # Submit all tool outputs
                    openai.Thread.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                    continue
                    
                if run.status == "completed":
                    break
                elif run.status in ["failed", "cancelled", "expired"]:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Assistant run failed with status: {run.status}"
                    )
                
                await asyncio.sleep(1)  # 1 second delay between checks

            # Get the assistant's response
            messages = openai.Thread.messages.list(thread_id=thread.id)
            assistant_message = next(
                (msg.content[0].text.value for msg in messages.data if msg.role == "assistant"),
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

# Create a single instance of the service
try:
    print("Creating OpenAI service instance...")
    openai_service = OpenAIService()
    print("OpenAI service instance created successfully")
except Exception as e:
    print(f"Failed to create OpenAI service instance: {str(e)}")
    raise

# Export the get_assistant_response function
async def get_assistant_response(user_message: str, db_context: str = None) -> str:
    return await openai_service.get_assistant_response(user_message, db_context)
