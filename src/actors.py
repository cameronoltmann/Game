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

class Zombie(Actor):
    appearance = ZOMBIE
    maxSpeed = BASE_SPEED * ZOMBIE_SPEED
    
class Soldier(Actor):
    appearance = SOLDIER
    maxSpeed = BASE_SPEED * SOLDIER_SPEED
    
class Civilian(Actor):
    appearance = CIVILIAN
    maxSpeed = BASE_SPEED * CIVILIAN_SPEED
    