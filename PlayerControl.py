# -*- coding: utf-8 -*-
__author__ = 'rast'

import vlc

"""
VLC Controller class

Manages VLC Instance with programmer-friendly commands
"""

class PlayerControl(object):

    def __init__(self, qtWindow):
        self.__instance = vlc.Instance()
        self.__mediaplayer = self.__instance.media_player_new()

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

