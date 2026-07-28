"""
SQL Runner Utility.
Loads and executes raw .sql files from the sql/ directory against the SQLite database.
"""

import os
import sqlite3
import pandas as pd
from typing import Dict, List, Optional

class SQLRunner:
    """Helper class to load, parse, and execute SQL scripts."""

    def __init__(self, db_path: str = "data/ecommerce.db", sql_dir: str = "sql"):
        self.db_path = db_path
        self.sql_dir = sql_dir

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def load_sql_file(self, filename: str) -> str:
        """Reads a .sql file from the sql/ directory."""
        file_path = os.path.join(self.sql_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"SQL file not found at: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def run_query(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """Executes a SQL query string and returns a DataFrame."""
        with self.get_connection() as conn:
            if params:
                return pd.read_sql_query(query, conn, params=params)
            return pd.read_sql_query(query, conn)

    def run_sql_file(self, filename: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """Loads and executes a .sql script."""
        query = self.load_sql_file(filename)
        return self.run_query(query, params)

    def list_sql_files(self) -> List[str]:
        """Lists all available .sql files in the sql/ directory."""
        if not os.path.exists(self.sql_dir):
            return []
        return sorted([f for f in os.listdir(self.sql_dir) if f.endswith(".sql")])

if __name__ == "__main__":
    runner = SQLRunner()
    print("Available SQL files:", runner.list_sql_files())
