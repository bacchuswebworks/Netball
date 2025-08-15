"""
Team and Player Management UI
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableView, 
    QPushButton, QLabel, QLineEdit, QComboBox, QFormLayout,
    QDialog, QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont
from models.database_manager import DatabaseManager
from models.schema import DatabaseSchema


class TeamsTableModel(QAbstractTableModel):
    """Table model for teams data"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.headers = ["ID", "Name", "Division"]
        self._load_data()
    
    def _load_data(self):
        """Load teams data from database"""
        self.teams_data = self.db_manager.fetch_all("""
            SELECT t.id, t.name, d.name as division_name
            FROM teams t
            JOIN divisions d ON t.division_id = d.id
            ORDER BY t.name
        """)
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.teams_data)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            
            if col == 0:  # ID
                return str(self.teams_data[row]['id'])
            elif col == 1:  # Name
                return self.teams_data[row]['name']
            elif col == 2:  # Division
                return self.teams_data[row]['division_name']
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None
    
    def refresh(self):
        """Refresh the data from database"""
        self.beginResetModel()
        self._load_data()
        self.endResetModel()


class PlayersTableModel(QAbstractTableModel):
    """Table model for players data"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.headers = ["ID", "Name", "Position", "Team"]
        self._load_data()
    
    def _load_data(self):
        """Load players data from database"""
        self.players_data = self.db_manager.fetch_all("""
            SELECT p.id, p.name, p.position, t.name as team_name
            FROM players p
            JOIN teams t ON p.team_id = t.id
            ORDER BY p.name
        """)
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.players_data)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            
            if col == 0:  # ID
                return str(self.players_data[row]['id'])
            elif col == 1:  # Name
                return self.players_data[row]['name']
            elif col == 2:  # Position
                return self.players_data[row]['position']
            elif col == 3:  # Team
                return self.players_data[row]['team_name']
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None
    
    def refresh(self):
        """Refresh the data from database"""
        self.beginResetModel()
        self._load_data()
        self.endResetModel()


class AddTeamDialog(QDialog):
    """Dialog for adding/editing teams"""
    
    def __init__(self, db_manager: DatabaseManager, team_id=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.team_id = team_id
        self.setup_ui()
        self.load_divisions()
        
        if team_id:
            self.setWindowTitle("Edit Team")
            self.load_team_data()
        else:
            self.setWindowTitle("Add Team")
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setModal(True)
        self.setFixedSize(300, 150)
        self.show()
        
        layout = QFormLayout()
        
        # Team name input
        self.name_edit = QLineEdit()
        layout.addRow("Team Name:", self.name_edit)
        
        # Division selection
        self.division_combo = QComboBox()
        layout.addRow("Division:", self.division_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        
        self.save_button.clicked.connect(self.save_team)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addRow("", button_layout)
        self.setLayout(layout)
    
    def load_divisions(self):
        """Load divisions into combo box"""
        divisions = self.db_manager.fetch_all("SELECT id, name FROM divisions ORDER BY name")
        self.division_combo.clear()
        for division in divisions:
            self.division_combo.addItem(division['name'], division['id'])
    
    def load_team_data(self):
        """Load existing team data for editing"""
        team = self.db_manager.fetch_one("""
            SELECT t.name, t.division_id 
            FROM teams t 
            WHERE t.id = ?
        """, (self.team_id,))
        
        if team:
            self.name_edit.setText(team['name'])
            # Find and select the division
            for i in range(self.division_combo.count()):
                if self.division_combo.itemData(i) == team['division_id']:
                    self.division_combo.setCurrentIndex(i)
                    break
    
    def save_team(self):
        """Save team to database"""
        name = self.name_edit.text().strip()
        division_id = self.division_combo.currentData()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Team name is required.")
            return
        
        if not division_id:
            QMessageBox.warning(self, "Validation Error", "Please select a division.")
            return
        
        try:
            if self.team_id:
                # Update existing team
                self.db_manager.execute_query(
                    "UPDATE teams SET name = ?, division_id = ? WHERE id = ?",
                    (name, division_id, self.team_id)
                )
            else:
                # Insert new team
                self.db_manager.execute_query(
                    "INSERT INTO teams (name, division_id) VALUES (?, ?)",
                    (name, division_id)
                )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save team: {str(e)}")


class AddPlayerDialog(QDialog):
    """Dialog for adding/editing players"""
    
    def __init__(self, db_manager: DatabaseManager, player_id=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.player_id = player_id
        self.setup_ui()
        self.load_teams()
        
        if player_id:
            self.setWindowTitle("Edit Player")
            self.load_player_data()
        else:
            self.setWindowTitle("Add Player")
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setModal(True)
        self.setFixedSize(300, 200)
        self.show()
        
        layout = QFormLayout()
        
        # Player name input
        self.name_edit = QLineEdit()
        layout.addRow("Player Name:", self.name_edit)
        
        # Position selection
        self.position_combo = QComboBox()
        positions = ["Goal Shooter", "Goal Attack", "Wing Attack", "Center", "Wing Defense", "Goal Defense", "Goal Keeper"]
        self.position_combo.addItems(positions)
        layout.addRow("Position:", self.position_combo)
        
        # Team selection
        self.team_combo = QComboBox()
        layout.addRow("Team:", self.team_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        
        self.save_button.clicked.connect(self.save_player)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addRow("", button_layout)
        self.setLayout(layout)
    
    def load_teams(self):
        """Load teams into combo box"""
        teams = self.db_manager.fetch_all("""
            SELECT t.id, t.name, d.name as division_name
            FROM teams t
            JOIN divisions d ON t.division_id = d.id
            ORDER BY t.name
        """)
        self.team_combo.clear()
        for team in teams:
            self.team_combo.addItem(f"{team['name']} ({team['division_name']})", team['id'])
    
    def load_player_data(self):
        """Load existing player data for editing"""
        player = self.db_manager.fetch_one("""
            SELECT p.name, p.position, p.team_id 
            FROM players p 
            WHERE p.id = ?
        """, (self.player_id,))
        
        if player:
            self.name_edit.setText(player['name'])
            # Find and select the position
            position_index = self.position_combo.findText(player['position'])
            if position_index >= 0:
                self.position_combo.setCurrentIndex(position_index)
            
            # Find and select the team
            for i in range(self.team_combo.count()):
                if self.team_combo.itemData(i) == player['team_id']:
                    self.team_combo.setCurrentIndex(i)
                    break
    
    def save_player(self):
        """Save player to database"""
        name = self.name_edit.text().strip()
        position = self.position_combo.currentText()
        team_id = self.team_combo.currentData()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Player name is required.")
            return
        
        if not team_id:
            QMessageBox.warning(self, "Validation Error", "Please select a team.")
            return
        
        try:
            if self.player_id:
                # Update existing player
                self.db_manager.execute_query(
                    "UPDATE players SET name = ?, position = ?, team_id = ? WHERE id = ?",
                    (name, position, team_id, self.player_id)
                )
            else:
                # Insert new player
                self.db_manager.execute_query(
                    "INSERT INTO players (name, position, team_id) VALUES (?, ?, ?)",
                    (name, position, team_id)
                )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save player: {str(e)}")


class TeamPlayerManagementWidget(QWidget):
    """Main widget for team and player management"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Setup the main UI"""
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Teams tab
        self.teams_tab = QWidget()
        self.setup_teams_tab()
        self.tab_widget.addTab(self.teams_tab, "Teams")
        
        # Players tab
        self.players_tab = QWidget()
        self.setup_players_tab()
        self.tab_widget.addTab(self.players_tab, "Players")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def setup_teams_tab(self):
        """Setup the teams tab"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Team Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_team_btn = QPushButton("Add Team")
        self.edit_team_btn = QPushButton("Edit Team")
        self.delete_team_btn = QPushButton("Delete Team")
        self.refresh_teams_btn = QPushButton("Refresh")
        
        self.add_team_btn.clicked.connect(self.add_team)
        self.edit_team_btn.clicked.connect(self.edit_team)
        self.delete_team_btn.clicked.connect(self.delete_team)
        self.refresh_teams_btn.clicked.connect(self.refresh_teams)
        
        button_layout.addWidget(self.add_team_btn)
        button_layout.addWidget(self.edit_team_btn)
        button_layout.addWidget(self.delete_team_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_teams_btn)
        
        layout.addLayout(button_layout)
        
        # Teams table
        self.teams_table = QTableView()
        self.teams_model = TeamsTableModel(self.db_manager)
        self.teams_table.setModel(self.teams_model)
        
        # Configure table
        self.teams_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.teams_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.teams_table.horizontalHeader().setStretchLastSection(True)
        self.teams_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        layout.addWidget(self.teams_table)
        self.teams_tab.setLayout(layout)
    
    def setup_players_tab(self):
        """Setup the players tab"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Player Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_player_btn = QPushButton("Add Player")
        self.edit_player_btn = QPushButton("Edit Player")
        self.delete_player_btn = QPushButton("Delete Player")
        self.refresh_players_btn = QPushButton("Refresh")
        
        self.add_player_btn.clicked.connect(self.add_player)
        self.edit_player_btn.clicked.connect(self.edit_player)
        self.delete_player_btn.clicked.connect(self.delete_player)
        self.refresh_players_btn.clicked.connect(self.refresh_players)
        
        button_layout.addWidget(self.add_player_btn)
        button_layout.addWidget(self.edit_player_btn)
        button_layout.addWidget(self.delete_player_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_players_btn)
        
        layout.addLayout(button_layout)
        
        # Players table
        self.players_table = QTableView()
        self.players_model = PlayersTableModel(self.db_manager)
        self.players_table.setModel(self.players_model)
        
        # Configure table
        self.players_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.players_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.players_table.horizontalHeader().setStretchLastSection(True)
        self.players_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        layout.addWidget(self.players_table)
        self.players_tab.setLayout(layout)
    
    def get_selected_team_id(self):
        """Get the ID of the currently selected team"""
        indexes = self.teams_table.selectedIndexes()
        if indexes:
            row = indexes[0].row()
            return self.teams_model.teams_data[row]['id']
        return None
    
    def get_selected_player_id(self):
        """Get the ID of the currently selected player"""
        indexes = self.players_table.selectedIndexes()
        if indexes:
            row = indexes[0].row()
            return self.players_model.players_data[row]['id']
        return None
    
    def add_team(self):
        """Add a new team"""
        dialog = AddTeamDialog(self.db_manager, parent=self)
        dialog.show()
        if dialog.exec() == QDialog.Accepted:
            self.refresh_teams()
    
    def edit_team(self):
        """Edit the selected team"""
        team_id = self.get_selected_team_id()
        if not team_id:
            QMessageBox.warning(self, "Selection Required", "Please select a team to edit.")
            return
        
        dialog = AddTeamDialog(self.db_manager, team_id, parent=self)
        dialog.show()
        if dialog.exec() == QDialog.Accepted:
            self.refresh_teams()
    
    def delete_team(self):
        """Delete the selected team"""
        team_id = self.get_selected_team_id()
        if not team_id:
            QMessageBox.warning(self, "Selection Required", "Please select a team to delete.")
            return
        
        # Get team name for confirmation
        team = self.db_manager.fetch_one("SELECT name FROM teams WHERE id = ?", (team_id,))
        if not team:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete team '{team['name']}'?\n\nThis will also delete all players in this team.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.execute_query("DELETE FROM teams WHERE id = ?", (team_id,))
                self.refresh_teams()
                self.refresh_players()  # Refresh players as some may have been deleted
                QMessageBox.information(self, "Success", "Team deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete team: {str(e)}")
    
    def add_player(self):
        """Add a new player"""
        dialog = AddPlayerDialog(self.db_manager, parent=self)
        dialog.show()
        if dialog.exec() == QDialog.Accepted:
            self.refresh_players()
    
    def edit_player(self):
        """Edit the selected player"""
        player_id = self.get_selected_player_id()
        if not player_id:
            QMessageBox.warning(self, "Selection Required", "Please select a player to edit.")
            return
        
        dialog = AddPlayerDialog(self.db_manager, player_id, parent=self)
        dialog.show()
        if dialog.exec() == QDialog.Accepted:
            self.refresh_players()
    
    def delete_player(self):
        """Delete the selected player"""
        player_id = self.get_selected_player_id()
        if not player_id:
            QMessageBox.warning(self, "Selection Required", "Please select a player to delete.")
            return
        
        # Get player name for confirmation
        player = self.db_manager.fetch_one("SELECT name FROM players WHERE id = ?", (player_id,))
        if not player:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete player '{player['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.execute_query("DELETE FROM players WHERE id = ?", (player_id,))
                self.refresh_players()
                QMessageBox.information(self, "Success", "Player deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete player: {str(e)}")
    
    def refresh_teams(self):
        """Refresh teams data"""
        self.teams_model.refresh()
    
    def refresh_players(self):
        """Refresh players data"""
        self.players_model.refresh()
    
    def refresh_data(self):
        """Refresh all data"""
        self.refresh_teams()
        self.refresh_players()
