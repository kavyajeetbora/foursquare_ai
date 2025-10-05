
"""
Main entry point for the AI bot.
"""

from pydantic import BaseModel, Field, field_validator
import json
from langchain_core.prompts import ChatPromptTemplate
from src.db.duckdb_utils import get_duckdb_connection
import json


class State(BaseModel):
    question: str = Field(
        default="",
        description="The natural language question or input provided by the user, intended to be translated into a DuckDB SQL query. Example: 'Show me all customers with orders above $100.'"
    )
    data_path: str = Field(
        default="",
        description="This is the data source of the table from where we will be querying using duckdb. This is a parquet file"
    )
    query: str = Field(
        default="",
        description="The generated DuckDB SQL query derived from the user's natural language question. Must conform to DuckDB's SQL syntax and conventions. Example: 'SELECT * FROM customers WHERE order_total > 100;'"
    )
    result: str = Field(
        default="",
        description="The output or result set returned by executing the DuckDB SQL query against the database, formatted as a JSON string. Example: '[{\"id\": 1, \"name\": \"Alice\", \"order_total\": 150}]'"
    )
    answer: str = Field(
        default="",
        description="The final natural language response generated for the user, summarizing or explaining the query results in a conversational manner. Example: 'Here are the customers with orders above 150.'"
    )

    @field_validator("result", mode="after")
    @classmethod
    def validate_result(cls, result: str) -> str:
        try:
            json.loads(result)
        except json.JSONDecodeError:
            raise ValueError("Result must be a valid JSON string")
        return result

class QueryOutput(BaseModel):
    query: str = Field(..., description="Syntactically valid DuckDB SQL query")

    @field_validator("query", mode="after")
    @classmethod
    def validate_query(cls, query: str) -> str:
        if not query.strip().endswith(";"):
            raise ValueError("DuckDB query must end with a semicolon")
        return query

class FourSquareChatBot:
    """NLP-to-SQL chatbot for querying DuckDB databases, optimized for Parquet files and FourSquare data."""

    def __init__(self, data_path: str, columns: list[str], llm, query_prompt_template, database: str = ":memory:"):
        """
        Initialize the chatbot with a DuckDB connection and schema.

        Args:
            data_path (str): Path to the Parquet file (e.g., S3 URL or local path).
            columns (list[str]): List of column names to include in the schema.
            llm: Language model instance for generating SQL queries and answers.
            database (str): DuckDB database path (default: ':memory:' for in-memory).
        """
        self.data_path = data_path
        self.columns = columns
        self.llm = llm
        self.query_prompt_template = query_prompt_template
        self.conn = get_duckdb_connection(database=database)
        self.table_info = self._get_db_schema(limit=5)

    def _get_db_schema(self, limit=5):
        """Generate schema information from the Parquet file with sample values."""
        data_schema = f"Columns:\n"
        sql_query = f"SELECT {','.join(self.columns)} FROM read_parquet('{self.data_path}') WHERE 1=1"
        for column in self.columns:
            sql_query += f" AND {column} IS NOT NULL"
        sql_query += f" LIMIT {limit};"

        sample_result = self._execute_sql(sql_query)['result']
        schema_details = self._execute_sql(f'DESCRIBE {sql_query}')['result']
        for i, column in enumerate(self.columns):
            data_type = schema_details[i][1]
            sample_values = ",".join([str(r[i]) for r in sample_result])
            data_schema += f"{i+1}. Name: {column} | Data Type: {data_type} | Sample values: {sample_values}"
            data_schema += "\n"
        return data_schema

    def _execute_sql(self, sql_query: str) -> list:
        """Execute a SQL query and return results."""
        try:
            result = self.conn.execute(sql_query).fetchall()

            return {"result": result, "error": None}
        except Exception as e:
            return f"Error executing SQL: {str(e)}"

    def generate_sql_query(self, state: State) -> QueryOutput:
        """Generate a DuckDB SQL query from the user's question."""
        prompt = self.query_prompt_template.invoke(
            {
                "top_k": 10,
                "table_info": self.table_info,
                "input": state.question,
                "data_path": self.data_path
            }
        )
        response = self.llm.invoke(prompt)
        cleaned_query = response.content.strip()

        if cleaned_query.startswith("```sql"):
            cleaned_query = cleaned_query[6:]
        if cleaned_query.endswith("```"):
            cleaned_query = cleaned_query[:-3]
        # if not cleaned_query.endswith(";"):
        #      cleaned_query += ";"
        return QueryOutput(query=cleaned_query.strip())

    def generate_answer(self, state: State) -> dict:
        """Generate a conversational answer using query results."""
        # Execute the query and store JSON result

        result = self._execute_sql(state.query)

        if isinstance(result, str) and result.startswith("Error"):
            state.result = json.dumps({"error": result})
            state.answer = f"Sorry, I couldn't process your query due to an error: {result}"
        else:
            state.result = result['result']

            # Generate conversational answer
            prompt = (
                "Given the following user question, corresponding SQL query, "
                "and SQL result, answer the user question in a conversational manner.\n\n"
                f"Question: {state.question}\n"
                f"SQL Query: {state.query}\n"
                f"SQL Result: {state.result}"
            )
            response = self.llm.invoke(prompt)
            state.answer = response.content

        return {"state": state}

    def process_question(self, question: str) -> dict:
        """Process a user question end-to-end and return the updated state."""
        state = State(question=question)
        query_output = self.generate_sql_query(state)
        state.query = query_output.query
        result = self.generate_answer(state)
        return result

    def __del__(self):
        """Clean up by closing the DuckDB connection."""
        if hasattr(self, "conn"):
            self.conn.close()