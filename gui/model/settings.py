from enum import Enum

from PySide6.QtCore import (
    QObject, 
    QDir,
    QFileInfo,
    Signal,
)

class EnvironmentManagers(Enum):
    CONDA = "conda"
    MINICONDA = "miniconda"
    MAMBA = "mamba"
    MICROMAMBA = "micromamba"

class Settings(QObject):
    workspace_path_changed = Signal(str)
    executable_file_path_changed = Signal(str)
    enviroment_manager_changed = Signal(str)
    environment_name_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._workspace_path = QDir()
        self._executable_file_path = QFileInfo()
        self._environment_manager = EnvironmentManagers.MICROMAMBA
        self._environment_name = ""

    @property
    def workspace_path(self) -> str:
        return self._workspace_path.absolutePath()

    @workspace_path.setter
    def workspace_path(self, value: QDir) -> None:
        if self._workspace_path != value:
            self._workspace_path = value
            self.workspace_path_changed.emit(value.absolutePath())

    @property
    def executable_file_path(self) -> str:
        return self._executable_file_path.absoluteFilePath()

    @executable_file_path.setter
    def executable_file_path(self, value: QFileInfo) -> None:
        if self._executable_file_path != value:
            self._executable_file_path = value
            self.executable_file_path_changed.emit(value.absoluteFilePath())

    @property
    def executable_folder_path(self) -> str:
        return self._executable_file_path.absolutePath()

    @property
    def environment_manager(self) -> str:
        return self._environment_manager.value

    @environment_manager.setter
    def environment_manager(self, value: EnvironmentManagers) -> None:
        if self._environment_manager != value:
            self._environment_manager = value
            self.enviroment_manager_changed.emit(value.value)

    @property
    def environment_name(self) -> str:
        return self._environment_name

    @environment_name.setter
    def environment_name(self, value: str) -> None:
        if self._environment_name != value:
            self._environment_name = value
            self.environment_name_changed.emit(value)

# create a global singleton instance
app_settings = Settings()