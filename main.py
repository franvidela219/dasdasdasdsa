import sys
from PyQt5.QtWidgets import QApplication
from ventana import GameTrackerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameTrackerApp()
    window.show()
    sys.exit(app.exec_())

