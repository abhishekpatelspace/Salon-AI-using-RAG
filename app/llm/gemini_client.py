import os
from typing import Iterable

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.llm.prompt import build_prompt

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def ask_gemini(
    message: str,
    context_chunks: Iterable[str] | None = None,
    memory_lines: Iterable[str] | None = None,
) -> str:
    if not GEMINI_API_KEY:
        print("[SalonAI] GEMINI_API_KEY is not configured.")
        return "SalonAI is temporarily unavailable. Please try again shortly or contact the salon directly."

    try:
        prompt = build_prompt(
            user_message=message,
            context_chunks=context_chunks,
            memory_lines=memory_lines,
        )

        client = genai.Client(api_key=GEMINI_API_KEY)
        
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
            ),
        )

        if response.text:
            return response.text.strip()
        
        return "SalonAI could not process your request right now. Please try again."

    except Exception as e:
        print(f"[SalonAI] Gemini API error: {e}")
        return "I'm sorry, SalonAI encountered an issue. Please try again later or contact the salon for assistance."
