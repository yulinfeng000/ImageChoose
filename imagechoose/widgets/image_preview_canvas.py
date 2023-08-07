from qtpy import QtWidgets
from qtpy import QtGui

class ImagePreviewCanvas(QtWidgets.QDockWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Image Preview")
        self.image_label = QtWidgets.QLabel()
        self.image_label.setPixmap(QtGui.QPixmap())


        canvasLayout = QtWidgets.QVBoxLayout()
        canvasLayout.setContentsMargins(0, 0, 0, 0)
        canvasLayout.setSpacing(0)
        canvasLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)

        canvasLayout.addWidget(self.image_label)

        self.canvasWidget = QtWidgets.QWidget()
        self.canvasWidget.setLayout(canvasLayout)


        self.setWidget(self.canvasWidget)

    def updateImage(self,image):
        self.image_label.setPixmap(QtGui.QPixmap(image))
    
        