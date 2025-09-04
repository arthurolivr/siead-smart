from datetime import date, timedelta
from src.services.commercial_analysis_service import CommercialAnalysisService
import pprint

pp = pprint.PrettyPrinter(indent=4)

# Crie uma instância do serviço
service = CommercialAnalysisService()

print("\n--- Testando o Serviço de Análise Comercial ---")
analysis_result = service.get_enrollment_analysis(
    date_start=date.today() - timedelta(days=90),
    date_end=date.today(),
    db_name="TODOS"
    # Você também pode testar os filtros aqui:
    # team="Equipe Comercial Gold"
)

print("Resultado da análise estruturada:")
pp.pprint(analysis_result)