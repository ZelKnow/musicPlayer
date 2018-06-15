from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os.path
import logging
import sys

class PlayListTitle(QFrame):
    '''播放列表的标题'''

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName('PlayListTitle')
        self.set_UI()

    def set_UI(self):
        self.setFrameShape(QFrame.NoFrame)

        self.close_button = QPushButton(self)
        self.close_button.setObjectName('CloseButton')
        self.close_button.setToolTip('关闭')

        self.title_label = XLabel(self)
        self.title_label.setObjectName('TitleLabel')
        self.title_label.set_text('播放列表')

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(5, 13, 5, 13)
        self.layout.addWidget(self.title_label)
        self.layout.addStretch(1)
        self.layout.addWidget(self.close_button)
        self.setLayout(self.layout)
        '''设置对齐方式：垂直居中'''
        self.layout.setAlignment(self.title_label, Qt.AlignVCenter)
        self.layout.setAlignment(self.close_button, Qt.AlignVCenter)

        with open('.\\qss\\play_list_title.qss', 'r') as file_obj:
            self.setStyleSheet(file_obj.read())


'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''

'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''


class PlayListTable(QScrollArea):
    '''播放列表主体'''

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName('PlayListTable')
        self.set_UI()

    def set_UI(self):
        self.setFrameShape(QFrame.NoFrame)

        '''
        QScrollArea只能设置一个widget
        因此要在这一个widget上添加其他widget
        比如ListEntry
        '''
        self.contents = QFrame(self)
        self.contents.setObjectName('Contents')
        self.contents.setFrameShape(QFrame.NoFrame)
        '''这个layout是给contents的'''
        self.set_layout()

        '''设置滚动条'''
        self.scroll_bar = QScrollBar(self)
        self.setVerticalScrollBar(self.scroll_bar)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        '''这个语句非常关键'''
        self.setWidgetResizable(True)
        self.setWidget(self.contents)

        with open('.\\qss\\play_list_table.qss', 'r') as file_obj:
            self.setStyleSheet(file_obj.read())

    def set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.addStretch(1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.contents.setLayout(self.layout)

    def insert_entry(self, entry, index):
        self.layout.insertWidget(index, entry)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test = PlayListTitle()
    test.show()
    sys.exit(app.exec_())

