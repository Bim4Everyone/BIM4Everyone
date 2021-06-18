import os, json, io
# -*- coding: utf-8 -*-
import os.path as op
from pyrevit import USER_ROAMING_DIR

# os.getenv('appdata')
PYREVIT_APP_DIR = op.join(USER_ROAMING_DIR, 'pyRevit')

class ConfigKeeper(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ConfigKeeper, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.path = op.join(PYREVIT_APP_DIR, 'speech_config.json')        
        self._load()

    def _load(self):
        self._changed = False
        if op.isfile(self.path):
            f = io.open(self.path, 'r', encoding='utf-8')
            self._storage = json.load(f)
            f.close()
        else:
            self._storage = {}

    def update(self):
        if self._changed:
            f = open(self.path, 'w')
            json.dump(self._storage, f)
            f.close()

            self._changed = False

    def __setitem__(self, key, value):
        self._changed = True
        self._storage[key] = value

    def __getitem__(self, key):
        return self._storage[key]

    def __contains__(self, key):
        return key in self._storage
 
    # def __del__(self):
    #     print "deleted"
    #     self.update()
