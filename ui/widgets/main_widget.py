from copy import deepcopy
from PyQt5.QtWidgets import QWidget
from scripts.db.settings_manager import SettingsManager
import torch
import cv2

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtWidgets import QFileDialog, QWidget, QDialogButtonBox, QFormLayout, \
    QDoubleSpinBox, QDialog, QSpinBox, QComboBox, QHBoxLayout, \
    QCheckBox, QTimeEdit
from PyQt5 import QtWidgets
from scripts.db.settings_manager import SettingsManager
from ui.qtdesigner.main_interface import Ui_MainInterface

from PyQt5.QtCore import Qt
from ui.widgets.video_viewer_widget import VideoViewerWidget


class MainWidget(VideoViewerWidget):
    def get_event_widget(self, pred):
        name = f"{pred['id']}/{pred['cls']} {pred['possibility'] * 100}%"

        status = f'{pred["start_timestamp"]}---{pred["end_timestamp"]}'

        eventWidget = QtWidgets.QWidget()
        eventWidget.pred = pred

        def edit_event():
            dialog = QDialog()
            dialog.setWindowTitle('Add event')
            dialog.setWindowModality(Qt.ApplicationModal)

            dialog.numberLabel = 'ID'
            dialog.numberBox = QSpinBox(dialog)
            dialog.numberBox.setValue(pred['id'])

            dialog.classLabel = 'Класс'
            dialog.classBox = QComboBox(dialog)
            dialog.classBox.addItems(SettingsManager().labels)
            dialog.classBox.setCurrentIndex(SettingsManager().labels.index(pred['cls']))

            dialog.centerLabel = 'Координаты центра'
            dialog.center_widget = QWidget()
            dialog.center_layout = QHBoxLayout(dialog.center_widget)
            dialog.center_widget.setLayout(dialog.center_layout)
            dialog.x_centerBox = QSpinBox(dialog)
            dialog.y_centerBox = QSpinBox(dialog)
            dialog.x_centerBox.setMaximum(10 ** 5)
            dialog.y_centerBox.setMaximum(10 ** 5)
            dialog.x_centerBox.setValue(pred['center'][0])
            dialog.y_centerBox.setValue(pred['center'][1])
            dialog.center_layout.addWidget(dialog.x_centerBox)
            dialog.center_layout.addWidget(dialog.y_centerBox)

            dialog.possibilityLabel = 'Вероятность'
            dialog.possibilityBox = QDoubleSpinBox(dialog)
            dialog.possibilityBox.setSingleStep(0.01)
            dialog.possibilityBox.setValue(pred['possibility'])

            dialog.startTimeLabel = 'Время начала'
            dialog.startTime = QTimeEdit(dialog)
            dialog.startTime.setDisplayFormat('hh:mm:ss')
            dialog.startTime.setTime(QTime.fromString(pred['start_timestamp'], 'hh:mm:ss'))

            dialog.endTimeLabel = 'Время конца'
            dialog.endTime = QTimeEdit(dialog)
            dialog.endTime.setDisplayFormat('hh:mm:ss')
            dialog.endTime.setTime(QTime.fromString(pred['end_timestamp'], 'hh:mm:ss'))

            dialog.layout = QFormLayout(dialog)
            dialog.layout.addRow(dialog.numberLabel, dialog.numberBox)
            dialog.layout.addRow(dialog.classLabel, dialog.classBox)
            dialog.layout.addRow(dialog.centerLabel, dialog.center_widget)
            dialog.layout.addRow(dialog.possibilityLabel, dialog.possibilityBox)
            dialog.layout.addRow(dialog.startTimeLabel, dialog.startTime)
            dialog.layout.addRow(dialog.endTimeLabel, dialog.endTime)

            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
            buttonBox.accepted.connect(dialog.accept)
            buttonBox.rejected.connect(dialog.reject)
            dialog.layout.addWidget(buttonBox)
            if dialog.exec():
                start_time = dialog.startTime.time()
                end_time = dialog.endTime.time()
                pred['id'] = dialog.numberBox.value()
                pred['cls'] = SettingsManager().labels[dialog.classBox.currentIndex()]
                pred['start_timestamp'] = f"{str(start_time.hour()).rjust(2, '0')}:{str(start_time.minute()).rjust(2, '0')}:{str(start_time.second()).rjust(2, '0')}"
                pred['end_timestamp'] = f"{str(end_time.hour()).rjust(2, '0')}:{str(end_time.minute()).rjust(2, '0')}:{str(end_time.second()).rjust(2, '0')}"
                pred['possibility'] = dialog.possibilityBox.value()
                pred['center'] = [dialog.x_centerBox.value(), dialog.y_centerBox.value()]
            self.update_prediction()
        
        def delete_event():
            del_i = None
            for i, elem in enumerate(self.main_controller.data):
                if elem['id'] == pred['id']:
                    del_i = i
                    break
            if del_i is not None:
                del self.main_controller.data[del_i]
                self.update_prediction()
        
        def show_event():
            self.cur_event_widget = eventWidget
        
        def show_bbox_event():
            if not any(self.main_controller.frameid2ind):
                return
            timing = list(map(int, pred['start_timestamp'].split(':')))
            secs = (timing[0] * 60 + timing[1]) * 60 + timing[2]
            frame_i = int(secs * self.main_controller.frame_rate)
            frame = self.main_controller.frames[self.main_controller.frameid2ind[frame_i]]
            frame = deepcopy(frame)
            frame = cv2.circle(frame, pred['center'], 32, (0, 0, 255), -1)#bgr

            (h, w) = frame.shape[:2]
            width = 640
            r = width / float(w)
            dim = (width, int(h * r))
            frame = cv2.resize(frame, dim, interpolation = cv2.INTER_LINEAR)

            cv2.imshow("predicted_frame", frame)
        
        eventWidget.setObjectName("eventWidget")
        eventExample = QtWidgets.QHBoxLayout(eventWidget)
        eventExample.setObjectName("eventExample")
        #imageEvent = QtWidgets.QLabel(eventWidget)
        #imageEvent.setObjectName("imageEvent")
        #pixmap = QPixmap('./icons/event.png')
        #imageEvent.setPixmap(pixmap)
        #eventExample.addWidget(imageEvent)
        infoEvent = QtWidgets.QVBoxLayout()
        infoEvent.setObjectName("infoEvent")
        topInfoEvent = QtWidgets.QLabel(eventWidget)
        topInfoEvent.setObjectName("topInfoEvent")
        topInfoEvent.setText(name)
        infoEvent.addWidget(topInfoEvent)
        bottomInfoEvent = QtWidgets.QLabel(eventWidget)
        bottomInfoEvent.setObjectName("bottomInfoEvent")
        bottomInfoEvent.setText(status)
        infoEvent.addWidget(bottomInfoEvent)
        eventExample.addLayout(infoEvent)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        eventExample.addItem(spacerItem1)
        editEventButton = QtWidgets.QPushButton(eventWidget)
        editEventButton.setStyleSheet("background-color: rgb(36, 49, 80);\n"
"qproperty-icon: url(\"./icons/edit_event.png\");")
        editEventButton.setText("")
        editEventButton.setObjectName("editEventButton")
        eventExample.addWidget(editEventButton)
        showEventButton = QtWidgets.QPushButton(eventWidget)
        showEventButton.setStyleSheet("background-color: rgb(36, 49, 80);\n"
"qproperty-icon: url(\"./icons/show_event.png\");")
        showEventButton.setText("")
        showEventButton.setObjectName("showEventButton")
        eventExample.addWidget(showEventButton)

        showBBoxEventButton = QtWidgets.QPushButton(eventWidget)
        showBBoxEventButton.setStyleSheet("background-color: rgb(36, 49, 80);\n"
"qproperty-icon: url(\"./icons/pred.png\");")
        showBBoxEventButton.setText("")
        showBBoxEventButton.setObjectName("showBBoxEventButton")
        eventExample.addWidget(showBBoxEventButton)

        deleteEventButton = QtWidgets.QPushButton(eventWidget)
        deleteEventButton.setStyleSheet("background-color: rgb(36, 49, 80);\n"
"qproperty-icon: url(\"./icons/delete_event.png\");")
        deleteEventButton.setText("")
        deleteEventButton.setObjectName("deleteEventButton")
        eventExample.addWidget(deleteEventButton)

        editEventButton.clicked.connect(edit_event)
        deleteEventButton.clicked.connect(delete_event)
        showEventButton.clicked.connect(show_event)
        showBBoxEventButton.clicked.connect(show_bbox_event)

        return eventWidget
    
    def add_event(self):
        dialog = QDialog()
        dialog.setWindowTitle('Add event')
        dialog.setWindowModality(Qt.ApplicationModal)

        dialog.numberLabel = 'ID'
        dialog.numberBox = QSpinBox(dialog)

        dialog.classLabel = 'Класс'
        dialog.classBox = QComboBox(dialog)
        dialog.classBox.addItems(SettingsManager().labels)

        dialog.centerLabel = 'Координаты центра'
        dialog.center_widget = QWidget()
        dialog.center_layout = QHBoxLayout(dialog.center_widget)
        dialog.center_widget.setLayout(dialog.center_layout)
        dialog.x_centerBox = QSpinBox(dialog)
        dialog.y_centerBox = QSpinBox(dialog)
        dialog.x_centerBox.setMaximum(10 ** 5)
        dialog.y_centerBox.setMaximum(10 ** 5)
        dialog.center_layout.addWidget(dialog.x_centerBox)
        dialog.center_layout.addWidget(dialog.y_centerBox)

        dialog.possibilityLabel = 'Вероятность'
        dialog.possibilityBox = QDoubleSpinBox(dialog)
        dialog.possibilityBox.setSingleStep(0.01)

        dialog.startTimeLabel = 'Время начала'
        dialog.startTime = QTimeEdit(dialog)
        dialog.startTime.setDisplayFormat('hh:mm:ss')

        dialog.endTimeLabel = 'Время конца'
        dialog.endTime = QTimeEdit(dialog)
        dialog.endTime.setDisplayFormat('hh:mm:ss')

        dialog.layout = QFormLayout(dialog)
        dialog.layout.addRow(dialog.numberLabel, dialog.numberBox)
        dialog.layout.addRow(dialog.classLabel, dialog.classBox)
        dialog.layout.addRow(dialog.centerLabel, dialog.center_widget)
        dialog.layout.addRow(dialog.possibilityLabel, dialog.possibilityBox)
        dialog.layout.addRow(dialog.startTimeLabel, dialog.startTime)
        dialog.layout.addRow(dialog.endTimeLabel, dialog.endTime)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)
        dialog.layout.addWidget(buttonBox)
        if dialog.exec():
            start_time = dialog.startTime.time()
            end_time = dialog.endTime.time()
            event = {'id': dialog.numberBox.value(),
                     'cls': SettingsManager().labels[dialog.classBox.currentIndex()],
                     'start_timestamp': f"{str(start_time.hour()).rjust(2, '0')}:{str(start_time.minute()).rjust(2, '0')}:{str(start_time.second()).rjust(2, '0')}",
                     'end_timestamp': f"{str(end_time.hour()).rjust(2, '0')}:{str(end_time.minute()).rjust(2, '0')}:{str(end_time.second()).rjust(2, '0')}",
                     'possibility': dialog.possibilityBox.value(),
                     'center': [dialog.x_centerBox.value(), dialog.y_centerBox.value()]}
            self.main_controller.data.append(event)
        self.update_prediction()
        
    def clear_all_events(self):
        self.eventsScrollAreaContents = QtWidgets.QWidget()
        self.eventsScrollAreaContents.setGeometry(QtCore.QRect(0, 0, 330, 469))
        self.eventsScrollAreaContents.setObjectName("eventsScrollAreaContents")
        self.eventsScrollArea.setWidget(self.eventsScrollAreaContents)

        self.verticalLayout = QtWidgets.QVBoxLayout(self.eventsScrollAreaContents)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

    def update_prediction(self):
        self.clear_all_events()
        print('a')

        self.main_controller.data = list(sorted(self.main_controller.data, key=lambda x: (x['id'], 
                                                           int(x['start_timestamp'].split(':')[0]), 
                                                           int(x['start_timestamp'].split(':')[1]), 
                                                           int(x['start_timestamp'].split(':')[2]))))
        
        data = self.main_controller.data
        if self.filt is not None:
            new_data = []
            for i in range(len(data)):
                ID = data[i]['id']
                start_timestamp = [int(elem) for elem in data[i]['start_timestamp'].split(":")]
                end_timestamp = [int(elem) for elem in data[i]['end_timestamp'].split(":")]
                start_timestamp = (start_timestamp[0] * 60 + start_timestamp[1]) * 60 + start_timestamp[2]
                end_timestamp = (end_timestamp[0] * 60 + end_timestamp[1]) * 60 + end_timestamp[2]
                cond1 = self.filt[0] == -1 or ID == self.filt[0]
                cond2 = (self.filt[1] <= end_timestamp <= self.filt[2]) or\
                        (self.filt[1] <= start_timestamp <= self.filt[2]) or\
                        (start_timestamp <= self.filt[1] and end_timestamp >= self.filt[2])
                if cond1 and cond2:
                    new_data.append(data[i])
            data = new_data

        for pred in data:
            eventWidget = self.get_event_widget(pred)
            eventWidget.setParent(self.eventsScrollAreaContents)
            self.verticalLayout.addWidget(eventWidget)

        event_spacer = QtWidgets.QSpacerItem(20, 456, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(event_spacer)
    
    @property
    def cur_event_widget(self):
        return self._cur_event_widget
    
    @cur_event_widget.setter
    def cur_event_widget(self, val):
        if self._cur_event_widget:
            try:
                self._cur_event_widget.setStyleSheet("background-color: rgb(39, 58, 100)")
            except Exception:
                pass
        val.setStyleSheet("background-color: rgb(0, 28, 69)")

        self._cur_event_widget = val
        
        timing = list(map(int, val.pred['start_timestamp'].split(':')))
        secs = (timing[0] * 60 + timing[1]) * 60 + timing[2]
        frame_i = (secs * self.main_controller.frame_rate)
        self.mediaPlayer.setPosition(int(self.mediaPlayer.duration() * frame_i / self.main_controller.frames_count))

    def use_cuda_changed(self, _):
        self.main_controller = self.useCUDACheckbox.isChecked()

    def load_video(self):
        file_filter = ' '.join([f'*.{video_type}' for video_type in SettingsManager().video_types])
        filepath = QFileDialog.getOpenFileName(filter=f'Video file ({file_filter})')[0]
        if not any(filepath):
            return
        self.cur_video_path = filepath
        self.main_controller.load_frames(filepath)
    
    def filter_events(self):
        dialog = QDialog()
        dialog.setWindowTitle('Filter events')
        dialog.setWindowModality(Qt.ApplicationModal)

        dialog.numberLabel = 'ID'
        dialog.numberBox = QSpinBox(dialog)
        dialog.numberBox.setMinimum(-1)
        dialog.numberBox.setValue(-1)

        dialog.startTimeLabel = 'Время начала'
        dialog.startTime = QTimeEdit(dialog)
        dialog.startTime.setDisplayFormat('hh:mm:ss')

        dialog.endTimeLabel = 'Время конца'
        dialog.endTime = QTimeEdit(dialog)
        dialog.endTime.setDisplayFormat('hh:mm:ss')
        dialog.endTime.setTime(QTime(23, 59, 59))

        dialog.layout = QFormLayout(dialog)
        dialog.layout.addRow(dialog.numberLabel, dialog.numberBox)
        dialog.layout.addRow(dialog.startTimeLabel, dialog.startTime)
        dialog.layout.addRow(dialog.endTimeLabel, dialog.endTime)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)
        dialog.layout.addWidget(buttonBox)
        if dialog.exec():
            start_time = dialog.startTime.time()
            end_time = dialog.endTime.time()
            identification = dialog.numberBox.value()
            start_time = start_time.hour()*3600 + start_time.minute()*60 + start_time.second()
            end_time = end_time.hour()*3600 + end_time.minute()*60 + end_time.second()
            self.filt = [identification, start_time, end_time]

            self.filterEventButton.clicked.disconnect(self.filter_events)
            self.filterEventButton.clicked.connect(self.del_filter_events)
            self.filterEventButton.setText("Убрать фильтрацию")

            self.update_prediction()
    
    def del_filter_events(self):
        self.filt = None
        self.filterEventButton.setText("Фильтрация")
        self.filterEventButton.clicked.disconnect(self.del_filter_events)
        self.filterEventButton.clicked.connect(self.filter_events)
        self.update_prediction()

    def positionChanged(self, position):
        super().setPosition(position)
        self.positionSlider.setValue(position)
        if self.main_controller.frame_rate != 0 and self.positionSlider.maximum() != 0:
            secs = round(position * (self.main_controller.frames_count / self.main_controller.frame_rate) / self.positionSlider.maximum())
            h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
            self.timeLabel.setText(f"{str(h).rjust(2, '0')}:{str(m).rjust(2, '0')}:{str(s).rjust(2, '0')}")
        else:
            self.timeLabel.setText("00:00:00")

    def setPosition(self, position):
        super().setPosition(position)
        if self.main_controller.frame_rate != 0 and self.positionSlider.maximum() != 0:
            secs = round(position * (self.main_controller.frames_count / self.main_controller.frame_rate) / self.positionSlider.maximum())
            h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
            self.timeLabel.setText(f"{str(h).rjust(2, '0')}:{str(m).rjust(2, '0')}:{str(s).rjust(2, '0')}")
        else:
            self.timeLabel.setText("00:00:00")

    def __init__(self, main_controller, parent, ui=Ui_MainInterface):
        super().__init__(parent, ui)
        self.main_controller = main_controller

        self.useCUDACheckbox.setChecked(self.main_controller.use_cuda)
        self.useCUDACheckbox.setEnabled(torch.cuda.is_available())
        self.useCUDACheckbox.stateChanged.connect(self.use_cuda_changed)

        self.predictAllButton.clicked.connect(self.main_controller.predict_all)
        self.saveEverythingButton.clicked.connect(self.main_controller.save_everything)
        self.loadEverythingButton.clicked.connect(self.main_controller.load_everything)

        self.main_controller = main_controller

        self._cur_event_widget = None

        self.eventsScrollAreaContents = QtWidgets.QWidget()
        self.eventsScrollAreaContents.setGeometry(QtCore.QRect(0, 0, 330, 469))
        self.eventsScrollAreaContents.setObjectName("eventsScrollAreaContents")
        self.eventsScrollArea.setWidget(self.eventsScrollAreaContents)

        self.verticalLayout = QtWidgets.QVBoxLayout(self.eventsScrollAreaContents)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.addEventButton.clicked.connect(self.add_event)
        self.filterEventButton.clicked.connect(self.filter_events)
        self.filt = None
        
