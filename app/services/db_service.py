import psycopg2
import logging

logger = logging.getLogger(__name__)

def execute_sql_query(connection_string, query):
    try:
        logging.info(f"Executing query: {query}")
        with psycopg2.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                if cur.description:  # Check if query returns rows
                    logging.info("Query executed successfully, returning rows.")
                    return cur.fetchall()
                logging.info("Query executed successfully, no rows returned.")
                return "Query executed successfully, no rows returned."
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return f"Error executing query: {e}"
