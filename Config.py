__author__ = 'rast'

"""
Configuration handler
"""


class Config(object):

    config = {
        'folder': '.',  # where to look for videos
        'extensions': ['avi', 'mpg', 'mpeg', 'mkv', 'wmv',
                       'flv', 'mov', 'mp4', 'ts', 'dv', ],  # filetypes
        'files': [],  # selected files in current folder
    }
    def __init__(self):
        self.update(self.config)

    def load(self, filename):
        pass

    def update(self, newDic):
        for x in self.config.keys():  # clear old entries
            del x
        self.config = newDic
        self.__dict__.update(self.config)