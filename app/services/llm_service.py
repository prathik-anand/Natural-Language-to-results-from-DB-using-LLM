import logging
import openai
import re
from .schema_service import get_schema
from app.utils import get_db_connection_string
from .db_service import execute_sql_query as execute_query
from ..exceptions.exceptions import LLMServiceError, ValidationError

logger = logging.getLogger(__name__)

def is_safe_query(query):
    """Check if query is read-only"""
    if not query:
        logger.error("Empty query provided")
        raise ValidationError("Empty query provided")
        
    query_upper = query.upper()
    forbidden_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 
        'CREATE', 'ALTER', 'GRANT', 'EXECUTE', 'MERGE'
    ]
    
    for keyword in forbidden_keywords:
        if keyword in query_upper:
            logger.warning(f"Forbidden operation in query: {keyword}")
            raise ValidationError(f"Query contains forbidden operation: {keyword}")
            
    if not query_upper.strip().startswith('SELECT'):
        logger.warning("Only SELECT queries are allowed")
        raise ValidationError("Only SELECT queries are allowed")
        
    return True

def get_results(natural_language_query):
    """Main pipeline for processing natural language queries"""
    try:
        if not natural_language_query:
            logger.error("Empty query provided")
            raise ValidationError("Empty query provided")
            
        schema = get_schema(get_db_connection_string())
        sql = generate_sql_query(natural_language_query, schema)
        
        if not sql:
            logger.error("Failed to generate SQL query")
            raise LLMServiceError("Failed to generate SQL query")
            
        db_results = execute_query(get_db_connection_string(), sql)
        summary = generate_insights(natural_language_query, sql, db_results)
        
        if not summary:
            raise LLMServiceError("Failed to generate insights")
            
        return {
            "sql_query": sql,
            "insights": summary,
            "results": db_results
        }
        
    except Exception as e:
        logger.error(f"Error in get_results: {str(e)}", exc_info=True)
        if isinstance(e, (ValidationError, LLMServiceError)):
            raise e
        raise LLMServiceError("Failed to process query", original_error=e)
    
    
def generate_sql_query(natural_language_query, schema):
    """Generate SQL query from natural language"""
    try:
        if not natural_language_query or not schema:
            logging.error("Query or schema missing for SQL generation")
            raise ValidationError("Query and schema are required")
            
        schema_description = "\n".join(
            f"Table: {table}\nColumns: {', '.join([f'{col[0]} ({col[1]})' for col in columns])}"
            for table, columns in schema.items()
        )
        
        prompt = f"""
        You are an expert SQL assistant that ONLY generates READ-ONLY queries.
        Important: Only generate SELECT queries. No modifying queries allowed.
        
        Database schema:
        {schema_description}
        
        Convert this query into a READ-ONLY PostgreSQL SELECT query:
        "{natural_language_query}"
        Note: if query is out of schema, respond only with "User query is out of schema"
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a READ-ONLY SQL assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = response['choices'][0]['message']['content'].strip()
        if "User query is out of schema" in response_text:
            logging.warning("Query out of schema")
            raise ValidationError("Query cannot be processed with current schema")
            
        sql = extract_sql_from_llm_response(response_text)
        logging.info(f"Generated SQL: {sql}")
        if not sql:
            logging.error("Failed to extract valid SQL from response")
            raise LLMServiceError("Failed to extract valid SQL from response")
            
        return sql
        
    except Exception as e:
        logger.error(f"Error in generate_sql_query: {str(e)}", exc_info=True)
        if isinstance(e, (ValidationError, LLMServiceError)):
            raise e
        raise LLMServiceError("SQL generation failed", original_error=e)

def extract_sql_from_llm_response(llm_response):
    """Extract and validate SQL from LLM response"""
    try:
        logging.info("Extracting SQL from LLM response")
        sql_query_pattern = r"``` *sql\n(.*?)\n```"
        matches = re.finditer(sql_query_pattern, llm_response, re.DOTALL)
        
        for match in matches:
            sql_query = match.group(1).strip()
            if is_safe_query(sql_query):
                return sql_query
                
        return None
        
    except Exception as e:
        logger.error(f"Error extracting SQL: {str(e)}", exc_info=True)
        if isinstance(e, ValidationError):
            raise e
        raise LLMServiceError("Failed to extract SQL", original_error=e)

def generate_insights(user_query, sql_query, results):
    """Generate natural language insights from query results"""
    try:
        if not all([user_query, sql_query, results]):
            logging.error("Missing required parameters for insight generation")
            raise ValidationError("Missing required parameters for insight generation")
            
        prompt = f"""
        Analyze this query and results to provide insights:
        Original Question: {user_query}
        SQL Query: {sql_query}
        Results: {results}
        
        Provide clear, non-technical insights focused on the original question.
        Do not mention SQL or technical details in the response.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a data analyst providing insights."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response['choices'][0]['message']['content'].strip()
        
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}", exc_info=True)
        if isinstance(e, ValidationError):
            raise e
        raise LLMServiceError("Failed to generate insights", original_error=e)