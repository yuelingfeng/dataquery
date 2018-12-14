import sys
from PyQt5.QtWidgets import QApplication
from dataquery import DataQuery


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dq = DataQuery()
    dq.show()
    sys.exit(app.exec_())

