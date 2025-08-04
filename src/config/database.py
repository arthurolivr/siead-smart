import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseConnection:
    def __init__(self, prefix="DB1_"):
        self.prefix = prefix
        self.connection = None

    def connect(self):
        if self.connection is None or not self.connection.is_connected():
            self.connection = mysql.connector.connect(
                host=os.getenv(f"{self.prefix}HOST"),
                port=int(os.getenv(f"{self.prefix}PORT")),
                user=os.getenv(f"{self.prefix}USER"),
                password=os.getenv(f"{self.prefix}PASSWORD") or None,
                database=os.getenv(f"{self.prefix}DATABASE"),
                ssl_disabled=True
            )
        return self.connection

db_connection_1 = DatabaseConnection(prefix="DB1_")
db_connection_2 = DatabaseConnection(prefix="DB2_")