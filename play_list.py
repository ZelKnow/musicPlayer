from PyQt5.QtMultimedia import QMediaContent, QMediaMetaData
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from random import randint
from play_mode import PlayMode
from mutagen.mp3 import EasyMP3 as MP3
import utils
import enum
import sys


'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''
class PlayList(QFrame):
    '''
    播放列表
    '''

    sig_list_changed = pyqtSignal()
    sig_music_added = pyqtSignal(QUrl)
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

        self.sig_list_changed.connect(self.on_list_changed)
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

    
    def set_music_list(self, music_list, current_song=None):
        '''
        设置播放列表
        music_list：新的播放列表
        current_song：新的播放列表中将要播放的歌，类型是QUrl
        '''
        self.music_list = music_list
        if current_song == None:
            self.music_index = None
        elif current_song in music_list:
            self.music_index = music_list.index(current_song)
        else:
            self.music_index = None
        
        if music_list:
            self.music_count = len(music_list)
        else:
            self.music_count = 0

        self.sig_list_changed.emit()


    def set_music_index(self, music_index):
        if music_index >= 0 and music_index < len(self.music_list):
            self.music_index = music_index


    def add_music(self, song):
        '''
        向播放列表添加歌曲
        song类型是str（表示一个URL）或QUrl
        '''
        if isinstance(song, QUrl):
            self.music_list.append(song)
            self.music_count += 1
            self.sig_music_added.emit(song)

        elif isinstance(song, str):
            '''
            如果是本地文件的路径，一定要写fromLocalFile
            否则直接用QUrl(song)无法正常播放
            '''
            if 'http' in song or 'https' in song or 'file' in song:
                url = QUrl(song)
            else:
                url = QUrl.fromLocalFile(song)
            self.music_list.append(url)
            self.music_count += 1

            self.sig_music_added.emit(url)


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
                next_index -= 1
                if next_index < 0:
                    next_index = self.music_count - 1

            self.move_status_label(next_index)
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
                next_index += 1
                if next_index >= self.music_count:
                    next_index = 0

            self.move_status_label(next_index)
            self.music_index = next_index

            song_url = self.music_list[self.music_index]
            return QMediaContent(song_url)
        return None


    def create_entry(self, path):
        '''把创建entry和连接信号和槽封装'''
        entry = ListEntry(self.table, path, self.music_count - 1)
        entry.sig_double_clicked.connect(self.on_double_clicked)
        self.entries.append(entry)
        return (entry, self.music_count - 1)


    def move_status_label(self, index):
        '''
        移动表项的播放/暂停图标
        self.music_index还没有被修改的时候调用这个函数
        '''
        if self.music_index != None:
            self.entries[self.music_index].set_status_label(LabelImage.EMPTY)
            
            '''调整滚动条位置'''
            if self.music_index != index:
                self.table.ensureWidgetVisible(self.entries[index], 0, 200)

        self.entries[index].set_status_label(LabelImage.PLAY)


    def on_list_changed(self):
        '''播放列表发生变化'''
        pass


    def on_music_added(self, url):
        '''播放列表添加了一首歌'''
        path = url.path()
        path = path[1:]
        # print(path)
        entry, index = self.create_entry(path)
        self.table.insert_entry(entry, index)


    def on_double_clicked(self, index):
        '''播放列表第index项被双击'''
        if index >=0 and index < self.music_count:
            self.move_status_label(index)
            self.music_index = index
            '''使播放器切换歌曲'''
            self.sig_music_index_changed.emit()


    def on_music_played(self):
        '''
        播放器的PlayButton被按下
        相应的条目显示播放图标
        '''
        if self.music_index >= 0 and self.music_index < self.music_count:
            self.entries[self.music_index].set_status_label(LabelImage.PLAY)


    def on_music_paused(self):
        '''
        播放器的PauseButton被按下
        相应的条目显示暂停图标
        '''
        if self.music_index >= 0 and self.music_index < self.music_count:
            self.entries[self.music_index].set_status_label(LabelImage.PAUSE)


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

    def __init__(self, parent, path, index):
        '''url类型为QUrl'''
        super().__init__(parent)
        self.setObjectName('ListEntry')
        
        '''标识这个条目在播放列表中的位置'''
        self.index = index

        music_file = MP3(path)
        self.music_title = music_file.tags['title'][0]
        self.music_artist = music_file.tags['artist'][0]
        self.music_duration = utils.convert_time(int(music_file.info.length))

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

'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''



'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''
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
'''-------------------------------------------------------------------------'''
'''-------------------------------------------------------------------------'''

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test = PlayList()
    test.show()
    sys.exit(app.exec_())
