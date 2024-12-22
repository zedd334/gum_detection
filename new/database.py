import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file"""
    conn = None
    try:
        # 尝试建立数据库连接
        conn = sqlite3.connect(db_file)
        print(f"Connected to {db_file}")
    except Error as e:
        print(f"Error: {e}")
    return conn

def close_connection(conn):
    """Close the database connection"""
    if conn:
        conn.close()
        print("Connection closed.")
