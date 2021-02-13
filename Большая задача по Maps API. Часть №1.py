import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QRadioButton, QLabel
from PyQt5.QtGui import QPixmap
from io import BytesIO
from PIL import Image
from PyQt5 import uic
import requests
from PyQt5.QtCore import Qt

COORDS = [37.6155600, 55.7522200]
SCALE = 1.0


class MapWidget(QMainWindow):
    def __init__(self, coords, scale):
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.coords = coords
        self.scale = scale
        self.type_of_map = 'map'
        self.map_type.currentTextChanged.connect(self.change_map)
        self.initUI()

    def initUI(self):

        self.setWindowTitle('Карта')
        self.update_picture()

    def update_picture(self):
        map_params = {
            "ll": ",".join(map(lambda x: str(x), self.coords)),
            "l": self.type_of_map,
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
            self.scale -= 0.5
            if self.scale < 1:
                self.scale = 1

            self.update_picture()
        if event.key() == Qt.Key_PageUp:
            self.scale += 0.5
            if self.scale > 4:
                self.scale = 4

            self.update_picture()
        if event.key() == Qt.Key_Right:
            self.coords[0] += 0.25 / self.scale
            if self.coords[0] > 180:
                self.coords[0] = 180
            self.update_picture()

        if event.key() == Qt.Key_Left:
            self.coords[0] -= 0.25 / self.scale
            if self.coords[0] < 0:
                self.coords[0] = 0
            self.update_picture()

        if event.key() == Qt.Key_Up:
            self.coords[1] += 0.25 / self.scale
            if self.coords[1] > 90:
                self.coords[1] = 90
            self.update_picture()

        if event.key() == Qt.Key_Down:
            self.coords[1] -= 0.25 / self.scale
            if self.coords[1] < 0:
                self.coords[1] = 0
            self.update_picture()

    def change_map(self):
        text = self.map_type.currentText()
        if text == 'Схема':
            self.type_of_map = 'map'
        elif text == 'Спутник':
            self.type_of_map = 'sat'
        elif text == 'Гибрид':
            self.type_of_map = 'sat,skl'
        self.update_picture()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapWidget(COORDS, SCALE)
    ex.show()
    sys.exit(app.exec_())
