from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class XLabel(QLabel):
    '''
    自定义标签
    自动调整字符串的显示
    '''

    def __init__(self, parent):
        super().__init__(parent)
        self.text = None

        '''设置字体'''
        font = QFont('YouYuan')
        self.setFont(font)


    def set_text(self, text):
        self.text = text
        self.setToolTip(self.text)


    def resizeEvent(self, event):
        '''调整显示长度'''
        text_to_show = self.fontMetrics().elidedText(self.text,\
            Qt.ElideRight, event.size().width())
        self.setText(text_to_show)