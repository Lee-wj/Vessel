import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

from display import mainWin

class MyClass(QMainWindow, mainWin.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyClass, self).__init__(parent)
        self.setupUi(self)
        self.selectPic.clicked.connect(self.openimage)

    def openimage(self):
        imgName, imgType = QFileDialog.getOpenFileName(self, "打开图片", "", "*.jpg;;*.png;;All Files(*)")

        jpg = QtGui.QPixmap(imgName).scaled(self.showImage.width(), self.showImage.height())
        self.showImage.setPixmap(jpg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyClass()
    myWin.show()
    sys.exit(app.exec_())
