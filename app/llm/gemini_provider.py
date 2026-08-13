from google import genai
from google.genai import types

from app.config import settings
from app.llm.base import LLMProvider


class GeminiProvider(LLMProvider):

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. "
                "Add it to the .env file."
            )

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.model = settings.llm_model

    def generate(
        self,
        *,
        instructions: str,
        prompt: str,
    ) -> str:

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=instructions,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text.strip()