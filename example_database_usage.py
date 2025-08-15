#!/usr/bin/env python3
"""
Example usage of DatabaseManager class
"""

from models.database_manager import DatabaseManager


def main():
    """Demonstrate DatabaseManager functionality"""
    
    # Create a database manager instance
    db = DatabaseManager("example.db")
    
    try:
        # Create a test table
        print("Creating test table...")
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT,
                team_id INTEGER
            )
        """)
        
        # Insert some test data
        print("Inserting test data...")
        players = [
            ("Alice Johnson", "Goal Shooter", 1),
            ("Bob Smith", "Goal Attack", 1),
            ("Charlie Brown", "Wing Attack", 2),
            ("Diana Prince", "Center", 2)
        ]
        
        for name, position, team_id in players:
            db.execute_query(
                "INSERT INTO players (name, position, team_id) VALUES (?, ?, ?)",
                (name, position, team_id)
            )
        
        # Fetch all players
        print("\nAll players:")
        all_players = db.fetch_all("SELECT * FROM players ORDER BY name")
        for player in all_players:
            print(f"  {player['name']} - {player['position']} (Team {player['team_id']})")
        
        # Fetch a specific player
        print("\nLooking for Alice Johnson:")
        alice = db.fetch_one("SELECT * FROM players WHERE name = ?", ("Alice Johnson",))
        if alice:
            print(f"  Found: {alice['name']} - {alice['position']}")
        
        # Update a player
        print("\nUpdating Bob Smith's position...")
        db.execute_query(
            "UPDATE players SET position = ? WHERE name = ?",
            ("Goal Keeper", "Bob Smith")
        )
        
        # Verify the update
        bob = db.fetch_one("SELECT * FROM players WHERE name = ?", ("Bob Smith",))
        if bob:
            print(f"  Updated: {bob['name']} - {bob['position']}")
        
        # Count players by team
        print("\nPlayers by team:")
        team_counts = db.fetch_all("""
            SELECT team_id, COUNT(*) as count 
            FROM players 
            GROUP BY team_id 
            ORDER BY team_id
        """)
        for team in team_counts:
            print(f"  Team {team['team_id']}: {team['count']} players")
        
        print("\nDatabase operations completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up
        db.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
