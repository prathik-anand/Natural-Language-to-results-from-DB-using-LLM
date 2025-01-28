
# Natural Language Query into SQL Meaningful Insights

A Flask-based REST API service that converts natural language queries into meaningful insights using data within databases like Postgres through an LLM model such as OpenAI's GPT-4o-mini.

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

- **Endpoint**: POST `/query`
- **Description**: Converts a natural language query into SQL, executes it against the PostgreSQL database, and returns meaningful insights instead of raw results.

#### Request cURL:

```bash
curl -X POST http://localhost:5000/query -H "Content-Type: application/json" -d '{"query": "Show me all orders placed in the last 7 days."}'
```

#### Sucessful Response:

```json
{
    "status": "success",
    "sql_query": "SELECT postal_code, COUNT(*) AS sales_count\nFROM        orders\nGROUP BY postal_code\nORDER BY sales_count DESC",
    "insights": "Based on the data regarding which postal codes have the highest sales, several insights can be drawn:\n\n1. **Top Postal Codes**: The most successful postal code is 10035, with a total of 255 sales. It is followed closely by 10024 and 10009, showing that these areas are incredibly strong markets for the product..",
    "raw_results": [
   [10035, 255],
    [10024,226],
    [10009,221]
    ]
}
```

#### Error Response:
```json
{
    "status": "error",
    "error": {
        "type": "ValidationError",
        "message": "Query parameter is required",
        "details": "Additional error context if available"
    }
}
```

### Error Types
- **ValidationError (400)**: Input validation failed
- **DatabaseError (500):** Database operation failed
- **QueryGenerationError (500)**: SQL generation failed
- **LLMServiceError (503)**: OpenAI service error
- **SchemaError (500)**: Schema operation failed



### 2. Reload Database Schema

- **Endpoint**: POST `/schema/reload`
- **Description**: Refreshes the cached database schema to reflect any changes made to the underlying database structure.

#### Request cURL:

```bash
curl -X POST http://127.0.0.1:5000/schema/reload
```

#### Example Response:

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
   git clone https://github.com/prathik-anand/Natural-Language-to-results-from-DB-using-LLM.git
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:

   ```bash
   OPENAI_API_KEY=<your_openai_api_key>
   DATABASE_URL=<your_postgresql_database_url>
   DB_NAME=<your_postgres_db_name>
   DB_USER=<db_user_name>
   DB_PASSWORD=<dbpassword>
   DB_HOST=<hostname/ipaddress>
   DB_PORT=<postgres_port>
   ```

4. The server will start and be accessible at `http://localhost:5000`.

## Features

- **Natural Language to Meaningful Insights**: Uses GPT-4 to interpret user queries and provide insights, not just raw database results.
- **Read-Only Query Generation**: Ensures that all generated SQL queries are read-only to prevent any updates or insertions into the database.
- **Database Schema Caching**: Improves performance by caching database schema details.
- **Schema Reload Capability**: Allows refreshing schema cache when database structure changes.
- **PostgreSQL Support**: Built specifically for PostgreSQL databases.

## Caching

Schema caching is implemented using the `@cache_data` decorator to avoid repetitive schema queries. This significantly enhances performance for repeated operations.

### Refresh Schema Cache

To reload the schema when there are database structure changes, send a POST request to `/schema/reload`.
