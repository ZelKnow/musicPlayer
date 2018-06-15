from PyQt5.Qt import QApplication, QObject
from PyQt5.QtWidgets import QFrame, QPushButton, QSlider, QHBoxLayout, QLabel
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtCore import QUrl, pyqtSignal, Qt
import sys
import os
import re
import threading
import utils
from play_mode import PlayMode
from play_list import PlayList


'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''
class Player(QFrame):
    '''
    音乐播放器
    TODO 歌词系统
    '''

    def __init__(self, parent):
        super().__init__(parent)
        self.parent_widget = parent
        self.setObjectName('Player')
        self.set_UI()

        # if parent == None:
        #     self.setWindowFlags(Qt.FramelessWindowHint)

        '''用于播放音乐的对象'''
        self.music_player = QMediaPlayer(self)
        self.music_player.setVolume(70)
        self.music_player.setObjectName('MusicPlayer')
        '''
        歌曲列表
        列表要显示在播放器之外的地方，因此不能把父窗口设置成self
        '''
        self.play_list = PlayList(parent)
        '''播放进度'''
        self.position = 0

        self.set_connections()


    def set_UI(self):
        self.setFrameShape(QFrame.NoFrame)
        self.setMinimumSize(1200, 80)
        self.setMaximumSize(1500, 90)

        self.set_buttons()
        self.set_sliders()
        self.set_labels()
        self.set_layout()

        with open('.\\qss\\player.qss', 'r') as file_obj:
            self.setStyleSheet(file_obj.read())


    def set_buttons(self):
        '''
        创建按钮
        '上一首'按钮、'播放'按钮、'暂停'按钮、'下一首'按钮、'静音'按钮、'恢复音量'按钮、'播放模式'按钮、'歌词'按钮、'播放列表'按钮
        '''
        self.previous_button = QPushButton(self)
        self.previous_button.setObjectName('PreviousButton')
        self.previous_button.setToolTip('上一首')
        
        self.play_button = QPushButton(self)
        self.play_button.setObjectName('PlayButton')
        self.play_button.setToolTip('播放')

        self.pause_button = QPushButton(self)
        self.pause_button.setObjectName('PauseButton')
        self.pause_button.setToolTip('暂停')
        self.pause_button.hide()

        self.next_button = QPushButton(self)
        self.next_button.setObjectName('NextButton')
        self.next_button.setToolTip('下一首')

        self.mute_button = QPushButton(self)
        self.mute_button.setObjectName('MuteButton')
        self.mute_button.setToolTip('静音')

        self.recover_button = QPushButton(self)
        self.recover_button.setObjectName('RecoverButton')
        self.recover_button.setToolTip('恢复音量')
        self.recover_button.hide()

        self.random_button = QPushButton(self)
        self.random_button.setObjectName('RandomButton')
        self.random_button.setToolTip('随机播放')
        #self.random_button.hide()

        self.loop_button = QPushButton(self)
        self.loop_button.setObjectName('LoopButton')
        self.loop_button.setToolTip('列表循环')
        self.loop_button.hide()

        self.repeat_button = QPushButton(self)
        self.repeat_button.setObjectName('RepeatButton')
        self.repeat_button.setToolTip('单曲循环')
        self.repeat_button.hide()

        self.show_lyric_button = QPushButton(self)
        self.show_lyric_button.setObjectName('ShowLyricButton')
        self.show_lyric_button.setText('词')
        self.show_lyric_button.setToolTip('打开歌词')

        self.hide_lyric_button = QPushButton(self)
        self.hide_lyric_button.setObjectName('HideLyricButton')
        self.hide_lyric_button.setToolTip('关闭歌词')
        self.hide_lyric_button.hide()

        self.list_button = QPushButton(self)
        self.list_button.setObjectName('ListButton')
        self.list_button.setToolTip('播放列表')


    def set_sliders(self):
        '''
        创建滑块
        播放进度条、音量控制条
        '''
        self.progress_slider = QSlider(self)
        self.progress_slider.setObjectName('ProgressSlider')
        self.progress_slider.setOrientation(Qt.Horizontal)
        self.progress_slider.setTracking(False)

        self.volume_slider = QSlider(self)
        self.volume_slider.setObjectName('VolumeSlider')
        self.volume_slider.setOrientation(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)


    def set_labels(self):
        '''
        创建标签
        当前播放时间、歌曲总时间
        '''
        self.time_label = QLabel(self)
        self.time_label.setObjectName('TimeLabel')
        
        self.duration_label = QLabel(self)
        self.duration_label.setObjectName('DurationLabel')


    def set_layout(self):
        '''
        创建布局
        '''

        self.layout = QHBoxLayout()
        self.layout.setObjectName('Layout')

        self.layout.addWidget(self.previous_button)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.play_button)
        self.layout.addWidget(self.pause_button)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.next_button)
        
        self.layout.addSpacing(20)
        self.layout.addWidget(self.time_label)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.progress_slider)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.duration_label)

        self.layout.addSpacing(20)
        self.layout.addWidget(self.mute_button)
        self.layout.addWidget(self.recover_button)
        self.layout.addWidget(self.volume_slider)

        self.layout.addSpacing(20)
        self.layout.addWidget(self.loop_button)
        self.layout.addWidget(self.random_button)
        self.layout.addWidget(self.repeat_button)

        self.layout.addSpacing(20)
        self.layout.addWidget(self.show_lyric_button)
        self.layout.addWidget(self.hide_lyric_button)

        self.layout.addSpacing(20)
        self.layout.addWidget(self.list_button)

        self.layout.setStretchFactor(self.previous_button, 3)
        self.layout.setStretchFactor(self.play_button, 3)
        self.layout.setStretchFactor(self.pause_button, 3)
        self.layout.setStretchFactor(self.next_button, 3)
        self.layout.setStretchFactor(self.time_label, 2)
        self.layout.setStretchFactor(self.progress_slider, 25)
        self.layout.setStretchFactor(self.duration_label, 2)
        self.layout.setStretchFactor(self.mute_button, 2)
        self.layout.setStretchFactor(self.recover_button, 2)
        self.layout.setStretchFactor(self.volume_slider, 7)
        self.layout.setStretchFactor(self.loop_button, 2)
        self.layout.setStretchFactor(self.random_button, 2)
        self.layout.setStretchFactor(self.repeat_button, 2)
        self.layout.setStretchFactor(self.show_lyric_button, 2)
        self.layout.setStretchFactor(self.hide_lyric_button, 2)
        self.layout.setStretchFactor(self.list_button, 2)

        self.setLayout(self.layout)
        self.layout.setContentsMargins(20, 5, 20, 5)


    def set_connections(self):
        '''
        连接信号和槽
        '''
        self.previous_button.clicked.connect(self.on_previous_clicked)
        self.play_button.clicked.connect(self.on_play_clicked)
        self.pause_button.clicked.connect(self.on_pause_clicked)
        self.next_button.clicked.connect(self.on_next_clicked)

        self.random_button.clicked.connect(self.on_random_clicked)
        self.repeat_button.clicked.connect(self.on_repeat_clicked)
        self.loop_button.clicked.connect(self.on_loop_clicked)
        self.list_button.clicked.connect(self.on_list_clicked)

        self.mute_button.clicked.connect(self.on_mute_clicked)
        self.recover_button.clicked.connect(self.on_recover_clicked)

        self.music_player.durationChanged.connect(self.on_music_changed)

        self.music_player.positionChanged.connect(self.on_millionsecond_changed)
        self.progress_slider.valueChanged.connect(self.on_progress_changed)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)

        '''通过点击切歌'''
        self.play_list.sig_music_index_changed.connect(self.on_music_index_changed)
        
        self.play_button.clicked.connect(self.play_list.on_music_played)
        self.pause_button.clicked.connect(self.play_list.on_music_paused)


    def on_random_clicked(self):
        self.random_button.hide()
        self.repeat_button.show()
        self.play_list.set_play_mode(PlayMode.REPEAT)


    def on_repeat_clicked(self):
        self.repeat_button.hide()
        self.loop_button.show()
        self.play_list.set_play_mode(PlayMode.LOOP)


    def on_loop_clicked(self):
        self.loop_button.hide()
        self.random_button.show()
        self.play_list.set_play_mode(PlayMode.RANDOM)


    def on_list_clicked(self):
        if self.play_list.isVisible():
            self.play_list.hide()
        else:
            self.set_list_geometry()
            self.play_list.show()


    def on_previous_clicked(self):
        content = self.play_list.previous_music()
        self.play_music(content)
        if content:
            self.play_button.hide()
            self.pause_button.show()


    def on_play_clicked(self):
        flag = True
        if self.music_player.mediaStatus() == QMediaPlayer.NoMedia:
            '''检查播放器中是否有歌曲'''
            content = self.play_list.get_music()
            if content == None:
                '''歌单中没有歌曲'''
                flag = False
            self.play_music(content)
        else:
            self.play_music()
        if flag:
            self.play_button.hide()
            self.pause_button.show()


    def on_pause_clicked(self):
        self.music_player.pause()
        self.pause_button.hide()
        self.play_button.show()


    def on_next_clicked(self):
        content = self.play_list.next_music()
        self.play_music(content)
        if content:
            self.play_button.hide()
            self.pause_button.show()


    def on_mute_clicked(self):
        self.music_player.setMuted(True)
        self.mute_button.hide()
        self.recover_button.show()


    def on_recover_clicked(self):
        self.music_player.setMuted(False)
        self.recover_button.hide()
        self.mute_button.show()


    def on_music_changed(self):
        self.time_label.setText(utils.convert_time(0))
        total_time = self.music_player.duration() // 1000
        if total_time > 0:
            self.duration_label.setText(utils.convert_time(total_time))

            '''处理没有连接的异常'''
            try:
                self.progress_slider.valueChanged.disconnect(self.on_progress_changed)
                self.progress_slider.setRange(0, total_time)
                self.progress_slider.setValue(0)
                self.progress_slider.valueChanged.connect(self.on_progress_changed)
            except TypeError:
                self.progress_slider.setRange(0, total_time)
                self.progress_slider.setValue(0)


    def on_millionsecond_changed(self, current_position):
        current_position = current_position // 1000
        if current_position != self.position:
            self.position = current_position
            self.on_second_changed()

    
    def on_second_changed(self):
        self.time_label.setText(utils.convert_time(self.position))

        '''处理没有连接的异常，disconnect和connect必须配对使用，否则听歌体验极差'''
        try:
            self.progress_slider.valueChanged.disconnect(self.on_progress_changed)
            self.increase_progress()
            self.progress_slider.valueChanged.connect(self.on_progress_changed)
        except TypeError:
            self.increase_progress()


    def on_progress_changed(self, progress):
        ratio = progress / self.progress_slider.maximum()
        position = int(self.music_player.duration() * ratio)
        self.music_player.setPosition(position)


    def on_volume_changed(self, volume):
        '''播放器原本的音量较大，这里稍微减少一些'''
        volume = int(volume / 100 * 70)
        self.music_player.setVolume(volume)
        '''用户拖动音量条，自动从静音中恢复'''
        self.on_recover_clicked()


    def on_music_index_changed(self):
        '''通过播放列表切换歌曲'''
        content = self.play_list.get_music()
        self.play_music(content)

        self.pause_button.show()
        self.play_button.hide()


    def moveEvent(self, event):
        self.set_list_geometry()


    def increase_progress(self):
        '''进度增加1'''
        value = self.progress_slider.value()
        value += 1
        if value > self.progress_slider.maximum():
            self.on_next_clicked()
        else:
            self.progress_slider.setValue(value)
    

    def play_music(self, content=None):
        if content:
            self.music_player.setMedia(content)
        # url = QUrl.fromLocalFile('D:\\CloudMusic\\zun\\上海アリス幻樂団 - 少女幻葬 ～ Necro-Fantasy.mp3')
        # content = QMediaContent(url)
        # self.music_player.setMedia(content)
        self.music_player.play()


    def set_list_geometry(self):
        x = self.x() + self.width() - self.play_list.width()
        y = self.y() - self.play_list.height()
        self.play_list.move(x, y)

'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''