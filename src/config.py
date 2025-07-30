import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def get_database_config(db_name: str):
    """Retorna um dicionário com as configurações de conexão para o banco especificado."""
    prefix = db_name.upper()
    db_config = {
        "user": os.getenv(f"{prefix}_DB_USER"),
        "password": os.getenv(f"{prefix}_DB_PASSWORD"),
        "host": os.getenv(f"{prefix}_DB_HOST"),
        "database": os.getenv(f"{prefix}_DB_NAME"),
    }
    if not all(value is not None for value in db_config.values()):
        raise ValueError(f"Configurações para o banco '{prefix}' estão incompletas no .env")
    return db_config

def get_llm_api_key(provider: str = "GOOGLE") -> str | None:
    api_key = os.getenv(f"{provider.upper()}_API_KEY")
    if not api_key:
        print(f"AVISO: Chave de API para {provider} não encontrada.")
    return api_key

def get_model_paths(db_name: str):
    """CRÍTICO: Retorna os caminhos para os arquivos de modelo em subpastas específicas para cada DB."""
    models_dir = os.path.join('models', db_name.lower())
    return {
        "short_term": os.path.join(models_dir, 'short_term_model.pkl'),
        "long_term": os.path.join(models_dir, 'prophet_model.pkl')
    }