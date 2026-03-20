from dataclasses import dataclass
from typing import Collection, Protocol

from PySide6.QtCore import (
    QObject,
    Signal,
)

from gui.model.file_structure import (
    FileStructure,
    SingleFile,
    Directory,
)
from gui.model.operation import Operation


class FileProducerNode(Protocol):
    @property
    def produces(self) -> FileStructure:
        ...

    @property
    def file(self) -> str | None:
        ...

    @property
    def valid(self) -> bool:
        ...

    def to_cli(self) -> list[str]:
        ...


class FileConsumerNode():
    def __init__(
            self,
            requires: FileStructure,
            label: str,
            cli: str,
    ) -> None:
        self._requires = requires
        self._producers = []
        self._selected_index = 0
        self._label = label
        self._cli = cli

    @property
    def requires(self) -> FileStructure:
        return self._requires

    def add_producer(self, producer: FileProducerNode) -> None:
        self._producers.append(producer)

    @property
    def producers(self) -> list[FileProducerNode]:
        return self._producers

    @property
    def label(self) -> str:
        return self._label

    @property
    def cli_parameter(self) -> str:
        return f"{self._cli} {self.file}"

    @property
    def selected_index(self) -> int:
        return self._selected_index

    @selected_index.setter
    def selected_index(self, new_selected_index: int) -> None:
        self._selected_index = new_selected_index

    @property
    def selected_producer(self) -> FileProducerNode:
        print(f"{self.label} {self.selected_index}")
        return self.producers[self.selected_index]

    @property
    def file(self) -> str | None:
        return self.selected_producer.file

    @property
    def valid(self) -> bool:
        return self.selected_producer.valid
    
    def to_cli(self) -> list[str]:
        return self.selected_producer.to_cli()


class CommonParentDirectoryNode():
    def __init__(
            self,
            produces: Directory,
    ) -> None:
        self._produces = produces
        self._file_consumers = []
        for file_structure in self._produces.contents:
            file_consumer = FileConsumerNode(
                Directory([file_structure]),
                "Output inside common parent directory",
                "",
            )
            self._file_consumers.append(file_consumer)

    @property
    def produces(self) -> FileStructure:
        return self._produces

    @property
    def file_consumers(self) -> list[FileConsumerNode]:
        return self._file_consumers

    @property
    def file(self) -> str | None:
        return self.file_consumers[0].file

    @property
    def valid(self) -> bool:
        if not all(consumer.valid for consumer in self.file_consumers):
            return False

        # All child nodes must produce files with the same parent directory
        return len(set(consumer.file for consumer in self.file_consumers)) == 1

    def to_cli(self) -> list[str]:
        commands = []
        for consumer in self.file_consumers:
            commands.extend(consumer.to_cli())
        return commands


class FilePickerNode(QObject):
    file_changed = Signal(str)

    def __init__(self, produces: FileStructure):
        super().__init__()
        self._produces = produces
        self._file: str | None = None

    @property
    def produces(self) -> FileStructure:
        return self._produces

    @property
    def file(self) -> str | None:
        return self._file

    @file.setter
    def file(self, new_file: str | None) -> None:
        self._file = new_file
        self.file_changed.emit(self._file)

    @property
    def valid(self) -> bool:
        if self.file is None:
            return False
        return self.produces.matches(self.file)

    def to_cli(self) -> list[str]:
        return []


class OperationNode():
    def __init__(self,
        operation: Operation,
    ) -> None:
        self._name = operation.name
        self._description = operation.description
        self._cli = operation.cli
        self._produces = operation.produces
        self._file_consumers = []
        for file_name, cli, file_structure in operation.requires:
            file_consumer = FileConsumerNode(
                file_structure,
                file_name,
                cli,
            )
            file_picker = FilePickerNode(file_structure)
            file_consumer.add_producer(file_picker)
            self._file_consumers.append(file_consumer)

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def produces(self) -> FileStructure:
        return self._produces

    @property
    def file_consumers(self) -> list[FileConsumerNode]:
        return self._file_consumers

    @property
    def file(self) -> str | None:
        return "RAiSD_Images.runID"

    @property
    def valid(self) -> bool:
        return all([consumer.valid for consumer in self._file_consumers])

    def to_cli(self) -> list[str]:
        commands = []
        own_command = f"./RAiSD-AI {self._cli}"

        for file_consumer in self.file_consumers:
            commands.extend(file_consumer.to_cli())
            own_command += f" {file_consumer.cli_parameter}"
        commands.append(own_command)

        return commands

@dataclass
class OperationTree(QObject):
    root: OperationNode

    @classmethod
    def build_trees(
            cls,
            operations: Collection[Operation],
    ) -> list["OperationTree"]:
        trees: list[OperationTree] = []
        for root_operation in operations:
            root_node = OperationNode(root_operation)
            unexplored_nodes: list[OperationNode] = [root_node]
            while unexplored_nodes:
                current_node = unexplored_nodes[0]
                unexplored_nodes = unexplored_nodes[1:]
                for file_consumer in current_node.file_consumers:
                    for candidate_operation in operations:
                        if candidate_operation.produces == file_consumer.requires:
                            operation_node = OperationNode(candidate_operation)
                            file_consumer.add_producer(operation_node)
                            unexplored_nodes.append(operation_node)
                    # If the consumer is expecting a directory, try
                    # producing that directory from multiple operations.
                    if isinstance(file_consumer.requires, Directory):
                        common_parent_dir = CommonParentDirectoryNode(file_consumer.requires)
                        possible_unexplored = []
                        operations_exist: bool = True
                        for sub_consumer in common_parent_dir.file_consumers:
                            operation_exists: bool = False
                            for candidate_operation in operations:
                                if candidate_operation.produces == sub_consumer.requires:
                                    operation_exists = True
                                    operation_node = OperationNode(candidate_operation)
                                    sub_consumer.add_producer(operation_node)
                                    possible_unexplored.append(operation_node)
                            if not operation_exists:
                                operations_exist = False
                                break
                        if operations_exist:
                            file_consumer.add_producer(common_parent_dir)
                            unexplored_nodes.extend(possible_unexplored)

            tree = OperationTree(root_node)
            trees.append(tree)
        return trees


    def to_cli(self) -> list[str]:
        return self.root.to_cli()
