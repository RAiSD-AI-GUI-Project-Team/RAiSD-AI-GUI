from gui.model.run_record import RunRecord

import json
from datetime import datetime 
from gui.model.settings import app_settings
from gui.model.history_record import HistoryRecord
from gui.model.parameter import Parameter, OptionalParameter, MultiParameter

class RunResult():
    def __init__(
            self, 
            commands: list[str] = [],
            parameter_group_list: RunRecord | None = None,
            time_completed: datetime | None = None
        ):
        self._commands = commands
        self._parameter_group_list = parameter_group_list or RunRecord.from_yaml(app_settings.yaml_path)
        self._time_completed = time_completed

    def to_history_record(self) -> HistoryRecord:
        """
        Makes a history record with the information of the current RunResult.
        """
        parameters_dict = {}
        for parameter_group in self.parameter_group_list:
            for parameter in parameter_group:
                parameters_dict[parameter.name] = self.parameter_to_value(parameter)
        
        operations = [tree.root.run_id for tree in self._parameter_group_list.operation_trees]

        #TODO I do not like this, it is a temporary fix that will be resolved 
        # if we remove the runresult
        assert self._time_completed != None

        return HistoryRecord(
            self._parameter_group_list.run_id,
            self.commands,
            operations,
            parameters_dict,
            self._time_completed
        )

    def to_dict(self) -> dict:
        """
        Makes a dictionary with the information of the current RunResult. This
        is used to store in the history file.
        """
        parameters_dict = {}
        for parameter_group in self.parameter_group_list:
            for parameter in parameter_group:
                parameters_dict[parameter.name] = self.parameter_to_value(parameter)

        operations = [tree.root.run_id for tree in self._parameter_group_list.operation_trees]

        dict = {
            "name": self._parameter_group_list.run_id,
            "commands": self._commands,
            "operations": operations,
            "parameters": parameters_dict,
            "time_completed": self._time_completed
        }
        return dict

    def parameter_to_value(self, parameter: Parameter) -> str | dict:
        """
        Makes the dictionary or string that is stored as the value of each 
        parameter. Uses recursion for MultiParameter and OptionalParameter
        """
        if type(parameter) is MultiParameter: 
            parameters = {}
            for param in parameter.parameters:
                parameters[param.name] = self.parameter_to_value(param)
            return parameters
        if type(parameter) is OptionalParameter:
            value = {}
            value["enabled"] = parameter.value
            value[parameter.parameter.name] = self.parameter_to_value(parameter.parameter)
            return value
        else:
            return parameter.value
    
    @property
    def commands(self) -> list[str]:
        return self._commands
    
    @property
    def parameter_group_list(self) -> RunRecord:
        return self._parameter_group_list
    
    @property
    def time_completed(self) -> datetime | None:
        return self._time_completed
    

    def set_commands(self) -> None:
        """
        Sets the commands of a run based on the cli representation
        of the ParameterGroupList
        """
        self._commands = self._parameter_group_list.to_cli()

    def set_completed(self) -> None:
        self._commands = self._parameter_group_list.to_cli()
        self._time_completed = datetime.now()

    def populate(self, history_record: HistoryRecord) -> None:
        """
        Populates the current run result with the contents of a history record.
        This is used to fill the ResultsWidget in history with the contents
        of records when a user clicks on them.
        """
        self.parameter_group_list.run_id_parameter.value = history_record.name
        self._commands = history_record.commands
        dictionary = history_record.parameters
        for parameter_group in self._parameter_group_list:
            for parameter in parameter_group:
                if parameter.name in dictionary:
                    self.populate_parameter(parameter, dictionary[parameter.name])
                    #TODO: validiity checking?
        self._time_completed = history_record.time_completed
        for operation in history_record.operations:
            self._parameter_group_list.set_operation(operation, history_record.operations[operation])

    def populate_parameter(self, parameter: Parameter, value: dict | str) -> None:
        """
        Populates a parameter with the values from a dict or string. Uses
        recursion for optional parameters and multi parameters.
        """
        if type(parameter) is MultiParameter:
            for param in parameter.parameters:
                if isinstance(value, dict) and value[param.name]:
                    self.populate_parameter(param, value[param.name])
        elif type(parameter) is OptionalParameter:
            if isinstance(value, dict) and 'enabled' not in value:
                raise ValueError(
                    f"Incorrect format for {parameter.name}: {value}"
                    + "Optional parameter must have 'enabled' value."
                )
            
            if isinstance(value, dict) and isinstance(value["enabled"], bool):
                parameter.value = value["enabled"]
                if parameter.parameter in value:
                    self.populate_parameter(
                        parameter.parameter, 
                        value[parameter.parameter.name]
                    )
        else:
            parameter.value = value