# Netball Tournament Stats Application

A Python desktop application built with PySide6 and SQLite for managing netball tournament statistics.

## Project Structure

```
Netball/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── example_database_usage.py # Example of DatabaseManager usage
├── ui/                       # UI components and layouts
│   └── __init__.py
├── models/                   # Database models and schema
│   ├── __init__.py
│   └── database_manager.py   # SQLite database manager
├── controllers/              # Application logic and business rules
│   └── __init__.py
└── tests/                    # Test files
    ├── __init__.py
    ├── test_main.py          # Tests for main application
    └── test_database_manager.py # Tests for DatabaseManager
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

The application includes a `DatabaseManager` class for SQLite operations:

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

See `example_database_usage.py` for a complete example.

## Features

- PySide6-based desktop application
- SQLite database for data storage with DatabaseManager class
- Modular architecture with separate UI, models, and controllers
- Comprehensive test suite
- Database operations: INSERT, UPDATE, DELETE, SELECT
- Foreign key constraint support
- Context manager support for safe database operations

## Development

The application follows a Model-View-Controller (MVC) pattern:
- **Models**: Database models and data access layer
- **Views**: PySide6 UI components in the `ui/` directory
- **Controllers**: Business logic and application flow in the `controllers/` directory
