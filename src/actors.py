'''
Created on Nov 12, 2012

@author: Grud
'''

import pygame
import tilemap
import random

class Actor(pygame.sprite.Sprite):
    '''
    classdocs
    '''
    init_vals = {'sense_radius': 100,
                 'resource_path': 'res/'

                 } 

    def __init__(self):
        super(Actor, self).__init__()
        self.__class__.setInit(**self.__class__.init_vals)

    @classmethod
    def setInit(cls, **kwargs):
        for arg in kwargs:
            setattr(cls, arg, kwargs[arg])

class Zombie(Actor):
    def __init(self):
        super(Zombie, self).__init__()
        self.speed = (0,0)
        self.image = pygame.image.load('ball.gif')
        self.rect = self.image.get_rect()

class Ball(Actor):
    def __init__(self):
        super(Ball, self).__init__()
        self.speed = [random.randrange(4), random.randrange(4)]
        self.image = pygame.image.load(self.resource_path+'ball.gif')
        self.rect = self.image.get_rect()

    def update(self):
        self.rect = self.rect.move(self.speed)
        _, _, width, height = pygame.display.get_surface().get_rect()
        
        if self.rect.left < 0 or self.rect.right > width:
            self.speed[0] = -self.speed[0]
        if self.rect.top <0 or self.rect.bottom > height:
            self.speed[1] = -self.speed[1]

