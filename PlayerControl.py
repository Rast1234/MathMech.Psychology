# -*- coding: utf-8 -*-
__author__ = 'rast'

import vlc
import sys
import ctypes

"""Globally defined values
to access from SpeedDelegate
"""
maxSpeed = 20.0
minSpeed = 0.1

class PlayerControl(object):
    """
    VLC Controller class

    Manages VLC Instance with programmer-friendly commands
    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
             cls._instance = super(PlayerControl, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    files = []
    repeat = False

    def __init__(self, qt_frame, cmdline):
        self.__speed = 1.0
        self.__instance = vlc.Instance(cmdline)

        self.__mediaplayer = self.__instance.media_player_new()
        self.__mediaplayer.video_set_mouse_input(False)  # disable mouse in player
        self.__mediaplayer.video_set_key_input(False)  # disable keyboard
        self.__listplayer = self.__instance.media_list_player_new()

        self.Bind(qt_frame)

    def Bind(self, qt_frame):
        """
        the media player has to be 'connected' to the QFrame
        (otherwise a video would be displayed in it's own window)
        this is platform specific!
        you have to give the id of the QFrame (or similar object) to
        vlc, different platforms have different functions for this
        """
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

    def Open(self, files):
        self.__list = self.__instance.media_list_new(files)
        self.__listplayer.set_playback_mode(vlc.PlaybackMode.loop)
        self.__listplayer.set_media_player(self.__mediaplayer)  # very important!
        self.__listplayer.set_media_list(self.__list)  # grab the list
        self.__listplayer.play_item_at_index(0)

        #self.__media = self.__instance.media_new(file)  # create 'media' instance
        #tmp = self.__mediaplayer.set_media(self.__media)  # put it in the player


    def Play(self):
        """
        Play video
        """
        player = self.__listplayer
        #player = self.__mediaplayer
        if player.play() == -1:
            return
        else:
            player.play()

    def Pause(self):
        """
        Pause video
        """
        player = self.__listplayer
        player.pause()
        #player = self.__mediaplayer
        #player.set_pause(1)

    def Stop(self):
        """
        Stop video
        """
        player = self.__listplayer
        #player = self.__mediaplayer
        player.stop()

    def Shutdown(self):
        pass

    def IsPlaying(self):
        player = self.__listplayer
        #player = self.__mediaplayer
        return True if player.is_playing() else False

    def GetSpeed(self):
        #return self.__mediaplayer.get_rate() #fails under windows
        return self.__speed

    def SetSpeed(self, speed):
        self.__speed = speed
        if self.IsPlaying():
            self.Pause()
            self.__mediaplayer.set_rate(self.__speed)
            self.Play()
        else:
            self.__mediaplayer.set_rate(self.__speed)

    def SpeedChange(self, arg):
        if minSpeed <= self.__speed+arg <=maxSpeed:
            self.__speed += arg
        elif self.__speed+arg < minSpeed:
            self.__speed = minSpeed
        else:
            self.__speed = maxSpeed
        self.SetSpeed(self.__speed)
