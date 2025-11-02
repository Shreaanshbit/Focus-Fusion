from PyQt5.QtWidgets import QApplication
from ui import FocusFusionApp
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FocusFusionApp()
    window.show()
    sys.exit(app.exec_())
