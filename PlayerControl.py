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