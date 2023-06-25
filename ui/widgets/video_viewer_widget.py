from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from ui.widgets import BaseWidget
from PyQt5.QtWidgets import (QHBoxLayout, QPushButton, QSlider, QStyle, QLabel, QWidget, QVBoxLayout)
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

from PyQt5.QtCore import Qt


class VideoViewerWidget(BaseWidget):
    def none_cur_video_check(self):
        pass
        #if self.cur_frame is None:
        #    QMessageBox().warning(self, 'Warning', 'Не удается загрузить видео')

    def get_video_size(self) -> tuple:
        """Получение размера видео с учетом черно-белых полей"""
        if self.cur_frame is None:
            return 0, 0
        return self.cur_frame.width, self.cur_frame.height

    @property
    def cur_video_path(self):
        return self._cur_video_path

    @cur_video_path.setter
    def cur_video_path(self, value: int):
        self._cur_video_path = value

        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(value)))
        self.playButton.setEnabled(True)
        self.mediaPlayer.pause()

        self.none_cur_video_check()

    @property
    def cur_frame(self):
        frame = self.videoWidget.grab()
        if frame.isNull():
            return None
        return frame
    
    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
    
    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)
    
    def ui_postinit(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        btnSize = QSize(16, 16)
        self.videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        
        self.timeLabel = QLabel()
        self.timeLabel.setText("00:00:00")

        self.controlLayoutWidget = QWidget(self.mainLayoutWidget)
        self.controlLayoutWidget.setMaximumSize(QtCore.QSize(16777215, 30))

        self.controlLayout = QHBoxLayout(self.controlLayoutWidget)
        self.controlLayout.setContentsMargins(0, 0, 0, 0)
        self.controlLayout.addWidget(self.playButton)
        self.controlLayout.addWidget(self.positionSlider)
        self.controlLayout.addWidget(self.timeLabel)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

        self.verticalLayout.addWidget(self.videoWidget)
        self.verticalLayout.addWidget(self.controlLayoutWidget)

    def __init__(self, parent, ui):
        super().__init__(parent, ui)
        self.ui_postinit()

        self._cur_video_path = None

        self.loadVideosButton.clicked.connect(self.load_video)
