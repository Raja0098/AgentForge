# backend/services/gemini.py
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment")

genai_client = genai.Client(api_key=GEMINI_API_KEY)


def gemini_generate(prompt: str) -> str:
    """
    Call Gemini API with a prompt and return the response text.
    """
    try:
        response = genai_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"
