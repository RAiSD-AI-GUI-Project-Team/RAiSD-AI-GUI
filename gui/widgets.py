"""
A module containing base UI classes.

The classes extend default PySide widgets and layouts to make them
stylable and remove margins and spacing.
"""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QStyle,
    QStyleOption,
)
from PySide6.QtGui import (
    QPainter,
)


class StylableWidget(QWidget):
    def paintEvent(self, event) -> None:
        # Override paintEvent so that QSS styling is applied.
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(
            QStyle.PrimitiveElement.PE_Widget,
            opt,
            painter,
            self,
        )


class HBoxLayout(QHBoxLayout):
    def __init__(
            self,
            parent: QWidget,
            *,
            left: int = 0,
            top: int = 0,
            right: int = 0,
            bottom: int = 0,
            spacing: int = 0,
    ) -> None:
        super().__init__(parent)
        self.setContentsMargins(left, top, right, bottom)
        self.setSpacing(spacing)


class VBoxLayout(QVBoxLayout):
    def __init__(
            self,
            parent: QWidget,
            *,
            left: int = 0,
            top: int = 0,
            right: int = 0,
            bottom: int = 0,
            spacing: int = 0,
    ) -> None:
        super().__init__(parent)
        self.setContentsMargins(left, top, right, bottom)
        self.setSpacing(spacing)


class ResizableStackedWidget(QWidget):
    """
    A stacked widget that scales to the size of the current widget.
    """

    def __init__(
            self,
    ) -> None:
        """
        Initialize a `ResizableStackedWidget` object.
        """
        super().__init__()

        VBoxLayout(self)
        self._widgets : list[QWidget] = []
        self._current_index = 0

    @property
    def current_index(self) -> int:
        """
        The index of the child widget currently displayed.
        """
        return self._current_index

    @current_index.setter
    def current_index(self, new_index: int) -> None:
        self._current_index = new_index
        self._show_current_widget()

    def addWidget(self, widget: QWidget) -> None:
        layout = self.layout()
        if not layout:
            return
        layout.addWidget(widget)
        self._widgets.append(widget)
        self._show_current_widget()

    def _show_current_widget(self) -> None:
        layout = self.layout()
        if not layout:
            return
        if layout.count() == 0:
            return
        for widget in self._widgets:
            widget.hide()
        self._widgets[self.current_index].show()
        self.updateGeometry()
