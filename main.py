import sys
import os.path

import asyncio
import logging
from quamash import QEventLoop
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from widget import Navigation,Header,MainContent,DetailSings
from player import Player
from function import ConfigNavigation,ConfigWindow,ConfigDetailSings

from SearchFromHeader import ConfigHeader
from SearchArea import SearchArea
from ConfigSearchArea import ConfigSearchArea


# 用于承载整个界面。所有窗口的父窗口，所有窗口都可以在父窗口里找到索引。
class mainWindow(QWidget):
    """Window 承载整个界面。"""

    def __init__(self):
        super(mainWindow, self).__init__()
        self.setObjectName('MainWindow')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon('resource/format.ico'))
        self.setWindowTitle("Music")
        self.resize(1000, 800)

        self.setUI() # 加载各个组件
        self.setTab() # 设置tab
        self.setLines() # 对布局进行细线设置
        self.setLayouts() # 设置整体布局
        self.setFunction() #设置各项组件功能

        with open('QSS/window.qss', 'r') as f:
            self.setStyleSheet(f.read())

    def setUI(self):
        self.header = Header(self)
        self.navigation = Navigation(self)
        self.mainContent = MainContent(self)
        self.player = Player(self)
        self.mainContents = QTabWidget()
        self.detailSings = DetailSings(self)
        # 搜索页面
        self.searchArea = SearchArea(self)

    def setLayouts(self):
        self.mainLayout = QVBoxLayout() #垂直布局
        self.mainLayout.addWidget(self.header)
        self.mainLayout.addWidget(self.line1)

        self.contentLayout = QHBoxLayout() #水平布局
        self.contentLayout.setStretch(0, 70)
        self.contentLayout.setStretch(1, 570)

        self.contentLayout.addWidget(self.navigation)
        self.contentLayout.addWidget(self.line2)
        self.contentLayout.addWidget(self.mainContents)
        self.contentLayout.setSpacing(0)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addLayout(self.contentLayout)
        self.mainLayout.addWidget(self.line1)
        self.mainLayout.addWidget(self.player)

        self.mainLayout.setStretch(0, 43)
        self.mainLayout.setStretch(1, 0)
        self.mainLayout.setStretch(2, 576)
        self.mainLayout.setStretch(3, 50)

        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)

    # 布局。
    def setTab(self):
        """设置tab界面。"""
        # 增加搜索显示区域
        self.mainContents.addTab(self.searchArea, '')
        # self.mainContents.addTab(self.mainContent, '')
        self.mainContents.setCurrentIndex(0)

    def setLines(self):
        """设置布局小细线。"""
        self.line1 = QFrame(self) #用于在组件周围添加边框
        self.line1.setObjectName("line1")
        self.line1.setFrameShape(QFrame.HLine) #设置边框，水平线
        self.line1.setFrameShadow(QFrame.Plain) #设置窗口无阴影
        self.line1.setLineWidth(4) #设置线条宽度

        self.line2 = QFrame(self)
        self.line2.setObjectName("line2")
        self.line2.setFrameShape(QFrame.VLine)  # 设置边框，垂直线
        self.line2.setFrameShadow(QFrame.Plain)  # 设置窗口无阴影
        self.line2.setLineWidth(4)  # 设置线条宽度

    def setFunction(self):
        # self.config = ConfigWindow(self)
        self.navigation.config = ConfigNavigation(self.navigation)
        # self.detailSings.config = ConfigDetailSings(self.detailSings)
        self.searchArea.config = ConfigSearchArea(self.searchArea)
        self.header.config = ConfigHeader(self.header)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 将Qt事件循环写到asyncio事件循环里。
    # QEventLoop不是Qt原生事件循环，
    # 是被asyncio重写的事件循环。
    # eventLoop = QEventLoop(app)
    # asyncio.set_event_loop(eventLoop)

    main_window = mainWindow()
    main_window.show()
    sys.exit(app.exec_())

