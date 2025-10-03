import os
from dotenv import load_dotenv

load_dotenv()

def get_llm_api_key(provider: str) -> str | None:
    """Busca a chave de API correta com base no provedor solicitado."""
    provider_upper = provider.upper()
    
    if provider_upper == "GOOGLE":
        return os.getenv("GOOGLE_API_KEY")
    if provider_upper == "OPENROUTER":
        return os.getenv("OPENROUTER_API_KEY")
    if provider_upper == "AIMLAPI":
        return os.getenv("AIMLAPI_API_KEY")
    
    if provider_upper == "DEEPSEEK":
        return os.getenv("DEEPSEEK_API_KEY")
       
    return None