from PySide6.QtCore import (
    QFileInfo,
    QDir,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from gui.model.settings import EnvironmentManager, app_settings

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background-color: lightyellow;")
        layout = QVBoxLayout(self)
        settings_label = QLabel("Settings")
        layout.addWidget(settings_label)

        workspace_widget = QWidget()
        workspace_layout = QHBoxLayout(workspace_widget)

        self.workspace_label = QLabel()
        self._update_workspace_label(app_settings.workspace_path)
        app_settings.workspace_path_changed.connect(self._update_workspace_label)
        workspace_layout.addWidget(self.workspace_label, 1)

        self.workspace_chooser = QPushButton("Set Workspace")
        self.workspace_chooser.clicked.connect(app_settings.set_workspace_folder)
        workspace_layout.addWidget(self.workspace_chooser)

        layout.addWidget(workspace_widget)

        self.executable_label = QLabel()
        self._update_executable_label(app_settings.executable_file_path)
        app_settings.executable_file_path_changed.connect(self._update_executable_label)
        layout.addWidget(self.executable_label)

        self.environment_manager_label = QLabel()
        self._update_environment_manager_label(app_settings.environment_manager)
        app_settings.enviroment_manager_changed.connect(self._update_environment_manager_label)
        layout.addWidget(self.environment_manager_label)

        self.environment_name_label = QLabel()
        self._update_environment_name_label(app_settings.environment_name)
        app_settings.environment_name_changed.connect(self._update_environment_name_label)
        layout.addWidget(self.environment_name_label)

    def _update_workspace_label(self, path: QDir) -> None:
        self.workspace_label.setText(f"Current Workspace: '{path.absolutePath()}'")

    def _update_executable_label(self, path: QFileInfo) -> None:
        self.executable_label.setText(f"Current Executable: '{path.absoluteFilePath()}'")

    def _update_environment_manager_label(self, manager: EnvironmentManager) -> None:
        self.environment_manager_label.setText(f"Current Environment Manager: '{manager.value}'")

    def _update_environment_name_label(self, name: str) -> None:
        self.environment_name_label.setText(f"Current Environment Name: '{name}'")