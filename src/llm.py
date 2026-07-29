import os

from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_groq import ChatGroq

load_dotenv()


def get_llm():

    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=SecretStr(os.getenv("GROQ_API_KEY")),
        temperature=0.1,
        max_tokens=1024,
    )