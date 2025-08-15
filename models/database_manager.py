"""
Database manager for SQLite operations
"""

import sqlite3
import os
from typing import List, Tuple, Any, Optional


class DatabaseManager:
    """Manages SQLite database connections and operations"""
    
    def __init__(self, db_name: str = "netball_stats.db"):
        """Initialize the database manager
        
        Args:
            db_name: Name of the SQLite database file
        """
        self.db_name = db_name
        self.connection = None
        
    def connect(self) -> sqlite3.Connection:
        """Establish connection to the SQLite database
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_name)
            # Enable foreign key constraints
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Set row factory to return dictionaries
            self.connection.row_factory = sqlite3.Row
            
        return self.connection
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute a query that modifies the database (INSERT, UPDATE, DELETE)
        
        Args:
            query: SQL query string
            params: Optional parameters for the query
            
        Returns:
            int: Number of affected rows
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            return cursor.rowcount
            
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[sqlite3.Row]:
        """Fetch all rows from a SELECT query
        
        Args:
            query: SQL SELECT query string
            params: Optional parameters for the query
            
        Returns:
            List[sqlite3.Row]: List of row objects
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.fetchall()
            
        except sqlite3.Error as e:
            raise e
        finally:
            cursor.close()
    
    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[sqlite3.Row]:
        """Fetch a single row from a SELECT query
        
        Args:
            query: SQL SELECT query string
            params: Optional parameters for the query
            
        Returns:
            Optional[sqlite3.Row]: Single row object or None if no results
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.fetchone()
            
        except sqlite3.Error as e:
            raise e
        finally:
            cursor.close()
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def database_exists(self) -> bool:
        """Check if the database file exists
        
        Returns:
            bool: True if database file exists, False otherwise
        """
        return os.path.exists(self.db_name)
