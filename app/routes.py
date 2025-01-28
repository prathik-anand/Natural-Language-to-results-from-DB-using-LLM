import logging

from flask import Blueprint, jsonify, request
from openai.error import OpenAIError
from psycopg2 import Error as PostgresError

from .exceptions.exceptions import *
from .services.llm_service import generate_sql_query, get_results
from .services.schema_service import get_schema, reload_schema
from .services.db_service import execute_sql_query


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_blueprint = Blueprint('api', __name__)


@api_blueprint.errorhandler(BaseAppException)
def handle_error(error):
    logger.error(f"Error: {error.message}", exc_info=error.original_error)
    response = {
        "status": "error",
        "error": {
            "type": error.__class__.__name__,
            "message": error.message
        }
    }
    if error.original_error:
        response["error"]["details"] = str(error.original_error)
    return jsonify(response), error.status_code

@api_blueprint.route('/query', methods=['POST'])
def handle_query():
    try:
        data = request.json
        if not data or 'query' not in data:
            raise ValidationError("Query parameter is required")

        natural_language_query = data['query']
        
        try:
            response_data = get_results(natural_language_query)
        except OpenAIError as e:
            raise LLMServiceError("Failed to generate query", original_error=e)
        except PostgresError as e:
            raise DatabaseError("Failed to execute query", original_error=e)
        except ValueError as e:
            raise ValidationError(str(e))
            
        if not response_data:
            raise QueryGenerationError("Failed to generate meaningful results")

        return jsonify({
            "status": "success",
            "sql_query": response_data["sql_query"],
            "insights": response_data["insights"],
            "raw_results": response_data["results"]
        })
        
    except Exception as e:
        if not isinstance(e, BaseAppException):
            logger.error("Unexpected error", exc_info=e)
            raise BaseAppException("An unexpected error occurred", original_error=e)
        raise e

@api_blueprint.route('/schema/reload', methods=['POST'])
def reload_schema_endpoint():
    try:
        connection_string = get_db_connection_string()
        schema = reload_schema(connection_string)
        return jsonify({
            "status": "success",
            "message": "Schema reloaded successfully",
            "schema": schema
        })
    except PostgresError as e:
        raise SchemaError("Failed to reload schema", original_error=e)