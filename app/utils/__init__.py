import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection_string():
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    return f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}"
