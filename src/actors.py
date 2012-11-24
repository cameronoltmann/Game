'''
Created on Nov 12, 2012

@author: Grud
'''

import pygame
import tilemap
import random
import util

SENSE_RADIUS = 100
A_BASE = 0
A_ZOMBIE = 1
A_SOLDIER = 2
A_CIVILIAN = 3



class Actor(pygame.sprite.Sprite):
    '''
    classdocs
    '''
    first = True # set this false when first instance of an object is created
    initVals = {'sense_radius': SENSE_RADIUS,
                 'resourcePath': 'res/',
                 'image': A_BASE 
                 } 

    def __init__(self):
        '''
        inherit default settings from parent class - copy initVals when initializing first instance of class
        '''
        first = not self.__class__.hasattr(self.__class__.__name__)
        super(self.__class__, self).__init__()
        if first:
            self.__class__.setInit()

    @classmethod
    def setInit(cls, **kwargs):
        if not hasattr(super(cls), super):
            parent.setInit(super(parent, parent))
        cls.initVals = parent.initVals.copy()
        for key, arg in cls.initVals:
            setattr(cls, key, arg)
        for key, arg in kwargs:
            setattr(cls, key, arg)

    @classmethod
    def addInit(cls, vals):
        for k, v in vals.items():
            cls.initVals[k] = v

    def setMap(self, level):
        self.level = level

    def setLoc(self, loc):
        if self.level.canMoveTo(self, loc):
            self.loc = loc
            return True
        return False
    
    def move(self, step):
        return self.setLoc()
    
    def canTraverse(self, loc):
        return True

class Ball(Actor):
    '''
    Scrub this once the first actors are implemented
    '''
    def __init__(self):
        first = not self.__class__.hasattr('initVals')
        super(self.__class__, self).__init__()
        if first:
            self.__class__.setInit(super(self.__class__))
        self.speed = [random.randrange(4), random.randrange(4)]
        self.image = pygame.image.load(self.resourcePath+'ball.gif')
        self.rect = self.image.get_rect()

    def update(self):
        self.rect = self.rect.move(self.speed)
        _, _, width, height = pygame.display.get_surface().get_rect()
        
        if self.rect.left < 0 or self.rect.right > width:
            self.speed[0] = -self.speed[0]
        if self.rect.top <0 or self.rect.bottom > height:
            self.speed[1] = -self.speed[1]

class Zombie(Actor):
    def __init(self):
        first = not self.__class__.hasattr('initVals')
        super(self.__class__, self).__init__()
        if first:
            self.__class__.setInit(super(self.__class__))
            self.addInit({
                          'image': A_ZOMBIE
                          })

