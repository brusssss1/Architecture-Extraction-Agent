# llm_client.py
from openai import AsyncOpenAI

def create_groq_client(api_key: str) -> AsyncOpenAI:
    """Tạo client Groq (tương thích OpenAI)."""
    return AsyncOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

def create_deepseek_client(api_key: str) -> AsyncOpenAI:
    """Tạo client DeepSeek (cũng tương thích OpenAI)."""
    return AsyncOpenAI(
        base_url="https://api.deepseek.com/v1",
        api_key=api_key
    )