import sys
from PySide6.QtWidgets import QApplication
from view.main_view import MainViewModel

app = QApplication(sys.argv)
window = MainViewModel()
window.show()
sys.exit(app.exec())