'''
Created on Nov 12, 2012

@author: Grud
'''

import random
import math
import pygame
from pygame.locals import *

from tilemap import *
from util import *
from constants import *

class Actor(pygame.sprite.Sprite):
    '''
    classdocs
    '''
    # class defaults
    senseRadius = SENSE_RADIUS
    resourcePath = 'res/'
    appearance = ACTOR
    maxSpeed = BASE_SPEED
    # behaviour
    consistency = 0.99
    strategy = STRATEGY_RANDOM

    def __init__(self, level = None, loc = None):
        super(Actor, self).__init__()
        self.level = level
        self.loc = loc
        self.speed = 0.0
        self.direction = 0.0

    @classmethod
    def setInit(cls, **kwargs):
        for key, arg in kwargs.items():
            setattr(cls, key, arg)

    @classmethod
    def addInit(cls, vals):
        for k, v in vals.items():
            cls.initVals[k] = v

    def setMap(self, level):
        self.level = level

    def moveTo(self, loc):
        if self.level.canMoveTo(self, loc):
            self.loc = loc
            return True
        return False
    
    def move(self, direction, speed):
        return self.moveTo(self.loc.addVector(direction, speed))
    
    def update(self):
        if self.strategy == STRATEGY_RANDOM:
            if random.random()>self.consistency:
                self.speed = random.random()*self.maxSpeed
                self.direction = random.random()*2*math.pi
        self.move(self.direction, self.speed)
        
    def canTraverse(self, loc):
        return True

class Ball(Actor):
    '''
    Scrub this once the first real actors are implemented
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
    appearance = ZOMBIE
    maxSpeed = BASE_SPEED * ZOMBIE_SPEED
    
class Soldier(Actor):
    appearance = SOLDIER
    maxSpeed = BASE_SPEED * SOLDIER_SPEED
    
class Civilian(Actor):
    appearance = CIVILIAN
    maxSpeed = BASE_SPEED * CIVILIAN_SPEED
    