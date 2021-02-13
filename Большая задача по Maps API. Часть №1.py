import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QRadioButton, QLabel
from PyQt5.QtGui import QPixmap
from io import BytesIO
from PIL import Image
from PyQt5 import uic
import requests
from PyQt5.QtCore import Qt

COORDS = (37.6155600, 55.7522200)
SCALE = 1.0


class MapWidget(QMainWindow):
    def __init__(self, coords, scale):
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.coords = coords
        self.scale = scale
        self.initUI()

    def initUI(self):

        self.setWindowTitle('Карта')
        self.update_picture()

    def update_picture(self):
        map_params = {
            "ll": ",".join(map(lambda x: str(x), self.coords)),
            "l": "map",
            "spn": '1,1',
            "scale": self.scale

        }
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=map_params)
        if response:
            picture = Image.open(BytesIO(response.content))
            picture.save('map.png')
            pixmap = QPixmap('map.png')
            self.map_viewer.setPixmap(pixmap)
        else:
            pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            self.scale -= 1
            if self.scale < 1:
                self.scale = 1

            self.update_picture()
        if event.key() == Qt.Key_PageUp:
            self.scale += 1
            if self.scale > 4:
                self.scale = 4

            self.update_picture()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapWidget(COORDS, SCALE)
    ex.show()
    sys.exit(app.exec_())
