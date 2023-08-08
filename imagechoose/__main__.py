import sys
import os
from qtpy import QtWidgets
from qtpy.QtCore import Qt, QFile
from imagechoose.widgets.image_choose_list import ImageChooseBrowser
from imagechoose.widgets.image_preview_canvas import ImagePreviewCanvas
from imagechoose.utils import newAction


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("选图导出工具")

        # init widgets
        self.fileBrowser = ImageChooseBrowser(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.fileBrowser)

        self.imageCanvas = ImagePreviewCanvas(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.imageCanvas)

        # combine imageFileList and imageChooseList click event
        self.fileBrowser.imageFileList.display.itemSelectionChanged.connect(
            self.onImageFileListClicked
        )
        self.fileBrowser.imageChooseList.display.itemSelectionChanged.connect(
            self.onImageChooseListClicked
        )
        self.initHandleImageChooseBrowserKeyPressed()

        # menu bar
        menu = self.menuBar()
        menu.setNativeMenuBar(False)

        # add menu bar items
        menu.addAction(
            newAction(self, self.tr("打开文件夹"), self.onMenuOpenDirClicked, "Ctrl+O")
        )
        menu.addAction(
            newAction(self, self.tr("保存"), self.onMenuSaveClicked, "Ctrl+S")
        )

        self.show()
        self.resize(1400, 800)
        # self.resize(400 + (600 if self.imageCanvas.width() < 600 else self.imageCanvas.width()), 800 if self.imageCanvas.height() < 800 else self.imageCanvas.height())

    def onMenuSaveClicked(self):
        # print(self.fileBrowser.imageChooseList.dataList)
        # get save file dir from QFileDialog
        dir = QtWidgets.QFileDialog.getExistingDirectory(self, self.tr("目标目录"))
        if dir:
            pbar = QtWidgets.QProgressDialog(self.tr("保存中"), self.tr("取消"), 0, len(self.fileBrowser.imageChooseList.dataList), self)
            pbar.setWindowModality(Qt.WindowModal)
            for i,file_path in enumerate(self.fileBrowser.imageChooseList.dataList,start=1):
                if pbar.wasCanceled():
                    QtWidgets.QMessageBox.information(self, self.tr("保存进度"), self.tr("取消未完成的保存!"))
                    return 
                else:
                    QFile.copy(QFile(file_path), os.path.join(dir, os.path.basename(file_path)))
                    # QThread.sleep(1)
                    pbar.setValue(i)
            
            if pbar.close():
                QtWidgets.QMessageBox.information(self, self.tr("保存成功"), self.tr("导出完成"))


    def onMenuOpenDirClicked(self):
        dirs = QtWidgets.QFileDialog.getExistingDirectory(self, self.tr("目标目录"))
        if dirs:
            self.fileBrowser.updateRootDir(dirs)

    def onImageFileListClicked(self):
        self.fileBrowser.imageChooseList.display.clearSelection()
        currentItem = self.fileBrowser.imageFileList.display.currentItem()
        if currentItem is not None:
            self.imageCanvas.updateImage(currentItem.text())

    def onImageChooseListClicked(self):
        self.fileBrowser.imageFileList.display.clearSelection()
        currentItem = self.fileBrowser.imageChooseList.display.currentItem()
        if currentItem is not None:
            self.imageCanvas.updateImage(currentItem.text())

    def onImageChooseBrowserClicked(self):
        self.imageCanvas.updateImage(
            self.fileBrowser.imageFileList.display.currentItem().text()
        )

    def initHandleImageChooseBrowserKeyPressed(self):
        # handle image file list key pressed
        imageFileListOriginEvent = self.fileBrowser.imageFileList.display.keyPressEvent

        def handleImageFileListKeyPressed(event):
            key = event.key()
            if key == Qt.Key.Key_Return:
                currentItems = self.fileBrowser.imageFileList.display.selectedItems()
                self.fileBrowser.imageChooseList.addItems(
                    [item.text() for item in currentItems]
                )
            elif key == Qt.Key.Key_Left:
                self.fileBrowser.imageFileList.pagePrev()
            elif key == Qt.Key.Key_Right:
                self.fileBrowser.imageFileList.pageNext()
            else:
                imageFileListOriginEvent(event)

        self.fileBrowser.imageFileList.display.keyPressEvent = (
            handleImageFileListKeyPressed
        )

        # handle image choose list key pressed
        imageChooseListOriginEvent = (
            self.fileBrowser.imageChooseList.display.keyPressEvent
        )

        def handleImageChooseListKeyPressed(event):
            key = event.key()
            if key == Qt.Key.Key_Delete or key == Qt.Key.Key_Backspace:
              
                currentItems = self.fileBrowser.imageChooseList.display.selectedItems()
                if currentItems:
                    currentRow = self.fileBrowser.imageChooseList.display.currentRow()
                    self.fileBrowser.imageChooseList.removeItems(
                        [item.text() for item in currentItems]
                    )
                    self.fileBrowser.imageChooseList.display.setCurrentRow(
                        currentRow - 1
                    )
            elif key == Qt.Key.Key_Left:
                self.fileBrowser.imageChooseList.pagePrev()
            elif key == Qt.Key.Key_Right:
                self.fileBrowser.imageChooseList.pageNext()
            else:
                imageChooseListOriginEvent(event)

        self.fileBrowser.imageChooseList.display.keyPressEvent = (
            handleImageChooseListKeyPressed
        )



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
