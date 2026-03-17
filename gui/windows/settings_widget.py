from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)

from gui.model.settings import app_settings

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background-color: lightyellow;")
        layout = QVBoxLayout(self)
        settings_label = QLabel("Settings")
        layout.addWidget(settings_label)

        self.workspace_label = QLabel(app_settings.workspace_path)
        app_settings.workspace_path_changed.connect(self.workspace_label.setText)
        layout.addWidget(self.workspace_label)

        self.executable_label = QLabel(app_settings.executable_file_path)
        app_settings.executable_file_path_changed.connect(self.executable_label.setText)
        layout.addWidget(self.executable_label)

        self.environment_manager_label = QLabel(app_settings.environment_manager)
        app_settings.enviroment_manager_changed.connect(self.environment_manager_label.setText)
        layout.addWidget(self.environment_manager_label)

        self.environment_name_label = QLabel(app_settings.environment_name)
        app_settings.environment_name_changed.connect(self.environment_name_label.setText)
        layout.addWidget(self.environment_name_label)

