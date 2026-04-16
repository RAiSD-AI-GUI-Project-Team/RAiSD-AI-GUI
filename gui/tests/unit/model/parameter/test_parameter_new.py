from pytest import fixture, skip

from gui.model.parameter import (
    BoolParameter,
    IntParameter,
    FloatParameter,
    StringParameter,
    EnumParameter,
    FileParameter,
    OptionalParameter,
    MultiParameter,
    CountedMultiParameter,
    StringTableParameter,
)
from gui.model.parameter.constraint import Constraint
from gui.model.parameter.condition import Condition


class TestIntParameter:
    """Unit tests for IntParameter class."""

    @fixture(autouse=True)
    def set_int_param(self, mocker):
        # The typed Signal(Constraint) emit is causing segfaults when the payload is a MagicMock
        def fake_add_constraint(self, constraint, hidden=False):
            if not hidden:
                self._constraints.append(constraint)
            else:
                self._hidden_constraints.append(constraint)
            constraint.value = self.value
            constraint.valid_changed.connect(self._emit_valid_changed)
            constraint.enabled_changed.connect(self._emit_valid_changed)

        mocker.patch.object(IntParameter, "add_constraint", fake_add_constraint)

        self.mock_constraint = mocker.MagicMock(spec=Constraint)
        self.mock_constraint.valid = True
        self.mock_constraint.enabled = True

        self.int_param = IntParameter(
            name="testint",
            description="Test int parameter",
            flag="-testint ",
            operations={"IMG-GEN", "MDL-GEN"},
            default_value=0,
            constraints=[self.mock_constraint],
        )

        self.mock_condition = mocker.MagicMock(spec=Condition)
        self.mock_condition.value = True
        self.int_param.add_condition(self.mock_condition)

    def test_init_values(self):
        """Test IntParameter initialization with default value."""
        param = self.int_param
        assert param.name == "testint"
        assert param.description == "Test int parameter"
        assert param.flag == "-testint "
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.value == 0
        assert param.default_value == 0
        assert len(param.constraints) == 1
        assert param.constraints[0] is self.mock_constraint

    def test_set_value(self):
        """Test setting IntParameter value."""
        param = self.int_param
        param.value = 5
        assert param.value == 5

    def test_set_value_propagates_to_constraint(self):
        """Setting the value should push it into the constraint."""
        param = self.int_param
        param.value = 7
        assert self.mock_constraint.value == 7

    def test_reset_value(self):
        """Test resetting IntParameter value to default."""
        param = self.int_param
        param.value = 5
        param.reset_value()
        assert param.value == 0

    def test_enabled(self, mocker):
        """Test IntParameter's 'enabled' property."""
        # Arrange
        param = self.int_param
        mocker.patch.object(
            IntParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )
        # Assert
        assert not param.enabled

        # Arrange
        mocker.patch.object(
            IntParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=True,
        )
        # Assert
        assert param.enabled

    def test_enabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'IntParameter' is
        emitted when its internal condition reports a change to 'True'.
        """
        # Arrange
        param = self.int_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(True)

        # Assert
        slot.assert_called_once_with(True)

    def test_disabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'IntParameter' is
        emitted when its internal condition reports a change to 'False'.
        """
        # Arrange
        param = self.int_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(False)

        # Assert
        slot.assert_called_once_with(False)

    def test_valid(self):
        """Test IntParameter validity."""
        # Arrange
        param = self.int_param

        # Act + Assert: constraint says valid then parameter is valid
        self.mock_constraint.valid = True
        assert param.valid

        # Act + Assert: constraint says invalid then parameter is invalid
        self.mock_constraint.valid = False
        assert not param.valid

        # Act + Assert: invalid but disabled constraint so parameter is valid
        self.mock_constraint.enabled = False
        assert param.valid

    def test_valid_when_parameter_disabled(self, mocker):
        """A disabled parameter is always valid, even with a failing constraint."""
        # Arrange
        param = self.int_param
        self.mock_constraint.valid = False
        self.mock_constraint.enabled = True
        mocker.patch.object(
            IntParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )

        # Assert
        assert param.valid

    def test_to_cli(self, mocker):
        """Test IntParameter cli representation."""
        # Arrange
        param = self.int_param

        # Act + Assert: enabled + matching operation = flag and value
        assert param.to_cli('IMG-GEN') == f"{param.flag}{param.value}"
        param.value = new_value = 5
        assert param.to_cli('MDL-GEN') == f"{param.flag}{new_value}"

        # Act + Assert: operation not in 'operations' so empty string
        assert param.to_cli('SWP-SCN') == ""

        # Arrange: parameter disabled
        mocker.patch.object(
            IntParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )
        # Assert: disabled so empty string
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self, mocker):
        """Test that value_changed signal is emitted when IntParameter value changes."""
        # Arrange
        param = self.int_param
        self.mock_constraint.valid = True
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)

        # Act
        param.value = 5

        # Assert
        slot.assert_called_once_with(5, True)

    def test_invalid_value_changed_signal_emitted(self, mocker):
        # Arrange
        param = self.int_param
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)
        self.mock_constraint.valid = False

        # Act
        param.value = 15

        # Assert
        slot.assert_called_once_with(15, False)

    def test_to_dict(self):
        """to_dict returns the current value."""
        self.int_param.value = 7
        assert self.int_param.to_dict() == 7

    def test_str(self):
        """__str__ includes name and value."""
        result = str(self.int_param)
        assert "testint" in result
        assert "0" in result

    def test_reset_value_emits_value_reset(self, mocker):
        """reset_value emits the value_reset signal."""
        # Arrange
        slot = mocker.MagicMock()
        self.int_param.value_reset.connect(slot)
        self.int_param.value = 5

        # Act
        self.int_param.reset_value()

        # Assert
        slot.assert_called_once()

class TestBoolParameter:
    """Unit tests for BoolParameter class."""

    @fixture(autouse=True)
    def set_bool_param(self, mocker):
        self.bool_param = BoolParameter(
            name="testbool",
            description="Test bool parameter",
            flag="-testbool",
            operations={"IMG-GEN", "MDL-GEN"},
            default_value=False,
        )

        self.mock_condition = mocker.MagicMock(spec=Condition)
        self.mock_condition.value = True
        self.bool_param.add_condition(self.mock_condition)

    def test_init_values(self):
        """Test BoolParameter initialization with default value."""
        param = self.bool_param
        assert param.name == "testbool"
        assert param.description == "Test bool parameter"
        assert param.flag == "-testbool"
        assert param.operations == {"IMG-GEN", "MDL-GEN"}
        assert param.value is False
        assert param.default_value is False

    def test_set_value(self):
        """Test setting BoolParameter value."""
        param = self.bool_param
        param.value = True
        assert param.value is True

    def test_reset_value(self):
        """Test resetting BoolParameter value to default."""
        param = self.bool_param
        param.value = True
        param.reset_value()
        assert param.value is False

    def test_enabled(self, mocker):
        """Test BoolParameter's 'enabled' property."""
        # Arrange
        param = self.bool_param
        mocker.patch.object(
            BoolParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )
        # Assert
        assert not param.enabled

        # Arrange
        mocker.patch.object(
            BoolParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=True,
        )
        # Assert
        assert param.enabled

    def test_enabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'BoolParameter' is
        emitted when its internal condition reports a change to 'True'.
        """
        # Arrange
        param = self.bool_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(True)

        # Assert
        slot.assert_called_once_with(True)

    def test_disabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'BoolParameter' is
        emitted when its internal condition reports a change to 'False'.
        """
        # Arrange
        param = self.bool_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(False)

        # Assert
        slot.assert_called_once_with(False)

    def test_valid(self):
        """BoolParameter is always valid since it has no constraints."""
        param = self.bool_param
        assert param.valid
        param.value = True
        assert param.valid

    def test_to_cli(self, mocker):
        """Test BoolParameter cli representation."""
        # Arrange
        param = self.bool_param

        # Act + Assert: value is False so nothing is emitted even on a matching operation.
        assert param.to_cli("IMG-GEN") == ""

        # Act + Assert: value is True so the flag is emitted on matching operations.
        param.value = True
        assert param.to_cli("IMG-GEN") == param.flag
        assert param.to_cli("MDL-GEN") == param.flag

        # Act + Assert: operation not in 'operations' so empty string
        assert param.to_cli("SWP-SCN") == ""

        # Arrange: parameter disabled
        mocker.patch.object(
            BoolParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )
        # Assert: disabled so empty string
        assert param.to_cli("IMG-GEN") == ""

    def test_value_changed_signal_emitted(self, mocker):
        """Test that value_changed signal is emitted when BoolParameter value changes."""
        # Arrange
        param = self.bool_param
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)

        # Act
        param.value = True

        # Assert
        slot.assert_called_once_with(True, True)

    def test_to_dict(self):
        """to_dict returns the current value."""
        self.bool_param.value = True
        assert self.bool_param.to_dict() is True

    def test_str(self):
        """__str__ includes name and value."""
        result = str(self.bool_param)
        assert "testbool" in result
        assert "False" in result

    def test_reset_value_emits_value_reset(self, mocker):
        """reset_value emits the value_reset signal."""
        # Arrange
        slot = mocker.MagicMock()
        self.bool_param.value_reset.connect(slot)
        self.bool_param.value = True

        # Act
        self.bool_param.reset_value()

        # Assert
        slot.assert_called_once()


class TestFloatParameter:
    """Unit tests for FloatParameter class."""

    @fixture(autouse=True)
    def set_float_param(self, mocker):
        def fake_add_constraint(self, constraint, hidden=False):
            if not hidden:
                self._constraints.append(constraint)
            else:
                self._hidden_constraints.append(constraint)
            constraint.value = self.value
            constraint.valid_changed.connect(self._emit_valid_changed)
            constraint.enabled_changed.connect(self._emit_valid_changed)

        mocker.patch.object(FloatParameter, "add_constraint", fake_add_constraint)

        self.mock_constraint = mocker.MagicMock(spec=Constraint)
        self.mock_constraint.valid = True
        self.mock_constraint.enabled = True

        self.float_param = FloatParameter(
            name="testfloat",
            description="Test float parameter",
            flag="-testfloat",
            operations={"IMG-GEN", "MDL-GEN"},
            default_value=0.0,
            constraints=[self.mock_constraint],
        )

        self.mock_condition = mocker.MagicMock(spec=Condition)
        self.mock_condition.value = True
        self.float_param.add_condition(self.mock_condition)

    def test_init_values(self):
        """Test FloatParameter initialization with default value."""
        param = self.float_param
        assert param.name == "testfloat"
        assert param.description == "Test float parameter"
        assert param.flag == "-testfloat"
        assert param.operations == {"IMG-GEN", "MDL-GEN"}
        assert param.value == 0.0
        assert param.default_value == 0.0
        assert len(param.constraints) == 1
        assert param.constraints[0] is self.mock_constraint

    def test_set_value(self):
        """Test setting FloatParameter value."""
        param = self.float_param
        param.value = 5.0
        assert param.value == 5.0

    def test_set_value_propagates_to_constraint(self):
        """Setting the value should push it into the constraint."""
        param = self.float_param
        param.value = 3.14
        assert self.mock_constraint.value == 3.14

    def test_reset_value(self):
        """Test resetting FloatParameter value to default."""
        param = self.float_param
        param.value = 5.0
        param.reset_value()
        assert param.value == 0.0

    def test_enabled(self, mocker):
        """Test FloatParameter's 'enabled' property."""
        # Arrange
        param = self.float_param
        mocker.patch.object(
            FloatParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )
        # Assert
        assert not param.enabled

        # Arrange
        mocker.patch.object(
            FloatParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=True,
        )
        # Assert
        assert param.enabled

    def test_enabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'FloatParameter' is
        emitted when its internal condition reports a change to 'True'.
        """
        # Arrange
        param = self.float_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(True)

        # Assert
        slot.assert_called_once_with(True)

    def test_disabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'FloatParameter' is
        emitted when its internal condition reports a change to 'False'.
        """
        # Arrange
        param = self.float_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(False)

        # Assert
        slot.assert_called_once_with(False)

    def test_valid(self):
        """Test FloatParameter validity."""
        # Arrange
        param = self.float_param

        # Act + Assert: constraint says valid then parameter is valid
        self.mock_constraint.valid = True
        assert param.valid

        # Act + Assert: constraint says invalid then parameter is invalid
        self.mock_constraint.valid = False
        assert not param.valid

        # Act + Assert: invalid but disabled constraint so parameter is valid
        self.mock_constraint.enabled = False
        assert param.valid

    def test_valid_when_parameter_disabled(self, mocker):
        """A disabled parameter is always valid, even with a failing constraint."""
        # Arrange
        param = self.float_param
        self.mock_constraint.valid = False
        self.mock_constraint.enabled = True
        mocker.patch.object(
            FloatParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )

        # Assert
        assert param.valid

    def test_to_cli(self, mocker):
        """Test FloatParameter cli representation."""
        # Arrange
        param = self.float_param

        # Act + Assert: enabled + matching operation = flag and value
        assert param.to_cli("IMG-GEN") == f"{param.flag}{param.value}"
        param.value = new_value = 5.5
        assert param.to_cli("MDL-GEN") == f"{param.flag}{new_value}"

        # Act + Assert: operation not in 'operations' so empty string
        assert param.to_cli("SWP-SCN") == ""

        # Arrange: parameter disabled
        mocker.patch.object(
            FloatParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )
        # Assert: disabled so empty string
        assert param.to_cli("IMG-GEN") == ""

    def test_value_changed_signal_emitted(self, mocker):
        """Test that value_changed signal is emitted when FloatParameter value changes."""
        # Arrange
        param = self.float_param
        self.mock_constraint.valid = True
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)

        # Act
        param.value = 5.5

        # Assert
        slot.assert_called_once_with(5.5, True)

    def test_invalid_value_changed_signal_emitted(self, mocker):
        """Test that value_changed signal is emitted with valid=False when the constraint fails."""
        # Arrange
        param = self.float_param
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)
        self.mock_constraint.valid = False

        # Act
        param.value = 15.0

        # Assert
        slot.assert_called_once_with(15.0, False)

    def test_to_dict(self):
        """to_dict returns the current value."""
        self.float_param.value = 3.14
        assert self.float_param.to_dict() == 3.14

    def test_str(self):
        """__str__ includes name and value."""
        result = str(self.float_param)
        assert "testfloat" in result
        assert "0.0" in result

    def test_reset_value_emits_value_reset(self, mocker):
        """reset_value emits the value_reset signal."""
        # Arrange
        slot = mocker.MagicMock()
        self.float_param.value_reset.connect(slot)
        self.float_param.value = 5.0

        # Act
        self.float_param.reset_value()

        # Assert
        slot.assert_called_once()


class TestStringParameter:
    """Unit tests for StringParameter class."""

    @fixture(autouse=True)
    def set_string_param(self, mocker):
        def fake_add_constraint(self, constraint, hidden=False):
            if not hidden:
                self._constraints.append(constraint)
            else:
                self._hidden_constraints.append(constraint)
            constraint.value = self.value
            constraint.valid_changed.connect(self._emit_valid_changed)
            constraint.enabled_changed.connect(self._emit_valid_changed)

        mocker.patch.object(StringParameter, "add_constraint", fake_add_constraint)

        # Two mock constraints to mirror the integration tests that use a MaxLengthConstraint + RegexConstraint pair.
        self.mock_length_constraint = mocker.MagicMock(spec=Constraint)
        self.mock_length_constraint.valid = True
        self.mock_length_constraint.enabled = True

        self.mock_regex_constraint = mocker.MagicMock(spec=Constraint)
        self.mock_regex_constraint.valid = True
        self.mock_regex_constraint.enabled = True

        self.string_param = StringParameter(
            name="teststring",
            description="Test string parameter",
            flag="-teststring ",
            operations={"IMG-GEN", "MDL-GEN"},
            default_value="default",
            constraints=[self.mock_length_constraint, self.mock_regex_constraint],
        )

        self.mock_condition = mocker.MagicMock(spec=Condition)
        self.mock_condition.value = True
        self.string_param.add_condition(self.mock_condition)

    def test_init_values(self):
        """Test StringParameter initialization with default value."""
        param = self.string_param
        assert param.name == "teststring"
        assert param.description == "Test string parameter"
        assert param.flag == "-teststring "
        assert param.operations == {"IMG-GEN", "MDL-GEN"}
        assert param.value == "default"
        assert param.default_value == "default"
        assert len(param.constraints) == 2

    def test_set_value(self):
        """Test setting StringParameter value."""
        param = self.string_param
        param.value = "new_value"
        assert param.value == "new_value"

    def test_set_value_propagates_to_constraints(self):
        """Setting the value should push it into every constraint."""
        param = self.string_param
        param.value = "hello"
        assert self.mock_length_constraint.value == "hello"
        assert self.mock_regex_constraint.value == "hello"

    def test_reset_value(self):
        """Test resetting StringParameter value to default."""
        param = self.string_param
        param.value = "new_value"
        param.reset_value()
        assert param.value == "default"

    def test_enabled(self, mocker):
        """Test StringParameter's 'enabled' property."""
        # Arrange
        param = self.string_param
        mocker.patch.object(
            StringParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )
        # Assert
        assert not param.enabled

        # Arrange
        mocker.patch.object(
            StringParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=True,
        )
        # Assert
        assert param.enabled

    def test_enabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'StringParameter' is
        emitted when its internal condition reports a change to 'True'.
        """
        # Arrange
        param = self.string_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(True)

        # Assert
        slot.assert_called_once_with(True)

    def test_disabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'StringParameter' is
        emitted when its internal condition reports a change to 'False'.
        """
        # Arrange
        param = self.string_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(False)

        # Assert
        slot.assert_called_once_with(False)

    def test_valid_all_constraints_pass(self):
        """Valid when every enabled constraint reports valid."""
        param = self.string_param
        self.mock_length_constraint.valid = True
        self.mock_regex_constraint.valid = True
        assert param.valid

    def test_valid_one_constraint_fails(self):
        """Invalid as soon as one enabled constraint reports invalid."""
        param = self.string_param
        self.mock_length_constraint.valid = True
        self.mock_regex_constraint.valid = False
        assert not param.valid

    def test_valid_failing_constraint_disabled(self):
        """A failing constraint that is disabled does not break validity."""
        param = self.string_param
        self.mock_regex_constraint.valid = False
        self.mock_regex_constraint.enabled = False
        assert param.valid

    def test_valid_when_parameter_disabled(self, mocker):
        """A disabled parameter is always valid, even with a failing constraint."""
        # Arrange
        param = self.string_param
        self.mock_length_constraint.valid = False
        self.mock_length_constraint.enabled = True
        mocker.patch.object(
            StringParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )

        # Assert
        assert param.valid

    def test_to_cli(self, mocker):
        """Test StringParameter cli representation."""
        # Arrange
        param = self.string_param

        # Act + Assert: enabled + matching operation = flag and value
        assert param.to_cli("IMG-GEN") == f"{param.flag}{param.value}"
        new_value = "hello"
        param.value = new_value
        assert param.to_cli("MDL-GEN") == f"{param.flag}{new_value}"

        # Act + Assert: operation not in 'operations' so empty string
        assert param.to_cli("SWP-SCN") == ""

        # Arrange: parameter disabled
        mocker.patch.object(
            StringParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )
        # Assert: disabled so empty string
        assert param.to_cli("IMG-GEN") == ""

    def test_value_changed_signal_emitted(self, mocker):
        """Test that value_changed signal is emitted when StringParameter value changes."""
        # Arrange
        param = self.string_param
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)

        # Act
        param.value = "hello"

        # Assert
        slot.assert_called_once_with("hello", True)

    def test_invalid_value_changed_signal_emitted(self, mocker):
        """Test that value_changed signal is emitted with valid=False when a constraint fails."""
        # Arrange
        param = self.string_param
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)
        self.mock_regex_constraint.valid = False

        # Act
        param.value = "invalid value"

        # Assert
        slot.assert_called_once_with("invalid value", False)

    def test_to_dict(self):
        """to_dict returns the current value."""
        self.string_param.value = "hello"
        assert self.string_param.to_dict() == "hello"

    def test_str(self):
        """__str__ includes name and value."""
        result = str(self.string_param)
        assert "teststring" in result
        assert "default" in result

    def test_reset_value_emits_value_reset(self, mocker):
        """reset_value emits the value_reset signal."""
        # Arrange
        slot = mocker.MagicMock()
        self.string_param.value_reset.connect(slot)
        self.string_param.value = "new_value"

        # Act
        self.string_param.reset_value()

        # Assert
        slot.assert_called_once()


