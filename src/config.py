import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

MODELS_DIR = 'models'

SHORT_TERM_MODEL_PATH = os.path.join(MODELS_DIR, 'short_term_model.pkl')
LONG_TERM_MODEL_PATH = os.path.join(MODELS_DIR, 'prophet_model.pkl')

def get_database_config():
    """
    Lê o arquivo .env para determinar o banco de dados ativo (FAMART ou IPB)
    e retorna um dicionário com as credenciais corretas.
    """
    active_db_name = os.getenv("ACTIVE_DB", "FAMART").upper()
    prefix = active_db_name

    db_config = {
        "user": os.getenv(f"{prefix}_DB_USER"),
        "password": os.getenv(f"{prefix}_DB_PASSWORD"),
        "host": os.getenv(f"{prefix}_DB_HOST"),
        "database": os.getenv(f"{prefix}_DB_NAME"),
    }

    #if not all(db_config.values()):
    #    raise ValueError(f"Configurações de banco de dados para '{prefix}' estão incompletas no arquivo .env")
        
    return db_config

def get_llm_api_key(provider: str = "GOOGLE") -> str | None:
    """
    Busca a chave de API do provedor de LLM especificado (ex: GOOGLE, OPENAI)
    a partir das variáveis de ambiente ou do arquivo .env.
    """
    api_key = os.getenv(f"{provider.upper()}_API_KEY")
    if not api_key:
        print(f"AVISO: Chave de API para {provider} não encontrada no ambiente.")
    return api_key