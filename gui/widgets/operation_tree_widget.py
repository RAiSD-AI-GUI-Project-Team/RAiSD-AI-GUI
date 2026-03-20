from PySide6.QtWidgets import (
    QHBoxLayout,
    QFileDialog,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from gui.model.file_structure import(
    SingleFile,
    Directory,
)
from gui.model.operation_tree import (
    FileProducerNode,
    FileConsumerNode,
    CommonParentDirectoryNode,
    FilePickerNode,
    OperationNode,
    OperationTree,
)
from gui.widgets.resizable_stacked_widget import ResizableStackedWidget


class FileConsumerWidget(QWidget):
    def __init__(self, file_consumer_node: FileConsumerNode):
        super().__init__()
        self._file_consumer_node = file_consumer_node

        layout = QVBoxLayout(self)

        heading = QLabel(self._file_consumer_node.label)
        layout.addWidget(heading)
        self.file_producer_widget = ResizableStackedWidget()
        if len(self._file_consumer_node.producers) == 1:
            producer = self._file_consumer_node.producers[0]
            if isinstance(producer, FilePickerNode):
                producer_widget = FilePickerWidget(producer)
            elif isinstance(producer, OperationNode):
                producer_widget = OperationNodeWidget(producer)
            elif isinstance(producer, CommonParentDirectoryNode):
                producer_widget = CommonParentDirectoryNodeWidget(producer)
            else:
                raise NotImplemented
            self.file_producer_widget.addWidget(producer_widget)
        else:
            button_widget = QWidget()
            button_layout = QVBoxLayout(button_widget)

            button_heading = QLabel(
                "Select how you want to provide this input file or directory:"
            )
            button_layout.addWidget(button_heading)

            for i, producer in enumerate(self._file_consumer_node.producers):
                if isinstance(producer, FilePickerNode):
                    button_text = "Upload a file from your computer."
                    producer_widget = FilePickerWidget(producer)
                elif isinstance(producer, OperationNode):
                    button_text = "Run an operation to generate the input file or directory."
                    producer_widget = OperationNodeWidget(producer)
                elif isinstance(producer, CommonParentDirectoryNode):
                    button_text = "Run multiple operations to generate the input files."
                    producer_widget = CommonParentDirectoryNodeWidget(producer)
                else:
                    raise NotImplemented

                button = QRadioButton(button_text)
                button.setChecked(i == self._file_consumer_node.selected_index)
                button_layout.addWidget(button)

                self.file_producer_widget.addWidget(producer_widget)

                button.clicked.connect(lambda _, i=i: self._button_clicked(i))
            layout.addWidget(button_widget)
        layout.addWidget(self.file_producer_widget)

    def _button_clicked(self, i: int) -> None:
        self._file_consumer_node.selected_index = i
        self.file_producer_widget.setCurrentIndex(i)


class CommonParentDirectoryNodeWidget(QWidget):
    def __init__(self, common_parent_directory: CommonParentDirectoryNode):
        super().__init__()
        self._common_parent_directory = common_parent_directory

        layout = QVBoxLayout(self)

        heading = QLabel(
            "You can run the operations below "
            + "to generate the necessary input files:"
        )
        heading.setWordWrap(True)
        layout.addWidget(heading)

        for file_consumer in self._common_parent_directory.file_consumers:
            file_consumer_widget = FileConsumerWidget(file_consumer)
            layout.addWidget(file_consumer_widget)


class FilePickerWidget(QWidget):
    def __init__(self, file_picker: FilePickerNode):
        super().__init__()
        self._file_picker = file_picker

        layout = QVBoxLayout(self)
        self.button = QPushButton("Browse")
        self.button.clicked.connect(self._onpopup) 
        layout.addWidget(self.button)
        self._file_picker.file_changed.connect(self._file_picker_file_changed)

    def _onpopup(self):
        self.dialog = QFileDialog()
        if isinstance(self._file_picker.produces, Directory):
            self.dialog.setFileMode(QFileDialog.FileMode.Directory)
        self.dialog.show()
        self.dialog.fileSelected.connect(self._file_selected)

    def _file_selected(self, path):
        self._file_picker.file = path

    def _file_picker_file_changed(self, new_file: str):
        self.button.setText(new_file)


class OperationNodeWidget(QWidget):
    def __init__(self, operation_node: OperationNode):
        super().__init__()
        self._operation_node = operation_node

        layout = QVBoxLayout(self)

        name = QLabel(operation_node.name)
        layout.addWidget(name)

        description = QLabel(operation_node.description)
        description.setWordWrap(True)
        layout.addWidget(description)

        input_files_widget = QWidget()
        input_files_layout = QHBoxLayout(input_files_widget)
        for file_consumer in operation_node.file_consumers:
            file_consumer_widget = FileConsumerWidget(file_consumer)
            input_files_layout.addWidget(file_consumer_widget)
        layout.addWidget(input_files_widget)


class OperationTreeWidget(QWidget):
    def __init__(self, operation_tree: OperationTree):
        super().__init__()
        self._operation_tree = operation_tree

        layout = QVBoxLayout(self)

        body = OperationNodeWidget(self._operation_tree.root)
        layout.addWidget(body)
