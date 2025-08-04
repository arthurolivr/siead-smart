class BaseRepository:
    def __init__(self, connection_getter):
        self.connection_getter = connection_getter

    def execute_query(self, query, params=None):
        conn = self.connection_getter()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            cursor.close()