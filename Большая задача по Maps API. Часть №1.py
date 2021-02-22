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
MAP_X = 16
MAP_Y = 12
MAP_WIDTH = 600
MAP_HEIGHT = 400
TYPE_OF_MAP = 'map'
DELTA_MAP = '1,1'


class MapWidget(QMainWindow):
    def __init__(self, coords, scale):
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.coords = coords
        self.scale = scale
        self.mark = coords[:]
        self.mark_is_exist = False
        self.type_of_map = TYPE_OF_MAP
        self.postal_code_exist = False
        self.address = []
        self.map_type.currentTextChanged.connect(self.change_map)
        self.search_button.clicked.connect(self.search_place)
        self.reset_button.clicked.connect(self.reset_mark)
        self.postal_button.clicked.connect(self.change_postal_code)
        self.initUI()

    def initUI(self):

        self.setWindowTitle('Карта')
        self.update_picture()

    def update_picture(self):
        map_params = {
            "ll": ",".join(map(lambda x: str(x), self.coords)),
            "l": self.type_of_map,
            "spn": DELTA_MAP,
            "scale": self.scale,
            "size": f'{MAP_WIDTH},{MAP_HEIGHT}'
        }
        if self.mark_is_exist:
            map_params["pt"] = ",".join(map(lambda x: str(x), self.mark)) + ',pm2rdl'

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
            self.coords[0] += 0.25 / float(self.scale)
            if self.coords[0] > 180:
                self.coords[0] = 180
            self.update_picture()

        if event.key() == Qt.Key_Left:
            self.coords[0] -= 0.25 / float(self.scale)
            if self.coords[0] < 0:
                self.coords[0] = 0
            self.update_picture()

        if event.key() == Qt.Key_Up:
            self.coords[1] += 0.25 / float(self.scale)
            if self.coords[1] > 90:
                self.coords[1] = 90
            self.update_picture()

        if event.key() == Qt.Key_Down:
            self.coords[1] -= 0.25 / float(self.scale)
            if self.coords[1] < 0:
                self.coords[1] = 0
            self.update_picture()

    def mousePressEvent(self, event):
        if event.x() > MAP_X and event.x() < MAP_X + MAP_WIDTH and \
                event.y() > MAP_Y and event.y() < MAP_Y + MAP_HEIGHT:

            if event.button() == Qt.LeftButton:

                new_x = (event.x() - MAP_X - MAP_WIDTH // 2) / MAP_WIDTH
                new_y = (event.y() - MAP_Y - MAP_HEIGHT // 2) / MAP_HEIGHT
                print(self.coords)
                print('x')
                print(new_x)
                print('y')
                print(new_y)
                print('___')
                self.mark_is_exist = True
                self.mark = [self.coords[0], self.coords[1]]
                self.address = self.get_address()
                if len(self.address) == 2 and self.postal_code_exist:
                    self.address_line.setText(f'{self.address[0]}, {self.address[1]}')
                else:
                    self.address_line.setText(self.address[0])
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

    def get_coords(self, name):
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x"
        geo_params = {'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                      'geocode': name,
                      'format': 'json'}

        response = requests.get(geocoder_request, params=geo_params)
        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"]
            if toponym:
                toponym = toponym[0]["GeoObject"]
                coordinates = toponym["Point"]["pos"]
                return coordinates
            else:
                return 0

    def search_place(self):
        name_of_place = self.search_line.text()
        self.search_line.setEnabled(False)
        self.search_line.setEnabled(True)
        coords = self.get_coords(name_of_place)
        if not coords:
            return 0
        coords = coords.split(' ')
        self.coords = list(map(lambda x: float(x), coords))
        self.mark_is_exist = True
        self.mark = coords[:]
        self.address = self.get_address()
        if len(self.address) == 2 and self.postal_code_exist:
            self.address_line.setText(f'{self.address[0]}, {self.address[1]}')
        else:
            self.address_line.setText(self.address[0])
        self.update_picture()

    def reset_mark(self):
        self.mark_is_exist = False
        self.address_line.setText('')
        self.update_picture()

    def get_address(self):
        params = {
            'apikey': "40d1649f-0493-4b70-98ba-98533de7710b",
            'geocode': ",".join(map(lambda x: str(x), self.mark)),
            'format': 'json'
        }
        zapros = requests.get('https://geocode-maps.yandex.ru/1.x/', params=params)
        json_response = zapros.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        text = toponym['metaDataProperty']['GeocoderMetaData']['text']
        address = toponym['metaDataProperty']['GeocoderMetaData']['Address']
        if 'postal_code' in address:
            postal_code = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
            return [text, postal_code]
        else:
            return [text]

    def change_postal_code(self):
        if self.postal_code_exist:
            self.postal_code_exist = False
            self.address_line.setText(self.address[0])
        else:
            self.postal_code_exist = True
            if len(self.address) == 2:
                self.address_line.setText(f'{self.address[0]}, {self.address[1]}')
            else:
                self.address_line.setText(self.address[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapWidget(COORDS, SCALE)
    ex.show()
    sys.exit(app.exec_())
