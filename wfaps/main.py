import sys

from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel,
                             QPushButton, QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt
import numpy as np
#from tkinter import colorchooser
from tkinter.filedialog import askopenfilename

from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976
from colormath.color_objects import LabColor, sRGBColor, XYZColor
from vcolorpicker import *
from numpy import *
from colormath import *

class WPlaceImageGen(QWidget):
    def __init__(self):
        super().__init__()
        self.select_image_button = QPushButton("Select Image", self)
        self.copy_image_button = QPushButton("Copy Image", self)
        self.save_image_button = QPushButton("Save Image", self)

        self.v_color_box = QVBoxLayout()
        self.colors = []
        self.color_buttons = []
        self.add_color_button = QPushButton("+", self)

        self.og_image = QImage()
        self.new_image = QImage()
        self.og_image_label = QLabel(self)
        self.new_image_label = QLabel(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Stopwatch")

        general_layout = QHBoxLayout()
        #general_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(general_layout)

        v_image_box = QVBoxLayout()
        v_image_box.setAlignment(Qt.AlignmentFlag.AlignLeft)
        v_image_box.addWidget(self.og_image_label)
        v_image_box.addWidget(self.new_image_label)

        general_layout.addLayout(v_image_box)

        self.v_color_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        #v_color_box.addWidget(self.color_buttons)
        self.v_color_box.addWidget(self.add_color_button)
        general_layout.addLayout(self.v_color_box)
        #h_image_box = QHBoxLayout()

        self.og_image_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.new_image_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.og_image_label.setScaledContents(True)
        self.new_image_label.setScaledContents(True)
        self.og_image_label.setMaximumSize(300, 300)
        self.new_image_label.setMaximumSize(300, 300)

        h_button_box = QHBoxLayout()
        h_button_box.setAlignment(Qt.AlignmentFlag.AlignBottom)
        h_button_box.addWidget(self.select_image_button)
        h_button_box.addWidget(self.copy_image_button)
        h_button_box.addWidget(self.save_image_button)

        v_image_box.addLayout(h_button_box)

        self.setStyleSheet("""
            QPushButton, QLabel {
                padding: 20px;
                font-weight: bold;
                font-family: "Wingdings";
            }
            QPushButton {
                font-size: 50px;
            }
            QLabel {
                font-size: 120px;
                background-color: hsl(200, 100%, 85%);
                border-radius: 20px;
            }
        """)

        self.select_image_button.clicked.connect(self.select_image)
        self.copy_image_button.clicked.connect(self.copy_image)
        self.save_image_button.clicked.connect(self.save_image)

        self.add_color_button.clicked.connect(self.add_color)

    def select_image(self):
        img = askopenfilename()
        self.og_image.load(img)
        self.og_image_label.setPixmap(QPixmap(img))

    def copy_image(self):
        pixels = []
        self.new_image = QImage(self.og_image.width(),
                           self.og_image.height(),
                           QImage.Format.Format_RGBA8888)

        for y in range(self.og_image.height()):
            for x in range(self.og_image.width()):
                color = QColor(self.og_image.pixelColor(x, y))

                closest_color, delta = self.find_closest_color(
                    self.rgb_to_lab((color.red(), color.green(), color.blue())), self.colors)
                #print(f"Closest color: {closest_color}")

                #new_color = self.closest(self.colors, (color.red(), color.green(), color.blue()))
                #new_color = convert_color(color, LabColor)

                #final_color = QColor(int(new_color[0][1]), int(new_color[0][2]), int(new_color[0][3]))
                srgb = self.lab_to_rgb(closest_color)
                #print(f"final color -> {srgb}")
                r = int(round(srgb.rgb_r * 255))
                g = int(round(srgb.rgb_g * 255))
                b = int(round(srgb.rgb_b * 255))

                final_color = QColor(r, g, b)
                #self.new_image.setPixelColor(x, y, final_color)

        self.og_image_label.setPixmap(QPixmap.fromImage(self.og_image))
        self.new_image_label.setPixmap(QPixmap.fromImage(self.new_image))

    def lab_to_rgb(self, lab_color):
        temp_color = convert_color(lab_color, XYZColor)
        return convert_color(temp_color, sRGBColor)

    def rgb_to_lab(self, rgb):
        # rgb es una tupla (R, G, B) con valores 0-255
        rgb_scaled = sRGBColor(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
        lab = convert_color(rgb_scaled, LabColor)
        return lab

    def find_closest_color(self, lab_target, lista_lab):
        delta_e_min = float('inf')
        closest_color = None
        for color_lab in lista_lab:
            delta_e = delta_e_cie1976(lab_target, color_lab)
            delta_e = abs(delta_e)

            if delta_e < delta_e_min:
                delta_e_min = delta_e
                closest_color = color_lab
        return closest_color, delta_e_min

    def closest(self, colors, color):
        colors = np.array(colors)
        color = np.array(color)
        distances = np.sqrt(np.sum((colors - color) ** 2, axis=1))
        index_of_smallest = np.where(distances == np.amin(distances))
        smallest_distance = colors[index_of_smallest]
        print(f"smallest -> {smallest_distance}")
        print("fin de lo que sea")

        return smallest_distance

    def save_image(self):
        self.new_image.save("new_image.png")

    def add_color(self):
        rand_color = [255, 0, 0]
        random.shuffle(rand_color)
        self.color_buttons.append(QPushButton(""))
        self.color_buttons[-1].setStyleSheet(f"background-color:rgb("
                                             f"{rand_color[0]},{rand_color[1]}, {rand_color[2]})")
        self.color_buttons[-1].clicked.connect(lambda _, b=len(self.color_buttons) - 1: self.change_selected_color(b))
        self.v_color_box.addWidget(self.color_buttons[-1])

        self.colors.append(self.rgb_to_lab(rand_color))
        print(self.colors[-1])

    def change_selected_color(self, index):
        colorpicker = ColorPicker()
        color = colorpicker.getColor()
        self.color_buttons[index].setStyleSheet(f"background-color:rgb("
                                             f"{color[0]},{color[1]}, {color[2]})")
        self.colors[index] = self.rgb_to_lab(color)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("ding")
    imageGen = WPlaceImageGen()
    imageGen.setWindowTitle("wing")
    imageGen.show()

    sys.exit(app.exec())