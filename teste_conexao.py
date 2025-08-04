import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv("DB1_HOST"),
        port=int(os.getenv("DB1_PORT")),
        user=os.getenv("DB1_USER"),
        password=os.getenv("DB1_PASSWORD") or None,
        database=os.getenv("DB1_DATABASE"),
        ssl_disabled=True
    )
    print("✅ Conexão MySQL bem-sucedida!")
    conn.close()
except mysql.connector.Error as err:
    print("❌ Erro ao conectar no MySQL:")
    print(err)
