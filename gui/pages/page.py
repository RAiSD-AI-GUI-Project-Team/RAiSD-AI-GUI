from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QWidget,
    QStyle,
    QStyleOption,
)

class Page(QWidget):
    """
    An abstract base class for the main pages of the application.
    Each page should inherit from this class and 
    implement the _setup_ui and update_ui methods.
    """
    def __init__(self) -> None:
        """
        Initialize the page.
        """
        super().__init__()
        self.setObjectName("page")

    def _setup_ui(self) -> None:
        """
        Set up the UI elements of the page.

        This method should be implemented by each page subclass.
        """
        raise NotImplementedError()

    def paintEvent(self, event) -> None:
        """
        Override paintEvent so that QSS styling (background, border,
        etc.) is applied to this plain QWidget subclass.
        """
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
