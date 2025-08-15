"""
Tests for DatabaseSchema class
"""

import pytest
import os
import tempfile
import sqlite3
from models.database_manager import DatabaseManager
from models.schema import DatabaseSchema


class TestDatabaseSchema:
    """Test cases for DatabaseSchema class"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        # Create a temporary database file name for testing
        self.temp_db_name = tempfile.mktemp(suffix='.db')
        self.db_manager = DatabaseManager(self.temp_db_name)
        self.schema = DatabaseSchema(self.db_manager)
    
    def teardown_method(self):
        """Clean up after each test"""
        self.db_manager.close()
        # Remove the temporary database file
        if os.path.exists(self.temp_db_name):
            os.unlink(self.temp_db_name)
    
    def test_create_tables(self):
        """Test that all required tables are created"""
        # Create tables
        self.schema.create_tables()
        
        # Get all table names
        table_names = self.schema.get_table_names()
        
        # Check that all required tables exist
        required_tables = ['divisions', 'teams', 'players', 'matches', 'player_stats']
        for table in required_tables:
            assert table in table_names, f"Table {table} was not created"
        
        # Verify we have exactly the expected tables
        assert len(table_names) == len(required_tables)
    
    def test_table_exists_method(self):
        """Test the table_exists method"""
        # Initially no tables should exist
        assert not self.schema.table_exists('divisions')
        assert not self.schema.table_exists('teams')
        
        # Create tables
        self.schema.create_tables()
        
        # Now all tables should exist
        assert self.schema.table_exists('divisions')
        assert self.schema.table_exists('teams')
        assert self.schema.table_exists('players')
        assert self.schema.table_exists('matches')
        assert self.schema.table_exists('player_stats')
        
        # Non-existent table should return False
        assert not self.schema.table_exists('non_existent_table')
    
    def test_foreign_key_constraints_teams_to_divisions(self):
        """Test foreign key constraint between teams and divisions"""
        self.schema.create_tables()
        
        # Insert a division
        self.db_manager.execute_query(
            "INSERT INTO divisions (id, name) VALUES (?, ?)",
            (1, "Test Division")
        )
        
        # Insert a team with valid foreign key
        self.db_manager.execute_query(
            "INSERT INTO teams (id, name, division_id) VALUES (?, ?, ?)",
            (1, "Test Team", 1)
        )
        
        # Try to insert a team with invalid foreign key (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            self.db_manager.execute_query(
                "INSERT INTO teams (id, name, division_id) VALUES (?, ?, ?)",
                (2, "Invalid Team", 999)
            )
    
    def test_foreign_key_constraints_players_to_teams(self):
        """Test foreign key constraint between players and teams"""
        self.schema.create_tables()
        
        # Insert division and team
        self.db_manager.execute_query(
            "INSERT INTO divisions (id, name) VALUES (?, ?)",
            (1, "Test Division")
        )
        self.db_manager.execute_query(
            "INSERT INTO teams (id, name, division_id) VALUES (?, ?, ?)",
            (1, "Test Team", 1)
        )
        
        # Insert a player with valid foreign key
        self.db_manager.execute_query(
            "INSERT INTO players (id, name, position, team_id) VALUES (?, ?, ?, ?)",
            (1, "Test Player", "Goal Shooter", 1)
        )
        
        # Try to insert a player with invalid foreign key (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            self.db_manager.execute_query(
                "INSERT INTO players (id, name, position, team_id) VALUES (?, ?, ?, ?)",
                (2, "Invalid Player", "Goal Attack", 999)
            )
    
    def test_foreign_key_constraints_matches_to_divisions_and_teams(self):
        """Test foreign key constraints for matches table"""
        self.schema.create_tables()
        
        # Insert division and teams
        self.db_manager.execute_query(
            "INSERT INTO divisions (id, name) VALUES (?, ?)",
            (1, "Test Division")
        )
        self.db_manager.execute_query(
            "INSERT INTO teams (id, name, division_id) VALUES (?, ?, ?)",
            (1, "Team 1", 1)
        )
        self.db_manager.execute_query(
            "INSERT INTO teams (id, name, division_id) VALUES (?, ?, ?)",
            (2, "Team 2", 1)
        )
        
        # Insert a match with valid foreign keys
        self.db_manager.execute_query(
            "INSERT INTO matches (id, date, division_id, team1_id, team2_id, team1_score, team2_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (1, "2024-01-15", 1, 1, 2, 45, 42)
        )
        
        # Try to insert a match with invalid division_id (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            self.db_manager.execute_query(
                "INSERT INTO matches (id, date, division_id, team1_id, team2_id, team1_score, team2_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (2, "2024-01-16", 999, 1, 2, 40, 38)
            )
        
        # Try to insert a match with invalid team1_id (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            self.db_manager.execute_query(
                "INSERT INTO matches (id, date, division_id, team1_id, team2_id, team1_score, team2_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (3, "2024-01-17", 1, 999, 2, 40, 38)
            )
    
    def test_foreign_key_constraints_player_stats_to_players_and_matches(self):
        """Test foreign key constraints for player_stats table"""
        self.schema.create_tables()
        
        # Insert required data
        self.db_manager.execute_query(
            "INSERT INTO divisions (id, name) VALUES (?, ?)",
            (1, "Test Division")
        )
        self.db_manager.execute_query(
            "INSERT INTO teams (id, name, division_id) VALUES (?, ?, ?)",
            (1, "Test Team", 1)
        )
        # Need to create a second team for the match
        self.db_manager.execute_query(
            "INSERT INTO teams (id, name, division_id) VALUES (?, ?, ?)",
            (2, "Test Team 2", 1)
        )
        self.db_manager.execute_query(
            "INSERT INTO players (id, name, position, team_id) VALUES (?, ?, ?, ?)",
            (1, "Test Player", "Goal Shooter", 1)
        )
        self.db_manager.execute_query(
            "INSERT INTO matches (id, date, division_id, team1_id, team2_id, team1_score, team2_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (1, "2024-01-15", 1, 1, 2, 45, 42)
        )
        
        # Insert player stats with valid foreign keys
        self.db_manager.execute_query(
            "INSERT INTO player_stats (id, player_id, match_id, attempts, goals) VALUES (?, ?, ?, ?, ?)",
            (1, 1, 1, 15, 12)
        )
        
        # Try to insert player stats with invalid player_id (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            self.db_manager.execute_query(
                "INSERT INTO player_stats (id, player_id, match_id, attempts, goals) VALUES (?, ?, ?, ?, ?)",
                (2, 999, 1, 10, 8)
            )
        
        # Try to insert player stats with invalid match_id (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            self.db_manager.execute_query(
                "INSERT INTO player_stats (id, player_id, match_id, attempts, goals) VALUES (?, ?, ?, ?, ?)",
                (3, 1, 999, 10, 8)
            )
    
    def test_cascade_delete_division(self):
        """Test that deleting a division cascades to related records"""
        self.schema.create_tables()
        self.schema.insert_sample_data()
        
        # Verify we have data
        divisions = self.db_manager.fetch_all("SELECT * FROM divisions")
        teams = self.db_manager.fetch_all("SELECT * FROM teams")
        players = self.db_manager.fetch_all("SELECT * FROM players")
        matches = self.db_manager.fetch_all("SELECT * FROM matches")
        player_stats = self.db_manager.fetch_all("SELECT * FROM player_stats")
        
        assert len(divisions) > 0
        assert len(teams) > 0
        assert len(players) > 0
        assert len(matches) > 0
        assert len(player_stats) > 0
        
        # Delete a division
        self.db_manager.execute_query("DELETE FROM divisions WHERE id = ?", (1,))
        
        # Check that related records were deleted
        remaining_teams = self.db_manager.fetch_all("SELECT * FROM teams WHERE division_id = ?", (1,))
        assert len(remaining_teams) == 0
        
        # Check that players from deleted teams were also deleted
        remaining_players = self.db_manager.fetch_all("SELECT * FROM players WHERE team_id IN (SELECT id FROM teams WHERE division_id = ?)", (1,))
        assert len(remaining_players) == 0
        
        # Check that matches from deleted division were also deleted
        remaining_matches = self.db_manager.fetch_all("SELECT * FROM matches WHERE division_id = ?", (1,))
        assert len(remaining_matches) == 0
        
        # Check that player stats from deleted matches were also deleted
        remaining_stats = self.db_manager.fetch_all("SELECT * FROM player_stats WHERE match_id IN (SELECT id FROM matches WHERE division_id = ?)", (1,))
        assert len(remaining_stats) == 0
    
    def test_cascade_delete_team(self):
        """Test that deleting a team cascades to related records"""
        self.schema.create_tables()
        self.schema.insert_sample_data()
        
        # Delete a team
        self.db_manager.execute_query("DELETE FROM teams WHERE id = ?", (1,))
        
        # Check that players from deleted team were also deleted
        remaining_players = self.db_manager.fetch_all("SELECT * FROM players WHERE team_id = ?", (1,))
        assert len(remaining_players) == 0
        
        # Check that matches involving deleted team were also deleted
        remaining_matches = self.db_manager.fetch_all("SELECT * FROM matches WHERE team1_id = ? OR team2_id = ?", (1, 1))
        assert len(remaining_matches) == 0
    
    def test_cascade_delete_match(self):
        """Test that deleting a match cascades to related player stats"""
        self.schema.create_tables()
        self.schema.insert_sample_data()
        
        # Delete a match
        self.db_manager.execute_query("DELETE FROM matches WHERE id = ?", (1,))
        
        # Check that player stats from deleted match were also deleted
        remaining_stats = self.db_manager.fetch_all("SELECT * FROM player_stats WHERE match_id = ?", (1,))
        assert len(remaining_stats) == 0
    
    def test_unique_constraints(self):
        """Test unique constraints in the schema"""
        self.schema.create_tables()
        
        # Insert a division
        self.db_manager.execute_query(
            "INSERT INTO divisions (id, name) VALUES (?, ?)",
            (1, "Test Division")
        )
        
        # Try to insert another division with the same name (should fail due to UNIQUE constraint)
        with pytest.raises(sqlite3.IntegrityError):
            self.db_manager.execute_query(
                "INSERT INTO divisions (id, name) VALUES (?, ?)",
                (2, "Test Division")
            )
    
    def test_check_constraints(self):
        """Test check constraints in the schema"""
        self.schema.create_tables()
        
        # Insert division and teams
        self.db_manager.execute_query(
            "INSERT INTO divisions (id, name) VALUES (?, ?)",
            (1, "Test Division")
        )
        self.db_manager.execute_query(
            "INSERT INTO teams (id, name, division_id) VALUES (?, ?, ?)",
            (1, "Team 1", 1)
        )
        self.db_manager.execute_query(
            "INSERT INTO teams (id, name, division_id) VALUES (?, ?, ?)",
            (2, "Team 2", 1)
        )
        
        # Try to insert a match where team1_id equals team2_id (should fail due to CHECK constraint)
        with pytest.raises(sqlite3.IntegrityError):
            self.db_manager.execute_query(
                "INSERT INTO matches (id, date, division_id, team1_id, team2_id, team1_score, team2_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (1, "2024-01-15", 1, 1, 1, 45, 42)
            )
    
    def test_player_stats_unique_constraint(self):
        """Test unique constraint on player_id, match_id combination"""
        self.schema.create_tables()
        
        # Insert required data
        self.db_manager.execute_query(
            "INSERT INTO divisions (id, name) VALUES (?, ?)",
            (1, "Test Division")
        )
        self.db_manager.execute_query(
            "INSERT INTO teams (id, name, division_id) VALUES (?, ?, ?)",
            (1, "Test Team", 1)
        )
        # Need to create a second team for the match
        self.db_manager.execute_query(
            "INSERT INTO teams (id, name, division_id) VALUES (?, ?, ?)",
            (2, "Test Team 2", 1)
        )
        self.db_manager.execute_query(
            "INSERT INTO players (id, name, position, team_id) VALUES (?, ?, ?, ?)",
            (1, "Test Player", "Goal Shooter", 1)
        )
        self.db_manager.execute_query(
            "INSERT INTO matches (id, date, division_id, team1_id, team2_id, team1_score, team2_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (1, "2024-01-15", 1, 1, 2, 45, 42)
        )
        
        # Insert first player stats record
        self.db_manager.execute_query(
            "INSERT INTO player_stats (id, player_id, match_id, attempts, goals) VALUES (?, ?, ?, ?, ?)",
            (1, 1, 1, 15, 12)
        )
        
        # Try to insert another record with same player_id and match_id (should fail due to UNIQUE constraint)
        with pytest.raises(sqlite3.IntegrityError):
            self.db_manager.execute_query(
                "INSERT INTO player_stats (id, player_id, match_id, attempts, goals) VALUES (?, ?, ?, ?, ?)",
                (2, 1, 1, 10, 8)
            )
    
    def test_get_foreign_keys(self):
        """Test getting foreign key information"""
        self.schema.create_tables()
        
        # Get foreign keys for teams table
        fks = self.schema.get_foreign_keys('teams')
        assert len(fks) > 0
        
        # Check that teams table has foreign key to divisions
        team_fks = [fk['table'] for fk in fks]
        assert 'divisions' in team_fks
    
    def test_drop_tables(self):
        """Test dropping all tables"""
        self.schema.create_tables()
        
        # Verify tables exist
        assert self.schema.table_exists('divisions')
        assert self.schema.table_exists('teams')
        assert self.schema.table_exists('players')
        assert self.schema.table_exists('matches')
        assert self.schema.table_exists('player_stats')
        
        # Drop tables
        self.schema.drop_tables()
        
        # Verify tables no longer exist
        assert not self.schema.table_exists('divisions')
        assert not self.schema.table_exists('teams')
        assert not self.schema.table_exists('players')
        assert not self.schema.table_exists('matches')
        assert not self.schema.table_exists('player_stats')
