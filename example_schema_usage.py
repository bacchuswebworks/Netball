#!/usr/bin/env python3
"""
Example usage of DatabaseSchema class
"""

from models.database_manager import DatabaseManager
from models.schema import DatabaseSchema


def main():
    """Demonstrate DatabaseSchema functionality"""
    
    # Create a database manager instance
    db = DatabaseManager("netball_schema_example.db")
    schema = DatabaseSchema(db)
    
    try:
        print("Creating database schema...")
        schema.create_tables()
        
        # Check that all tables were created
        table_names = schema.get_table_names()
        print(f"Created tables: {', '.join(table_names)}")
        
        # Insert sample data
        print("\nInserting sample data...")
        schema.insert_sample_data()
        
        # Query and display divisions
        print("\nDivisions:")
        divisions = db.fetch_all("SELECT * FROM divisions ORDER BY id")
        for division in divisions:
            print(f"  {division['id']}: {division['name']}")
        
        # Query and display teams with their divisions
        print("\nTeams:")
        teams = db.fetch_all("""
            SELECT t.id, t.name, d.name as division_name 
            FROM teams t 
            JOIN divisions d ON t.division_id = d.id 
            ORDER BY t.id
        """)
        for team in teams:
            print(f"  {team['id']}: {team['name']} ({team['division_name']})")
        
        # Query and display players with their teams
        print("\nPlayers:")
        players = db.fetch_all("""
            SELECT p.id, p.name, p.position, t.name as team_name 
            FROM players p 
            JOIN teams t ON p.team_id = t.id 
            ORDER BY p.id
        """)
        for player in players:
            print(f"  {player['id']}: {player['name']} - {player['position']} ({player['team_name']})")
        
        # Query and display matches
        print("\nMatches:")
        matches = db.fetch_all("""
            SELECT m.id, m.date, m.team1_score, m.team2_score,
                   t1.name as team1_name, t2.name as team2_name,
                   d.name as division_name
            FROM matches m 
            JOIN teams t1 ON m.team1_id = t1.id
            JOIN teams t2 ON m.team2_id = t2.id
            JOIN divisions d ON m.division_id = d.id
            ORDER BY m.date
        """)
        for match in matches:
            print(f"  {match['id']}: {match['team1_name']} {match['team1_score']} - {match['team2_score']} {match['team2_name']} ({match['division_name']}) - {match['date']}")
        
        # Query and display player statistics
        print("\nPlayer Statistics:")
        stats = db.fetch_all("""
            SELECT ps.id, p.name as player_name, ps.attempts, ps.goals,
                   ROUND(CAST(ps.goals AS FLOAT) / ps.attempts * 100, 1) as accuracy,
                   t.name as team_name, m.date as match_date
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.id
            JOIN teams t ON p.team_id = t.id
            JOIN matches m ON ps.match_id = m.id
            ORDER BY ps.goals DESC
        """)
        for stat in stats:
            accuracy = stat['accuracy'] if stat['accuracy'] else 0
            print(f"  {stat['player_name']} ({stat['team_name']}): {stat['goals']}/{stat['attempts']} goals ({accuracy}%) - {stat['match_date']}")
        
        # Demonstrate foreign key constraints
        print("\nTesting foreign key constraints...")
        
        # Try to insert a team with non-existent division (should fail)
        try:
            db.execute_query(
                "INSERT INTO teams (id, name, division_id) VALUES (?, ?, ?)",
                (999, "Invalid Team", 999)
            )
            print("  ❌ Foreign key constraint failed - should not have allowed invalid division_id")
        except Exception as e:
            print(f"  ✅ Foreign key constraint working: {type(e).__name__}")
        
        # Demonstrate cascade delete
        print("\nTesting cascade delete...")
        
        # Count records before deletion
        divisions_before = len(db.fetch_all("SELECT * FROM divisions"))
        teams_before = len(db.fetch_all("SELECT * FROM teams"))
        players_before = len(db.fetch_all("SELECT * FROM players"))
        matches_before = len(db.fetch_all("SELECT * FROM matches"))
        stats_before = len(db.fetch_all("SELECT * FROM player_stats"))
        
        print(f"  Before deletion: {divisions_before} divisions, {teams_before} teams, {players_before} players, {matches_before} matches, {stats_before} stats")
        
        # Delete a division (should cascade to related records)
        db.execute_query("DELETE FROM divisions WHERE id = ?", (1,))
        
        # Count records after deletion
        divisions_after = len(db.fetch_all("SELECT * FROM divisions"))
        teams_after = len(db.fetch_all("SELECT * FROM teams"))
        players_after = len(db.fetch_all("SELECT * FROM players"))
        matches_after = len(db.fetch_all("SELECT * FROM matches"))
        stats_after = len(db.fetch_all("SELECT * FROM player_stats"))
        
        print(f"  After deletion: {divisions_after} divisions, {teams_after} teams, {players_after} players, {matches_after} matches, {stats_after} stats")
        
        # Verify cascade worked
        if divisions_after < divisions_before and teams_after < teams_before:
            print("  ✅ Cascade delete working correctly")
        else:
            print("  ❌ Cascade delete not working correctly")
        
        print("\nDatabase schema demonstration completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up
        db.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
