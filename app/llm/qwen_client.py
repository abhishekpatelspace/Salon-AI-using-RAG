import json
import os
import urllib.request
import urllib.error
from typing import Iterable

from dotenv import load_dotenv

from app.llm.prompt import build_prompt

load_dotenv()

QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1").rstrip("/")
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")


def ask_qwen(
    message: str,
    context_chunks: Iterable[str] | None = None,
    memory_lines: Iterable[str] | None = None,
) -> str:
    if not QWEN_API_KEY:
        print("[SalonAI] QWEN_API_KEY is not configured.")
        return "SalonAI is temporarily unavailable. Please try again shortly or contact the salon directly."

    try:
        prompt = build_prompt(
            user_message=message,
            context_chunks=context_chunks,
            memory_lines=memory_lines,
        )

        payload = {
            "model": QWEN_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
        }

        url = f"{QWEN_BASE_URL}/chat/completions"
        data = json.dumps(payload).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {QWEN_API_KEY}"
        }

        req = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                choices = res_json.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
                return "SalonAI could not process your request right now. Please try again."
            else:
                print(f"[SalonAI] Qwen API returned status code: {response.status}")
                return "SalonAI is temporarily unavailable. Please try again shortly."

    except urllib.error.URLError as e:
        print(f"[SalonAI] Failed to connect to Qwen API at {QWEN_BASE_URL}: {e}")
        return "I'm sorry, SalonAI could not connect to the AI service. Please check your internet connection."
    except Exception as e:
        print(f"[SalonAI] Internal error: {e}")
        return "I'm sorry, SalonAI encountered an issue. Please try again later or contact the salon for assistance."
