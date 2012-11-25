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

class Strategy(object):
    def think(self, actor):
        pass

class StrategyRandom(Strategy):
    @classmethod
    def think(cls, actor):
        if random.random()>actor.consistency or actor.speed>actor.maxSpeed/2:
            actor.speed = random.random()*actor.maxSpeed/2
            actor.direction = random.random()*2*math.pi
    
class StrategyChase(Strategy):
    @classmethod
    def think(cls, actor):
        actor.speed = min(actor.maxSpeed, actor.loc.distanceTo(actor.target.loc))
        actor.direction = actor.loc.directionTo(actor.target.loc)
        
class StrategyFlee(Strategy):
    @classmethod
    def think(cls, actor):
        fearDirection = actor.loc.directionTo(actor.fear.loc)
        if actor.speed != actor.maxSpeed or random.random()>actor.consistency or abs(actor.direction-(fearDirection+math.pi))>math.pi/4:
            #actor.direction = fearDirection + math.pi 
            fleeDirection = fearDirection + math.pi
            actor.direction = (actor.direction+fleeDirection)/2
            #actor.direction = fearDirection + math.pi*.5 + random.random()*math.pi*.5 
        if actor.loc == actor.lastLoc:
            actor.direction = random.random()*2*math.pi
        actor.speed = actor.maxSpeed
        
class StrategyCivilian(Strategy):
    @classmethod
    def think(cls, actor):
        visibleMobs = actor.level.getVisibleMobs([actor])
        visibleZombies = 0
        closestZombie = 1e+15
        for mob in visibleMobs:
            #logging.debug('%s sees %s!' % (actor, mob))
            if mob.__class__ is Zombie:
                dist = actor.loc.distanceTo(mob.loc)
                if dist<closestZombie*.8:
                    closestZombie = dist
                    actor.fear = mob
                visibleZombies += 1
        if not visibleZombies:
            actor.fear = None
        if actor.fear:
            StrategyFlee.think(actor)
        else:
            StrategyRandom.think(actor)

class StrategyZombie(Strategy):
    @classmethod
    def think(cls, actor):
        visibleMobs = actor.level.getVisibleMobs([actor])
        visibleTargets = 0
        for mob in visibleMobs:
            #logging.debug('%s sees %s!' % (actor, mob))
            if mob.__class__ is not Zombie:
                if not actor.target:
                    actor.target = mob
                visibleTargets += 1
        if not visibleTargets:
            actor.target = None
        if actor.target:
            StrategyChase.think(actor)
        else:
            StrategyRandom.think(actor)

class Actor(pygame.sprite.DirtySprite):
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
    strategy = StrategyRandom
    target = None
    fear = None

    def __init__(self, level = None, loc = None):
        super(Actor, self).__init__()
        self.blendmode = BLEND_MIN
        self.level = level
        self.loc = self.lastLoc = loc
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
        self.lastLoc = self.loc
        if self.moveTo(self.loc.addVector(direction, speed)):
            return True
        quadrant = int((direction / (2*math.pi)) * 4)
        if self.moveTo(self.loc.addVector(quadrant*2*math.pi/4, speed)):
            return True
        quadrant += 1
        if self.moveTo(self.loc.addVector(quadrant*2*math.pi/4, speed)):
            return True
    
    def update(self):
        self.strategy.think(self)
        self.move(self.direction, self.speed)
        
    def canTraverse(self, loc):
        if self.level.getTile(self.level.tileByPos(loc)) == TILE_WALL:
            return False
        return True

class Zombie(Actor):
    appearance = ZOMBIE
    maxSpeed = BASE_SPEED * ZOMBIE_SPEED
    strategy = StrategyZombie
    senseRadius = Actor.senseRadius*0.7
    
class Soldier(Actor):
    appearance = SOLDIER
    maxSpeed = BASE_SPEED * SOLDIER_SPEED
    strategy = StrategyCivilian

class Civilian(Actor):
    appearance = CIVILIAN
    maxSpeed = BASE_SPEED * CIVILIAN_SPEED
    strategy = StrategyCivilian
    