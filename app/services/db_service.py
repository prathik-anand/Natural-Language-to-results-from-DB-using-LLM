import psycopg2

def execute_sql_query(connection_string, query):
    try:
        with psycopg2.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                if cur.description:  # Check if query returns rows
                    return cur.fetchall()
                return "Query executed successfully, no rows returned."
    except Exception as e:
        return f"Error executing query: {e}"
