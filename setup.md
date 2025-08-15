---

# Netball Tournament Stats Application – Cursor Development Prompts (Updated for Per-Match Stats)

**Stack:** Python + PySide6 + SQLite

## Key Change

* **Relevant stats** (e.g., attempts, goals, rebounds, interceptions, turnovers, etc.) are entered **per match**.
* **Calculated stats** (e.g., accuracy, points, games played, goal difference) are derived from match records.
* Team and player totals are always calculated from match-level data.

---

## **1. Project Setup**

**Implementation Prompt:**

```
You are my AI coding partner.
Create the basic folder structure for a Python desktop application using PySide6 and SQLite.
Include:
- main.py entry point
- /ui for UI files
- /models for database models
- /controllers for logic
- /tests for test files

Initialize a PySide6 application window with a blank MainWindow class.
Ensure the app runs successfully.
```

**Test Prompt:**

```
Write a pytest test to ensure the PySide6 app launches and MainWindow is created without errors.
```

---

## **2. Database Setup (SQLite)**

**Implementation Prompt:**

```
Create a DatabaseManager class to manage SQLite connections and queries.
Methods:
- connect()
- execute_query(query, params=None)
- fetch_all(query, params=None)
- fetch_one(query, params=None)

Database file name: netball_stats.db
```

**Test Prompt:**

```
Write tests to ensure:
- Database file is created.
- execute_query inserts data.
- fetch_all and fetch_one return correct results.
```

---

## **3. Database Schema Creation**

**Implementation Prompt:**

```
Using DatabaseManager, create tables:
1. divisions(id, name)
2. teams(id, name, division_id)
3. players(id, name, position, team_id)
4. matches(id, date, division_id, team1_id, team2_id, team1_score, team2_score)
5. player_stats(id, player_id, match_id, attempts, goals, center_passes, tips, rebounds, interceptions, turnovers)

Foreign keys must be set.
```

**Test Prompt:**

```
Write tests to ensure:
- All required tables exist.
- Foreign keys work (e.g., deleting a match removes its player_stats).
```

---

## **4. Team & Player Management UI**

**Implementation Prompt:**

```
Create a PySide6 UI to:
- Add teams (select division)
- Add players (select position, assign team)
Display in QTableView with edit/delete options.
Save to SQLite.
```

**Test Prompt:**

```
Write tests with pytest-qt to ensure adding/editing/deleting teams and players works.
```

---

## **5. Fixture Creation**

**Implementation Prompt:**

```
Implement fixture auto-generation by division:
- Each team plays all others once.
- Save fixtures in matches table.
```

**Test Prompt:**

```
Write tests to confirm:
- All matchups are generated.
- No duplicates.
- Correct match count for n teams.
```

---

## **6. Match Results & Stat Entry**

**Implementation Prompt:**

```
Create a match result entry screen where the user selects a match and:
- Inputs team scores.
- Inputs per-player stats for that match (attempts, goals, center passes, tips, rebounds, interceptions, turnovers).
Save data to matches and player_stats tables.

Ensure calculated stats are NOT entered here — only raw per-match inputs.
```

**Test Prompt:**

```
Write tests to ensure:
- Entering results updates matches table.
- Entering player stats updates player_stats table.
- Editing results updates stats correctly.
```

---

## **7. Calculated Team Statistics**

**Implementation Prompt:**

```
Create a function to calculate team stats from matches table:
- Games Played
- Wins, Draws, Losses
- Goals For, Goals Against
- Goal Difference
- Points (Win=3, Draw=1, Loss=0)

Do NOT store totals — calculate live when requested.
```

**Test Prompt:**

```
Write tests to confirm team stats calculations match expected values for given match records.
```

---

## **8. Calculated Player Statistics**

**Implementation Prompt:**

```
Create a function to calculate player stats from player_stats table:
- Attempts, Goals
- Accuracy (Goals/Attempts)
- Center Passes, Tips, Rebounds, Interceptions, Turnovers

Totals are derived from all matches played by the player.
```

**Test Prompt:**

```
Write tests to confirm player stats calculations are correct for different match datasets.
```

---

## **9. CSV Import/Export**

**Implementation Prompt:**

```
Implement CSV functions:
- Import teams/players from CSV with headers: Team,Division,Player,Position
- Export teams, players, matches, and calculated stats to CSV
Validate on import.
```

**Test Prompt:**

```
Write tests to ensure CSV import/export matches data in the database.
```

---

## **10. Reports (PDF)**

**Implementation Prompt:**

```
Using ReportLab, generate PDFs for:
- Current team standings
- Player statistics leaderboard

Values must be calculated from database, not stored.
```

**Test Prompt:**

```
Write tests to ensure PDFs are generated and contain non-empty data.
```

---