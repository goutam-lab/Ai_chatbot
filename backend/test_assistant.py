import asyncio
from app.services.openai_service import get_assistant_response

async def test_assistant():
    user_message = "Find me restaurants in Banashankari."
    response = await get_assistant_response(user_message)
    print("Assistant Response:", response)

if __name__ == "__main__":
    asyncio.run(test_assistant())
