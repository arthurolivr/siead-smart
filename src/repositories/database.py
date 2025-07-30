from sqlalchemy import create_engine
from urllib.parse import quote_plus
from config import get_database_config

def get_db_engine(db_name: str):
    
    db_config = get_database_config(db_name)
    
    password = db_config.get('password')
    if password is None:

        raise ValueError(f"A senha para o banco de dados '{db_name}' não foi configurada no arquivo .env.")

    password_encoded = quote_plus(password)
    
    db_url = (
        f"mysql+mysqlconnector://{db_config['user']}:{password_encoded}@"
        f"{db_config['host']}/{db_config['database']}"
    )
    
    return create_engine(db_url)