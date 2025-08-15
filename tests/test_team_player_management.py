"""
Tests for Team and Player Management UI
"""

import pytest
import os
import tempfile
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from models.database_manager import DatabaseManager
from models.schema import DatabaseSchema
from ui.team_player_management import (
    TeamPlayerManagementWidget, AddTeamDialog, AddPlayerDialog,
    TeamsTableModel, PlayersTableModel
)


class TestTeamPlayerManagement:
    """Test cases for Team and Player Management UI"""
    
    @pytest.fixture(autouse=True)
    def setup(self, qtbot):
        """Set up test environment before each test"""
        # Create a temporary database file name for testing
        self.temp_db_name = tempfile.mktemp(suffix='.db')
        self.db_manager = DatabaseManager(self.temp_db_name)
        self.schema = DatabaseSchema(self.db_manager)
        
        # Create tables and insert sample data
        self.schema.create_tables()
        self.schema.insert_sample_data()
        
        # Create the main widget
        self.widget = TeamPlayerManagementWidget(self.db_manager)
        qtbot.addWidget(self.widget)
        self.widget.show()
        
        yield
        
        # Clean up
        self.db_manager.close()
        if os.path.exists(self.temp_db_name):
            os.unlink(self.temp_db_name)
    
    def test_widget_creation(self, qtbot):
        """Test that the widget is created successfully"""
        assert self.widget is not None
        assert self.widget.isVisible()
        assert self.widget.tab_widget is not None
        assert self.widget.tab_widget.count() == 2  # Teams and Players tabs
    
    def test_teams_table_model(self, qtbot):
        """Test the teams table model"""
        model = self.widget.teams_model
        
        # Check that data is loaded
        assert model.rowCount() > 0
        assert model.columnCount() == 3  # ID, Name, Division
        
        # Check first row data
        index = model.index(0, 1)  # Name column
        assert model.data(index) is not None
        
        # Test refresh
        initial_count = model.rowCount()
        model.refresh()
        assert model.rowCount() == initial_count
    
    def test_players_table_model(self, qtbot):
        """Test the players table model"""
        model = self.widget.players_model
        
        # Check that data is loaded
        assert model.rowCount() > 0
        assert model.columnCount() == 4  # ID, Name, Position, Team
        
        # Check first row data
        index = model.index(0, 1)  # Name column
        assert model.data(index) is not None
        
        # Test refresh
        initial_count = model.rowCount()
        model.refresh()
        assert model.rowCount() == initial_count
    
    def test_add_team_dialog(self, qtbot):
        """Test adding a new team"""
        # Click Add Team button
        qtbot.mouseClick(self.widget.add_team_btn, Qt.LeftButton)
        
        # Wait for dialog to appear
        qtbot.wait(200)
        
        # Find the dialog
        dialog = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, AddTeamDialog):
                dialog = widget
                break
        
        assert dialog is not None
        
        # Fill in team details
        qtbot.keyClicks(dialog.name_edit, "Test Team")
        dialog.division_combo.setCurrentIndex(0)  # Select first division
        
        # Save the team
        qtbot.mouseClick(dialog.save_button, Qt.LeftButton)
        
        # Check that dialog is closed
        qtbot.wait(100)
        
        # Verify team was added to database
        team = self.db_manager.fetch_one("SELECT * FROM teams WHERE name = ?", ("Test Team",))
        assert team is not None
        assert team['name'] == "Test Team"
    
    def test_edit_team_dialog(self, qtbot):
        """Test editing an existing team"""
        # Select first team in table
        self.widget.teams_table.selectRow(0)
        
        # Click Edit Team button
        qtbot.mouseClick(self.widget.edit_team_btn, Qt.LeftButton)
        
        # Wait for dialog to appear
        qtbot.wait(200)
        
        # Find the dialog
        dialog = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, AddTeamDialog):
                dialog = widget
                break
        
        assert dialog is not None
        assert dialog.team_id is not None  # Should be editing mode
        
        # Modify team name
        dialog.name_edit.clear()
        qtbot.keyClicks(dialog.name_edit, "Updated Team")
        
        # Save the team
        qtbot.mouseClick(dialog.save_button, Qt.LeftButton)
        
        # Wait for dialog to close
        qtbot.wait(100)
        
        # Verify team was updated in database
        team = self.db_manager.fetch_one("SELECT * FROM teams WHERE name = ?", ("Updated Team",))
        assert team is not None
        assert team['name'] == "Updated Team"
    
    def test_delete_team(self, qtbot, monkeypatch):
        """Test deleting a team"""
        # Get initial count
        initial_teams = len(self.db_manager.fetch_all("SELECT * FROM teams"))
        
        # Select first team in table
        self.widget.teams_table.selectRow(0)
        
        # Mock the confirmation dialog to return Yes
        def mock_question(*args, **kwargs):
            return QMessageBox.Yes
        
        monkeypatch.setattr(QMessageBox, 'question', mock_question)
        
        # Click Delete Team button
        qtbot.mouseClick(self.widget.delete_team_btn, Qt.LeftButton)
        
        # Wait for deletion to complete
        qtbot.wait(100)
        
        # Verify team was deleted from database
        remaining_teams = len(self.db_manager.fetch_all("SELECT * FROM teams"))
        assert remaining_teams == initial_teams - 1
    
    def test_add_player_dialog(self, qtbot):
        """Test adding a new player"""
        # Switch to Players tab
        self.widget.tab_widget.setCurrentIndex(1)
        
        # Click Add Player button
        qtbot.mouseClick(self.widget.add_player_btn, Qt.LeftButton)
        
        # Wait for dialog to appear
        qtbot.wait(200)
        
        # Find the dialog
        dialog = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, AddPlayerDialog):
                dialog = widget
                break
        
        assert dialog is not None
        
        # Fill in player details
        qtbot.keyClicks(dialog.name_edit, "Test Player")
        dialog.position_combo.setCurrentIndex(0)  # Select first position
        dialog.team_combo.setCurrentIndex(0)  # Select first team
        
        # Save the player
        qtbot.mouseClick(dialog.save_button, Qt.LeftButton)
        
        # Wait for dialog to close
        qtbot.wait(100)
        
        # Verify player was added to database
        player = self.db_manager.fetch_one("SELECT * FROM players WHERE name = ?", ("Test Player",))
        assert player is not None
        assert player['name'] == "Test Player"
    
    def test_edit_player_dialog(self, qtbot):
        """Test editing an existing player"""
        # Switch to Players tab
        self.widget.tab_widget.setCurrentIndex(1)
        
        # Select first player in table
        self.widget.players_table.selectRow(0)
        
        # Click Edit Player button
        qtbot.mouseClick(self.widget.edit_player_btn, Qt.LeftButton)
        
        # Wait for dialog to appear
        qtbot.wait(200)
        
        # Find the dialog
        dialog = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, AddPlayerDialog):
                dialog = widget
                break
        
        assert dialog is not None
        assert dialog.player_id is not None  # Should be editing mode
        
        # Modify player name
        dialog.name_edit.clear()
        qtbot.keyClicks(dialog.name_edit, "Updated Player")
        
        # Save the player
        qtbot.mouseClick(dialog.save_button, Qt.LeftButton)
        
        # Wait for dialog to close
        qtbot.wait(100)
        
        # Verify player was updated in database
        player = self.db_manager.fetch_one("SELECT * FROM players WHERE name = ?", ("Updated Player",))
        assert player is not None
        assert player['name'] == "Updated Player"
    
    def test_delete_player(self, qtbot, monkeypatch):
        """Test deleting a player"""
        # Switch to Players tab
        self.widget.tab_widget.setCurrentIndex(1)
        
        # Get initial count
        initial_players = len(self.db_manager.fetch_all("SELECT * FROM players"))
        
        # Select first player in table
        self.widget.players_table.selectRow(0)
        
        # Mock the confirmation dialog to return Yes
        def mock_question(*args, **kwargs):
            return QMessageBox.Yes
        
        monkeypatch.setattr(QMessageBox, 'question', mock_question)
        
        # Click Delete Player button
        qtbot.mouseClick(self.widget.delete_player_btn, Qt.LeftButton)
        
        # Wait for deletion to complete
        qtbot.wait(100)
        
        # Verify player was deleted from database
        remaining_players = len(self.db_manager.fetch_all("SELECT * FROM players"))
        assert remaining_players == initial_players - 1
    
    def test_validation_errors(self, qtbot):
        """Test validation errors in dialogs"""
        # Test team validation
        qtbot.mouseClick(self.widget.add_team_btn, Qt.LeftButton)
        
        dialog = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, AddTeamDialog):
                dialog = widget
                break
        
        assert dialog is not None
        
        # Try to save without name
        qtbot.mouseClick(dialog.save_button, Qt.LeftButton)
        
        # Should show validation error
        qtbot.wait(100)
        
        # Close dialog
        qtbot.mouseClick(dialog.cancel_button, Qt.LeftButton)
        
        # Test player validation
        self.widget.tab_widget.setCurrentIndex(1)
        qtbot.mouseClick(self.widget.add_player_btn, Qt.LeftButton)
        
        dialog = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, AddPlayerDialog):
                dialog = widget
                break
        
        assert dialog is not None
        
        # Try to save without name
        qtbot.mouseClick(dialog.save_button, Qt.LeftButton)
        
        # Should show validation error
        qtbot.wait(100)
        
        # Close dialog
        qtbot.mouseClick(dialog.cancel_button, Qt.LeftButton)
    
    def test_refresh_functionality(self, qtbot):
        """Test refresh functionality"""
        # Test teams refresh
        initial_count = self.widget.teams_model.rowCount()
        qtbot.mouseClick(self.widget.refresh_teams_btn, Qt.LeftButton)
        assert self.widget.teams_model.rowCount() == initial_count
        
        # Test players refresh
        self.widget.tab_widget.setCurrentIndex(1)
        initial_count = self.widget.players_model.rowCount()
        qtbot.mouseClick(self.widget.refresh_players_btn, Qt.LeftButton)
        assert self.widget.players_model.rowCount() == initial_count
    
    def test_selection_functionality(self, qtbot):
        """Test table selection functionality"""
        # Test team selection
        self.widget.teams_table.selectRow(0)
        team_id = self.widget.get_selected_team_id()
        assert team_id is not None
        
        # Test player selection
        self.widget.tab_widget.setCurrentIndex(1)
        self.widget.players_table.selectRow(0)
        player_id = self.widget.get_selected_player_id()
        assert player_id is not None
    
    def test_cascade_delete_team(self, qtbot, monkeypatch):
        """Test that deleting a team cascades to delete its players"""
        # Get initial counts
        initial_teams = len(self.db_manager.fetch_all("SELECT * FROM teams"))
        initial_players = len(self.db_manager.fetch_all("SELECT * FROM players"))
        
        # Select first team in table
        self.widget.teams_table.selectRow(0)
        
        # Mock the confirmation dialog to return Yes
        def mock_question(*args, **kwargs):
            return QMessageBox.Yes
        
        monkeypatch.setattr(QMessageBox, 'question', mock_question)
        
        # Click Delete Team button
        qtbot.mouseClick(self.widget.delete_team_btn, Qt.LeftButton)
        
        # Wait for deletion to complete
        qtbot.wait(100)
        
        # Verify team and its players were deleted
        remaining_teams = len(self.db_manager.fetch_all("SELECT * FROM teams"))
        remaining_players = len(self.db_manager.fetch_all("SELECT * FROM players"))
        
        assert remaining_teams == initial_teams - 1
        assert remaining_players < initial_players  # Some players should be deleted due to cascade
    
    def test_dialog_cancel(self, qtbot):
        """Test canceling dialogs"""
        # Test team dialog cancel
        qtbot.mouseClick(self.widget.add_team_btn, Qt.LeftButton)
        
        dialog = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, AddTeamDialog):
                dialog = widget
                break
        
        assert dialog is not None
        
        # Cancel the dialog
        qtbot.mouseClick(dialog.cancel_button, Qt.LeftButton)
        qtbot.wait(100)
        assert not dialog.isVisible()
        
        # Test player dialog cancel
        self.widget.tab_widget.setCurrentIndex(1)
        qtbot.mouseClick(self.widget.add_player_btn, Qt.LeftButton)
        
        dialog = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, AddPlayerDialog):
                dialog = widget
                break
        
        assert dialog is not None
        
        # Cancel the dialog
        qtbot.mouseClick(dialog.cancel_button, Qt.LeftButton)
        qtbot.wait(100)
        assert not dialog.isVisible()
