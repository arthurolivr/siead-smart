import pandas as pd
from datetime import date
from src.repositories.venda_repository import VendaRepository
import unicodedata

def strip_accents(text: str) -> str:
    """Remove acentos de uma string."""
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

class CommercialAnalysisService:
    def __init__(self):
        self.venda_repo = VendaRepository()

    def get_enrollment_summary(self, date_start: date, date_end: date, db_name: str) -> dict:
        raw_data = self.venda_repo.fetch_enrollment_data(date_start, date_end, db_name, group_by=None)
        if not raw_data:
            return {"total_quantity": 0, "total_value": 0}
        df = pd.DataFrame(raw_data)
        return {
            "total_quantity": len(df),
            "total_value": df['value'].sum()
        }

    def get_performance_ranking(self, date_start: date, date_end: date, db_name: str, group_by: str) -> pd.DataFrame:
        result = self.venda_repo.fetch_enrollment_data(date_start, date_end, db_name, group_by=group_by)
        # Tratar equipes nulas (sem nome)
        df = pd.DataFrame(result)
        if 'name' in df.columns:
            df['name'] = df['name'].fillna('Equipe sem nome')
        return df

    def get_payment_breakdown(self, date_start: date, date_end: date, db_name: str) -> pd.DataFrame:
        result = self.venda_repo.fetch_enrollment_data(date_start, date_end, db_name, group_by="payment_method")
        df = pd.DataFrame(result)
        
        if not df.empty:
            def categorize_payment(method):
                # Remove acentos e converte para maiúsculas para uma comparação robusta
                method_normalized = strip_accents(method.upper())
                if 'PIX' in method_normalized: return 'PIX'
                if 'CARTAO' in method_normalized: return 'Cartão' # Agora compara com 'CARTAO'
                if 'BOLETO' in method_normalized: return 'Boleto'
                return 'Outros'

            df['category'] = df['name'].apply(categorize_payment)
            summary = df.groupby('category').agg(
                quantity=('quantity', 'sum'),
                total_value=('total_value', 'sum')
            ).reset_index().rename(columns={'category': 'name'})
            return summary
            
        return df