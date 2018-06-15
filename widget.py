from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


import hashlib
import os.path
import logging
import sys

logger = logging.getLogger(__name__)


# 左侧的导航栏，包括发现音乐/歌单/本地音乐。
class Navigation(QScrollArea):
    def __init__(self, parent=None):
        """各类导航信息。"""
        super(Navigation, self).__init__(parent)
        self.parent = parent
        self.frame = QFrame()
        self.setMaximumWidth(200)
        self.setWidget(self.frame)
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(200)

        self.setUI()

    def setUI(self):
        #读取样式
        with open('QSS/navigation.qss', 'r') as f:
            style = f.read()
            self.setStyleSheet(style)
            self.frame.setStyleSheet(style)

        self.setLabels() # 包括显示信息： 探索音乐 我的音乐 我的收藏。
        self.setListViews()  # 包括详细的内容：音乐库，朋友，MV等。
        self.setLayouts() #设置布局

        # 定义3个事件函数
        self.navigationListFunction = self.none
        self.nativeListFunction = self.none
        self.singsFunction = self.none

    # 布局。
    def setLabels(self):
        """设置每个框题标签。"""
        self.recommendLabel = QLabel(" 探索音乐")
        self.recommendLabel.setObjectName("recommendLabel")
        self.recommendLabel.setMaximumHeight(30)

        self.myMusic = QLabel(" 我的音乐")
        self.myMusic.setObjectName("myMusic")
        self.myMusic.setMaximumHeight(30)

        self.singsListLabel = QLabel(" 我的收藏")
        self.singsListLabel.setObjectName("singsListLabel")
        self.singsListLabel.setMaximumHeight(30)

    def setListViews(self):
        """定义每个框题中的的ListView"""
        self.navigationList = QListWidget()
        self.navigationList.setMaximumHeight(110)
        self.navigationList.setObjectName("navigationList")
        self.navigationList.addItem(QListWidgetItem(QIcon('resource/music1.png'), " 音乐库"))
        self.navigationList.addItem(QListWidgetItem(QIcon('resource/friend.png'), " 朋友"))
        self.navigationList.addItem(QListWidgetItem(QIcon('resource/movie.png'), " MV"))
        self.navigationList.setCurrentRow(0)

        self.nativeList = QListWidget()
        self.nativeList.setObjectName("nativeList")
        self.nativeList.setMaximumHeight(90)
        self.nativeList.addItem(QListWidgetItem(QIcon('resource/notes.png'), " 本地音乐"))
        self.nativeList.addItem(QListWidgetItem(QIcon('resource/download_icon.png'), " 我的下载"))

        self.collectionList = QListWidget();
        self.collectionList.setObjectName("collectionList")
        self.collectionList.setMaximumHeight(30)
        self.collectionList.addItem(QListWidgetItem(QIcon('resource/collection.png'), " 收藏歌单"))

    def setLayouts(self):
        """设置布局。"""
        self.mainLayout = VBoxLayout(self.frame)
        self.mainLayout.addSpacing(10)
        self.mainLayout.addWidget(self.recommendLabel)
        self.mainLayout.addSpacing(3)
        self.mainLayout.addWidget(self.navigationList)
        self.mainLayout.addSpacing(1)

        self.mainLayout.addWidget(self.myMusic)
        self.mainLayout.addSpacing(2)
        self.mainLayout.addWidget(self.nativeList)
        self.mainLayout.addSpacing(1)

        self.mainLayout.addWidget(self.singsListLabel)
        self.mainLayout.addSpacing(2)
        self.mainLayout.addWidget(self.collectionList)
        self.mainLayout.addSpacing(1)

        self.mainLayout.addStretch(1)

        self.setContentsMargins(0, 0, 0, 0)

    # 功能。
    def none(self):
        # 没有用的空函数。
        pass

# 用于继承，多次调用。
class ScrollArea(QScrollArea):
    """包括一个ScrollArea做主体承载一个QFrame的基础类。"""
    scrollDown = pyqtSignal()

    def __init__(self, parent=None):
        super(ScrollArea, self).__init__()
        self.parent = parent
        self.frame = QFrame()
        self.frame.setObjectName('frame')
        # 用于发出scroll滑到最底部的信号。
        self.verticalScrollBar().valueChanged.connect(self.sliderPostionEvent)

        self.setWidgetResizable(True)

        self.setWidget(self.frame)

    def noInternet(self):
        # 设置没有网络的提示。
        self.noInternetLayout = QGridLayout()
        self.setLayout(self.mainLayout)

        self.Tip = QLabel("您已进入没有网络的异次元，打破次元壁 →", self)
        self.TipButton = QPushButton("打破次元壁", self)
        self.TipButton.setObjectName("TipButton")

        self.TipLayout = QHBoxLayout()
        self.TipLayout.addWidget(self.Tip)
        self.TipLayout.addWidget(self.TipButton)

        # self.indexAllSings.setLayout(self.TipLayout)

        self.noInternetLayout.addLayout(self.TipLayout, 0, 0, Qt.AlignCenter|Qt.AlignTop)

        self.frame.setLayout(self.noInternetLayout)

    def sliderPostionEvent(self):
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            self.scrollDown.emit()

    def maximumValue(self):
        return self.verticalScrollBar().maximum()

class VBoxLayout(QVBoxLayout):

    def __init__(self, *args):
        super(VBoxLayout, self).__init__(*args)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

class HBoxLayout(QHBoxLayout):

    def __init__(self, *args):
        super(HBoxLayout, self).__init__(*args)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

# 标题栏类
class Header(QFrame):

    def __init__(self, parent=None):

        super(Header, self).__init__()
        self.setObjectName('Header')
        self.parent = parent

        with open('QSS/header.qss', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

        self.setUI()


    def setUI(self):
        self.setButtons() # 按钮设置。
        self.setLabels()  # 标签设置。
        self.setLineEdits() # 输入框设置。
        self.setLines()  # 细线装饰设置。
        self.setLayouts() # 布局设置。

    # 布局。
    def setButtons(self):
        """创建所有的按钮。"""

        self.closeButton = QPushButton('×', self)
        self.closeButton.setObjectName("closeButton")
        self.closeButton.setMinimumSize(21, 17)
        self.closeButton.clicked.connect(QCoreApplication.instance().quit)

        self.showminButton = QPushButton('_', self)
        self.showminButton.setObjectName("minButton")
        self.showminButton.setMinimumSize(21, 17)

        self.showmaxButton = QPushButton('□')
        self.showmaxButton.setObjectName("maxButton")
        self.showmaxButton.setMaximumSize(21, 17)

        self.loginButton = QPushButton("VIP用户", self)
        self.loginButton.setObjectName("loginButton")

        self.prevButton = QPushButton("<")
        self.prevButton.setObjectName("prevButton")
        self.prevButton.setMaximumSize(28, 22)
        self.prevButton.setMinimumSize(28, 22)

        self.nextButton = QPushButton(">")
        self.nextButton.setObjectName("nextButton")
        self.nextButton.setMaximumSize(28, 22)
        self.nextButton.setMinimumSize(28, 22)

    def setLabels(self):
        """创建标签。"""
        self.descriptionLabel = QLabel(self)
        self.descriptionLabel.setText("<b>KASW Music</b>")

    def setLineEdits(self):
        """创建搜素框。"""
        self.searchLine = SearchLineEdit(self)
        self.searchLine.setPlaceholderText("寻找音乐资源")
        # self.searchLine.setButtonSlot(self.display)

    def display(self):
        print("hello")

    def setLines(self):
        """设置装饰用小细线。"""
        self.line1 = QFrame(self)
        self.line1.setObjectName("line1")
        self.line1.setFrameShape(QFrame.VLine)
        self.line1.setFrameShadow(QFrame.Plain)
        self.line1.setMaximumSize(2, 25)

    def setLayouts(self):
        """设置布局。"""
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.addWidget(self.descriptionLabel)
        self.mainLayout.addSpacing(40)
        self.mainLayout.addWidget(self.prevButton)
        self.mainLayout.addWidget(self.nextButton)
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(self.searchLine)
        self.mainLayout.addStretch(1)
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(self.loginButton)
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(self.line1)
        self.mainLayout.addSpacing(30)
        self.mainLayout.addWidget(self.showminButton)
        self.mainLayout.addWidget(self.showmaxButton)
        self.mainLayout.addSpacing(3)
        self.mainLayout.addWidget(self.closeButton)
        self.setLayout(self.mainLayout)

    #事件。
    """重写鼠标事件，实现窗口拖动。"""
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.m_drag = True
            self.parent.m_DragPosition = event.globalPos()-self.parent.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        try:
            if event.buttons() and Qt.LeftButton:
                self.parent.move(event.globalPos()-self.parent.m_DragPosition)
                event.accept()
        except AttributeError:
            pass

    def mouseReleaseEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.m_drag = False

class SearchLineEdit(QLineEdit):
    """创建搜索框"""

    def __init__(self, parent=None):
        super(SearchLineEdit, self).__init__()
        self.setObjectName("SearchLine")
        self.parent = parent
        self.setMinimumSize(218, 20)
        with open('QSS/searchLine.qss', 'r') as f:
            self.setStyleSheet(f.read())

        self.button = QPushButton(self)
        self.button.setMaximumSize(13, 13)
        self.button.setCursor(QCursor(Qt.PointingHandCursor))

        self.setTextMargins(3, 0, 19, 0)

        self.spaceItem = QSpacerItem(150, 10, QSizePolicy.Expanding)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addSpacerItem(self.spaceItem)
        # self.mainLayout.addStretch(1)
        self.mainLayout.addWidget(self.button)
        self.mainLayout.addSpacing(10)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)

    def setButtonSlot(self, funcName):
        self.button.clicked.connect(funcName)

# 主要内容区，包括最新的歌单。
class MainContent(ScrollArea):
    # 定义一个滑到了最低部的信号。
    # 方便子控件得知已经滑到了最底部，要做些加载的动作。

    def __init__(self, parent=None):
        """主内容区，包括推荐歌单等。"""
        super(MainContent, self).__init__()
        self.parent = parent
        self.setObjectName("MainContent")

        # 连接导航栏的按钮。
        # self.parent.navigation.navigationListFunction = self.navigationListFunction
        with open("QSS/mainContent.qss", 'r', encoding='utf-8') as f:
            self.style = f.read()
            self.setStyleSheet(self.style)

        self.tab = QTabWidget()
        self.tab.setObjectName("contentsTab")

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.tab)

        self.frame.setLayout(self.mainLayout)

    def addTab(self, widget, name=''):
        self.tab.addTab(widget, name)

class TableWidget(QTableWidget):
    #第一个参数为标题数量，第二个参数为标题名称列表
    def __init__(self, count, headerLables):
        super(TableWidget, self).__init__()
        self.setColumnCount(count)
        self.setHorizontalHeaderLabels(headerLables)

        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def setColumnWidths(self, widths:dict):
        for key in widths:
            self.setColumnWidth(key, widths[key])


# 歌单详情页。
class DetailSings(ScrollArea):

    def __init__(self, parent=None):
        super(DetailSings, self).__init__(self)

        # self.hide()
        self.parent = parent
        self.setObjectName('detailSings')
        with open('QSS/detailSings.qss', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

        self.setLabels()
        self.setButtons()
        self.setTabs()
        self.setLayouts()

    # 布局。
    def setLabels(self):
        self.picLabel = PicLabel(width=200, height=200)
        self.picLabel.setObjectName('picLabel')

        self.titleLabel = QLabel(self.frame)
        self.titleLabel.setObjectName('titleLabel')
        self.titleLabel.setWordWrap(True)
        self.titleLabel.setMaximumHeight(40)

        self.authorPic = QLabel(self.frame)
        self.authorName = QLabel(self.frame)
        self.authorName.setObjectName('authorName')
        self.authorName.setMaximumHeight(28)

        self.descriptionText = QTextEdit(self.frame)
        self.descriptionText.setReadOnly(True)
        self.descriptionText.setObjectName('descriptionText')
        self.descriptionText.setMaximumWidth(450)
        self.descriptionText.setMaximumHeight(100)
        self.descriptionText.setMinimumHeight(100)

    def setButtons(self):
        self.showButton = QPushButton("歌单")
        self.showButton.setObjectName('showButton')
        self.showButton.setMaximumSize(36, 20)

        self.descriptionButton = QPushButton(" 简介 ：")
        self.descriptionButton.setObjectName('descriptionButton')
        self.descriptionButton.setMaximumSize(36, 36)

        self.playAllButton = QPushButton("全部播放")
        self.playAllButton.setIcon(QIcon('resource/playAll.png'))
        self.playAllButton.setObjectName('playAllButton')
        self.playAllButton.setMaximumSize(90, 24)

    def setTabs(self):
        self.contentsTab = QTabWidget(self.frame)

        self.singsTable = TableWidget(3, ['音乐标题', '歌手', '时长'])
        self.singsTable.setObjectName('singsTable')
        self.singsTable.setMinimumWidth(self.width())
        self.singsTable.setColumnWidths({i: j for i, j in zip(range(3),
                                                              [self.width() / 3 * 1.25, self.width() / 3 * 1.25,
                                                               self.width() / 3 * 0.5])})

        self.contentsTab.addTab(self.singsTable, "歌曲列表")

    def setLayouts(self):
        self.mainLayout = VBoxLayout()

        self.topLayout = VBoxLayout()

        self.descriptionLayout = VBoxLayout()
        self.titleLayout = HBoxLayout()
        self.titleLayout.addWidget(self.showButton)
        self.titleLayout.addSpacing(5)
        self.titleLayout.addWidget(self.titleLabel)

        self.authorLayout = HBoxLayout()
        self.authorLayout.addWidget(self.authorPic)
        self.authorLayout.addWidget(self.authorName)
        self.authorLayout.addStretch(1)

        self.descriptLayout = HBoxLayout()
        self.descriptLayout.addWidget(self.descriptionButton)
        self.descriptLayout.addWidget(self.descriptionText)

        self.descriptionLayout.addSpacing(5)
        self.descriptionLayout.addLayout(self.titleLayout)
        self.descriptionLayout.addLayout(self.authorLayout)
        self.descriptionLayout.addSpacing(5)
        self.descriptionLayout.addWidget(self.playAllButton)
        self.descriptionLayout.addSpacing(10)
        self.descriptionLayout.addLayout(self.descriptLayout)

        self.topLayout.addWidget(self.picLabel)
        self.topLayout.addSpacing(18)
        self.topLayout.addLayout(self.descriptionLayout)

        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addWidget(self.contentsTab)

        self.frame.setLayout(self.mainLayout)


def checkOneFolder(folderName:str):
    if not os.path.isdir(folderName):
        os.mkdir(folderName)

    def _check(func):
        def _exec(*args):
            try:
                func(*args)
            except:
                logger.warning('读取或保存cookies出错 文件夹名: {0}'.format(folderName), exc_info=True)
                print('读取或保存cookies出错', folderName)

        return _exec
    return _check



# 缓存目录。
cacheFolder = 'cache'

## 对<img src=1.jpg>的初步探索。
# 暂只接受http(s)和本地目录。
class PicLabel(QLabel):

    def __init__(self, src=None, width=200, height=200, pixMask=None):
        super(PicLabel, self).__init__()
        global picsThreadPool

        self.src = None

        self.width = width
        self.height = height

        self.pixMask = None
        if pixMask:
            self.pixMask = pixMask
        if src:
            self.setSrc(src)

        if self.width:
            self.setMaximumSize(self.width, self.height)
            self.setMinimumSize(self.width, self.height)

    @checkOneFolder(cacheFolder)
    def setSrc(self, src):
        src = str(src)
        if 'http' in src or 'https' in src:
            cacheList = os.listdir(cacheFolder)

            # names = str(src[src.rfind('/')+1:])
            names = makeMd5(src)
            localSrc = cacheFolder+'/'+names
            if names in cacheList:
                self.setSrc(localSrc)
                self.src = localSrc
                return

            task = GetPicture(self, src)
            picsThreadPool.start(task)
        else:
            self.src = src
            pix = QPixmap(src)
            pix.load(src)
            pix = pix.scaled(self.width, self.height)
            # mask需要与pix是相同大小。
            if self.pixMask:
                mask = QPixmap(self.pixMask)
                mask = mask.scaled(self.width, self.height)
                pix.setMask(mask.createHeuristicMask())

            self.setPixmap(pix)

    def getSrc(self):
        """返回该图片的地址。"""
        return self.src



if __name__ == "__main__":
    app = QApplication(sys.argv)
    test = DetailSings()
    test.show()
    sys.exit(app.exec_())
