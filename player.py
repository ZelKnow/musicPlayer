from PyQt5.Qt import QApplication, QObject
from PyQt5.QtWidgets import QFrame, QPushButton, QSlider, QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QUrl, pyqtSignal, Qt, QTimer
import sys
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

    sig_music_status_changed = pyqtSignal(bool)

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
        self.millionsecond = 0
        self.second = 0

        self.lyric_panel = LyricPanel()

        self.set_connections()


    def set_UI(self):
        self.setFrameShape(QFrame.NoFrame)
        self.setMinimumSize(1200, 80)
        self.setMaximumHeight(100)

        self.set_buttons()
        self.set_sliders()
        self.set_labels()
        self.set_layout()

        with open('.\\QSS\\player.qss', 'r') as file_obj:
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
        self.show_lyric_button.setFont(QFont('YouYuan', 14))
        self.show_lyric_button.setToolTip('打开歌词')

        self.hide_lyric_button = QPushButton(self)
        self.hide_lyric_button.setObjectName('HideLyricButton')
        self.hide_lyric_button.setText('词')
        self.hide_lyric_button.setFont(QFont('YouYuan', 14))
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
        self.time_label.setFont(QFont('YouYuan'))
        
        self.duration_label = QLabel(self)
        self.duration_label.setObjectName('DurationLabel')
        self.duration_label.setFont(QFont('YouYuan'))


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
        # self.layout.setStretchFactor(self.show_lyric_button, 2)
        # self.layout.setStretchFactor(self.hide_lyric_button, 2)
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

        self.show_lyric_button.clicked.connect(self.on_show_lyric_clicked)
        self.hide_lyric_button.clicked.connect(self.on_hide_lyric_clicked)

        self.music_player.durationChanged.connect(self.on_music_changed)

        self.music_player.positionChanged.connect(self.on_millionsecond_changed)
        self.music_player.positionChanged.connect(self.lyric_panel.on_millionsecond_changed)
        self.progress_slider.valueChanged.connect(self.on_progress_changed)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)

        '''通过点击切歌'''
        self.play_list.sig_music_index_changed.connect(self.on_music_index_changed)
        '''播放状态改变，同时改变图标'''
        self.sig_music_status_changed.connect(self.play_list.on_music_status_changed)
        
        # self.play_button.clicked.connect(self.play_list.on_music_played)
        # self.pause_button.clicked.connect(self.play_list.on_music_paused)


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
            self.play_list.raise_()


    def on_previous_clicked(self):
        content = self.play_list.previous_music()
        self.play_music(content)
        if content:
            self.play_button.hide()
            self.pause_button.show()
            self.sig_music_status_changed.emit(False)


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
            self.sig_music_status_changed.emit(False)

            if self.lyric_panel.isVisible():
                self.lyric_panel.restart_lyric()


    def on_pause_clicked(self):
        self.music_player.pause()
        self.pause_button.hide()
        self.play_button.show()
        self.sig_music_status_changed.emit(True)

        if self.lyric_panel.isVisible():
                self.lyric_panel.pause_lyric()


    def on_next_clicked(self):
        content = self.play_list.next_music()
        self.play_music(content)
        if content:
            self.play_button.hide()
            self.pause_button.show()
            self.sig_music_status_changed.emit(False)


    def on_mute_clicked(self):
        self.music_player.setMuted(True)
        self.mute_button.hide()
        self.recover_button.show()


    def on_recover_clicked(self):
        self.music_player.setMuted(False)
        self.recover_button.hide()
        self.mute_button.show()


    def on_music_changed(self):
        self.time_label.setText(utils.time_int_to_str(0))
        total_time = self.music_player.duration() // 1000
        if total_time > 0:
            self.duration_label.setText(utils.time_int_to_str(total_time))

            '''处理没有连接的异常'''
            try:
                self.progress_slider.valueChanged.disconnect(self.on_progress_changed)
                self.progress_slider.setRange(0, total_time)
                self.progress_slider.setValue(0)
                self.progress_slider.valueChanged.connect(self.on_progress_changed)
            except TypeError:
                self.progress_slider.setRange(0, total_time)
                self.progress_slider.setValue(0)

            if self.lyric_panel.isVisible():
                lyric, title = self.play_list.get_lyric_and_title()
                current_time = 0
                total_time = self.music_player.duration()
                self.lyric_panel.show_lyric(lyric, title, current_time, total_time)


    def on_millionsecond_changed(self, current_position):
        self.millionsecond = current_position
        current_position = current_position // 1000
        if current_position != self.second:
            self.second = current_position
            self.on_second_changed()

    
    def on_second_changed(self):
        self.time_label.setText(utils.time_int_to_str(self.second))

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
        '''
        播放列表中正在播放的歌曲切换了
        有可能是通过点击播放列表切歌
        也有可能是播放新加入的歌曲
        '''
        content = self.play_list.get_music()
        self.play_music(content)

        self.pause_button.show()
        self.play_button.hide()

        self.sig_music_status_changed.emit(False)


    def on_show_lyric_clicked(self):
        self.show_lyric_button.hide()
        self.hide_lyric_button.show()

        if self.music_player.mediaStatus() != QMediaPlayer.NoMedia:
            lyric, title = self.play_list.get_lyric_and_title()
            current_time = self.millionsecond
            total_time = self.music_player.duration()
            self.lyric_panel.show_lyric(lyric, title, current_time, total_time)
        else:
            self.lyric_panel.show_lyric(None, None, None, None)


    def on_hide_lyric_clicked(self):
        self.hide_lyric_button.hide()
        self.show_lyric_button.show()
        self.lyric_panel.hide_lyric()


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
        self.music_player.play()


    def set_list_geometry(self):
        x = self.x() + self.width() - self.play_list.width()
        y = self.y() - self.play_list.height()
        self.play_list.move(x, y)


'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''


class LyricPanel(QFrame):
    '''歌词面板'''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('LyricPanel')
        self.set_UI()


    def set_UI(self):
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFrameShape(QFrame.NoFrame)
        self.setFixedHeight(100)
        self.setFixedWidth(800)
        self.setAttribute(Qt.WA_TranslucentBackground)

        desktop = QApplication.desktop()
        desktop_rect = desktop.screenGeometry()
        self.move((desktop_rect.width() - 800) // 2, 0)

        self.set_labels()
        self.set_layout()

        self.hide()

        with open('QSS\\lyric_panel.qss', 'r') as file_obj:
            self.setStyleSheet(file_obj.read())


    def set_labels(self):
        self.lyric_label = LLabel(self)
        self.lyric_label.setObjectName('LyricLabel')


    def set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.lyric_label)
        
        self.setLayout(self.layout)


    def show_lyric(self, lyric, title, current_time, total_time):
        self.lyric_label.show_lyric(lyric, title, current_time, total_time)
        self.show()


    def hide_lyric(self):
        self.lyric_label.stop_timer()
        self.hide()


    def pause_lyric(self):
        if self.lyric_label.timer:
            self.lyric_label.timer.stop()


    def restart_lyric(self):
        if self.lyric_label.timer:
            self.lyric_label.timer.start(30)


    def on_millionsecond_changed(self, current_time):
        self.lyric_label.time = current_time


'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''


class LLabel(QLabel):
    '''歌词标签'''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('LLabel')
        self.set_UI()

        self.lyric = None
        self.lyric_length = None
        # self.lyric_width = 0
        # self.mask_width = 0
        self.index = 0
        self.timer = None
        self.time = None


    def set_UI(self):
        self.set_font()
        self.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.setAttribute(Qt.WA_TranslucentBackground)
        

    def set_font(self):
        self.font = QFont('微软雅黑', 30)
        self.font.setBold(True)
        self.setFont(self.font)


    def show_lyric(self, lyric, title, current_time, total_time):
        '''从current_time开始显示歌词'''
        self.lyric = lyric
        self.time = current_time

        if lyric:
            '''歌词存在则显示歌词'''
            idx = 0
            size = len(lyric)
            while idx < size and lyric[idx][0] < current_time:
                idx += 1
            
            idx = max(idx - 1, 0)
            self.index = idx
            self.lyric_length = size
            self.setText(lyric[idx][1])

            '''设置定时器'''
            if self.timer != None:
                del self.timer
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.on_timeout)
            self.timer.start(30)

        elif title:
            '''歌词不存在，显示歌名'''
            self.index = None
            self.setText(title)

        else:
            '''没有音乐正在播放'''
            self.index = None
            self.setText('KASW Music Player')


    def stop_timer(self):
        if self.timer:
            self.timer.stop()
            del self.timer
            self.timer = None


    def on_timeout(self):
        if self.index < self.lyric_length - 1:
            if self.lyric[self.index + 1][0] < self.time:
                self.index += 1
                self.setText(self.lyric[self.index][1])