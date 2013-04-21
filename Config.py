# -*- coding: utf-8 -*-
__author__ = 'rast'

"""
Configuration handler
"""


class Config(object):

    config = {
        'folder': '.\\video',  # where to look for videos
        'extensions': ['avi', 'mpg', 'mpeg', 'mkv', 'wmv',
                       'flv', 'mov', 'mp4', 'ts', 'dv', ],  # filetypes
        'files': [],  # selected files in current folder
        'totaltime': 15  # in seconds
        'rules': [  # timing rules: (time, speed)
            (5, 3),
            (3, 1)
        ]
        'default_speed': 1  # when all rules passed ant totaltime is not reached
        'interrupts': 7  # pauses during totaltime
        # TODO: interrupts behavior
    }
    def __init__(self):
        self.update(self.config)

    def load(self, filename):
        pass

    def update(self, newDic):
        for x in self.config.keys():  # clear old entries
            del x
        self.config = newDic
        self.__dict__.update(self.config)  # __dict__ is a magic

    def reverseUpdate(self):
        for x in self.config.keys():
            self.config[x] = self.__dict__[x]