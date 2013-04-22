# -*- coding: utf-8 -*-
__author__ = 'rast'

import vlc
import sys
import ctypes


class PlayerControl(object):
    """
    VLC Controller class

    Manages VLC Instance with programmer-friendly commands
    """
    def __init__(self, qt_frame):
        self.__instance = vlc.Instance()
        self.__mediaplayer = self.__instance.media_player_new()
        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this

        pycobject_hwnd = qt_frame.winId()

        if sys.platform == "linux2":  # for Linux using the X Server
            self.__mediaplayer.set_xwindow(pycobject_hwnd)
        elif sys.platform == "win32":  # for Windows
            ctypes.pythonapi.PyCObject_AsVoidPtr.restype = ctypes.c_void_p
            ctypes.pythonapi.PyCObject_AsVoidPtr.argtypes = [ctypes.py_object]
            int_hwnd = ctypes.pythonapi.PyCObject_AsVoidPtr(pycobject_hwnd)
            self.__mediaplayer.set_hwnd(int_hwnd)
        elif sys.platform == "darwin":  # for MacOS
            self.__mediaplayer.set_agl(pycobject_hwnd)

    def Open(self, fileName):
        #create 'media' instance
        self.__media = self.__instance.media_new(fileName)
        #put it in the player
        self.__mediaplayer.set_media(self.__media)
        self.Play()

    def Play(self):
        """
        Play video
        """
        if self.__mediaplayer.play() == -1:
            # self.fail('Ошибка', 'Не выбрано ни одного файла.')
            return
        self.__mediaplayer.play()

    def Pause(self):
        """
        Pause video
        """
        if self.__mediaplayer.is_playing():
            self.__mediaplayer.pause()

    def Stop(self):
        """
        Stop video
        """
        self.__mediaplayer.stop()
