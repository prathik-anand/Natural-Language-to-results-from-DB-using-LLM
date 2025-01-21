import psycopg2
import openai
from dotenv import load_dotenv
import os
import re

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

print("OpenAI API Key:", openai.api_key)

# Global cache to store the database schema
SCHEMA_CACHE = None


load_dotenv()

# Database configuration from .env
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

def fetch_schema_from_db(connection_string):
    """
    Fetch the schema from the PostgreSQL database.
    
    Args:
        connection_string: Connection string for the PostgreSQL database.

    Returns:
        A dictionary representation of the database schema.
    """
    schema = {}
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            # Retrieve all table names
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE';
            """)
            tables = cur.fetchall()

            for table in tables:
                table_name = table[0]
                # Retrieve columns and their data types for each table
                cur.execute(f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = %s;
                """, (table_name,))
                schema[table_name] = cur.fetchall()
    return schema

def load_schema(connection_string):
    """
    Load the schema from the database and cache it globally.

    Args:
        connection_string: Connection string for the PostgreSQL database.

    Returns:
        The cached schema.
    """
    global SCHEMA_CACHE
    SCHEMA_CACHE = fetch_schema_from_db(connection_string)
    return SCHEMA_CACHE

def get_schema(connection_string):
    """
    Retrieve the cached schema, or load it if not already cached.

    Args:
        connection_string: Connection string for the PostgreSQL database.

    Returns:
        The cached schema.
    """
    global SCHEMA_CACHE
    if SCHEMA_CACHE is None:
        return load_schema(connection_string)
    return SCHEMA_CACHE

def reload_schema(connection_string):
    """
    Reload the schema from the database and update the cache.

    Args:
        connection_string: Connection string for the PostgreSQL database.

    Returns:
        The updated schema.
    """
    return load_schema(connection_string)

def generate_sql_query(natural_language_query, schema):
    """
    Generate a SQL query from a natural language query using OpenAI's API.

    Args:
        natural_language_query: The input natural language query.
        schema: The database schema information.

    Returns:
        A SQL query based on the input query and schema.
    """
    # Prepare the prompt with schema context
    schema_description = "\n".join(
        f"Table: {table}\nColumns: {', '.join([f'{col[0]} ({col[1]})' for col in columns])}"
        for table, columns in schema.items()
    )
    prompt = f"""
    You are an expert SQL assistant. Below is the database schema:
    {schema_description}

    Convert the following natural language query into a valid PostgreSQL SQL query:
    "{natural_language_query}"

    Ensure the SQL is syntactically correct and follows best practices.
    """

    # Call OpenAI's GPT model
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant specialized in SQL."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

def execute_sql_query(connection_string, query):
    """
    Execute a SQL query on the PostgreSQL database and fetch results.

    Args:
        connection_string: Connection string for the PostgreSQL database.
        query: The SQL query to execute.

    Returns:
        The query results, or an error message if execution fails.
    """
    try:
        with psycopg2.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                if cur.description:  # Check if query returns rows
                    return cur.fetchall()
                return "Query executed successfully, no rows returned."
    except Exception as e:
        return f"Error executing query: {e}"

def extract_sql_from_llm_response(llm_response):
    """
    Extracts the SQL query from an LLM response.

    Parameters:
        llm_response (str): The text response from the LLM.

    Returns:
        str: The extracted SQL query, or None if no query is found.
    """
    # Regular expression to extract SQL query
    sql_query_pattern = r"``` *sql\n(.*?)\n```"

    # Perform regex search
    matches = re.finditer(sql_query_pattern, llm_response, re.DOTALL)
    
    # Return the first match or None
    for match in matches:
        return match.group(1)
    return None

if __name__ == "__main__":
    # Configuration
    CONNECTION_STRING = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"

    # Step 1: Load Schema
    print("Loading schema...")
    schema = get_schema(CONNECTION_STRING)
    print("Schema loaded successfully.")

    # Step 2: Generate SQL Query
    natural_language_query = "Show me all customers who placed orders in the last 30 days."
    print(f"Natural Language Query: {natural_language_query}")

    llm_response = generate_sql_query(natural_language_query, schema)
    print(f"Generated LLM response:\n{llm_response}")
    
    #extract sql
    sql_query=extract_sql_from_llm_response(llm_response)
    print(f"Generated SQL query{sql_query}")

    # Step 3: Execute SQL Query
    print("Executing SQL query...")
    results = execute_sql_query(CONNECTION_STRING, llm_response)
    print(f"Query Results:\n{results}")

    # Step 4: Reload Schema (if necessary)
    print("Reloading schema...")
    schema = reload_schema(CONNECTION_STRING)
    print("Schema reloaded successfully.")
