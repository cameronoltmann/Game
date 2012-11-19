from src.game import Game
import logging
import pygame
import os

logging.getLogger().setLevel('DEBUG')
file_root = os.getcwd()

if __name__ == '__main__':
	init_vals = {'size': (1024, 768),
			 	#'mode': pygame.FULLSCREEN,
			 	'resource_path': file_root + '/res/'
			 }
	game = Game( **init_vals )