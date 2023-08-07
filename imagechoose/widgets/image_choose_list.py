import os
import math
from qtpy import QtWidgets
from qtpy import QtCore
from qtpy import QtGui
from imagechoose.utils import newAction


class PaginationListWidget(QtWidgets.QWidget):
    def __init__(self,parents):
        super().__init__(parents)
        
        self.currentPage = 1
        self.pageSize = 100

        # model
        # 原始数据
        self.dataList = set()

        # view
        self.display = QtWidgets.QListWidget()
        self.display.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        )

        # page control
        self.pagination = QtWidgets.QWidget()
        self.paginationLayout = QtWidgets.QHBoxLayout()

        self.pageNextBtn = QtWidgets.QPushButton(self.tr(">"), self)
        self.pageText = QtWidgets.QLabel(self.tr("1/1"), self)
        self.pagePrevBtn = QtWidgets.QPushButton(self.tr("<"), self)

        self.paginationLayout.addWidget(self.pagePrevBtn)
        self.paginationLayout.addWidget(self.pageText)
        self.paginationLayout.addWidget(self.pageNextBtn)
        self.paginationLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.pagination.setLayout(self.paginationLayout)

        # main layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.display)
        layout.addWidget(self.pagination)
        self.setLayout(layout)


        # connect
        self.pageNextBtn.clicked.connect(self.pageNext)
        self.pagePrevBtn.clicked.connect(self.pagePrev)

        

    @property
    def renderList(self):
        return list(self.dataList)[
            (self.currentPage - 1) * self.pageSize : self.currentPage * self.pageSize
        ]

    @property
    def totalPage(self):
        if len(self.dataList) <= self.pageSize:
            return 1
        return math.ceil(len(self.dataList) / self.pageSize) 

    def render(self,displayList):
        "渲染指定列表"
        self.display.clear()
        self.display.addItems(displayList)

    def replace(self, data):
        "用指定新数据替换原有数据"
        # print(data)
        if isinstance(data, list):
            self.dataList = set(data)
        else:
            self.dataList = data
        # print(self.dataList)
        self.currentPage = 1
        self.render(self.renderList)
        self.updatePaginationInfo(1)

    def updatePaginationInfo(self,page):
        "更新分页信息"
        self.currentPage = page
        self.pageText.setText(f"{self.currentPage}/{self.totalPage}")

    def pagePrev(self):
        "上一页"
        if self.currentPage > 1:
            self.currentPage -= 1
            self.render(self.renderList)
            self.updatePaginationInfo(self.currentPage)

    def pageNext(self):
        "下一页"
        if self.currentPage < self.totalPage:
            self.currentPage += 1
            self.render(self.renderList)
            self.updatePaginationInfo(self.currentPage)

    def addItems(self,items):
        if isinstance(items,str):
            items = [items]
        for i in items:
            self.dataList.add(i)
        self.render(self.renderList)
        self.updatePaginationInfo(self.currentPage)

    def removeItems(self,items):
        if isinstance(items,str):
            items = [items]
        if len(items) <= 0:
            return
        for i in items:
            try:
                self.dataList.remove(i)
            except KeyError:
                pass
        
        if len(self.renderList) <= 0:
            self.currentPage = self.currentPage - 1 if self.currentPage > 1 else 1
        self.render(self.renderList)
        self.updatePaginationInfo(self.currentPage)
    
class ImageChooseBrowser(QtWidgets.QDockWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.setObjectName("ImageChooseBrowser")
        self.files = set()

        self.imageSearch = QtWidgets.QLineEdit()
        self.imageFileList = PaginationListWidget(self)

        imageFileListLayout = QtWidgets.QVBoxLayout()
        imageFileListLayout.setContentsMargins(0, 0, 0, 0)
        imageFileListLayout.setSpacing(0)

        # combine imageSearch and imageFileList as a new widget
        imageFileListLayout.addWidget(self.imageSearch)
        imageFileListLayout.addWidget(self.imageFileList)
        imageFileListWidget = QtWidgets.QWidget()
        imageFileListWidget.setLayout(imageFileListLayout)

        # combine imageFileList and imageChooseList
        self.imageChooseList = PaginationListWidget(self)
        # make imageFileList can select multiple items
        self.imageChooseList.display.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        )
        imageChooseBrowserLayout = QtWidgets.QVBoxLayout()
        imageChooseBrowserLayout.addWidget(imageFileListWidget)
        imageChooseBrowserLayout.addWidget(self.imageChooseList)

        self.imageChooseBrowserWidget = QtWidgets.QWidget()
        self.imageChooseBrowserWidget.setLayout(imageChooseBrowserLayout)

        self.setWidget(self.imageChooseBrowserWidget)

        self.imageSearch.textChanged.connect(self.onSearchTextChanged)
        self.imageSearch.returnPressed.connect(self.onSearchReturnKeyPressed)
        self.imageFileList.display.itemDoubleClicked.connect(self.onImageFileListDoubleClicked)
        self.imageChooseList.display.itemDoubleClicked.connect(self.onImageChooseListDoubleClicked)

        # add right click menu
        self.imageFileList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.imageFileList.customContextMenuRequested.connect(self.onImageFileListRightClicked)

        self.imageChooseList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.imageChooseList.customContextMenuRequested.connect(self.onImageChooseListRightClicked)

    def findImage(self, root_dir):
        files = set()
        for dirpath, dirs, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith(".jpg") or filename.endswith(".png"):
                    files.add(os.path.join(dirpath, filename))
        return files


    def updateRootDir(self, root_dir):
        self.setWindowTitle(root_dir)
        self.files = self.findImage(root_dir)
        self.imageFileList.replace(self.files)

    def onSearchTextChanged(self):
        if self.imageSearch.text() == "":
            self.imageFileList.replace(self.files)

    def onSearchReturnKeyPressed(self):
        if (search_text := self.imageSearch.text()) != "":
            results = set([f for f in self.files if search_text in f])
            self.imageFileList.replace(results)
            

    def onImageFileListDoubleClicked(self):
        if target := self.imageFileList.display.currentItem():
            self.imageChooseList.addItems(target.text())

    def onImageChooseListDoubleClicked(self):
        if target := self.imageChooseList.display.currentItem():
            self.imageChooseList.removeItems(target.text())

    def onImageFileListRightClicked(self):
        # display menu
        menu = QtWidgets.QMenu(self)

        def addSelectedIntoChooseList():
            items = self.imageFileList.display.selectedItems()
            self.imageChooseList.addItems([item.text() for item in items])
        
        menu.addAction(
            newAction(
                self.imageFileList, self.tr("&加入选择"), addSelectedIntoChooseList
            )
        )
        menu.exec_(QtGui.QCursor.pos())

    def onImageChooseListRightClicked(self):
        menu = QtWidgets.QMenu(self)

        def deleteFromChooseList():
            items = self.imageChooseList.display.selectedItems()
            self.imageChooseList.removeItems([item.text() for item in items])

        menu.addAction(
            newAction(
                self.imageChooseList, self.tr("&移出"), deleteFromChooseList
            )
        )
        menu.exec_(QtGui.QCursor.pos())
