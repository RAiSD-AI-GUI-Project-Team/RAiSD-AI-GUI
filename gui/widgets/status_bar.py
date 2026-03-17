from PySide6.QtCore import (
    Signal,
    QDir,
)
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedLayout,
    QScrollArea,
    QPushButton,
    QLabel,
    QStatusBar,
)

from gui.model.settings import app_settings

class StatusBar(QStatusBar):
    workspace_path_changed = Signal(QDir)

    def __init__(self) -> None:
        super().__init__()
        self.setStyleSheet("background-color: lightgray;")

        self.workspace_button = QPushButton()
        self.workspace_button.clicked.connect(app_settings.set_workspace_folder)
        self.workspace_path_changed.connect(self.update_workspace_button)
        self.update_workspace_button(app_settings.workspace_path)

        self.addWidget(self.workspace_button)

    def update_workspace_button(self, new_workspace: QDir) -> None:
        self.workspace_button.setText(f"Current Workspace: '{new_workspace.absolutePath()}'")