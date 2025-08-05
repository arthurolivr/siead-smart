class BaseRepository:
    def __init__(self, connection_getter):
        self.connection_getter = connection_getter

    def execute_query(self, query, params=None):
        try:
            conn = self.connection_getter()
        except Exception as e:
            print(f"Erro ao obter conexão: {e}")
            raise  # Relevante para continuar a propagar a exceção, se necessário
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            cursor.close()