"""
Database utility functions for DuckDB and other DBs.
"""
import duckdb

def get_connection(db_path=':memory:'):
    return duckdb.connect(database=db_path)
