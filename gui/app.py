import sys
import sass

from PySide6.QtCore import (
    QDir,
    QFileInfo,
)
from PySide6.QtWidgets import (
    QApplication,
    QStyleFactory,
)

from gui.model.settings import app_settings, EnvironmentManager
from gui.model.parameter_group_list import ParameterGroupList
from gui.windows.main import MainWindow
from gui.model.run_result import RunResult



def main():
    app = QApplication(sys.argv)

    # Set styling
    with open("gui/style/variables.scss", "r") as f:
        variables = f.read()

    with open("gui/style/style.qss", "r") as f:
        stylesheet = f.read()

    final_stylesheet = variables + stylesheet
    final_stylesheet = sass.compile(string=final_stylesheet)

    app.setStyleSheet(final_stylesheet)

    # Set main window
    window = MainWindow()
    window.resize(1200,800)
    window.show()
    app.exec()
    print("App closed")


if __name__ == "__main__":
    main()
