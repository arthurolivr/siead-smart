import pandas as pd
import pickle
from datetime import date, timedelta
from config import get_model_paths
from repositories.VendaRepository import fetch_revenue_for_day

_loaded_models = {}

def get_models(db_name: str):
    db_name_lower = db_name.lower()
    if db_name_lower not in _loaded_models:
        model_paths = get_model_paths(db_name_lower)
        try:
            with open(model_paths['short_term'], 'rb') as f:
                short_term = pickle.load(f)
            with open(model_paths['long_term'], 'rb') as f:
                long_term = pickle.load(f)
            _loaded_models[db_name_lower] = {"short_term": short_term, "long_term": long_term}
        except FileNotFoundError:
            raise RuntimeError(f"Modelos para '{db_name}' não encontrados. Execute o script de treino: python scripts/TrainModel.py --db {db_name_lower}")
    return _loaded_models[db_name_lower]

def _predict_single_db(target_date: date, db_name: str) -> float:
    models = get_models(db_name)
    previous_day_revenue = fetch_revenue_for_day(target_date - timedelta(days=1), db_name)
    
    features = pd.DataFrame({
        'day_of_week': [target_date.weekday()], 'day_of_month': [target_date.day],
        'month': [target_date.month], 'year': [target_date.year],
        'week_of_year': [target_date.isocalendar()[1]],
        'is_month_end': [1 if (target_date + timedelta(days=1)).month != target_date.month else 0],
        'previous_day_revenue': [previous_day_revenue]
    })
    
    prediction = models['short_term'].predict(features)
    return prediction.clip(min=0)[0]

def predict_daily_revenue(target_date: date, db_name: str) -> float:
    if db_name.upper() == 'TODOS':
        revenue_famart = _predict_single_db(target_date, 'FAMART')
        revenue_ipb = _predict_single_db(target_date, 'IPB')
        return revenue_famart + revenue_ipb
    else:
        return _predict_single_db(target_date, db_name)

def _summarize_single_db(days: int, db_name: str) -> dict:
    models = get_models(db_name)
    prophet_model = models['long_term']
    future = prophet_model.make_future_dataframe(periods=days)
    forecast = prophet_model.predict(future).tail(days)
    forecast['yhat'] = forecast['yhat'].clip(lower=0)
    
    return {
        "total_revenue": forecast['yhat'].sum(),
        "daily_average": forecast['yhat'].mean()
    }

def summarize_long_term_forecast(days: int, db_name: str) -> dict:
    if db_name.upper() == 'TODOS':
        summary_famart = _summarize_single_db(days, 'FAMART')
        summary_ipb = _summarize_single_db(days, 'IPB')
        
        total_revenue = summary_famart['total_revenue'] + summary_ipb['total_revenue']
        daily_average = summary_famart['daily_average'] + summary_ipb['daily_average']
        
        return {"total_revenue": total_revenue, "daily_average": daily_average}
    else:
        return _summarize_single_db(days, db_name)