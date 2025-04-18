import os
import logging
from openai import AsyncOpenAI
from typing import Optional
import asyncio

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.timeout = 60  # Increased from default 30 seconds
        self.logger = logging.getLogger(__name__)

    async def process_message(self, message: str) -> Optional[str]:
        try:
            response = await asyncio.wait_for(
                self._call_openai(message),
                timeout=self.timeout
            )
            return response
        except asyncio.TimeoutError:
            self.logger.error("OpenAI request timed out")
            raise
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            raise

    async def _call_openai(self, message: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise

    # Include other existing methods as needed
