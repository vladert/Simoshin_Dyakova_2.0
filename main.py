import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QComboBox
from PyQt5.QtGui import QPixmap
from requests import get


class StaticYandexMap:
    def __init__(self, center_longitude, center_latitude, map_type='map'):
        self.params = {
            'll': f'{center_longitude},{center_latitude}',
            'l': map_type,
            'z': 10,
        }
    def get_url(self):
        base_url = 'https://static-maps.yandex.ru/1.x/'
        return f"{base_url}?{'&'.join([f'{key}={value}' for key, value in self.params.items()])}"


class MapWindow(QMainWindow):
    def __init__(self, apikey, coordinates, zoom, parent=None):
        super().__init__(parent)
        self.apikey = apikey
        self.coordinates = coordinates
        self.zoom = zoom
        self.image = None
        self.create_ui()
        self.load_map()

    def create_ui(self):
        self.setWindowTitle("Карта")
        self.setGeometry(300, 300, 550, 350)
        coordinates_label = QLabel("Введите координаты:")
        self.coordinates_input = QLineEdit()
        update_button = QPushButton("Обновить карту")
        update_button.clicked.connect(self.update_map)
        central_widget = QWidget()
        layout = QVBoxLayout()
        self.map_label = QLabel()
        self.map_type_combo = QComboBox()
        self.map_type_combo.addItems(['Схема', 'Спутник', 'Гибрид'])
        self.map_type_combo.currentIndexChanged.connect(self.change_map_type)
        layout.addWidget(self.map_type_combo)
        layout.addWidget(coordinates_label)
        layout.addWidget(self.coordinates_input)
        layout.addWidget(update_button)
        layout.addWidget(self.map_label)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_map(self):
        static_map = StaticYandexMap(*map(float, self.coordinates.split(',')))
        static_map.params['z'] = self.zoom
        url = static_map.get_url()
        response = get(url)
        if response.status_code == 200:
            with open("map_temp.jpg", "wb") as file:
                file.write(response.content)
            self.image = QPixmap("map_temp.jpg")
            self.map_label.setPixmap(self.image)
            self.map_label.setFocus()
        else:
            self.map_label.setText('Ошибка загрузки карты')

    def update_map(self):
        self.coordinates = self.coordinates_input.text()
        self.load_map()

    def keyPressEvent(self, event):
        step = 0.1
        if event.key() == 16777238:  # PgUp
            if self.zoom < 17:
                self.zoom += 1
                self.load_map()
        elif event.key() == 16777239:  # PgDown
            if self.zoom > 0:
                self.zoom -= 1
                self.load_map()
        elif event.key() == 16777235:  # Вверх
            lat, lon = map(float, self.coordinates.split(','))
            lat = min(85, lat + step)  # Ограничение максимальной широты
            self.coordinates = f"{lon},{lat}"
            self.load_map()
        elif event.key() == 16777237:  # Вниз
            lat, lon = map(float, self.coordinates.split(','))
            lat = lat + step
            self.coordinates = f"{lon},{lat}"
            self.load_map()

    def change_map_type(self):
        map_types = {'Схема': 'map', 'Спутник': 'sat', 'Гибрид': 'sat,skl'}
        self.map_type = map_types[self.map_type_combo.currentText()]
        self.load_map()


if __name__ == '__main__':
    apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
    coordinates = "37.620070,55.753630"
    zoom = 10
    app = QApplication(sys.argv)
    window = MapWindow(apikey, coordinates, zoom)
    window.show()
    sys.exit(app.exec_())