# Netball Tournament Stats Application

A Python desktop application built with PySide6 and SQLite for managing netball tournament statistics.

## Project Structure

```
Netball/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── example_database_usage.py # Example of DatabaseManager usage
├── example_schema_usage.py   # Example of DatabaseSchema usage
├── example_team_player_ui.py # Example of team/player management UI
├── ui/                       # UI components and layouts
│   ├── __init__.py
│   └── team_player_management.py # Team and player management UI
├── models/                   # Database models and schema
│   ├── __init__.py
│   ├── database_manager.py   # SQLite database manager
│   └── schema.py            # Database schema and table definitions
├── controllers/              # Application logic and business rules
│   └── __init__.py
└── tests/                    # Test files
    ├── __init__.py
    ├── test_main.py          # Tests for main application
    ├── test_database_manager.py # Tests for DatabaseManager
    ├── test_schema.py        # Tests for database schema
    └── test_team_player_management.py # Tests for team/player management UI
```

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

## Running Tests

To run the tests:
```bash
pytest tests/
```

## Database Usage

The application includes a `DatabaseManager` class for SQLite operations and a `DatabaseSchema` class for table management:

### DatabaseManager
```python
from models.database_manager import DatabaseManager

# Create database manager
db = DatabaseManager("netball_stats.db")

# Execute queries
db.execute_query("CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT)")
db.execute_query("INSERT INTO players (name) VALUES (?)", ("Alice",))

# Fetch data
players = db.fetch_all("SELECT * FROM players")
player = db.fetch_one("SELECT * FROM players WHERE name = ?", ("Alice",))

# Use as context manager
with DatabaseManager("netball_stats.db") as db:
    # Database operations
    pass
```

### DatabaseSchema
```python
from models.database_manager import DatabaseManager
from models.schema import DatabaseSchema

# Create schema manager
db = DatabaseManager("netball_stats.db")
schema = DatabaseSchema(db)

# Create all tables with foreign key relationships
schema.create_tables()

# Insert sample data
schema.insert_sample_data()

# Check table existence
if schema.table_exists('players'):
    print("Players table exists")
```

See `example_database_usage.py` and `example_schema_usage.py` for complete examples.

### Team and Player Management UI

The application includes a comprehensive UI for managing teams and players:

```python
from models.database_manager import DatabaseManager
from models.schema import DatabaseSchema
from ui.team_player_management import TeamPlayerManagementWidget

# Create database and schema
db = DatabaseManager("netball_stats.db")
schema = DatabaseSchema(db)
schema.create_tables()
schema.insert_sample_data()

# Create the management widget
management_widget = TeamPlayerManagementWidget(db)
management_widget.show()
```

Features:
- **Teams Management**: Add, edit, and delete teams with division selection
- **Players Management**: Add, edit, and delete players with position and team assignment
- **Data Validation**: Form validation for required fields
- **Cascade Delete**: Deleting a team automatically deletes its players
- **Real-time Updates**: Tables refresh automatically after operations

See `example_team_player_ui.py` for a complete example.

## Features

- PySide6-based desktop application
- SQLite database for data storage with DatabaseManager class
- Modular architecture with separate UI, models, and controllers
- Comprehensive test suite
- Database operations: INSERT, UPDATE, DELETE, SELECT
- Foreign key constraint support with cascade delete
- Context manager support for safe database operations
- Complete database schema for netball tournament statistics
- Sample data insertion for testing and demonstration
- Team and player management UI with add/edit/delete functionality
- QTableView with custom table models for data display

## Development

The application follows a Model-View-Controller (MVC) pattern:
- **Models**: Database models and data access layer
- **Views**: PySide6 UI components in the `ui/` directory
- **Controllers**: Business logic and application flow in the `controllers/` directory
