"""
Tests for DatabaseManager class
"""

import pytest
import os
import tempfile
import sqlite3
from models.database_manager import DatabaseManager


class TestDatabaseManager:
    """Test cases for DatabaseManager class"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        # Create a temporary database file name for testing
        self.temp_db_name = tempfile.mktemp(suffix='.db')
        self.db_manager = DatabaseManager(self.temp_db_name)
    
    def teardown_method(self):
        """Clean up after each test"""
        self.db_manager.close()
        # Remove the temporary database file
        if os.path.exists(self.temp_db_name):
            os.unlink(self.temp_db_name)
    
    def test_database_creation(self):
        """Test that database file is created when connecting"""
        # Database should not exist initially
        assert not self.db_manager.database_exists()
        
        # Connect to create the database
        conn = self.db_manager.connect()
        assert conn is not None
        
        # Execute a simple query to actually create the database file
        self.db_manager.execute_query("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        
        # Database should now exist
        assert self.db_manager.database_exists()
        
        # Verify it's a valid SQLite database
        assert os.path.getsize(self.temp_db_name) > 0
    
    def test_connection_singleton(self):
        """Test that connect() returns the same connection instance"""
        conn1 = self.db_manager.connect()
        conn2 = self.db_manager.connect()
        
        assert conn1 is conn2
        assert self.db_manager.connection is conn1
    
    def test_execute_query_insert(self):
        """Test that execute_query can insert data"""
        # Create a test table
        create_table_query = """
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            value INTEGER
        )
        """
        self.db_manager.execute_query(create_table_query)
        
        # Insert data
        insert_query = "INSERT INTO test_table (name, value) VALUES (?, ?)"
        affected_rows = self.db_manager.execute_query(insert_query, ("Test Name", 42))
        
        assert affected_rows == 1
        
        # Verify data was inserted
        result = self.db_manager.fetch_one("SELECT * FROM test_table WHERE name = ?", ("Test Name",))
        assert result is not None
        assert result['name'] == "Test Name"
        assert result['value'] == 42
    
    def test_execute_query_update(self):
        """Test that execute_query can update data"""
        # Create and populate test table
        self.db_manager.execute_query("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                value INTEGER
            )
        """)
        
        self.db_manager.execute_query(
            "INSERT INTO test_table (name, value) VALUES (?, ?)", 
            ("Original", 10)
        )
        
        # Update data
        update_query = "UPDATE test_table SET name = ?, value = ? WHERE name = ?"
        affected_rows = self.db_manager.execute_query(
            update_query, ("Updated", 20, "Original")
        )
        
        assert affected_rows == 1
        
        # Verify data was updated
        result = self.db_manager.fetch_one("SELECT * FROM test_table WHERE name = ?", ("Updated",))
        assert result is not None
        assert result['name'] == "Updated"
        assert result['value'] == 20
    
    def test_execute_query_delete(self):
        """Test that execute_query can delete data"""
        # Create and populate test table
        self.db_manager.execute_query("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        self.db_manager.execute_query(
            "INSERT INTO test_table (name) VALUES (?)", 
            ("To Delete",)
        )
        
        # Verify data exists
        result = self.db_manager.fetch_one("SELECT * FROM test_table WHERE name = ?", ("To Delete",))
        assert result is not None
        
        # Delete data
        delete_query = "DELETE FROM test_table WHERE name = ?"
        affected_rows = self.db_manager.execute_query(delete_query, ("To Delete",))
        
        assert affected_rows == 1
        
        # Verify data was deleted
        result = self.db_manager.fetch_one("SELECT * FROM test_table WHERE name = ?", ("To Delete",))
        assert result is None
    
    def test_fetch_all(self):
        """Test that fetch_all returns correct results"""
        # Create and populate test table
        self.db_manager.execute_query("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                value INTEGER
            )
        """)
        
        # Insert multiple rows
        test_data = [
            ("Alice", 100),
            ("Bob", 200),
            ("Charlie", 300)
        ]
        
        for name, value in test_data:
            self.db_manager.execute_query(
                "INSERT INTO test_table (name, value) VALUES (?, ?)",
                (name, value)
            )
        
        # Fetch all data
        results = self.db_manager.fetch_all("SELECT * FROM test_table ORDER BY name")
        
        assert len(results) == 3
        
        # Verify data
        assert results[0]['name'] == "Alice"
        assert results[0]['value'] == 100
        assert results[1]['name'] == "Bob"
        assert results[1]['value'] == 200
        assert results[2]['name'] == "Charlie"
        assert results[2]['value'] == 300
    
    def test_fetch_one(self):
        """Test that fetch_one returns correct results"""
        # Create and populate test table
        self.db_manager.execute_query("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                value INTEGER
            )
        """)
        
        self.db_manager.execute_query(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ("Test Name", 42)
        )
        
        # Fetch single row
        result = self.db_manager.fetch_one(
            "SELECT * FROM test_table WHERE name = ?",
            ("Test Name",)
        )
        
        assert result is not None
        assert result['name'] == "Test Name"
        assert result['value'] == 42
    
    def test_fetch_one_no_results(self):
        """Test that fetch_one returns None when no results found"""
        # Create empty test table
        self.db_manager.execute_query("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        # Try to fetch non-existent data
        result = self.db_manager.fetch_one(
            "SELECT * FROM test_table WHERE name = ?",
            ("Non Existent",)
        )
        
        assert result is None
    
    def test_context_manager(self):
        """Test that DatabaseManager works as a context manager"""
        with DatabaseManager(self.temp_db_name) as db:
            # Create a test table
            db.execute_query("""
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            """)
            
            # Insert data
            db.execute_query(
                "INSERT INTO test_table (name) VALUES (?)",
                ("Test",)
            )
            
            # Verify data
            result = db.fetch_one("SELECT * FROM test_table WHERE name = ?", ("Test",))
            assert result is not None
            assert result['name'] == "Test"
        
        # Connection should be closed after context manager exits
        assert db.connection is None
    
    def test_foreign_key_constraints(self):
        """Test that foreign key constraints are enabled"""
        # Create tables with foreign key relationship
        self.db_manager.execute_query("""
            CREATE TABLE parent_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        self.db_manager.execute_query("""
            CREATE TABLE child_table (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (parent_id) REFERENCES parent_table(id)
            )
        """)
        
        # Insert parent
        self.db_manager.execute_query(
            "INSERT INTO parent_table (name) VALUES (?)",
            ("Parent",)
        )
        
        # Insert child with valid foreign key
        self.db_manager.execute_query(
            "INSERT INTO child_table (parent_id, name) VALUES (?, ?)",
            (1, "Child")
        )
        
        # Try to insert child with invalid foreign key (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            self.db_manager.execute_query(
                "INSERT INTO child_table (parent_id, name) VALUES (?, ?)",
                (999, "Invalid Child")
            )
    
    def test_error_handling(self):
        """Test that database errors are properly handled"""
        # Try to execute invalid SQL
        with pytest.raises(sqlite3.OperationalError):
            self.db_manager.execute_query("INVALID SQL QUERY")
        
        # Try to fetch from non-existent table
        with pytest.raises(sqlite3.OperationalError):
            self.db_manager.fetch_all("SELECT * FROM non_existent_table")
