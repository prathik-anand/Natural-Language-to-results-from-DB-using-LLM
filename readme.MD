
# Natural Language to SQL Query Generator

A Flask-based REST API service that converts natural language queries into results using data within database like Postgres using LLM model like openai-gpt-40-mini.

## Architecture

The project follows a modular architecture with the following components:

### Core Components
- **Flask Application** (`app/__init__.py`): The main entry point for the application.
- **API Routes** (`app/routes.py`): Defines REST API endpoints for user interaction.
- **Database Service** (`app/services/db_service.py`): Handles execution of SQL queries on the PostgreSQL database.
- **Schema Service** (`app/services/schema_service.py`): Manages database schema, including loading and caching.
- **LLM Service** (`app/services/llm_service.py`): Uses OpenAI's GPT model to convert natural language into SQL.
- **Configuration** (`app/utils/config.py`): Handles configuration from environment variables.
- **Helpers** (`app/utils/helpers.py`): Provides utility functions, including caching functionality.

## API Endpoints

### 1. Convert Natural Language to SQL
- **Endpoint**: `POST /query`
- **Description**: Converts a natural language query into SQL, executes it against the PostgreSQL database, and returns the result.
- **Request cURL**: 
  ```bash
  curl -X POST http://localhost:5000/query -H "Content-Type: application/json" -d '{"query": "Show me all orders placed in the last 7 days."}'
  ```

- **Example Response**:
  ```json
  {
    "status": 1,
    "sql_query": "SELECT postal_code, SUM(quantity) as total_sales FROM orders GROUP BY postal_code ORDER BY total_sales DESC LIMIT 1;",
    "result": "Most sold items are in postal code of 10035 and 924 orders have placed"
  }
  ```

### 2. Reload Database Schema
- **Endpoint**: `POST /schema/reload`
- **Description**: Refreshes the cached database schema to reflect any changes made to the underlying database structure.
- **Request cURL**: 
  ```bash
  curl -X POST http://127.0.0.1:5000/schema/reload
  ```
- **Example Response**:
  ```json
  {
    "status": "success",
    "message": "Schema cache reloaded."
  }
  ```

## Setup

### Prerequisites
- **Python**: Version 3.8 or higher.
- **PostgreSQL**: A running PostgreSQL database instance.
- **OpenAI API Key**: A valid API key for OpenAI.

### Environment Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with the following variables:
   ```plaintext
   OPENAI_API_KEY=<your_openai_api_key>
   DATABASE_URL=<your_postgresql_database_url>
   DB_NAME=<your_postgres_db_name>
   DB_USER=<db_user_name>
   DB_PASSWORD=<dbpassword>
   DB_HOST=<hostname/ipaddress>
   DB_PORT=<postgres_port>
   ```


The server will start and be accessible at `http://localhost:5000`.


## Features

- **Natural Language to SQL Conversion**: Uses GPT-4 to interpret user queries and generate SQL statements.
- **Database Schema Caching**: Improves performance by caching database schema details.
- **Schema Reload Capability**: Allows refreshing schema cache when database structure changes.
- **PostgreSQL Support**: Built specifically for PostgreSQL databases.

## Caching

Schema caching is implemented using the `@cache_data` decorator to avoid repetitive schema queries. This significantly enhances performance for repeated operations.

### Refresh Schema Cache
To reload the schema when there are database structure changes, send a `POST` request to `/schema/reload`.


