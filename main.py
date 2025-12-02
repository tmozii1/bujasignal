# main.py
import sys
from PyQt5.QtWidgets import QApplication

from roi_window import RoiWindow


def main():
    app = QApplication(sys.argv)
    w = RoiWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
