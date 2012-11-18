'''
Created on Nov 12, 2012

@author: Grud
'''

import pygame
import tilemap

class Actor(pygame.sprite.Sprite):
    '''
    classdocs
    '''
    

    def __init__(self):
        '''
        Constructor
        '''
        super(Actor, self).__init__()
        

class Zombie(Actor):
    def __init(self):
        super(Zombie, self).__init__()
        self.speed = (0,0)
        self.image = pygame.image.load('ball.gif')
        self.rect = self.image.get_rect()
