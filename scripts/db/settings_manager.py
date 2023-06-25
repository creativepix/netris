import os
import json
from constants import SETTINGS_PATH
from scripts.patterns import Singleton


class SettingsManager:
    __metaclass__ = Singleton

    def save_settings(self):
        if not self._is_initialized:
            return
        settings = {attr: getattr(self, attr) for attr in self.__dict__.keys() if not attr.startswith('_')}
        with open(SETTINGS_PATH, 'w', encoding='utf8') as f:
            json.dump(settings, f)

    def load_settings(self):
        if os.path.exists(SETTINGS_PATH):
            try:
                settings = json.load(open(SETTINGS_PATH, 'r', encoding='utf8'))
            except json.JSONDecodeError:
                settings = {}
        else:
            settings = {}
        for key, val in settings.items():
            if val != getattr(self, key):
                object.__setattr__(self, key, val)

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)
        self.save_settings()

    def __init__(self):
        self._is_initialized = False

        self.main_window_title = 'Лебедяхи'
        self.video_types = ['mp4', 'flv', 'ts', 'mts', 'avi']

        #self.yololabels2labels = ['Грузовик', 'Трактор', 'Экскаватор', 'Кран', 'Кран', 'Прочие', 'Грузовик']
        self.yololabels2labels = ['Грузовик', 'Трактор', 'Экскаватор', 'Кран', 'Кран', 'Прочие']
        self.labels = ['Грузовик', 'Трактор', 'Экскаватор', 'Кран', 'Прочие']

        self.keep_each_x_frame = 10

        #TODO
        self.min_duration_secs = 10

        self.load_settings()
        self._is_initialized = True
