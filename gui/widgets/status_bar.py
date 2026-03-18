from PySide6.QtCore import (
    Slot,
    QDir,
)
from PySide6.QtWidgets import (
    QLabel,
    QStatusBar,
)

from gui.model.settings import app_settings


class StatusBar(QStatusBar):
    """
    Class to represent the status bar of the RAiSD-AI GUI application.
    """
    def __init__(self) -> None:
        """
        Initialize the `StatusBar`.
        """
        super().__init__()
        self.setStyleSheet("background-color: lightgray;")

        # Label to show the current workspace path
        self.workspace_label = QLabel()
        self.update_workspace_label(app_settings.workspace_path)
        self.addWidget(self.workspace_label)

    @Slot(QDir)
    def update_workspace_label(self, new_workspace: QDir) -> None:
        """Update the workspace label to show the current workspace path."""
        self.workspace_label.setText(f"Current Workspace: '{new_workspace.absolutePath()}'")