from enum import Enum

from PySide6.QtCore import (
    QObject, 
    QDir,
    QFileInfo,
    Signal,
)
from PySide6.QtWidgets import (
    QFileDialog,
)

class EnvironmentManager(Enum):
    CONDA = "conda"
    MINICONDA = "miniconda"
    MAMBA = "mamba"
    MICROMAMBA = "micromamba"

class Settings(QObject):
    workspace_path_changed = Signal(QDir)
    executable_file_path_changed = Signal(QFileInfo)
    enviroment_manager_changed = Signal(EnvironmentManager)
    environment_name_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._workspace_path = QDir()
        self._executable_file_path = QFileInfo()
        self._environment_manager = EnvironmentManager.MICROMAMBA
        self._environment_name = ""

    @property
    def workspace_path(self) -> QDir:
        return self._workspace_path

    @workspace_path.setter
    def workspace_path(self, value: QDir) -> None:
        if self._workspace_path != value:
            self._workspace_path = value
            self.workspace_path_changed.emit(value)

    @property
    def executable_file_path(self) -> QFileInfo:
        return self._executable_file_path

    @executable_file_path.setter
    def executable_file_path(self, value: QFileInfo) -> None:
        if self._executable_file_path != value:
            self._executable_file_path = value
            self.executable_file_path_changed.emit(value)

    @property
    def executable_folder_path(self) -> QDir:
        return self._executable_file_path.absoluteDir()

    @property
    def environment_manager(self) -> EnvironmentManager:
        return self._environment_manager

    @environment_manager.setter
    def environment_manager(self, value: EnvironmentManager) -> None:
        if self._environment_manager != value:
            self._environment_manager = value
            self.enviroment_manager_changed.emit(value)

    @property
    def environment_name(self) -> str:
        return self._environment_name

    @environment_name.setter
    def environment_name(self, value: str) -> None:
        if self._environment_name != value:
            self._environment_name = value
            self.environment_name_changed.emit(value)

    def set_workspace_folder(self) -> None:
        new_workspace_folder_str = QFileDialog.getExistingDirectory(
            None,
            "Select Workspace Folder",
            self._workspace_path.absolutePath(),
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        if not new_workspace_folder_str:  # Check for empty string (canceled)
            return  
        try:
            app_settings.workspace_path = QDir(new_workspace_folder_str)
        except Exception as e:
            print(f"Error setting workspace: {e}")

# create a global singleton instance
app_settings = Settings()