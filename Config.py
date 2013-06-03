# -*- coding: utf-8 -*-
__author__ = 'rast'

import pickle

class Config(object):
    """
    Configuration handler
    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
             cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    config = {

        # good thing for future
        'version': 1,

        # config file extension
        'ext': 'testcfg',

        # where to look for videos
        'folder': u'',

        # help file  name top open
        'help': u'./Инструкция.pdf',

        # automatically run external program?
        'auto_run': False,

        # program to run
        'exe': u'calc.exe',

        # filetypes to look for
        'extensions': [u'avi', u'mpg', u'mpeg', u'mkv', u'wmv',
                       u'flv', u'mov', u'mp4', u'ts', u'dv', ],

        # selected files in current folder
        'files': [],

        # timing rules: (time, speed)
        'rules': [
                  (0, 1),
        ],

        # total run time in seconds
        'totaltime': 0,

        # emulate command-line arguments
        'vlc_args': [
            '--ignore-config',
            # optimizations:
            '--ffmpeg-hurry-up',  # skip frames when there's not enough time
            '--ffmpeg-skip-idct=4',  # skip inverse discrete cosine transform for all frames
            '--ffmpeg-skip-frame=4',  # force skip all frames
            '--ffmpeg-fast',  # extended speed control mode, might be buggy
            '--ffmpeg-hw',  # force hardware decoding if possible
            '--drop-late-frames',  # default ON
            '--skip-frames',  # works on MPEG2, default ON
            #'--file-caching=60000',  # int [0..60000] ms
            '--postproc-q=0',  # [0..6] disable post-processing
            # misc
            '--quiet',
            #'--quiet-synchro',  # dont log synchro messages
            '--no-video-title-show',  # don't show new file name
            '--no-spu',  # no layers rendering (OSD etc)
            '--verbose=0',  # [0,1,2]: messages, warnings, debug
            '--no-interact',  # do not show any dialogs
            '--hotkeys-mousewheel-mode=2',  # [0,1,2]: vol, pos, none
            '--no-keyboard-events',  # don't process keyboard
            '--no-mouse-events',  # don't process mouse
            '--no-audio',
            #'--run-time=10.5'  # play, in seconds (float)
            #'--config', 'vlc.conf',
            #'-vvv',  # debug
        ],

    }

    def __init__(self):
        self.update(self.config)

    def reset(self):
        self.rules = []
        self.totaltime = 0
        self.auto_run = False
        self.reverseUpdate()

    def load(self, filename):
        try:
            with open(filename, "rb") as out:
                newConfig = pickle.load(out)
                self.update(newConfig)
        except:
            raise

    def save(self, filename):
        self.reverseUpdate()
        try:
            with open(filename, "wb") as out:
                pickle.dump(self.config, out, pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print e

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
