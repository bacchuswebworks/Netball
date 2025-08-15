"""
Database schema for Netball Tournament Stats Application
"""

from models.database_manager import DatabaseManager


class DatabaseSchema:
    """Manages database schema creation and initialization"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize schema manager
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
    
    def create_tables(self):
        """Create all required tables with proper foreign key relationships"""
        
        # 1. Divisions table
        self.db_manager.execute_query("""
            CREATE TABLE IF NOT EXISTS divisions (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
        """)
        
        # 2. Teams table with foreign key to divisions
        self.db_manager.execute_query("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                division_id INTEGER NOT NULL,
                FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE CASCADE
            )
        """)
        
        # 3. Players table with foreign key to teams
        self.db_manager.execute_query("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                team_id INTEGER NOT NULL,
                FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
            )
        """)
        
        # 4. Matches table with foreign keys to divisions and teams
        self.db_manager.execute_query("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL,
                division_id INTEGER NOT NULL,
                team1_id INTEGER NOT NULL,
                team2_id INTEGER NOT NULL,
                team1_score INTEGER DEFAULT 0,
                team2_score INTEGER DEFAULT 0,
                FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE CASCADE,
                FOREIGN KEY (team1_id) REFERENCES teams(id) ON DELETE CASCADE,
                FOREIGN KEY (team2_id) REFERENCES teams(id) ON DELETE CASCADE,
                CHECK (team1_id != team2_id)
            )
        """)
        
        # 5. Player stats table with foreign keys to players and matches
        self.db_manager.execute_query("""
            CREATE TABLE IF NOT EXISTS player_stats (
                id INTEGER PRIMARY KEY,
                player_id INTEGER NOT NULL,
                match_id INTEGER NOT NULL,
                attempts INTEGER DEFAULT 0,
                goals INTEGER DEFAULT 0,
                center_passes INTEGER DEFAULT 0,
                tips INTEGER DEFAULT 0,
                rebounds INTEGER DEFAULT 0,
                interceptions INTEGER DEFAULT 0,
                turnovers INTEGER DEFAULT 0,
                FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
                FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
                UNIQUE(player_id, match_id)
            )
        """)
    
    def drop_tables(self):
        """Drop all tables in correct order (respecting foreign key constraints)"""
        tables = [
            'player_stats',
            'matches', 
            'players',
            'teams',
            'divisions'
        ]
        
        for table in tables:
            self.db_manager.execute_query(f"DROP TABLE IF EXISTS {table}")
    
    def get_table_names(self):
        """Get list of all table names in the database"""
        tables = self.db_manager.fetch_all("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        return [table['name'] for table in tables]
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a specific table exists
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            bool: True if table exists, False otherwise
        """
        result = self.db_manager.fetch_one("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name = ?
        """, (table_name,))
        return result is not None
    
    def get_foreign_keys(self, table_name: str):
        """Get foreign key information for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of foreign key information
        """
        return self.db_manager.fetch_all(f"""
            PRAGMA foreign_key_list({table_name})
        """)
    
    def insert_sample_data(self):
        """Insert sample data for testing purposes"""
        
        # Insert divisions
        divisions = [
            (1, "Premier Division"),
            (2, "Division 1"),
            (3, "Division 2")
        ]
        
        for div_id, name in divisions:
            self.db_manager.execute_query(
                "INSERT OR IGNORE INTO divisions (id, name) VALUES (?, ?)",
                (div_id, name)
            )
        
        # Insert teams
        teams = [
            (1, "Red Dragons", 1),
            (2, "Blue Eagles", 1),
            (3, "Green Lions", 2),
            (4, "Yellow Tigers", 2)
        ]
        
        for team_id, name, div_id in teams:
            self.db_manager.execute_query(
                "INSERT OR IGNORE INTO teams (id, name, division_id) VALUES (?, ?, ?)",
                (team_id, name, div_id)
            )
        
        # Insert players
        players = [
            (1, "Alice Johnson", "Goal Shooter", 1),
            (2, "Bob Smith", "Goal Attack", 1),
            (3, "Charlie Brown", "Wing Attack", 2),
            (4, "Diana Prince", "Center", 2),
            (5, "Eve Wilson", "Goal Keeper", 3),
            (6, "Frank Miller", "Goal Defense", 3)
        ]
        
        for player_id, name, position, team_id in players:
            self.db_manager.execute_query(
                "INSERT OR IGNORE INTO players (id, name, position, team_id) VALUES (?, ?, ?, ?)",
                (player_id, name, position, team_id)
            )
        
        # Insert matches
        matches = [
            (1, "2024-01-15", 1, 1, 2, 45, 42),
            (2, "2024-01-22", 2, 3, 4, 38, 35)
        ]
        
        for match_id, date, div_id, team1_id, team2_id, score1, score2 in matches:
            self.db_manager.execute_query(
                "INSERT OR IGNORE INTO matches (id, date, division_id, team1_id, team2_id, team1_score, team2_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (match_id, date, div_id, team1_id, team2_id, score1, score2)
            )
        
        # Insert player stats
        player_stats = [
            (1, 1, 1, 15, 12, 0, 0, 0, 0, 2),
            (2, 2, 1, 10, 8, 0, 0, 0, 0, 1),
            (3, 3, 1, 8, 6, 0, 0, 0, 0, 3),
            (4, 4, 1, 12, 10, 0, 0, 0, 0, 1),
            (5, 5, 2, 14, 11, 0, 0, 0, 0, 2),
            (6, 6, 2, 9, 7, 0, 0, 0, 0, 1)
        ]
        
        for stat_id, player_id, match_id, attempts, goals, center_passes, tips, rebounds, interceptions, turnovers in player_stats:
            self.db_manager.execute_query(
                "INSERT OR IGNORE INTO player_stats (id, player_id, match_id, attempts, goals, center_passes, tips, rebounds, interceptions, turnovers) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (stat_id, player_id, match_id, attempts, goals, center_passes, tips, rebounds, interceptions, turnovers)
            )
