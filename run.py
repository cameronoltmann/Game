import logging
import pygame
import os
from src.game import Game
from src.settings import Settings

logging.getLogger().setLevel('DEBUG')
file_root = os.getcwd()

if __name__ == '__main__':
    initVals = {'size': (1024, 768),
                #'mode': pygame.FULLSCREEN,
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