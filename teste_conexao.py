from dotenv import load_dotenv
import os

try:
    import pymysql as mysql
except ImportError:
    import mysql.connector as mysql

load_dotenv()

try:
    conn = mysql.connect(
        host=os.getenv("DB1_HOST"),
        port=int(os.getenv("DB1_PORT")),
        user=os.getenv("DB1_USER"),
        password=os.getenv("DB1_PASSWORD") or None,
        database=os.getenv("DB1_DATABASE"),
        ssl_disabled=True
    )

    print("✅ Conexão MySQL bem-sucedida!")
    conn.close()
except Exception as err:
    print("❌ Erro ao conectar no MySQL:")
    print(err)
