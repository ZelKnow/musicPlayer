# !/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'HYA'
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from widget import ScrollArea
import sys


# 去除了margin和spacing的布局框。
class VBoxLayout(QVBoxLayout):

    def __init__(self, *args):
        super(VBoxLayout, self).__init__(*args)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)


class HBoxLayout(QHBoxLayout):

    def __init__(self, *args):
        super(HBoxLayout, self).__init__(*args)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)


class TableWidget(QTableWidget):

    def __init__(self, count, headerLables):
        super(TableWidget, self).__init__()
        self.setColumnCount(count)
        self.setHorizontalHeaderLabels(headerLables)

        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def setColumnWidths(self, widths:dict):
        for key in widths:
            self.setColumnWidth(key, widths[key])


class SingsSearchResultFrameBase(QFrame):

    def __init__(self, parent):
        super(SingsSearchResultFrameBase, self).__init__()
        self.parent = parent

        self.singsFrameLayout = VBoxLayout(self)

        self.noSingsContentsLabel = QLabel(self)
        self.noSingsContentsLabel.setMaximumHeight(60)

        self.noSingsContentsLabel.setObjectName("noSingsLabel")
        self.noSingsContentsLabel.hide()

        self.singsResultTable = TableWidget(3, ['音乐标题', '歌手', '时长'])
        self.singsResultTable.setObjectName('singsTable')
        self.singsResultTable.setMinimumWidth(self.parent.width())
        self.singsResultTable.setColumnWidths({i: j for i, j in zip(range(3),
                                                                    [self.parent.width() / 3 * 1.25,
                                                                     self.parent.width() / 3 * 1.25,
                                                                     self.parent.width() / 3 * 0.5])})

        self.singsFrameLayout.addWidget(self.singsResultTable, Qt.AlignTop | Qt.AlignCenter)

        self.centerLabelLayout = HBoxLayout()
        self.centerLabelLayout.addStretch(1)
        self.centerLabelLayout.addWidget(self.noSingsContentsLabel)
        self.centerLabelLayout.addStretch(1)

        self.singsFrameLayout.addLayout(self.centerLabelLayout)


class NetEaseSearchResultFrame(SingsSearchResultFrameBase):

    def __init__(self, parent):
        super(NetEaseSearchResultFrame, self).__init__(parent)


class XiamiSearchResultFrame(SingsSearchResultFrameBase):

    def __init__(self, parent):
        super(XiamiSearchResultFrame, self).__init__(parent)


class QQSearchResultFrame(SingsSearchResultFrameBase):

    def __init__(self, parent):
        super(QQSearchResultFrame, self).__init__(parent)

# 搜索结果显示页
class SearchArea(ScrollArea):
    def __init__(self, parent=None):
        super(SearchArea, self).__init__(self)
        self.parent = parent
        self.setObjectName("Search Area")
        with open('QSS/searchArea.qss', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
        # self.frame = QFrame()
        self.mainLayout = QVBoxLayout(self.frame)

        self.titleLabel = QLabel(self.frame)

        # 搜索结果的tab。
        self.contentsTab = QTabWidget(self.frame)

        # 加入布局。
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.contentsTab)

        self.setSingsFrame()

    # 布局。
    def setSingsFrame(self):
        # 单曲界面。
        self.neteaseSearchFrame = NetEaseSearchResultFrame(self)
        self.contentsTab.addTab(self.neteaseSearchFrame, "网易云")

        self.xiamiSearchFrame = XiamiSearchResultFrame(self)
        self.contentsTab.addTab(self.xiamiSearchFrame, "虾米")

        self.qqSearchFrame = QQSearchResultFrame(self)
        self.contentsTab.addTab(self.qqSearchFrame, 'QQ')

    # 功能。
    def setText(self, text):
        self.text = text
        # self.text = '周杰伦'
        # print(self.text)
        self.titleLabel.setText("搜索<font color='#23518F'>“{0}”</font><br>".format(self.text))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = SearchArea()
    main_window.show()
    sys.exit(app.exec_())
