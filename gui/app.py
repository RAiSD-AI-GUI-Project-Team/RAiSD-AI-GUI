import sys

from PySide6.QtCore import (
    QDir,
    QFileInfo,
)
from PySide6.QtWidgets import (
    QApplication, 
    QStyleFactory,
)

from gui.model.settings import app_settings, EnvironmentManagers
from gui.model.parameter_group_list import ParameterGroupList
from gui.windows.main import MainWindow


def main():
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("windowsvista"))

    app_settings.workspace_path = QDir()
    app_settings.executable_file_path = QFileInfo(QDir().absoluteFilePath("RAiSD-AI"))
    app_settings.environment_manager = EnvironmentManagers.MICROMAMBA
    app_settings.environment_name = "raisd-ai"

    parameter_group_list = ParameterGroupList.from_configuration_file(
        "gui/..."
    ) # TODO: implement config file and write path

    window = MainWindow(parameter_group_list=parameter_group_list)  
    window.show()
    app.exec()
    print("App closed")


if __name__ == "__main__":
    main()
