import sqlite3

class DatabaseConnector:
    """
    A tool for connecting to databases.
    """
    def __init__(self, db_path: str = "../memory/local.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        print(f"Connected to database: {self.db_path}")

    def execute_query(self, query: str):
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
