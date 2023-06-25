from copy import deepcopy
import torch
from ultralytics import YOLO
import cv2
import numpy as np

from scripts.db.settings_manager import SettingsManager

yolo_model = YOLO('weights/yolo/best.pt', task='detect')
from ultralytics.tracker import register_tracker
from ultralytics.yolo.utils import IterableSimpleNamespace, yaml_load
from ultralytics.yolo.utils.checks import check_yaml
from ultralytics.tracker.trackers import BOTSORT,BYTETracker
from math import sqrt

from tqdm.auto import tqdm
import torch
import numpy as np
from scipy.spatial.distance import cosine
import torch
from PIL import Image
import torch
from torch.nn import CosineSimilarity
from torchvision.transforms import functional as F
from transformers import CLIPImageProcessor, CLIPModel, CLIPTokenizer
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(250, 30)
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setGeometry(QtCore.QRect(0, 0, 250, 30))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        self.progressBar.setMinimumSize(QtCore.QSize(250, 30))
        self.progressBar.setMaximumSize(QtCore.QSize(250, 30))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Progress bar"))


class ProgressBar(QtWidgets.QDialog, Ui_Form):
    def __init__(self, desc = None, parent=None):
        super(ProgressBar, self).__init__(parent)
        self.setupUi(self)
        self.show()

        if desc != None:
            self.setDescription(desc)

    def setValue(self, val):
        self.progressBar.setProperty("value", val)

    def setMax(self, val):
        self.progressBar.setProperty("maximum", val)

    def setDescription(self, desc):
        self.setWindowTitle(desc)    


def predict(frames, frameid2ind, frame_rate, device=torch.device('cpu')):
    def frame2timestamp(frame_i):
        secs = int(frame_i // (frame_rate / SettingsManager().keep_each_x_frame))
        h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
        return f"{str(h).rjust(2, '0')}:{str(m).rjust(2, '0')}:{str(s).rjust(2, '0')}"

    yolo_model.to(device)

    pb = ProgressBar()
    pb.progressBar.setMaximum(len(frames))

    tracks = {}
    for frame_i, frame in tqdm(enumerate(frames), total=len(frames)):
        results = yolo_model.track(frame, persist=True, imgsz=1280)
        for box in results[0].boxes:
            box_id = box.id.detach().cpu().numpy().astype(int)[0]
            tracked_box = {'track_id': box_id,
                           'frame_i': frame_i,
                           'cls': box.cls.detach().cpu().numpy().astype(int)[0], 
                           'xywh': box.xywh.detach().cpu().numpy().astype(int)[0],
                           'xyxy': box.xyxy.detach().cpu().numpy().astype(int)[0],
                           'conf': round(box.conf.detach().cpu().numpy().astype(float)[0], 2)}
            tracks[box_id] = tracks.get(box_id, []) + [tracked_box]

        pb.setValue(frame_i)
        QApplication.processEvents()
    
    pb.close()
    
    preds = []
    for id, boxes in tqdm(enumerate(tracks.values()), total=len(tracks)):
        secs1 = int(boxes[0]['frame_i'] // (frame_rate / SettingsManager().keep_each_x_frame))
        secs2 = int(boxes[-1]['frame_i'] // (frame_rate / SettingsManager().keep_each_x_frame))
        if (secs2 - secs1) < SettingsManager().min_duration_secs:
            continue

        classes = {}
        for box in boxes:
            classes[box['cls']] = classes.get(box['cls'], 0) + box['conf']
        cls, conf = max(list(classes.items()), key=lambda elem: elem[1])
        conf /= sum([int(box['cls'] == cls) for box in boxes])

        pred = {}
        pred['id'] = id
        pred['cls'] = SettingsManager().yololabels2labels[boxes[0]['cls']]

        pred['start_timestamp'] = frame2timestamp(boxes[0]['frame_i'])
        pred['end_timestamp'] = frame2timestamp(boxes[-1]['frame_i'])
        pred['possibility'] = float(round(conf, 2))

        pred['center'] = list(map(int, boxes[0]['xywh'][:2]))

        preds.append(pred)

    return preds
