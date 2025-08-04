import os
from dotenv import load_dotenv

load_dotenv()

def get_llm_api_key(provider: str) -> str:
    if provider.upper() == "GOOGLE":
        return os.getenv("GOOGLE_API_KEY")
    return None