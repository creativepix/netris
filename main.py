import sys
from PyQt5.QtWidgets import QApplication
from ui.main_controller import MainController

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_controller = MainController()
    main_controller.show()
    sys.exit(app.exec_())
