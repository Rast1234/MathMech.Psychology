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
        """
        the media player has to be 'connected' to the QFrame
        (otherwise a video would be displayed in it's own window)
        this is platform specific!
        you have to give the id of the QFrame (or similar object) to
        vlc, different platforms have different functions for this
        """
        self.__instance = vlc.Instance()
        self.__mediaplayer = self.__instance.media_player_new(cmdline)
        self.__mediaplayer.video_set_mouse_input(False)  # disable mouse in player
        self.__mediaplayer.video_set_key_input(False)  # disable keyboard

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

        # bind to player events
        manager = self.__mediaplayer.event_manager()
        manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.__OnFileEnd)
        manager.event_attach(vlc.EventType.MediaPlayerPlaying, self.__OnPlay)
        manager.event_attach(vlc.EventType.MediaPlayerPaused, self.__OnPause)

    def Open(self, file):
        print "try to open: ", file
        self.__media = self.__instance.media_new(file)  # create 'media' instance
        print "new media instance: ", self.__media
        tmp = self.__mediaplayer.set_media(self.__media)  # put it in the player
        print "passed to player: ", tmp

    def OpenList(self, fileList, repeat):
        self.files = fileList
        self.repeat = repeat
        file = self.files.pop(0)
        self.Open(file)
        if self.repeat:
            self.files.append(file)

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
        print self.files
        if self.files:
            file = self.files.pop(0)
            print "next file = ", file
            self.Open(file)
            self.Play()
            print "opened next file"
            if self.repeat:
                self.files.append(file)
        else:  # last file
            print "last file"
            pass

    def __OnPlay(self, evt):
        pass

    def __OnPause(self, evt):
        pass