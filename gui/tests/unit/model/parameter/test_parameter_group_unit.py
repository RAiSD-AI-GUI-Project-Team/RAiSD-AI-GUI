from pytest import raises
from unittest.mock import MagicMock
from gui.tests.utils.mock_signal import MockSignal

from gui.model.parameter import ParameterGroup

def make_mock_parameter(enabled: bool = True, valid: bool = True, cli_output: str = "") -> MagicMock:
    """ Create a mock Parameter with a MockSignal """
    param = MagicMock()
    param.enabled = enabled
    param.valid = valid
    param.to_cli = MagicMock(return_value=cli_output)
    param.enabled_changed = MockSignal(bool)
    return param

class TestParameterGroupUnit:
    """Unit tests for ParameterGroup class."""

    def test_init_name(self):
        """Test that the group stores its name."""
        group = ParameterGroup(name="g")
        assert group.name == "g"

    def test_init_empty_parameters(self):
        """Test ParameterGroup initialization when the parameters list is empty."""
        group = ParameterGroup(name="empty_group")
        assert group.parameters == []
        assert not group.enabled

    def test_init_parameters_none_defaults_to_empty_list(self):
        """Test that parameter group without parameters defaults to an empty list."""
        group = ParameterGroup(name="g")
        assert group.parameters == []

    def test_init_enabled_true_when_param_is_enabled(self):
        """Test that a group initialised with at an enabled parameter reports enabled=True."""
        param = make_mock_parameter(enabled=True)
        group = ParameterGroup(name="g", parameters=[param])
        assert group.enabled is True

    def test_init_enabled_false_when_params_disabled(self):
        """Test that a group initialised with disabled parameter reports enabled=False."""
        param = make_mock_parameter(enabled=False)
        group = ParameterGroup(name="g", parameters=[param])
        assert group.enabled is False

    def test_init_connects_enabled_changed_for_each_param(self):
        """Test that __init__ connects to enabled_changed of every parameter."""
        param1 = make_mock_parameter()
        param2 = make_mock_parameter()
        ParameterGroup(name="g", parameters=[param1, param2])
        assert len(param1.enabled_changed.slots) == 1
        assert len(param2.enabled_changed.slots) == 1

    def test_enabled_false_when_all_params_become_disabled(self):
        """Test enabled becomes False when all parameters are disabled via signal."""
        param1 = make_mock_parameter(enabled=True)
        param2 = make_mock_parameter(enabled=True)
        group = ParameterGroup(name="g", parameters=[param1, param2])
        assert group.enabled is True

        param1.enabled = False
        param1.enabled_changed.emit(False)
        assert group.enabled is True

        param2.enabled = False
        param2.enabled_changed.emit(False)
        assert group.enabled is False

    def test_add_parameter_appends_to_list(self):
        """Test adding a parameter to an existing ParameterGroup actually adds the parameter to the group."""
        group = ParameterGroup(name="g")
        param = make_mock_parameter()
        group.add_parameter(param)
        assert len(group.parameters) == 1
        assert group.parameters[0] is param

    def test_add_parameter_connects_enabled_changed(self):
        """Test that add_parameter connects to the parameter's enabled_changed signal."""
        group = ParameterGroup(name="g")
        param = make_mock_parameter()
        group.add_parameter(param)
        assert len(param.enabled_changed.slots) == 1

    def test_add_enabled_param_to_disabled_group_enables_group(self):
        """Test that adding an enabled parameter to a disabled group updates the group's enabled state."""
        group = ParameterGroup(name="g")
        assert group.enabled is False
        param = make_mock_parameter(enabled=True)
        group.add_parameter(param)
        assert group.enabled is True

    def test_adding_disabled_param_to_disabled_group_stays_disabled(self):
        """Test that adding a disabled parameter to a disabled group leaves the group disabled."""
        group = ParameterGroup(name="g")
        param = make_mock_parameter(enabled=False)
        group.add_parameter(param)
        assert group.enabled is False

    def test_adding_disabled_param_to_enabled_group_stays_enabled(self):
        """Test that adding a disabled parameter to an already-enabled group leaves the group enabled."""
        param_old = make_mock_parameter(enabled=True)
        group = ParameterGroup(name="g", parameters=[param_old])
        param_new = make_mock_parameter(enabled=False)
        group.add_parameter(param_new)
        assert group.enabled is True

    def test_add_parameter_emits_enabled_changed_when_group_becomes_enabled(self):
        """Test that enabled_changed is emitted when adding an enabled param enables the group."""
        group = ParameterGroup(name="g")
        emitted = []
        group.enabled_changed.connect(lambda v: emitted.append(v))

        param = make_mock_parameter(enabled=True)
        group.add_parameter(param)

        assert emitted == [True]

    def test_add_parameter_does_not_emit_enabled_changed_when_state_unchanged(self):
        """Test that enabled_changed is not emitted when add_parameter doesn't change enabled state."""
        param_old = make_mock_parameter(enabled=True)
        group = ParameterGroup(name="g", parameters=[param_old])

        emitted = []
        group.enabled_changed.connect(lambda v: emitted.append(v))

        param_new = make_mock_parameter(enabled=False)
        group.add_parameter(param_new)

        assert emitted == []

    def test_valid_all_valid(self):
        """Test validity of ParameterGroup when all parameters are valid."""
        param1 = make_mock_parameter(valid=True)
        param2 = make_mock_parameter(valid=True)
        group = ParameterGroup(name="g", parameters=[param1, param2])
        assert group.valid is True

    def test_valid_one_invalid(self):
        """Test validity of ParameterGroup when a single parameter is invalid."""
        param1 = make_mock_parameter(valid=True)
        param2 = make_mock_parameter(valid=False)
        group = ParameterGroup(name="g", parameters=[param1, param2])
        assert group.valid is False

    def test_valid_empty_group(self):
        """Test that an empty group is considered valid."""
        group = ParameterGroup(name="empty_group")
        assert group.valid is True

    def test_to_cli_joins_nonempty_param_outputs(self):
        """Test to_cli joins non-empty parameter CLI outputs with spaces."""
        param1 = make_mock_parameter(cli_output="-a val")
        param2 = make_mock_parameter(cli_output="-b")
        group = ParameterGroup(name="g", parameters=[param1, param2])
        assert group.to_cli("OP") == "-a val -b"

    def test_to_cli_skips_empty_param_outputs(self):
        """Test to_cli skips parameters that return an empty string."""
        param1 = make_mock_parameter(cli_output="-a")
        param2 = make_mock_parameter(cli_output="")
        group = ParameterGroup(name="g", parameters=[param1, param2])
        assert group.to_cli("OP") == "-a"

    def test_to_cli_passes_operation_to_each_param(self):
        """Test that to_cli forwards the operation string to every parameter."""
        param1 = make_mock_parameter(cli_output="-a")
        param2 = make_mock_parameter(cli_output="-b")
        group = ParameterGroup(name="g", parameters=[param1, param2])
        group.to_cli("MDL-GEN")
        param1.to_cli.assert_called_once_with("MDL-GEN")
        param2.to_cli.assert_called_once_with("MDL-GEN")

    def test_to_cli_empty_group(self):
        """Test to_cli returns an empty string when the parameter list is empty."""
        group = ParameterGroup(name="empty_group")
        result = group.to_cli('MDL-GEN')
        assert result == ""

    def test_to_cli_invalid_parameter(self):
        """Test that a parameter group with valid parameter has the same CLI output
         as a parameter group with the same parameter, but invalid."""
        param_valid = make_mock_parameter(valid=True, cli_output="-flag_string val")
        group_valid = ParameterGroup(name="g", parameters=[param_valid])

        param_invalid = make_mock_parameter(valid=False, cli_output="-flag_string val")
        group_invalid = ParameterGroup(name="g", parameters=[param_invalid])

        assert group_valid.to_cli("OP") == group_invalid.to_cli("OP")

    def test_iter(self):
        """Test that iterating over a ParameterGroup yields its parameters."""
        param1 = make_mock_parameter()
        param2 = make_mock_parameter()
        group = ParameterGroup(name="g", parameters=[param1, param2])
        assert list(group) == [param1, param2]

    def test_iter_empty_group(self):
        """Test that iterating over an empty ParameterGroup yields nothing."""
        group = ParameterGroup(name="empty_group")
        assert list(group) == []

    def test_getitem(self):
        """Test index access on a ParameterGroup."""
        param1 = make_mock_parameter()
        param2 = make_mock_parameter()
        group = ParameterGroup(name="g", parameters=[param1, param2])
        assert group[0] is param1
        assert group[1] is param2

    def test_getitem_out_of_range(self):
        """Test that out-of-range index access raises IndexError."""
        group = ParameterGroup(name="g")
        with raises(IndexError):
            _ = group[0]

    def test_str(self):
        """Test __str__ includes the group name and CLI output."""
        group = ParameterGroup(name="my_group")
        assert "my_group" in str(group)

