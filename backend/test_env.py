import os
from dotenv import load_dotenv

print("Testing environment variables...")
load_dotenv(override=True)

print(f"OPENAI_API_KEY exists: {'OPENAI_API_KEY' in os.environ}")
print(f"OPENAI_API_KEY value: {os.getenv('OPENAI_API_KEY')}")
print(f"Current working directory: {os.getcwd()}")
print(f".env file location: {os.path.join(os.getcwd(), '.env')}")
