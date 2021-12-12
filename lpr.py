import lpr_ui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

import cv2.cv2 as cv2
from detect import detect
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'


class Processer:
    def __init__(self, ui):
        self.current_frame = None
        self.ui = ui
        self.timer_camera = QTimer()
        self.capture = None

    def open_image(self):
        image_name, _ = QFileDialog.getOpenFileName(None, "打开图片", "", "Images(*.jpg *.png *.jpeg *bmp);;All Files(*)")
        self.current_frame = cv2.imread(image_name)
        self.set_frame(self.ui.frame_container, self.current_frame)
        self.process()

    def open_video(self):
        video_name, _ = QFileDialog.getOpenFileName(None, "打开视频", "", "Videos(*.mp4 *.avi);;All Files(*)")
        print(video_name)
        self.capture = cv2.VideoCapture(video_name)
        self.timer_camera.timeout.connect(self.show_video)
        self.timer_camera.start(10)

    def show_video(self):
        success, frame = self.capture.read()
        if success:
            result_image, plate_image, result = detect(frame)
            if result_image is not None:
                self.set_frame(ui.frame_container, result_image)
            if plate_image is None:
                self.ui.label_4.setAlignment(Qt.AlignCenter)
                self.ui.label_4.setText("车牌识别未成功！")
            else:
                self.set_frame(ui.plate_container, plate_image)
                self.ui.label_4.setAlignment(Qt.AlignCenter)
                self.ui.label_4.setText(result)

            self.timer_camera.start(10)

    def set_frame(self, container, image):
        container.setAlignment(Qt.AlignCenter)
        container_h = container.height()
        container_w = container.width()
        if container_h > container_w:
            width = container_w
            height = int(image.shape[0] * (width / image.shape[1]))
        else:
            height = container_h
            width = int(image.shape[1] * (height / image.shape[0]))
            if width > container_w:
                ratio = container_w / container_h
                width = int(height * ratio)

        frame = cv2.resize(image, (width, height))

        shrink = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        QtImg = QImage(shrink.data,
                       shrink.shape[1],
                       shrink.shape[0],
                       shrink.shape[1] * 3,
                       QImage.Format_RGB888)

        container.setPixmap(QPixmap.fromImage(QtImg))

    def process(self):
        result_image, plate_image, result = detect(self.current_frame)
        if result_image is not None:
            self.set_frame(ui.frame_container, result_image)
        if plate_image is None:
            self.ui.label_4.setAlignment(Qt.AlignCenter)
            self.ui.label_4.setText("车牌识别未成功！")
        else:
            self.set_frame(ui.plate_container, plate_image)
            self.ui.label_4.setAlignment(Qt.AlignCenter)
            self.ui.label_4.setText(result)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = lpr_ui.Ui_MainWindow()
    ui.setupUi(MainWindow)

    p = Processer(ui)
    ui.set_click_event(ui.imgTestButton, p.open_image)
    ui.set_click_event(ui.videoTestButton, p.open_video)

    MainWindow.show()
    sys.exit(app.exec_())


