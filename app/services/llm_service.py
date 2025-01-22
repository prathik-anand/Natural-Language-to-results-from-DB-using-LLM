import openai
import re
from .schema_service import get_schema
from app.utils import get_db_connection_string
from .db_service import execute_sql_query as execute_query

def is_safe_query(query):
    """Check if query is read-only"""
    # Convert to uppercase for case-insensitive matching
    query_upper = query.upper()
    
    # List of forbidden SQL operations
    forbidden_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 
        'CREATE', 'ALTER', 'GRANT', 'EXECUTE', 'MERGE'
    ]
    
    # Check for forbidden keywords
    for keyword in forbidden_keywords:
        if keyword in query_upper:
            return False
            
    # Ensure query starts with SELECT
    if not query_upper.strip().startswith('SELECT'):
        return False
        
    return True

def get_results(natural_language_query):
    sql=generate_sql_query(natural_language_query, get_schema(get_db_connection_string()))
    db_results=execute_query(get_db_connection_string(), sql)
    summary=generate_insights(natural_language_query, sql, db_results)
    return summary


def generate_sql_query(natural_language_query, schema):
    schema_description = "\n".join(
        f"Table: {table}\nColumns: {', '.join([f'{col[0]} ({col[1]})' for col in columns])}"
        for table, columns in schema.items()
    )
    prompt = f"""
    You are an expert SQL assistant that ONLY generates READ-ONLY queries.
    Important: Only generate SELECT queries. Do not generate any INSERT, UPDATE, DELETE or other modifying queries.

    Database schema:
    {schema_description}

    Convert this query into a READ-ONLY PostgreSQL SELECT query:
    "{natural_language_query}"
    Note: if query is out of schema, don't just try to make up answer instead say only "User query is out of schema"
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a READ-ONLY SQL assistant. Never generate queries that modify data."},
            {"role": "user", "content": prompt}
        ]
    )
    response_message=response['choices'][0]['message']['content'].strip()
    if(response_message in "User query is out of schema"):
        raise ValueError("Query cannot be processed by system")
    return extract_sql_from_llm_response(response_message)



def extract_sql_from_llm_response(llm_response):
    sql_query_pattern = r"``` *sql\n(.*?)\n```"
    matches = re.finditer(sql_query_pattern, llm_response, re.DOTALL)
    for match in matches:
        sql_query = match.group(1)
        # Validate query is read-only before returning
        if is_safe_query(sql_query):
            return sql_query
        else:
            raise ValueError("Generated query contains unsafe operations")
    return None

def generate_insights(user_query, sql_query, results):
    prompt = f"""
    Analyze this database query and results of it and provide summary for user based on Original User Question and Query Results, make sure to give answer for non technical person and Don't mention anything about sql query in your response, just try to answer in terms of Original User Question:
    
    Original User Question: {user_query}
    SQL Query Used: {sql_query}
    Query Results: {results}
    
    Keep response clear and concise.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a data analyst providing insights from SQL query results."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']