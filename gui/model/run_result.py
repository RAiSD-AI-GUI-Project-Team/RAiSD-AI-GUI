from gui.model.parameter_group_list import ParameterGroupList
class RunResult():
    def __init__(
            self, 
            parameter_group_list: ParameterGroupList
        ):
        self._results_path = None
        self._info_files = None
        self._commands = None
        self._parameter_group_list = parameter_group_list

    @classmethod
    def from_history_file(cls, path:str) -> list["RunResult"]:
        #TODO: implement parsing
        pass

    @classmethod
    def from_str(cls, string: str) -> "RunResult":
        #TODO: implement parsing
        pass

    def populate_parameter_group_list(
            self, 
            parameter_group_list: ParameterGroupList, 
            command: str
        ) -> ParameterGroupList:
        #TODO: implement
        pass

    def to_str(self) -> str:
        #TODO: implement file representation
        pass

    @property
    def path(self) -> str:
        return self._results_path
    
    @property
    def info_files(self) -> list[str]:
        return self._info_files
    
    @property
    def parameter_group_list(self) -> ParameterGroupList:
        return self._parameter_group_list