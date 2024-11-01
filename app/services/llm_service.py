import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key = os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

async def get_llm_response(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text
