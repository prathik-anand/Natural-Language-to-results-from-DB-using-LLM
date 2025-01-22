from flask import Blueprint, jsonify, request
from .exceptions.exceptions import DatabaseError, QueryGenerationError, ValidationError
from .services.llm_service import generate_sql_query, get_results
from .services.schema_service import get_schema, reload_schema
from .utils import get_db_connection_string
from .services.db_service import execute_sql_query as execute_query

api_blueprint = Blueprint('api', __name__)

@api_blueprint.errorhandler(DatabaseError)
@api_blueprint.errorhandler(QueryGenerationError)
@api_blueprint.errorhandler(ValidationError)
def handle_error(error):
    response = {
        "error": error.message,
        "type": error.__class__.__name__
    }
    return jsonify(response), error.status_code

@api_blueprint.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    if not data or 'query' not in data:
        raise ValidationError("Query is required")

    natural_language_query = data['query']
    
    try:
        connection_string = get_db_connection_string()
        summary = get_results(natural_language_query)
        if(summary is None):
            return jsonify({
            "status":-1,
            "sql_query": None,
            "message":"System is not able to prosses the query",
            "results": None
        })
        ##results = execute_query(connection_string, sql_query)
        
        return jsonify({
            ##"sql_query": sql_query,
            "results": summary
        })
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise e
        elif "database" in str(e).lower():
            raise DatabaseError(f"Database error: {str(e)}")
        else:
            raise QueryGenerationError(f"Query generation failed: {str(e)}")

@api_blueprint.route('/schema/reload', methods=['POST'])
def reload_schema_endpoint():
    try:
        connection_string = get_db_connection_string()
        schema = reload_schema(connection_string)
        return jsonify(schema)
    except Exception as e:
        raise DatabaseError(f"Schema reload failed: {str(e)}")