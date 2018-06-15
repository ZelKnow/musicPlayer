from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from asy_base import aAsync, toTask
from widget import *
from api import netease
from SearchArea import SearchArea


class ConfigHeader(QObject):
    loginCookiesFolder = 'cookies/headers/loginInfor.cks'
    allCookiesFolder = [loginCookiesFolder]

    def __init__(self, header):
        super(ConfigHeader, self).__init__()
        self.header = header


        # self.loginThread = RequestThread(self, None, self.loginFinished)
        # self.loginThread.breakSignal.connect(self.emitWarning)

        # self.header.loginBox.connectLogin(self.login)
        
        self.loginInfor = {}
        self.result = None
        self.songsDetail = None
        # 用于确定登陆状态。
        self.code = 200
        # 用于确定是否最大化.   
        self.isMax = False

        self.bindConnect()
        
        # self.loadCookies()

    def bindConnect(self):
        # self.header.closeButton.clicked.connect(self.header.parent.close)
        self.header.showminButton.clicked.connect(self.header.parent.showMinimized)
        self.header.showmaxButton.clicked.connect(self.showMaxiOrRevert)
        # self.header.loginButton.clicked.connect(self.showLoginBox)
        # self.header.prevButton.clicked.connect(self.header.parent.config.prevTab)
        # self.header.nextButton.clicked.connect(self.header.parent.config.nextTab)
        
        self.header.searchLine.setButtonSlot(self.search)
        # self.header.searchLine.setButtonSlot(self.display)

    def display(self):
        print("hello")


    def showMaxiOrRevert(self):
        if self.isMax:
            self.header.parent.showNormal()
            self.isMax = False
        else:
            self.header.parent.showMaximized()
            self.isMax = True

    # @toTask
    def search(self):
        
        text = self.header.searchLine.text()
        #print("aaaaaaaaa", text)
        # future = aAsync(netease.search, text)
        # self.result = yield from future
        self.result = netease.search(text)
        if not self.result['songCount']:
            songsIds = []
            self.result['songs'] = []
        else: 
            songsIds = [i['id'] for i in self.result['songs']]

            self.songsDetail = {j:'http{0}'.format(i) for i, j in enumerate(songsIds)}
           
            # 进行重新编辑方便索引。
            songs = self.result['songs']
            self.result['songs'] = [{'name':i['name'], 
            'artists': i['ar'], 
            'picUrl': i['al']['picUrl'],
            'mp3Url': self.songsDetail[i['id']],
            'duration': i['dt'],
            'music_id':i['id']} for i in songs]

        songsCount = self.result['songCount']

        # 总数是0即没有找到。
        if not songsCount:
            songs = []
        else:
            songs = self.result['songs'] 

        # print(songs)

        self.header.parent.searchArea.setText(text)

        self.header.parent.searchArea.config.setSingsData(songs)

        # self.header.parent.config.setTabIndex(4)

    def showLoginBox(self):
        self.header.loginBox.open()

    def login(self):
        informations = self.header.loginBox.checkAndGetLoginInformation()
        
        if not informations:
            return 

        self.loginThread.setTarget(self.loadLoginInformations)
        self.loginThread.setArgs(informations)
        self.loginThread.start()

    def loadLoginInformations(self, informations:tuple):
        result = netease.login(*informations)
        # 网络不通或其他问题。
        if not result:
            self.loginThread.breakSignal.emit('请检查网络后重试~.')
            self.code = 500
            return

        code = result.get('code')
        if str(code) != '200':
            self.loginThread.breakSignal.emit(str(result.get('msg')))
            self.code = 500
            return 

        self.loginInfor = result
        self.code = 200

    def loginFinished(self):
        if str(self.code) == '200': 
            self.header.loginBox.accept()
            self.setUserData()

    # @toTask
    def setUserData(self):
        profile = self.loginInfor['profile']
        avatarUrl = profile['avatarUrl']
        self.header.userPix.setSrc(avatarUrl)
        # 加载该账户创建及喜欢的歌单。
        userId = profile['userId']
        future = aAsync(netease.user_playlist, userId)
        data = yield from future

        nickname = profile['nickname']
        self.header.loginButton.setText(nickname)

        self.header.loginButton.clicked.disconnect()
        self.header.loginButton.clicked.connect(self.exitLogin)
        
        self.header.parent.navigation.config.setPlaylists(data)
  
    def emitWarning(self, warningStr):
        self.header.loginBox.setWarningAndShowIt(warningStr)

    def exitLogin(self):
        self.loginInfor = {}
        self.header.loginButton.setText('未登录 ▼')
        self.header.loginButton.clicked.connect(self.showLoginBox)
        self.header.userPix.setSrc('resource/nouser.png')
        self.header.parent.navigation.config.clearPlaylists()

    # @checkFolder(allCookiesFolder)
    def saveCookies(self):
        with open(self.loginCookiesFolder, 'wb') as f:
            pickle.dump(self.loginInfor, f)

    # @checkFolder(allCookiesFolder)
    def loadCookies(self):
        with open(self.loginCookiesFolder, 'rb') as f:
            self.loginInfor = pickle.load(f)
        self.setUserData()
        self.header.loginButton.clicked.disconnect()
        self.header.loginButton.clicked.connect(self.exitLogin)
