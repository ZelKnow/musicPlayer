from PyQt5.QtWidgets import QLineEdit, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

"""处理时间，处理成00:00:00的格式。"""
def deal_time(x):
    x = str(x)
    if len(x) == 1:
        x = '0' + x

    return x

def itv2time(iItv):
    iItv = int(iItv)

    # 地板除求小时整数。
    h = iItv//3600
    # 求余数。
    h_remainder = iItv % 3600

    # 地板除求分钟整数。
    m = h_remainder // 60
    # 求余数 为秒。
    s = h_remainder % 60

    return ":".join(map(deal_time,(m,s)))




if __name__ == '__main__':
    # import sys

    # app = QApplication(sys.argv)

    # main = SearchLineEdit()

    # main.show()

    # sys.exit(app.exec_())
    print(itv2time(51525675423))