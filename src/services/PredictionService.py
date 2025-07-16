# src/siead_smart/services/PredictionService.py (CORRIGIDO)
import pandas as pd
import pickle
from datetime import date, timedelta
# MUDANÇA: Importações relativas para "subir um nível"
from ..config import SHORT_TERM_MODEL_PATH, LONG_TERM_MODEL_PATH
from ..repositories.VendaRepository import fetch_revenue_for_day

# ... (o resto do arquivo permanece o mesmo) ...
try:
    with open(SHORT_TERM_MODEL_PATH, 'rb') as f:
        short_term_model = pickle.load(f)
    with open(LONG_TERM_MODEL_PATH, 'rb') as f:
        prophet_model = pickle.load(f)
except FileNotFoundError as e:
    raise RuntimeError(f"Modelo não encontrado. Execute o script de treino primeiro. Erro: {e}")

def predict_daily_revenue(target_date: date) -> float:
    previous_day = target_date - timedelta(days=1)
    previous_day_revenue = fetch_revenue_for_day(previous_day)
    
    is_month_end_flag = 1 if (target_date + timedelta(days=1)).month != target_date.month else 0

    features = pd.DataFrame({
        'day_of_week': [target_date.weekday()],
        'day_of_month': [target_date.day],
        'month': [target_date.month],
        'year': [target_date.year],
        'week_of_year': [target_date.isocalendar()[1]],
        'is_month_end': [is_month_end_flag],
        'previous_day_revenue': [previous_day_revenue]
    })
    
    prediction = short_term_model.predict(features)
    return prediction.clip(min=0)[0]

def summarize_long_term_forecast(days_to_forecast: int) -> dict:
    future = prophet_model.make_future_dataframe(periods=days_to_forecast)
    forecast_df = prophet_model.predict(future).tail(days_to_forecast)
    
    forecast_df['yhat'] = forecast_df['yhat'].clip(lower=0)
    
    total_revenue = forecast_df['yhat'].sum()
    daily_average = forecast_df['yhat'].mean()
    
    return {
        "total_revenue": total_revenue,
        "daily_average": daily_average
    }