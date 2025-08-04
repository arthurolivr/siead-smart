from datetime import date
from src.repositories.venda_repository import VendaRepository

# Cria a instância do repositório
repo = VendaRepository()

# Define a data que deseja testar
data_alvo = date(2025, 3, 31)

# Chama a função
resultado = repo.fetch_registration_fee_by_date(data_alvo, db_name="TODOS")  # o db_name não é usado nesse caso

# Exibe o resultado
print(resultado)