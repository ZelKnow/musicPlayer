# !/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'HYA'
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from widget import ScrollArea
import sys
import addition

from api import netease
from SearchArea import *
# from SearchResultTable import SearchResultTable

class ConfigSearchArea(QObject):

    download = pyqtSignal(dict)
    def __init__(self, searchArea):
        super(ConfigSearchArea, self).__init__()

        # current show-table's index.
        self.currentIndex = 0
        # current widgets name。
        self.currentName = '网易云'

        # parent.
        self.searchArea = searchArea
        
        # get storage folder
        # self.downloadFolder = self.searchArea.parent.config.getDownloadFolder()

        self.transTime = addition.itv2time
        
        self.searchEngineers = {'网易云': netease, '虾米': netease, 'QQ': netease}
        # TODO 
        # to config singsFrameBase instead of configing them respective.
        self.searchResultTableIndexs = {'网易云':self.searchArea.neteaseSearchFrame.singsResultTable, 
            '虾米':self.searchArea.neteaseSearchFrame.singsResultTable , 
            'QQ':self.searchArea.neteaseSearchFrame.singsResultTable}

        self.musicList = []
        self.noContents = "很抱歉 未能找到关于<font style='text-align: center;' color='#23518F'>“{0}”</font>的{1}。"

        self.bindConnect()
        self.setContextMenu()

    def bindConnect(self):
        self.searchArea.contentsTab.tabBarClicked.connect(self.searchBy)

        self.searchArea.neteaseSearchFrame.singsResultTable.itemDoubleClicked.connect(self.itemDoubleClickedEvent)
        self.searchArea.neteaseSearchFrame.singsResultTable.itemDoubleClicked.connect(self.itemDoubleClickedEvent)
        self.searchArea.neteaseSearchFrame.singsResultTable.itemDoubleClicked.connect(self.itemDoubleClickedEvent)
        
        self.searchArea.neteaseSearchFrame.singsResultTable.contextMenuEvent = self.contextEvent
        self.searchArea.neteaseSearchFrame.singsResultTable.contextMenuEvent = self.contextEvent
        self.searchArea.neteaseSearchFrame.singsResultTable.contextMenuEvent = self.contextEvent

    def setContextMenu(self):
        self.actionDownloadSong = QAction('下载', self)
        self.actionDownloadSong.triggered.connect(self.downloadSong)

    # @toTask
    def downloadSong(self, x):
        # x is useless, but must be.
        # 
        musicInfo = self.musicList[self.currentIndex]
        url = musicInfo.get('url')
        if 'http:' not in url and 'https:' not in url:
                songId = musicInfo.get('music_id')
                future = aAsync(netease.singsUrl, [songId])
                url = yield from future
                url = url[0].get('url')
                musicInfo['url'] = url

        self.download.emit(musicInfo)

    def searchBy(self, index):
        currentWidgetName = self.searchArea.contentsTab.tabText(index)
        self.currentName = currentWidgetName
        self.search(currentWidgetName)

    # @toTask
    def search(self, name):
        """接受name信息，由这个引擎进行搜索。"""
        searchEngineer = self.searchEngineers[name]
        # data = yield from aAsync(searchEngineer.search, self.searchArea.text)
        data = searchEngineer.search(self.searchArea.text)
        if not data['songCount']:
            songsIds = []
            data['songs'] = []
        else: 
            songsIds = [i['id'] for i in data['songs']]

            if name == '网易云':
                songsDetail = {i:'http' for i in songsIds}
            elif name == '虾米' or name == 'QQ':
                songsDetail = {i:'http' for i in songsIds}
                # songsDetail = {i['id']:i['mp3Url'] for i in data['songs']}

            # 进行重新编辑方便索引。
            songs = data['songs']
            data['songs'] = [{'name':i['name'], 
            'artists': i['ar'], 
            'picUrl': i['al']['picUrl'],
            'mp3Url': songsDetail[i['id']],
            'duration': i['dt'],
            'music_id':i['id'],
            'lyric': i.get('lyric')} for i in songs]

        songsCount = data['songCount']

        # 总数是0即没有找到。
        if not songsCount:
            songs = []
        else:
            songs = data['songs'] 

        # print(songs)
        self.setSingsData(songs)

    def setSingsData(self, data):
        # 单曲搜索结果。
        # data是一个字典列表
        searchArea = self.searchArea.contentsTab.currentWidget()
        if not len(data):
            # self.contentsTab.addTab()
            searchArea.noSingsContentsLabel.setText(self.noContents.format(self.searchArea.text, '单曲'))
            searchArea.singsResultTable.hide()
            searchArea.noSingsContentsLabel.show()
        else:
            searchArea.singsResultTable.setRowCount(len(data))

            musicList = []
            for count, datas in enumerate(data):
                picUrl = datas['picUrl']
                url = datas['mp3Url']
                name = datas['name']
                authors = ','.join([t['name'] for t in datas['artists']])
                duration = self.transTime(datas['duration']/1000)
                musicId = datas['music_id']

                searchArea.singsResultTable.setItem(count, 0, QTableWidgetItem(name))
                searchArea.singsResultTable.setItem(count, 1, QTableWidgetItem(authors))
                searchArea.singsResultTable.setItem(count, 2, QTableWidgetItem(duration))
                musicList.append({'url': url, 
                    'name': name, 
                    'time':duration, 
                    'author':authors, 
                    'music_img': picUrl,
                    'music_id': musicId})

            searchArea.noSingsContentsLabel.hide()
            searchArea.singsResultTable.show()

            self.musicList = musicList

    def itemDoubleClickedEvent(self):
        currentRow = self.searchArea.contentsTab.currentWidget().singsResultTable.currentRow()
        data = self.musicList[currentRow]
        print(data)
        # self.searchArea.parent.playWidgets.setPlayerAndPlayList(data)
        # self.searchArea.parent.player.play_list.add_music(data)


    def contextEvent(self, event):
        currentWidget = self.searchResultTableIndexs.get(self.currentName)
        if not currentWidget:
            return

        item = currentWidget.itemAt(currentWidget.mapFromGlobal(QCursor.pos()))
        self.menu = QMenu(currentWidget)

        self.menu.addAction(self.actionDownloadSong)
        
        try:
            self.currentIndex = item.row() - 1
        # 在索引是最后一行时会获取不到。
        except:
            self.currentIndex = -1

        self.menu.exec_(QCursor.pos())


