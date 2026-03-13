import sys

from PySide6.QtWidgets import QApplication, QStyleFactory

from gui.model.parameter_group_list import ParameterGroupList
from gui.windows.main import MainWindow


def main():
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("windowsvista"))

    parameter_group_list = ParameterGroupList.from_configuration_file(
        "gui/..."
    ) # TODO: implement config file and write path

    run_result = RunResult(parameter_group_list, QDir.currentPath())
    window.show()
    app.exec()
    print("App closed")


if __name__ == "__main__":
    main()
