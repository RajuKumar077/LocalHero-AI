"""
ai/gemini_client.py — Gemini API wrapper
"""

import os
import base64
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_MODEL_NAME = "gemini-2.5-flash"
_client_ready = False


def _init():
    global _client_ready
    if _client_ready:
        return
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Please add your key to the .env file."
        )
    genai.configure(api_key=api_key)
    _client_ready = True


def analyze_text_issue(issue_text: str) -> str:
    """Send a civic issue text to Gemini and return structured analysis."""
    _init()
    from ai.prompts import TEXT_ISSUE_PROMPT

    model = genai.GenerativeModel(_MODEL_NAME)
    prompt = TEXT_ISSUE_PROMPT.format(USER_INPUT=issue_text)

    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.2),
    )
    return response.text


def analyze_image_issue(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """Send an image to Gemini Vision and return structured analysis."""
    _init()
    from ai.prompts import IMAGE_ISSUE_PROMPT

    model = genai.GenerativeModel(_MODEL_NAME)
    image_part = {"mime_type": mime_type, "data": image_bytes}

    response = model.generate_content(
        [IMAGE_ISSUE_PROMPT, image_part],
        generation_config=genai.types.GenerationConfig(temperature=0.2),
    )
    return response.text


def generate_complaint_letter(
    issue: str, location: str, citizen_name: str = ""
) -> str:
    """Generate a formal complaint letter."""
    _init()
    from ai.prompts import COMPLAINT_PROMPT

    model = genai.GenerativeModel(_MODEL_NAME)
    prompt = COMPLAINT_PROMPT.format(
        ISSUE=issue,
        LOCATION=location,
        CITIZEN_NAME=citizen_name or "A Concerned Citizen",
    )
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.4),
    )
    return response.text


def answer_civic_question(question: str, context: str) -> str:
    """Answer a civic question using RAG-retrieved context."""
    _init()
    from ai.prompts import RAG_PROMPT

    model = genai.GenerativeModel(_MODEL_NAME)
    prompt = RAG_PROMPT.format(QUESTION=question, RETRIEVED_CONTEXT=context)
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.3),
    )
    return response.text
