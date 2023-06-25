import torch
import pandas as pd
import numpy as np

from PyQt5 import QtGui
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QMainWindow, QWidget
from constants import FFMPEG_BIN, FFPROBE_BIN
import cv2

from scripts.db.settings_manager import SettingsManager
from ui.widgets import MainWidget

import numpy as np
import torch
import pandas as pd
import json
from PyQt5 import QtGui
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import subprocess as sp
from scripts.db.settings_manager import SettingsManager

from pred import predict


class BaseWindow(QMainWindow):
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        rect = QRect(0, 0, a0.size().width(), a0.size().height())
        if self.widget.geometry():
            self.widget.setGeometry(rect)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        self.widget.keyPressEvent(a0)

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        self.widget.keyReleaseEvent(a0)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.widget.mousePressEvent(a0)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.widget.mouseMoveEvent(a0)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.widget.mouseReleaseEvent(a0)

    def __init__(self, widget_type, *widget_args, title='Title'):
        super(BaseWindow, self).__init__()
        self.setWindowTitle(title)

        self.widget = widget_type(*widget_args)
        self.widget.show()
        self.resize(self.widget.size())


class MainWindow(BaseWindow):
    def __init__(self, main_controller):
        super().__init__(MainWidget, main_controller, self, title=SettingsManager().main_window_title)


class MainController:
    def save_everything(self):
        filepath = QFileDialog.getSaveFileName(filter='JSON files (*.json)')[0]
        if not any(filepath):
            return
        json.dump(self.data, open(filepath, 'w', encoding='utf-8'))
    
    def load_frames(self, video_path):
        command = [FFPROBE_BIN,
           '-v', 'error',
           '-select_streams', 'v:0',
           '-count_packets',
           '-show_entries', 'stream=nb_read_packets',
           '-of', 'csv=p=0',
           video_path]
        pipe = sp.Popen(command, stdout=sp.PIPE)
        frames_count = int(pipe.stdout.read())

        command = [FFPROBE_BIN,
           '-v', 'error',
           '-select_streams', 'v:0',
           '-show_entries', 'stream=width,height,r_frame_rate',
           '-of', 'csv=s=x:p=0',
           video_path]
        pipe = sp.Popen(command, stdout=sp.PIPE)
        w, h, frame_rate = pipe.stdout.read().replace(b"\r\n", b"").split(b"x")
        w, h, frame_rate = int(w), int(h), int(frame_rate.split(b"/")[0]) / int(frame_rate.split(b"/")[1])

        self.frame_rate = frame_rate
        self.frames_count = frames_count

        size_img = (w, h)
        command = [FFMPEG_BIN,
                   '-i', video_path,
                   '-f', 'image2pipe',
                   '-pix_fmt', 'rgb24',
                   '-vcodec', 'rawvideo', '-']
        pipe = sp.Popen(command, stdout=sp.PIPE)
        last_frame_i = 0
        for frame_i in range(self.frames_count):
            raw_frame = pipe.stdout.read(size_img[0] * size_img[1] * 3)
            frame = np.frombuffer(raw_frame, dtype='uint8')
            if frame.shape[0] == 0:
                break
            self.frameid2ind[frame_i] = last_frame_i

            if (frame_i + 1) % SettingsManager().keep_each_x_frame != 0:
                continue

            frame = frame.reshape((size_img[1], size_img[0], 3))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frames.append(frame)
            last_frame_i += 1
            self.frameid2ind[frame_i] = last_frame_i

    def load_everything(self):
        filepath = QFileDialog.getOpenFileName(filter='JSON files (*.json)')[0]
        if not any(filepath):
            return
        try:
            self.data = json.load(open(filepath, 'r', encoding='utf-8'))
            self.update_prediction()
        except pd.errors.ParserError:
            QMessageBox().warning(
                self, 'Warning', '''Что-то пошло не так при чтении файла''')
            return

    def predict_all(self):
        preds = predict(self.frames, self.frameid2ind, self.frame_rate, device=torch.device('cuda' if self.use_cuda else 'cpu'))
        self.data = preds
        self.update_prediction()

    def update_prediction(self):
        self.main_window.widget.update_prediction()

    def show(self):
        self.main_window.show()

    def __init__(self) -> None:
        self.data = []
        self.frames = []
        self.frameid2ind = {}
        self.frames_count = 0
        self.frame_rate = 0
        self.use_cuda = torch.cuda.is_available()

        self.main_window = MainWindow(self)
