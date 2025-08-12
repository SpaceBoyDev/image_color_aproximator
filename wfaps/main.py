import ctypes
import sys
from tkinter.filedialog import askopenfilename

from PIL import ImageGrab
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QFrame,
                             QPushButton, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QSizePolicy)
from colormath.color_conversions import convert_color
from colormath.color_diff import *
from colormath.color_objects import LabColor, sRGBColor, XYZColor
from numpy import *
from pynput import keyboard
from pynput import mouse

wplace_colors = [
    [0, 0, 0],
    [60, 60, 60],
    [120, 120, 120],
    [210, 210, 210],
    [255, 255, 255],
    [96, 0, 24],
    [237, 28, 36],
    [255, 127, 39],
    [246, 170, 9],
    [249, 221, 59],
    [255, 250, 188],
    [14, 185, 104],
    [19, 230, 123],
    [135, 255, 94],
    [12, 129, 110],
    [16, 174, 166],
    [19, 225, 190],
    [40, 80, 158],
    [64, 147, 228],
    [96, 247, 242],
    [107, 80, 246],
    [153, 177, 251],
    [120, 12, 153],
    [170, 56, 185],
    [224, 159, 249],
    [203, 0, 122],
    [236, 31, 128],
    [243, 141, 169],
    [104, 70, 52],
    [149, 104, 42],
    [248, 178, 119],
]

user32 = ctypes.windll.user32
LoadCursor = user32.LoadCursorW
SetCursor = user32.SetCursor

IDC_ARROW = 32512
IDC_WAIT = 32514


class WPlaceImageGen(QWidget):
    def __init__(self):
        super().__init__()

        self.select_image_button = QPushButton("Select Image", self)
        self.copy_image_button = QPushButton("Copy Image", self)
        self.save_image_button = QPushButton("Save Image", self)
        self.import_wplace_button = QPushButton("Import wplace basic colors", self)

        self.colors_to_save = []

        self.v_color_box = QVBoxLayout()
        self.color_grid = QGridLayout()
        self.max_cols = 5
        self.color_picked = [0, 0, 0]

        self.mouselistnr = mouse.Listener(on_click=self.onClick)

        self.colors = []
        self.color_buttons = []
        self.add_color_button = QPushButton("+", self)

        self.og_img_name = None
        self.og_image = QImage()
        self.new_image = QImage()
        self.og_image_label = QLabel(self)
        self.new_image_label = QLabel(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Stopwatch")

        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        general_layout = QVBoxLayout()
        horizontal_layout = QHBoxLayout()
        # general_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(general_layout)
        general_layout.addLayout(horizontal_layout)
        horizontal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        v_image_box = QVBoxLayout()
        horizontal_layout.addLayout(v_image_box)
        # v_image_box.setAlignment(Qt.AlignmentFlag.AlignLeft)
        v_image_box.addWidget(self.og_image_label)
        v_image_box.addWidget(self.new_image_label)

        self.v_color_box.addLayout(self.color_grid)
        self.color_grid.addWidget(self.add_color_button)
        # self.v_color_box.setSpacing(30)
        self.v_color_box.setAlignment(Qt.AlignmentFlag.AlignTrailing)
        horizontal_layout.addLayout(self.v_color_box)

        self.og_image_label.setScaledContents(True)
        self.og_image_label.setMaximumSize(350, 350)
        self.og_image_label.setFrameShape(QFrame.Panel)
        self.og_image_label.setFrameShadow(QFrame.Sunken)
        self.og_image_label.setLineWidth(3)

        # self.new_image_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.new_image_label.setScaledContents(True)
        self.new_image_label.setMaximumSize(350, 350)
        self.new_image_label.setFrameShape(QFrame.Panel)
        self.new_image_label.setFrameShadow(QFrame.Sunken)
        self.new_image_label.setLineWidth(3)

        h_button_box = QHBoxLayout()
        general_layout.addLayout(h_button_box)

        h_button_box.setAlignment(Qt.AlignmentFlag.AlignBottom)
        h_button_box.addWidget(self.select_image_button)
        h_button_box.addWidget(self.copy_image_button)
        h_button_box.addWidget(self.save_image_button)
        h_button_box.addWidget(self.import_wplace_button)

        self.setStyleSheet("""
            QPushButton, QLabel {
                padding: 20px;
                font-family: "calibri";
            }
            QPushButton {
                font-size: 50px;
            }
            QLabel {
                font-size: 120px;
            }
        """)

        self.select_image_button.clicked.connect(self.select_image)
        self.copy_image_button.clicked.connect(self.copy_image)
        self.save_image_button.clicked.connect(self.save_image)
        self.import_wplace_button.clicked.connect(lambda _, b=wplace_colors: self.import_colors(b))

        self.add_color_button.clicked.connect(self.add_color)
        self.add_color_button.setStyleSheet("""
            font-size: 30px""")

    def import_colors(self, colors):
        for i, color in enumerate(colors):
            self.add_color()
            self.change_selected_color_special(i, color)

    def select_image(self):
        img = askopenfilename()
        self.og_img_name = img
        self.og_image.load(img)
        self.og_image_label.setPixmap(QPixmap(img))

    def copy_image(self):
        if len(self.colors) < 1 or self.og_image.isNull():
            return
        pixels = []
        self.new_image = QImage(self.og_image.width(),
                                self.og_image.height(),
                                QImage.Format.Format_ARGB32)

        for y in range(self.og_image.height()):
            for x in range(self.og_image.width()):
                color = QColor(self.og_image.pixelColor(x, y))
                if color.alpha() == 0:
                    self.new_image.setPixelColor(x, y, color)
                    continue
                closest_color, delta = self.find_closest_color(
                    self.rgb_to_lab((color.red(), color.green(), color.blue())), self.colors)

                srgb = self.lab_to_rgb(closest_color)
                r = int(round(srgb.rgb_r * 255))
                g = int(round(srgb.rgb_g * 255))
                b = int(round(srgb.rgb_b * 255))

                final_color = QColor(r, g, b)
                self.new_image.setPixelColor(x, y, final_color)

        self.og_image_label.setPixmap(QPixmap.fromImage(self.og_image))
        self.new_image_label.setPixmap(QPixmap.fromImage(self.new_image))

    def lab_to_rgb(self, lab_color):
        temp_color = convert_color(lab_color, XYZColor)
        return convert_color(temp_color, sRGBColor)

    def rgb_to_lab(self, rgb):
        rgb_scaled = sRGBColor(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
        lab = convert_color(rgb_scaled, LabColor)
        return lab

    def find_closest_color(self, lab_target, lista_lab):
        delta_e_min = float('inf')
        closest_color = None
        for color_lab in lista_lab:
            delta_e = delta_e_cie2000(lab_target, color_lab)
            delta_e = abs(delta_e)

            if delta_e < delta_e_min:
                delta_e_min = delta_e
                closest_color = color_lab
        return closest_color, delta_e_min

    def save_image(self):
        if not self.new_image.isNull():
            self.new_image.save(f"{self.og_img_name}_approximated.png")

    def add_color(self):

        self.color_buttons.append(QPushButton(""))
        self.color_buttons[-1].setStyleSheet("font-size: 30px")
        self.color_buttons[-1].clicked.connect(lambda _, b=len(self.color_buttons) - 1: self.change_selected_color(b))

        fila = (len(self.colors) // self.max_cols)
        columna = len(self.colors) % self.max_cols
        self.color_grid.addWidget(self.color_buttons[-1], columna, fila)

        self.colors.append(self.rgb_to_lab((255, 255, 255)))
        # self.colors.append((255,255,255))

        fila = (len(self.colors) // self.max_cols)
        columna = len(self.colors) % self.max_cols
        self.color_grid.addWidget(self.add_color_button, columna, fila)
        self.colors_to_save.append([255, 255, 255])

    def change_selected_color_special(self, index, color):
        self.color_buttons[index].setStyleSheet(f"font-size: 30px;"
                                                f"background-color:rgb({color[0]}, {color[1]}, {color[2]})")
        self.colors[index] = self.rgb_to_lab(color)
        self.colors_to_save[index] = color

    def change_selected_color(self, index):
        color = self.pick_color()
        self.color_buttons[index].setStyleSheet(f"font-size: 30px;"
                                                f"background-color:rgb({color[0]}, {color[1]}, {color[2]})")
        self.colors[index] = self.rgb_to_lab(color)
        self.colors_to_save[index] = color

    def set_cursor(self, cursor_id):
        cursor = LoadCursor(None, cursor_id)
        SetCursor(cursor)

    def pick_color(self):
        app.setOverrideCursor(Qt.CursorShape.WaitCursor)
        with mouse.Listener(on_click=self.onClick) as self.mouselstnr:
            self.mouselstnr.join()
        app.restoreOverrideCursor()
        return self.color_picked

    def getHex(self, rgb):
        return '%02X%02X%02X' % rgb

    def checkColor(self, x, y):
        bbox = (x, y, x + 1, y + 1)
        im = ImageGrab.grab(bbox=bbox)
        rgbim = im.convert('RGB')
        r, g, b = rgbim.getpixel((0, 0))
        self.color_picked = [r, g, b]

    def onClick(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            self.checkColor(x, y)
            self.mouselstnr.stop()
            return False

    def onRel(self, key):
        if key == keyboard.Key.esc:
            mlstnr.stop()
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("ding")
    imageGen = WPlaceImageGen()
    imageGen.setWindowTitle("wing")
    imageGen.show()

    sys.exit(app.exec())
