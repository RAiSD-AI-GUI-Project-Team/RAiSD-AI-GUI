from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from pathlib import Path
import os

from PySide6.QtCore import QObject, Signal

T = TypeVar("T")


class AbstractQObjectMeta(type(ABC), type(QObject)):
    """
    Metaclass for an abstract base QObject class.
    """

    pass


class Parameter(ABC, QObject, Generic[T], metaclass=AbstractQObjectMeta):
    """
    A base class for parameters to be filled in using the GUI.

    The class inherits from `ABC` to make it abstract, from `QObject`
    to use the signal mechanism and from `Generic` to add type hints
    based on the type of value that the parameter stores.
    """

    value_changed: Signal

    def __init__(
            self,
            name: str, description: str, flag: str,
            default_value: T,
    ) -> None:
        """
        Initialize a `Parameter` object.

        :param name: the name of the parameter
        :type name: str

        :param description: a longer description of the parameter
        :type description: str

        :param flag: the command-line flag of the parameter
        :type flag: str

        :param default_value: the default value of the parameter
        :type default_value: T
        """
        super().__init__(self)
        self.name = name
        self.description = description
        self.default_value = default_value
        self._value = default_value
        self.flag = flag

    @property
    def value(self) -> T:
        """
        The current value of the parameter.
        """
        return self._value

    @value.setter
    def value(self, new_value: T) -> None:
        self._value = new_value
        self.value_changed.emit(self.value, self.valid)

    def reset_value(self) -> None:
        """
        Reset the value of the parameter to the default value.
        """
        self._value = self.default_value

    @property
    def valid(self) -> bool:
        """
        Whether the current value of the parameter is valid.
        """
        return True

    @abstractmethod
    def to_cli(self) -> str:
        """
        Represent the parameter for the command line, taking into
        account its current value.

        :return: the command-line representation
        :rtype: str
        """
        pass


class BoolParameter(Parameter[bool]):
    """
    A boolean parameter in the GUI.

    The value of a boolean parameter is always valid.
    """

    value_changed = Signal(bool, bool)

    def to_cli(self) -> str:
        # A boolean parameter is represented in the command line by the
        # presence or absence of its flag.
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

# --- Possible identified file types in the system ---
#ms, vcf, fasta
#angsd vcf
#gz (vcf)
#unordered vcf

class FileParameter(Parameter[list[str]]):
    """
    A file path parameter in the GUI

    Stores the list of file paths selected by the user. The file parameter accepts a list of
    file parameters, and it has the option to allow single or multiple file inputs.

    The value is valid when all the following holds:
    - The value list is not empty.
    - If it is not multiple (multiple = False), there should only be a single file in the list.
    - Every file in the list exists and readable and their file extension is in the accepted_formats

    Three different modes are there:
    1. accepted_formats is filled:
        a. hard_block is True -> This will result in user only being able to select the files that match the type in accepted_formats
        b. hard_block is False -> User can select any file, but a warning will be displayed if the file type does not match the ones in accepted formats.
    2. accepted_formats is None:
        a. hard_block is False -> User can upload any file. The system notifies the user any file type is accepted here.
        b. hard_block is True -> No, need to use this configuration. Yet, user can upload any file. But user is not notified.
    """
    value_changed = Signal(list, bool)

    def __init__(
        self,
        name: str,
        description: str,
        flag: str,
        accepted_formats: list[str] | None = None, #set this for hard-blocking the user from selecting different files "vasta", "vcf", "ms"
        hard_block: bool = False, #the flag indicating whether the accepted format is hard block for the user
        multiple: bool = False, #the flag indicating whether multiple files are allowed or not
        default_value: list[str] | None = None,
    ) -> None:
        self.hard_block = hard_block
        if hard_block:
            self.accepted_formats = (
                [ext if ext.startswith(".") else f".{ext}" for ext in accepted_formats]
                if accepted_formats is not None else None
            )
            self.expected_formats = None
        if not hard_block:
            self.expected_formats = (
                [ext if ext.startswith(".") else f".{ext}" for ext in accepted_formats]
                if accepted_formats is not None else None
            )
            self.accepted_formats = None
        self.multiple = multiple
        super().__init__(name, description, flag, default_value or [])

    @property
    def valid(self) -> bool:
        if not self.value:
            return False
        if not self.multiple and len(self.value) > 1:
            return False
        return all(
            Path(f).is_file()
            and os.access(Path(f), os.R_OK)
            and (self.accepted_formats is None or Path(f).suffix.lower() in self.accepted_formats or Path(f).suffix.lower() in self.expected_formats)
            for f in self.value)

    @property
    def file_extensions(self) -> list[str]:
        return [Path(f).suffix.lower() for f in self.value if f]

    @property
    def matches_expected(self) -> bool:
        if not self.value or self.expected_formats is None:
            return True
        return all(
            Path(f).suffix.lower() in self.expected_formats
            for f in self.value
        )

    @Parameter.value.setter
    def value(self, new_value: list[str]) -> None:
        self._value = new_value
        self.value_changed.emit(self.value, self.valid)

    def __str__(self) -> str:
        return (
            f'FileParameter('
            f'name: "{self.name}", '
            f'description: "{self.description}", '
            f'accepted_formats: {self.accepted_formats}, '
            f'value: "{self.value}", '
            f'valid: {self.valid})'
        )

    def to_cli(self) -> str:
        if self.valid:
            return " ".join(f"{self.flag} {f}" for f in self.value)
        return ""