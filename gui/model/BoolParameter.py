from PySide6.QtCore import Signal

from gui.model.Parameter import Parameter


class BoolParameter(Parameter[bool]):
    value_changed = Signal(bool, bool)

    def to_cli(self) -> str:
        if self.value:
            return self.flag
        else:
            return ""
    
    def __str__(self) -> str:
        return (
            f'BoolParameter('
            + f'name: "{self.name}", '
            + f'description: "{self.description})", '
            + f'value: {self.value}, '
            + f'valid: {self.valid})'
        )