"""
groq_client.py

Handles communication with the Groq LLM.
"""

import os

from dotenv import load_dotenv
from groq import Groq

from src.config import GROQ_MODEL

from src.utils.logger import get_logger

logger = get_logger(__name__)   

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found. Please add it to your .env file."
    )

client = Groq(api_key=API_KEY)

def generate_response(prompt: str) -> str:
    """
    Send a prompt to Groq and return the generated response.
    """

    logger.info("Sending request to Groq API")

    try:

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=700,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are FinSight AI, an expert financial analyst. "
                        "Explain predictions using financial reasoning and "
                        "academic evidence. Never invent facts."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

    except Exception:

        logger.exception(
            "Groq API request failed (model: llama-3.3-70b-versatile)"
        )

        raise

    if not completion.choices:

        logger.error("Groq returned an empty response")

        raise ValueError(
            "Groq returned no completion."
        )

    try:

        output = completion.choices[0].message.content

    except Exception:

        logger.exception(
            "Failed to parse Groq response"
        )

        raise

    logger.info("Groq response parsed successfully")

    return output


if __name__ == "__main__":

    response = generate_response(
        "Explain why moving averages are useful in stock forecasting."
    )

    print(response)