import sys
import os
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.siead_smart.repositories.sales_repository import fetch_all_sales

try:
    print("Starting model validation process...")
    
    # --- 1. Carregar Dados Usando a Camada de Dados ---
    print("Fetching historical data from the data layer...")
    df = fetch_all_sales()
    print("Data fetched successfully.")

    # --- 2. Preparar Dados e Criar Features ---
    df['sale_date'] = pd.to_datetime(df['data_venda'])
    daily_df = df.groupby('sale_date')['valor_total'].sum().to_frame(name='total_revenue')
    
    regression_df = daily_df.copy()
    assert isinstance(regression_df.index, pd.DatetimeIndex)

    regression_df['day_of_week'] = regression_df.index.dayofweek
    regression_df['day_of_month'] = regression_df.index.day
    regression_df['month'] = regression_df.index.month
    regression_df['year'] = regression_df.index.year
    regression_df['week_of_year'] = regression_df.index.isocalendar().week.astype(int)
    regression_df['is_month_end'] = regression_df.index.is_month_end.astype(int)
    regression_df['previous_day_revenue'] = regression_df['total_revenue'].shift(1).fillna(0)

    # --- 3. Separar Dados para Treino e Teste ---
    days_to_test = 30
    train_data = regression_df[:-days_to_test]
    test_data = regression_df[-days_to_test:]

    print(f"\nUsing {len(train_data)} days to train the model.")
    print(f"Using {len(test_data)} days to validate the prediction.")

    X_train = train_data.drop('total_revenue', axis=1)
    y_train = train_data['total_revenue']
    X_test = test_data.drop('total_revenue', axis=1)
    y_real = test_data['total_revenue']

    # --- 4. Treinar o Modelo XGBoost Otimizado ---
    print("\nTraining a temporary optimized XGBoost model...")
    temp_model = XGBRegressor(
        n_estimators=1000,
        learning_rate=0.01,
        early_stopping_rounds=5, # Parada antecipada para otimização
        random_state=42
    )
    temp_model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_real)],
        verbose=False # Mantém o terminal limpo
    )

    # --- 5. Fazer Previsões e Avaliar ---
    print("Making predictions for the test period...")
    y_predicted = temp_model.predict(X_test)
    y_predicted = y_predicted.clip(min=0) # Garante que não haja previsões negativas

    print("\n--- REFINED MODEL EVALUATION ---")
    validation_df = pd.DataFrame({'Real': y_real, 'Predicted': y_predicted}, index=y_real.index)
    validation_df['Difference'] = validation_df['Real'] - validation_df['Predicted']
    validation_df['Difference_%'] = (validation_df['Difference'] / validation_df['Real']).replace([float('inf'), -float('inf')], 0) * 100

    mae = mean_absolute_error(y_real, y_predicted)
    print(f"\nThe model's Mean Absolute Error (MAE) is: R$ {mae:,.2f}")
    print("This means, on average, the model's predictions are off by this amount.")

    print("\nVisualizing the first 10 days of validation:")
    print(validation_df.head(10))

    # --- 6. Gerar Gráfico de Comparação ---
    print("\nGenerating comparison plot...")
    plt.figure(figsize=(15, 7))
    plt.plot(validation_df.index, validation_df['Real'], label='Actual Revenue', marker='o', linestyle='-')
    plt.plot(validation_df.index, validation_df['Predicted'], label='Predicted Revenue', marker='x', linestyle='--')
    plt.title('Optimized Model Validation: Actual vs. Predicted Revenue (Last 30 Days)')
    plt.ylabel('Revenue (R$)')
    plt.xlabel('Date')
    plt.legend()
    plt.grid(True)
    plt.show()

except Exception as e:
    print(f"\nFATAL ERROR DURING VALIDATION: {e}")
    sys.exit(1)