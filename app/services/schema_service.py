import psycopg2
from app.utils.helpers import cache_data

SCHEMA_CACHE = None

def fetch_schema_from_db(connection_string):
    schema = {}
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """)
            tables = cur.fetchall()

            for table in tables:
                table_name = table[0]
                cur.execute(f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = %s;
                """, (table_name,))
                schema[table_name] = cur.fetchall()
    return schema

@cache_data
def get_schema(connection_string):
    global SCHEMA_CACHE
    if SCHEMA_CACHE is None:
        SCHEMA_CACHE = fetch_schema_from_db(connection_string)
    return SCHEMA_CACHE

def reload_schema(connection_string):
    global SCHEMA_CACHE
    SCHEMA_CACHE = fetch_schema_from_db(connection_string)
    return SCHEMA_CACHE
