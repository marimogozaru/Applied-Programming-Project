import sys
from PySide6.QtWidgets import QApplication
from view.main_view import MainView

app = QApplication(sys.argv)
window = MainView()
window.show()
sys.exit(app.exec())