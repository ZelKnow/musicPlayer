from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from asy_base import toTask,aAsync
from widget import *
import sys
import os.path

class ConfigWindow(QObject):

    def __init__(self, window):
        super(ConfigWindow, self).__init__()
        self.window = window

        # 用于存储Tab的历史，方便前后切换。
        # 只存储5个，不考虑效率问题。
        self.history = []
        self.currentIndex = -1
        # 前后切换时也会触发currentChanged信号，
        # 前后切换时不允许增加新的历史也不允许删除旧的历史。
        self.isTab = False

        self.bindConnect()

    def addTab(self, widget, name=''):
        self.window.mainContents.addTab(widget, name)

    def allTab(self):
        return self.window.mainContents.count()

    def addTabHistory(self, index):
        length = len(self.history)
        if not self.isTab:
            if length < 5:
                self.history.append(index)
            else:
                self.history.pop(0)
                self.history.append(index)
            # 不是前后切换时将当前的索引定为末尾一个。
            self.currentIndex = length
        else:
            self.isTab = False

    def bindConnect(self):
        self.window.mainContents.currentChanged.connect(self.addTabHistory)

    def nextTab(self):
        # 后一个的切换。

        if self.currentIndex  == len(self.history)-1 or self.currentIndex == -1:
            return
        else:
            self.isTab = True
            self.currentIndex += 1
            self.window.mainContents.setCurrentIndex(self.history[self.currentIndex])

    def prevTab(self):
        # 前一个的切换。
        if self.currentIndex == 0 or self.currentIndex == -1:
            return
        else:
            self.isTab = True
            self.currentIndex -= 1
            self.window.mainContents.setCurrentIndex(self.history[self.currentIndex])

    def setTabIndex(self, index):
        self.window.mainContents.setCurrentIndex(index)

    def getDownloadFolder(self):
        return self.window.downloadFrame.config.myDownloadFolder

class ConfigNavigation(QObject):

    def __init__(self, navigation):
        super(ConfigNavigation, self).__init__()
        self.navigation = navigation

        self.detailFrame = self.navigation.parent.detailSings
        # mainWindow
        self.mainContents = self.navigation.parent

        self.nativeListFunction = self.tabNativeFrame
        self.singsFunction = self.none

        self.playlists = []

        self.result = None
        self.singsUrls = None
        self.coverImgUrl = None

        # self.api = netease

        self.bindConnect()

    def bindConnect(self):
        self.navigation.navigationList.itemPressed.connect(self.navigationListItemClickEvent)
        self.navigation.nativeList.itemPressed.connect(self.nativeListItemClickEvent)

    def navigationListItemClickEvent(self):
        """用户处理导航栏的点击事件。"""
        # 处理其他组件取消选中。
        # for i in self.playlists:
        #     if i.isChecked():
        #         i.setCheckable(False)
        #         i.setCheckable(True)
        #         break
        #
        # self.navigation.nativeList.setCurrentRow(-1)
        #
        # """处理事件。"""
        # self.navigationListFunction()

        self.navigation.parent.mainContents.addTab(self.navigation.parent.mainContent, '')
        
        print("huangyikai")

    def nativeListItemClickEvent(self, item):
        """本地功能的点击事件。"""
        for i in self.playlists:
            if i.isChecked():
                i.setCheckable(False)
                i.setCheckable(True)
                break

        self.navigation.navigationList.setCurrentRow(-1)

        """处理事件。"""
        self.nativeListFunction(item)
        print("huan.....")


    def singsButtonClickEvent(self):
        """歌单的点击事件。"""
        self.navigation.navigationList.setCurrentRow(-1)
        self.navigation.nativeList.setCurrentRow(-1)

        """处理事件。"""
        self.singsFunction()

    def setPlaylists(self, datas):
        # 布局原因，需要在最后加一个stretch才可以正常布局。
        # 所以这边先将最后一个stretch删去，将所有的内容添加完成后在加上。
        self.navigation.mainLayout.takeAt(self.navigation.mainLayout.count( ) -1)
        # for i in datas:
        #     button = PlaylistButton(self, i['id'], i['coverImgUrl'], QIcon('resource/notes2.png'), i['name'])
        #     button.hasClicked.connect(self.startRequest)
        #     button = QPushButton()
        #     self.playlists.append(button)
        #     self.navigation.mainLayout.addWidget(button)
        #
        # self.navigation.mainLayout.addStretch(1)

    def clearPlaylists(self):
        for i in self.playlists:
            i.deleteLater()

        self.playlists = []

        for i in range(11, self.navigation.mainLayout.count()):
            self.navigation.mainLayout.takeAt(i)

        self.navigation.mainLayout.addStretch(1)

    @toTask
    def startRequest(self, ids, coverImgUrl):
        self.coverImgUrl = coverImgUrl
        self.singsButtonClickEvent()

        future = aAsync(self.api.details_playlist, ids)
        self.result = yield from future
        # 由于旧API不在直接返回歌曲地址，需要获取歌曲号后再次进行请求。
        singsIds = [i['id'] for i in self.result['tracks']]
        # 此处还有些问题。
        # 由于是两次url请求，稍微变得有点慢。
        # future = aAsync(self.api.singsUrl, singsIds)
        # data = yield from future
        # self.singsUrls = {i['id']:i['url'] for i in data}
        # self.singsUrls = [self.singsUrls[i] for i in singsIds]
        self.singsUrls = ['http{0}'.format(i) for i, j in enumerate(singsIds)]

        self.detailFrame.config.setupDetailFrames(self.result, self.singsUrls, singsIds)
        self.detailFrame.picLabel.setSrc(self.coverImgUrl)
        self.detailFrame.picLabel.setStyleSheet('''QLabel {padding: 10px;}''')

        # 隐藏原来的区域，显示现在的区域。
        self.mainContents.mainContents.setCurrentIndex(1)

    def navigationListFunction(self):
        isVisible = self.navigation.parent.mainContent.tab.isVisible()
        if self.navigation.navigationList.currentRow() == 0:
            # 发现音乐。
            self.navigation.parent.mainContents.setCurrentIndex(0)

    def tabNativeFrame(self, item):
        if item .text() == ' 本地音乐':
            self.mainContents.mainContents.setCurrentIndex(2)
        elif item.text() == ' 我的下载':
            self.mainContents.mainContents.setCurrentIndex(3)

    def none(self):
        pass

class ConfigDetailSings(QObject):
    download = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(ConfigDetailSings, self).__init__()
        self.detailSings = parent
        self.musicList = []

        self.currentIndex = 0

        self.grandparent = self.detailSings.parent
        self.player = self.grandparent.playWidgets.player
        self.playList = self.grandparent.playWidgets
        self.currentMusic = self.grandparent.playWidgets.currentMusic
        self.transTime = transTime

        self.detailSings.singsTable.contextMenuEvent = self.singsFrameContextMenuEvent

        self.bindConnect()
        self.setContextMenu()

    def bindConnect(self):
        self.detailSings.playAllButton.clicked.connect(self.addAllMusicToPlayer)
        self.detailSings.singsTable.itemDoubleClicked.connect(self.itemDoubleClickedEvent)

    def setContextMenu(self):
        self.actionNextPlay = QAction('下一首播放', self)
        self.actionNextPlay.triggered.connect(self.addToNextPlay)

        self.actionDownloadSong = QAction('下载', self)
        self.actionDownloadSong.triggered.connect(self.downloadSong)

    def addToNextPlay(self):
        data = self.musicList[self.currentIndex]
        self.player.setAllMusics([data])
        self.playList.playList.addMusic(data)
        self.playList.playList.addPlayList(data['name'], data['author'], data['time'])

    @toTask
    def downloadSong(self, x):
        musicInfo = self.musicList[self.currentIndex]
        url = musicInfo.get('url')
        if 'http:' not in url and 'https:' not in url:
            songId = musicInfo.get('music_id')
            future = aAsync(netease.singsUrl, [songId])
            url = yield from future
            url = url[0].get('url')
            musicInfo['url'] = url

        self.download.emit(musicInfo)

    def addAllMusicToPlayer(self):
        self.playList.setPlayerAndPlaylists(self.musicList)

    def setupDetailFrames(self, datas, singsUrls, singsIds):
        result = datas
        self.musicList = []

        self.detailSings.singsTable.clearContents()

        self.detailSings.titleLabel.setText(result['name'])
        self.detailSings.authorName.setText(result['creator']['nickname'])
        description = result['description']
        # 有些没有简介会报错的。
        if not description:
            description = ''

        self.detailSings.descriptionText.setText(description)
        # 这边添加歌曲的信息到table。
        self.detailSings.singsTable.setRowCount(result['trackCount'])

        for i, j, t, x in zip(result['tracks'], range(result['trackCount']), singsUrls, singsIds):
            names = i['name']
            musicName = QTableWidgetItem(names)
            self.detailSings.singsTable.setItem(j, 0, musicName)

            author = i['artists'][0]['name']
            musicAuthor = QTableWidgetItem(author)
            self.detailSings.singsTable.setItem(j, 1, musicAuthor)

            times = self.transTime(i['duration'] / 1000)
            musicTime = QTableWidgetItem(times)
            self.detailSings.singsTable.setItem(j, 2, musicTime)

            music_img = i['album']['blurPicUrl']

            lyric = i.get('lyric')

            self.musicList.append({'url': t,
                                   'name': names,
                                   'time': times,
                                   'author': author,
                                   'music_img': music_img,
                                   'music_id': x,
                                   'lyric': lyric})

    # 事件。
    def itemDoubleClickedEvent(self):
        currentRow = self.detailSings.singsTable.currentRow()
        data = self.musicList[currentRow]

        self.playList.setPlayerAndPlayList(data)

    def singsFrameContextMenuEvent(self, event):
        item = self.detailSings.singsTable.itemAt(self.detailSings.singsTable.mapFromGlobal(QCursor.pos()))
        self.menu = QMenu(self.detailSings.singsTable)

        self.menu.addAction(self.actionNextPlay)
        self.menu.addAction(self.actionDownloadSong)

        try:
            self.currentIndex = item.row() - 1
        # 在索引是最后一行时会获取不到。
        except:
            self.currentIndex = -1

        self.menu.exec_(QCursor.pos())

