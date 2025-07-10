import pandas as pd
import pickle
import os
from datetime import date, timedelta
import xgboost

MODELS_DIR = 'models'

try:
    with open(os.path.join(MODELS_DIR, 'decision_tree_model.pkl'), 'rb') as f:
        short_term_model = pickle.load(f)
    with open(os.path.join(MODELS_DIR, 'prophet_model.pkl'), 'rb') as f:
        prophet_model = pickle.load(f)
except FileNotFoundError:
    raise RuntimeError(f"ERRO: Modelos não encontrados em '{MODELS_DIR}'. Execute 'train.py' primeiro.")

def prever_faturamento_diario(data_str: str) -> str:
    
    try:
        data_alvo = date.fromisoformat(data_str)
    except ValueError:
        return "Formato de data inválido. Por favor, use 'AAAA-MM-DD'."
        
    venda_dia_anterior_estimada = 35000 
    eh_fim_de_mes_flag = 1 if (data_alvo + timedelta(days=1)).month != data_alvo.month else 0

    features = pd.DataFrame({
        'dia_da_semana': [data_alvo.weekday()], 'dia_do_mes': [data_alvo.day],
        'mes': [data_alvo.month], 'ano': [data_alvo.year],
        'semana_do_ano': [data_alvo.isocalendar()[1]],
        'eh_fim_de_mes': [eh_fim_de_mes_flag],
        'venda_dia_anterior': [venda_dia_anterior_estimada]
    })
    previsao = short_term_model.predict(features)
    valor_final = previsao.clip(min=0)[0]
    return f"A previsão de faturamento para {data_alvo.strftime('%d/%m/%Y')} é de R$ {valor_final:,.2f}."

def resumir_previsao_longo_prazo(dias_a_prever: int) -> str:
    futuro = prophet_model.make_future_dataframe(periods=dias_a_prever)
    previsao_df = prophet_model.predict(futuro).tail(dias_a_prever)
    previsao_df['yhat'] = previsao_df['yhat'].clip(lower=0)
    previsao_df['yhat_upper'] = previsao_df['yhat_upper'].clip(lower=0)
    
    faturamento_total = previsao_df['yhat'].sum()
    media_diaria = previsao_df['yhat'].mean()
    
    return f"Para os próximos {dias_a_prever} dias, a previsão é de um faturamento total de R$ {faturamento_total:,.2f}, com uma média diária de R$ {media_diaria:,.2f}."