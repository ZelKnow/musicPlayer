from PyQt5.QtWidgets import QPushButton, QFrame, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QScrollArea, QScrollBar, QWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaMetaData
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QUrl, Qt, pyqtSignal
from random import randint
from play_mode import PlayMode
from xlabel import XLabel
import utils
import enum


'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''
class PlayList(QFrame):
    '''
    播放列表
    '''

    sig_music_added = pyqtSignal(dict)
    sig_music_index_changed = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.parent_widget = parent
        self.setObjectName('PlayList')
        self.set_UI()

        '''播放列表，元素是QUrl'''
        self.music_list = []
        self.music_count = 0
        self.play_mode = PlayMode.RANDOM

        self.last_play = None
        self.music_index = None

        self.entries = []

        self.set_connections()
    

    def set_UI(self):
        self.setFrameShape(QFrame.Box)
        self.title = PlayListTitle(self)
        self.table = PlayListTable(self)

        '''
        在构造函数没有结束前
        geometry()的返回值是错误的
        不能在这个函数里面setGeometry()
        '''

        self.set_layout()
        with open('.\\qss\\play_list.qss', 'r') as file_obj:
            self.setStyleSheet(file_obj.read())
        self.hide()   


    def set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.table, 1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.setLayout(self.layout)


    def set_connections(self):
        self.title.close_button.clicked.connect(self.hide)
        self.sig_music_added.connect(self.on_music_added)
        '''
        由于ListEntry是动态创建、销毁的
        信号和槽的连接不放在这个函数中
        放在了on_music_added函数中
        '''


    def set_play_mode(self, mode):
        '''切换播放模式'''
        if mode in PlayMode:
            self.play_mode = mode


    def add_music(self, music_info, play=False):
        '''
        向播放列表添加歌曲
        music_info类型是字典
        music_info['url']
        music_info['name']
        music_info['time']
        music_info['author']
        music_info['music_img']
        play标识是否立即播放
        '''
        url = music_info['url']
        flag = False

        if isinstance(url, QUrl):
            flag = True

        elif isinstance(url, str):
            '''
            如果是本地文件的路径，要写fromLocalFile
            否则直接用QUrl(song)无法正常播放
            '''
            if 'http' in url or 'https' in url or 'file' in url:
                url = QUrl(url)
            else:
                url = QUrl.fromLocalFile(url)
            flag = True

        if flag:
            self.music_list.append(url)
            self.music_count += 1
            self.sig_music_added.emit(music_info)

            if play:
                self.music_index = self.music_count - 1
                self.sig_music_index_changed.emit()


    def get_music(self):
        '''
        得到当前播放的歌
        如果music_index为None，根据播放方式选择一个值
        如果播放列表为空，返回None
        '''
        if self.music_list:
            if self.music_index == None:
                if self.play_mode == PlayMode.RANDOM:
                    self.music_index = randint(0, self.music_count - 1)
                else:
                    self.music_index = 0
            song_url = self.music_list[self.music_index]
            return QMediaContent(song_url)
        return None


    def previous_music(self):
        '''切换到上一首歌'''
        if self.music_list and self.music_index != None:
            if self.play_mode == PlayMode.RANDOM:
                next_index = randint(0, self.music_count - 1)

            elif self.play_mode == PlayMode.LOOP:
                next_index  = self.music_index - 1
                if next_index < 0:
                    next_index = self.music_count - 1

            elif self.play_mode == PlayMode.REPEAT:
                next_index = self.music_index

            self.music_index = next_index
            song_url = self.music_list[self.music_index]
            return QMediaContent(song_url)
        return None

    
    def next_music(self):
        '''切换到下一首歌'''
        if self.music_list and self.music_index != None:
            if self.play_mode == PlayMode.RANDOM:
                next_index = randint(0, self.music_count - 1)

            elif self.play_mode == PlayMode.LOOP:
                next_index = self.music_index + 1
                if next_index >= self.music_count:
                    next_index = 0

            elif self.play_mode == PlayMode.REPEAT:
                next_index = self.music_index

            self.music_index = next_index
            song_url = self.music_list[self.music_index]
            return QMediaContent(song_url)
        return None


    def create_entry(self, music_info):
        '''把创建entry、连接信号和槽封装'''
        entry = ListEntry(self.table, music_info, self.music_count - 1)
        entry.sig_double_clicked.connect(self.on_double_clicked)
        return (entry, self.music_count - 1)


    def on_music_added(self, music_info):
        '''
        播放列表添加了一首歌
        创建新的ListEntry并添加到table中
        此时self.music_count已经更新
        '''
        entry, index = self.create_entry(music_info)
        self.entries.append(entry)
        self.table.insert_entry(entry, index)


    def on_double_clicked(self, index):
        '''
        播放列表第index项被双击
        处理ListEntry的sig_double_clicked信号
        '''
        if index >=0 and index < self.music_count:
            self.music_index = index
            '''使播放器切换歌曲'''
            self.sig_music_index_changed.emit()

    
    def on_music_status_changed(self, is_paused):
        '''
        当歌曲播放状态改变（切歌、播放、暂停）时
        调整播放列表中的图片
        '''
        if self.last_play != None:
            if self.last_play >= 0 and self.last_play < self.music_count:
                self.entries[self.last_play].set_status_label(LabelImage.EMPTY)
        self.last_play = self.music_index

        if self.music_index != None:
            if self.music_index >= 0 and self.music_index < self.music_count:
                if is_paused:
                    self.entries[self.music_index].set_status_label(LabelImage.PAUSE)
                else:
                    self.entries[self.music_index].set_status_label(LabelImage.PLAY)
                    self.table.ensureWidgetVisible(self.entries[self.music_index], 0, 300)


'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''



'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''
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


'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''



'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''
@enum.unique
class LabelImage(enum.Enum):
    '''标签图像'''
    EMPTY = 0
    PLAY = 1
    PAUSE = 2


class ListEntry(QFrame):
    '''
    播放列表中的条目
    TODO: 右键菜单
    '''

    sig_double_clicked = pyqtSignal(int)

    def __init__(self, parent, music_info, index):
        '''
        music_info['url']  music_info['name']  music_info['time']
        music_info['author']  music_info['music_img']
        '''

        super().__init__(parent)
        self.setObjectName('ListEntry')
        
        '''标识这个条目在播放列表中的位置'''
        self.index = index

        self.music_title = music_info['name']
        self.music_artist = music_info['author']
        self.music_duration = music_info['time']
        self.music_image = music_info['music_img']

        self.set_UI()


    def set_UI(self):
        self.setFrameShape(QFrame.NoFrame)
        
        self.set_labels()
        self.set_layout()

        with open('.\\qss\\list_entry.qss', 'r') as file_obj:
            self.setStyleSheet(file_obj.read())



    def set_labels(self):
        self.status_label = XLabel(self)
        self.status_label.setObjectName('StatusLabel')
        
        self.song_label = XLabel(self)
        self.song_label.setObjectName('SongLabel')
        self.song_label.set_text(self.music_title)
        # self.song_label.setText(self.music_title)

        self.artist_label = XLabel(self)
        self.artist_label.setObjectName('ArtistLabel')
        self.artist_label.set_text(self.music_artist)
        # self.artist_label.setText(self.music_artist)

        self.duration_label = XLabel(self)
        self.duration_label.setObjectName('DurationLabel')
        self.duration_label.set_text(self.music_duration)
        # self.duration_label.setText(self.music_duration)


    def set_layout(self):
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.layout.addWidget(self.status_label)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.song_label, 42)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.artist_label, 17)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.duration_label, 8)
        self.setLayout(self.layout)


    def mouseDoubleClickEvent(self, event):
        # print(self.index)
        self.sig_double_clicked.emit(self.index)


    def set_status_label(self, image):
        if image == LabelImage.EMPTY:
            pixmap = QPixmap()
        elif image == LabelImage.PLAY:
            pixmap = QPixmap('.\\images\\play_2.png')
        elif image == LabelImage.PAUSE:
            pixmap = QPixmap('.\\images\\pause_2.png')

        self.status_label.setScaledContents(True)
        self.status_label.setPixmap(pixmap)
        self.status_label.setAlignment(Qt.AlignCenter)

'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''