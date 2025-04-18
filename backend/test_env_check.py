import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if the API key is loaded
print("Testing environment variables...")
print(f"OPENAI_API_KEY exists: {'OPENAI_API_KEY' in os.environ}")
print(f"OPENAI_API_KEY value: {os.getenv('OPENAI_API_KEY')}")
