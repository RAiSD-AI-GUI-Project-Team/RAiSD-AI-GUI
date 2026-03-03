from typing import Any
from abc import ABC

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton

from gui.model.parameter import (
    Parameter,
    BoolParameter,
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
        along with a label and reset button.

        The method checks the type of the given parameter in order to
        create the suitable widget (e.g. a dropdown menu for an enum
        parameter). This is the recommended method of creating a
        `ParameterWidget` object.

        The method also creates a label that displays the parameter's
        name and a reset button that restores the default value. These
        are returned in a horizontal layout alongside the `ParameterWidget` object.

        :param parameter: the parameter
        :type parameter: Parameter[Any]

        :return: the label with reset button container and the widget
        :rtype: tuple[QWidget, ParameterWidget]
        """
        # Create label
        label_widget = QLabel(parameter.name)

        # Create reset button
        reset_button = QPushButton("Reset")
        reset_button.setToolTip(f"Reset to default value: {parameter.default_value}")

        # Create container for label and reset button
        label_container = QWidget()
        label_layout = QHBoxLayout(label_container)
        label_layout.addWidget(label_widget)
        label_layout.addWidget(reset_button)
        label_layout.setContentsMargins(0, 0, 0, 0)

        # Create appropriate widget based on parameter type
        if isinstance(parameter, BoolParameter):
            widget = BoolParameterWidget(parameter)
        else:
            # TODO: implement selection of widget subclass for other parameter types
            raise NotImplementedError(f"ParameterWidget#from_parameter not implemented for {type(parameter)}!")

        # Connect reset button to parameter's reset method
        reset_button.clicked.connect(lambda: parameter.reset_value())

        return label_container, widget


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
