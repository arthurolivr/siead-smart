from datetime import date
from src.repositories.venda_repository import VendaRepository
from src.utils.logger import get_logger

logger = get_logger("deploy")

# Cria a instância do repositório
repo = VendaRepository()

# Define a data que deseja testar
data_inicio = date(2025, 3, 31)
data_fim = date(2025, 3, 31)

logger.info(">>> INÍCIO DA EXECUÇÃO <<<")

# TESTE
#resultado = repo.fetch_all_sales('TODOS')
# Chama a função
resultado = repo.fetch_registration_fee_by_date(data_inicio, data_fim, db_name="TODOS")  # o db_name não é usado nesse caso

logger.info("result: %s", resultado)

# Exibe o resultado
print(repr(resultado))