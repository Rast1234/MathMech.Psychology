# -*- coding: utf-8 -*-
__author__ = 'rast'

from PySide import QtCore


class Config(object):
    """
    Configuration handler
    """

    config = {

        # good thing for future
        'version': 1,

        # where to look for videos
        'folder': '.\\video',

        # or, when it fails..
        'default_folder': './video',

        # filetypes to look for
        'extensions': ['avi', 'mpg', 'mpeg', 'mkv', 'wmv',
                       'flv', 'mov', 'mp4', 'ts', 'dv', ],

        # selected files in current folder
        'files': [],

        # how long to work, in seconds
        'totaltime': 15,

        # repeat until time is over
        'repeat': False,

        # timing rules: (time, speed)
        'rules': [
                  (5, 3),
                  (3, 1)
        ],

        # when all rules passed and totaltime is not reached
        'default_speed': 1,

        # pauses during totaltime
        # TODO: interrupts behavior
        'interrupts': 7,

        # emulate command-line arguments
        'vlc_args': [
            '--no-audio',
            '--ignore-config',
            #'--config', 'vlc.conf',
            #'-vvv',  # debug
        ],

        # hotkeys
        'keys': {
            'fullscreen': (QtCore.Qt.Key_F, QtCore.Qt.Key_F11),
            'exit': (QtCore.Qt.Key_Escape, ),
            'speedUp': (QtCore.Qt.Key_Equal, ),
            'speedDown': (QtCore.Qt.Key_Minus, ),
        },
    }

    def __init__(self):
        self.update(self.config)

    def load(self, filename):
        pass

    def update(self, newDic):
        """
        Make config keys available as class fields:
        instance.config['files'] to instance.files
        """
        for x in self.config.keys():  # clear old entries
            del x
        self.config = newDic
        self.__dict__.update(self.config)  # __dict__ is a magic

    def reverseUpdate(self):
        """
        Update config hash with actual values
         (they could change during work)
        """
        for x in self.config.keys():
            self.config[x] = self.__dict__[x]