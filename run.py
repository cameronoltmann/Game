import logging
import os
import pygame
from pygame.locals import *
from src.game import Game
from src.settings import Settings
#import cProfile

logging.getLogger().setLevel('DEBUG')
file_root = os.getcwd()

if __name__ == '__main__':
    initVals = {
                #'size': (1920, 1080),
                #'size': (1024, 768),
                #'size': (640, 480),
                'mode': pygame.FULLSCREEN,
                 'resourcePath': file_root + '/res/'
             }
    ## Defaults for config file
    initVals['defaults'] = {Settings.default_section:
                    {'Home' : file_root,
                    'Graveyard' : './_graveyard',
                    'Logging' : 'True',
                    'Logfile' : 'actions.log',
                    'Ext' : '.avi .mpg .mkv .mp4'
                    }
                }
    game = Game( **initVals )