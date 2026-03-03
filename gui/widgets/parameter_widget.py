from typing import Any
from abc import ABC

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QCheckBox,
    QSpinBox, QDoubleSpinBox
)

from gui.model.parameter import (
    Parameter,
    BoolParameter,
    IntParameter,
    FloatParameter,
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
        elif isinstance(parameter, IntParameter):
            return label, IntParameterWidget(parameter)
        elif isinstance(parameter, FloatParameter):
            return label, FloatParameterWidget(parameter)

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


class IntParameterWidget(ParameterWidget):
    """
    A widget to edit an integer parameter with optional bounds.
    """

    def __init__(self, parameter: IntParameter) -> None:
        """
        Initialize an IntParameterWidget object.

        :param parameter: the integer parameter to reference
        :type parameter: IntParameter
        """
        super().__init__(parameter)

        layout = QVBoxLayout(self)
        self._spinbox = QSpinBox()
        
        # Set bounds if specified
        if parameter.lower_bound is not None:
            self._spinbox.setMinimum(parameter.lower_bound)
        else:
            self._spinbox.setMinimum(-2147483648)  # INT_MIN
            
        if parameter.upper_bound is not None:
            self._spinbox.setMaximum(parameter.upper_bound)
        else:
            self._spinbox.setMaximum(2147483647)  # INT_MAX
            
        self._spinbox.setValue(parameter.value)
        layout.addWidget(self._spinbox)

        # Add bounds label if bounds are specified
        if parameter.lower_bound is not None or parameter.upper_bound is not None:
            bounds_text = f"Valid range: [{parameter.lower_bound or '-∞'}, {parameter.upper_bound or '∞'}]"
            bounds_label = QLabel(bounds_text)
            bounds_label.setStyleSheet("color: gray; font-size: 9pt;")
            layout.addWidget(bounds_label)

        self._spinbox.valueChanged.connect(self._spinbox_value_changed)
        parameter.value_changed.connect(self._parameter_value_changed)

    @Slot(int)
    def _spinbox_value_changed(self, new_value: int) -> None:
        self.parameter.value = new_value

    @Slot(int, bool)
    def _parameter_value_changed(self, new_value: int, valid: bool) -> None:
        self._spinbox.setValue(new_value)


class FloatParameterWidget(ParameterWidget):
    """
    A widget to edit a floating point parameter with optional bounds.
    """

    def __init__(self, parameter: FloatParameter) -> None:
        """
        Initialize a FloatParameterWidget object.

        :param parameter: the float parameter to reference
        :type parameter: FloatParameter
        """
        super().__init__(parameter)

        layout = QVBoxLayout(self)
        self._spinbox = QDoubleSpinBox()
        
        # Set bounds if specified
        if parameter.lower_bound is not None:
            self._spinbox.setMinimum(parameter.lower_bound)
        else:
            self._spinbox.setMinimum(float('-inf'))
            
        if parameter.upper_bound is not None:
            self._spinbox.setMaximum(parameter.upper_bound)
        else:
            self._spinbox.setMaximum(float('inf'))
            
        self._spinbox.setValue(parameter.value)
        self._spinbox.setDecimals(4)  # Default precision
        layout.addWidget(self._spinbox)

        # Add bounds label if bounds are specified
        if parameter.lower_bound is not None or parameter.upper_bound is not None:
            bounds_text = f"Valid range: [{parameter.lower_bound or '-∞'}, {parameter.upper_bound or '∞'}]"
            bounds_label = QLabel(bounds_text)
            bounds_label.setStyleSheet("color: gray; font-size: 9pt;")
            layout.addWidget(bounds_label)

        self._spinbox.valueChanged.connect(self._spinbox_value_changed)
        parameter.value_changed.connect(self._parameter_value_changed)

    @Slot(float)
    def _spinbox_value_changed(self, new_value: float) -> None:
        self.parameter.value = new_value

    @Slot(float, bool)
    def _parameter_value_changed(self, new_value: float, valid: bool) -> None:
        self._spinbox.setValue(new_value)
