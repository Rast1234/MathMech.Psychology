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

    files = []
    repeat = False

    def __init__(self, qt_frame, cmdline):
        self.__instance = vlc.Instance(cmdline)
        self.__mediaplayer = self.__instance.media_player_new()
        self.__mediaplayer.video_set_mouse_input(False)  # disable mouse in player
        self.__mediaplayer.video_set_key_input(False)  # disable keyboard

        self.Bind(qt_frame)

        # connect to player events
        manager = self.__mediaplayer.event_manager()
        manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.__OnFileEnd)
        manager.event_attach(vlc.EventType.MediaPlayerPlaying, self.__OnPlay)
        manager.event_attach(vlc.EventType.MediaPlayerPaused, self.__OnPause)

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

    def Open(self, files, repeat):
        self.__list = self.__instance.media_list_new(files)
        self.__listplayer = self.__instance.media_list_player_new()
        if repeat:
            self.__listplayer.set_playback_mode(vlc.PlaybackMode.loop)
        else:
            self.__listplayer.set_playback_mode(vlc.PlaybackMode.default)
        self.__listplayer.set_media_player(self.__mediaplayer)  # very important!
        self.__listplayer.set_media_list(self.__list)  # grab the list
        self.__listplayer.play_item_at_index(0)

        #self.__media = self.__instance.media_new(file)  # create 'media' instance
        #tmp = self.__mediaplayer.set_media(self.__media)  # put it in the player


    def Play(self):
        """
        Play video
        """
        if self.__mediaplayer.play() == -1:
            return
        self.__mediaplayer.play()

    def Pause(self):
        """
        Pause video
        """
        self.__mediaplayer.set_pause(1)

    def Stop(self):
        """
        Stop video
        """
        self.__mediaplayer.stop()

    def Shutdown(self):
        pass

    def IsPlaying(self):
        return self.__mediaplayer.is_playing()

    def SetSpeed(self, speed):
        if self.IsPlaying():
            self.Pause()
            self.__mediaplayer.set_rate(speed)
            self.Play()
        else:
            self.__mediaplayer.set_rate(speed)

    def __OnFileEnd(self, evt):
        pass

    def __OnPlay(self, evt):
        pass

    def __OnPause(self, evt):
        pass