from typing import Any
from abc import ABC
from pathlib import Path

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QCheckBox, QFileDialog, QPushButton

from gui.model.parameter import (
    Parameter,
    BoolParameter, FileParameter,
)


class AbstractQWidgetMeta(type(ABC), type(QWidget)):
    """
    Metaclass for an abstract base QWidget class.
    """

    pass


class ParameterWidget(ABC, QWidget, metaclass=AbstractQWidgetMeta):
    """
    A base class for input widgets to fill in parameters using the GUI.

    The class inherits from `ABC` to make it abstract and from
    `QWidget`.

    A `ParameterWidget` object holds a reference to a `Parameter`
    object, which it updates with values entered by the user.

    `ParameterWidget` objects should not be created directly, but
    through the `from_parameter` factory method.
    """

    def __init__(self, parameter: Parameter[Any]):
        """
        Initialize a `ParameterWidget` object.

        :param parameter: the parameter to reference
        :type parameter: Parameter[Any]
        """
        super().__init__()
        self._parameter = parameter

    @property
    def parameter(self) -> Parameter[Any]:
        """
        The `Parameter` object referenced by the widget.
        """
        return self._parameter        

    @classmethod
    def from_parameter(cls, parameter: Parameter[Any]) -> tuple[QWidget, "ParameterWidget"]:
        """
        Create a suitable `ParameterWidget` for a given `Parameter`,
        along with a label.

        The method checks the type of the given parameter in order to
        create the suitable widget (e.g. a dropdown menu for an enum
        parameter). This is the recommended method of creating a
        `ParameterWidget` object.

        The method also creates a label that displays the parameter's
        name and returns it alongside the `ParameterWidget` object.

        :param parameter: the parameter
        :type parameter: Parameter[Any]

        :return: the label and the widget
        :rtype: tuple[QWidget, ParameterWidget]
        """
        label: QWidget = QLabel(parameter.name)

        if isinstance(parameter, BoolParameter):
            return label, BoolParameterWidget(parameter)
        elif isinstance(parameter, FileParameter):
            return label, FileParameterWidget(parameter)

        # TODO: implement selection of widget subclass for other parameter types
        raise NotImplementedError(f"ParameterWidget#from_parameter not implemented for {type(parameter)}!")


class BoolParameterWidget(ParameterWidget):
    """
    A widget to edit a boolean parameter.
    """

    def __init__(self, parameter: Parameter[bool]) -> None:
        """
        Initialize a `BoolParameterWidget` object.

        :param parameter: the boolean parameter to reference
        :type parameter: Parameter[bool]
        """
        super().__init__(parameter)

        layout = QVBoxLayout(self)
        self._checkbox = QCheckBox()
        self._checkbox.setCheckState(
            Qt.CheckState.Checked
            if parameter.value
            else Qt.CheckState.Unchecked
        )
        layout.addWidget(self._checkbox)

        self._checkbox.checkStateChanged.connect(self._check_state_changed)
        parameter.value_changed.connect(self._parameter_value_changed)

    @Slot(Qt.CheckState)
    def _check_state_changed(self, new_check_state: Qt.CheckState) -> None:
        match new_check_state:
            case Qt.CheckState.Checked:
                self.parameter.value = True
            case Qt.CheckState.Unchecked:
                self.parameter.value = False

    @Slot(bool, bool)
    def _parameter_value_changed(self, new_value: bool, valid: bool) -> None:
        self._checkbox.setChecked(new_value)

class FileParameterWidget(ParameterWidget):
    """
    A widget to edit a file parameter.

    Provides a browse button that opens a file dialog that is filtered with file types that are allowed file types.
    Depending on the state of multiple flag, the file dialog enforces multiple or singular file selection.
    Displays the currently selected file path(s).
    """
    def __init__(self, parameter: FileParameter) -> None:
        super().__init__(parameter)
        self._file_parameter: FileParameter = parameter

        layout = QVBoxLayout(self)

        self._path_label = QLabel("No file selected")
        layout.addWidget(self._path_label)

        mode = "multiple files" if parameter.multiple else "one file"
        hint = QLabel(f"Select {mode} — Allowed types: {', '.join(parameter.accepted_formats)}")
        layout.addWidget(hint)

        parameter.value_changed.connect(self._parameter_value_changed)

        file_browse = QPushButton('Browse')
        file_browse.clicked.connect(self._open_file_dialog)

        layout.addWidget(file_browse)


    @Slot(list, bool)
    def _parameter_value_changed(self, file_paths: list[str], valid: bool) -> None:
        if file_paths:
            self._path_label.setText("\n".join(file_paths))
        else:
            self._path_label.setText("No file selected")

    @Slot()
    def _open_file_dialog(self) -> None:
        """
        Helper function that opens the OS file picker. If multiple flag is True, it uses getOpenFileNames
        to allow for multiple file selection. Otherwise, if multiple flag is False, it uses getOpenFileName
        to allow for only a single file selection.
        """
        if self._file_parameter.multiple:
            filenames, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Files",
                self._file_parameter.value[0] if self._file_parameter.value else "",
                self._build_filter()
            )
        else:
            single, _ = QFileDialog.getOpenFileName(
                self,
                "Select File",
                self._file_parameter.value[0] if self._file_parameter.value else "",
                self._build_filter()
            )
            filenames = [single] if single else []

        if filenames:
            self._file_parameter.value = [Path(f).as_posix() for f in filenames]

    def _build_filter(self) -> str:
        """
        Helper function to filter and show only allowed file types to the user
        """
        extensions = " ".join(f"*{ext}" for ext in self._file_parameter.accepted_formats)
        return f"Allowed files ({extensions})"

