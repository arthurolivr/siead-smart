import pandas as pd
from sqlalchemy import create_engine 
from urllib.parse import quote_plus 
from xgboost import XGBRegressor
from prophet import Prophet
import pickle
import os
import sys

# --- Bloco de Configuração ---
DB_CONFIG = {
    'host': 'localhost',
    'database': 'famart',
    'user': 'root',
    'password': '!F@mart+'
}
MODELS_DIR = 'models' 

engine = None 
try:
    print("Iniciando o processo de treinamento...")
    
    print("Conectando ao banco de dados com SQLAlchemy...")
    
    password_encoded = quote_plus(DB_CONFIG['password'])
    db_url = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{password_encoded}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    
    engine = create_engine(db_url)
    
    query = "SELECT data_venda, valor_total FROM venda" 
    df = pd.read_sql(query, engine) 
    print("Dados carregados. Preparando features...")

    df['data_venda'] = pd.to_datetime(df['data_venda'])
    df_diario = df.groupby('data_venda')['valor_total'].sum().to_frame()

    # --- Engenharia de Features (completa) ---
    df_reg = df_diario.copy()
    assert isinstance(df_reg.index, pd.DatetimeIndex)
    df_reg['dia_da_semana'] = df_reg.index.dayofweek
    df_reg['dia_do_mes'] = df_reg.index.day
    df_reg['mes'] = df_reg.index.month
    df_reg['ano'] = df_reg.index.year
    df_reg['semana_do_ano'] = df_reg.index.isocalendar().week.astype(int)
    df_reg['eh_fim_de_mes'] = df_reg.index.is_month_end.astype(int) 
    df_reg['venda_dia_anterior'] = df_reg['valor_total'].shift(1).fillna(0)

    # --- Treinar o Modelo de Curto Prazo (XGBoost Otimizado) ---
    print("\n--- Treinando Modelo de Curto Prazo (XGBoost) ---")
    X = df_reg.drop('valor_total', axis=1)
    y = df_reg['valor_total']

    short_term_model = XGBRegressor(
        n_estimators=500,
        learning_rate=0.01,
        random_state=42
    )
    short_term_model.fit(X, y)
    print("Modelo de Curto Prazo (XGBoost) treinado.")

    # --- Treinamento do Prophet ---
    print("\n--- Treinando Modelo de Longo Prazo (Prophet) ---")
    df_prophet = df_diario.reset_index().rename(columns={'data_venda': 'ds', 'valor_total': 'y'})
    prophet_model = Prophet(daily_seasonality=True) # type: ignore
    prophet_model.add_country_holidays(country_name='BR')
    prophet_model.fit(df_prophet)
    print("Modelo Prophet treinado.")

    # --- Salvar os Modelos no Disco ---
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)

    with open(os.path.join(MODELS_DIR, 'decision_tree_model.pkl'), 'wb') as f:
        pickle.dump(short_term_model, f)
    print("Modelo de Curto Prazo (XGBoost) salvo em 'models/'.")

    with open(os.path.join(MODELS_DIR, 'prophet_model.pkl'), 'wb') as f:
        pickle.dump(prophet_model, f)
    print("Modelo Prophet salvo em 'models/'.")

    print("\nProcesso de treinamento concluído!")

except Exception as e:
    print(f"\nERRO FATAL: {e}")
    sys.exit(1)
finally:
    if engine:
        engine.dispose()
        print("Conexão com o banco de dados encerrada.")