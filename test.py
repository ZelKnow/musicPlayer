from PyQt5.Qt import QApplication, QObject
from PyQt5.QtWidgets import QFrame, QVBoxLayout
from PyQt5.QtCore import  Qt
from PyQt5.QtGui import QFontDatabase
import sys
import os
import re
import threading
from utils import convert_time
from play_mode import PlayMode
from play_list import PlayList
from player import Player


class MainWindow(QFrame):
    '''主窗口'''
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('MainWindow')
        self.player = Player(self)

        self.set_UI()
        self.show()


    def set_UI(self):
        self.setMinimumSize(1300, 800)
        self.setMaximumSize(1600, 1000)

        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.player)
        self.setLayout(layout)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    play_list = window.player.play_list
    path = 'E:\\music\\'
    song_list = os.listdir(path)
    for file in song_list:
        play_list.add_music(path + file)
    # play_list.add_music('http://music.163.com/song/media/outer/url?id=65534.mp3')

    app.exec_()