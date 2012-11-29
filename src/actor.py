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

class Attack(object):
    range = ACTORSIZE
    damage = 1.0
    delay = 60
    countdown = 0
    special = None
    condition = None
    
    def __init__(self, owner=None):
        self.owner = owner
    
    def setOwner(self, owner):
        self.owner = owner

    def canHit(self, target):
        return self.owner.loc.distanceTo(target.loc) <= self.range
    
    def attack(self, target):
        if self.ready() and self.canHit(target):
            target.damage(self)
            self.onHit(target)
            self.countdown = self.delay

    def onHit(self, target):
        if self.special and self.condition == ON_HIT:
            target.addEffect(self.special())
    
    def onKill(self, target):
        pass
            
    def proc(self, target):
        if self.ready():
            target.damage(self)
        
    def tick(self):
        if self.countdown:
            self.countdown -= 1
    
    def ready(self):
        return self.countdown==0

class Rifle(Attack):
    range = BLOCKSIZE * 3
    damage = 3.0
    delay = 45

class Incubate(Attack):
    range = 0
    damage = 0
    delay = 120
    countdown = delay

    def attack(self, target):
        if self.ready() and self.canHit(target):
            target.die()
            target.level.mobs.add(Zombie(target.level, target.loc))

class Infection(Attack):
    range = 0
    damage = 0.1
    delay = 10
    special = Incubate
    condition = ON_DEATH
    
    def onKill(self, target):
        body = Corpse(target.level, target.loc)
        body.addEffect(Incubate())
        target.level.mobs.add(body)

class Bite(Attack):
    range = ACTORSIZE
    damage = 1.5
    delay = 60
    special = Infection
    condition = ON_HIT
    
class Punch(Attack):
    range = ACTORSIZE
    
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

class StrategyAttackNearestZombie(Strategy):
    @classmethod
    def think(cls, actor):
        for weapon in actor.weapons:
            if weapon.ready():
                visibleMobs = actor.level.getVisibleMobs([actor])
                zombieDistance = 1e+10
                nearestZombie = None
                for mob in visibleMobs:
                    if  isinstance(mob, Zombie):
                        if actor.loc.distanceTo(mob.loc)<zombieDistance:
                            nearestZombie = mob
                            zombieDistance = actor.loc.distanceTo(mob.loc)
                if nearestZombie:
                    weapon.attack(nearestZombie)
        
class StrategyFleeZombies(Strategy):
    @classmethod
    def think(cls, actor):
        visibleMobs = actor.level.getVisibleMobs([actor])
        visibleZombies = 0
        impulse = Loc(0, 0)
        for mob in visibleMobs:
            if isinstance(mob, Zombie):
                impulse = impulse.addVector(actor.loc.directionTo(mob.loc)+math.pi, actor.senseRadius/max(actor.loc.distanceTo(mob.loc), 1))
            elif mob != actor:
                if actor.loc.distanceTo(mob.loc)<ACTORSIZE:
                    impulse = impulse.addVector(actor.loc.directionTo(mob.loc)+math.pi, ACTORSIZE/max(actor.loc.distanceTo(mob.loc), 1))
                impulse = impulse.addVector(actor.loc.directionTo(mob.loc), actor.loc.distanceTo(mob.loc)/actor.senseRadius)
        x, y = actor.loc.loc
        if not actor.canTraverse((x, y-BLOCKSIZE)):
            impulse = impulse.addVector(math.pi*1.5, (BLOCKSIZE - y % BLOCKSIZE) * WALL_PHOBIA)
        if not actor.canTraverse((x+BLOCKSIZE, y)):
            impulse = impulse.addVector(math.pi*1, (x % BLOCKSIZE)* WALL_PHOBIA)
        if not actor.canTraverse((x, y+BLOCKSIZE)):
            impulse = impulse.addVector(math.pi*.5, (y % BLOCKSIZE) * WALL_PHOBIA)
        if not actor.canTraverse((x-BLOCKSIZE, y)):
            impulse = impulse.addVector(0, (BLOCKSIZE - x % BLOCKSIZE) * WALL_PHOBIA)
        impulseVector = Loc(0, 0).getVector(impulse)
        impulseVector[1] = min(impulseVector[1], actor.maxSpeed)
        actor.direction, actor.speed = impulseVector

class StrategyCivilian(Strategy):
    @classmethod
    def think(cls, actor):
        StrategyAttackNearestZombie.think(actor)
        StrategyFleeZombies.think(actor)
        if actor.speed == 0.0:
            StrategyRandom.think(actor)

class StrategySoldier(Strategy):
    @classmethod
    def think(cls, actor):
        StrategyAttackNearestZombie.think(actor)
        StrategyFleeZombies.think(actor)

class StrategyZombie(Strategy):
    @classmethod
    def think(cls, actor):
        visibleMobs = actor.level.getVisibleMobs([actor])
        visibleTargets = 0
        for mob in visibleMobs:
            #logging.debug('%s sees %s!' % (actor, mob))
            if mob.__class__ not in (Zombie, Corpse):
                if not actor.target:
                    actor.target = mob
                visibleTargets += 1
        if not visibleTargets:
            actor.target = None
        if actor.target:
            for weapon in actor.weapons:
                weapon.attack(actor.target)
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
    health = 10
    killable = True
    range = 64
    damage = 3
    delay = 60
    startingWeapons = None
     
    def __init__(self, level = None, loc = None):
        super(Actor, self).__init__()
        self.blendmode = BLEND_MIN
        self.level = level
        self.loc = self.lastLoc = loc
        self.speed = 0.0
        self.direction = 0.0
        self.weapons = []
        self.effects = []
        if self.level:
            self.level.setActorImage(self)
        if self.startingWeapons:
            for weapon in self.startingWeapons:
                self.addWeapon(weapon())

    @classmethod
    def setInit(cls, **kwargs):
        for key, arg in kwargs.items():
            setattr(cls, key, arg)

    @classmethod
    def addInit(cls, vals):
        for k, v in vals.items():
            cls.initVals[k] = v

    def addWeapon(self, weapon):
        self.weapons.append(weapon)
        weapon.setOwner(self)

    def addEffect(self, effect):
        if effect.__class__ not in [e.__class__ for e in self.effects]:
            self.effects.append(effect)
            effect.setOwner(self)
        
    def die(self):
        for mob in self.level.mobs:
            if mob.target == self:
                mob.target = None
        for effect in self.effects:
            if effect.condition == ON_DEATH:
                effect.onKill(self)
        self.kill()
        
    def damage(self, weapon):
        if self.killable:
            self.health -= weapon.damage
            logging.debug('%s hit by %s\'s %s for %s damage!' % (self, weapon.owner, weapon, weapon.damage))
            if self.health<=0:
                self.die()
    
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
        if self.strategy:
            self.strategy.think(self)
        self.move(self.direction, self.speed)
        for weapon in self.weapons:
            weapon.tick()
        for effect in self.effects:
            if effect.ready():
                effect.attack(self)
            effect.tick()
        
    def canTraverse(self, loc):
        if self.level.getTile(self.level.tileByPos(loc)) == TILE_WALL:
            return False
        return True

class Zombie(Actor):
    appearance = ZOMBIE
    maxSpeed = BASE_SPEED * ZOMBIE_SPEED
    health = 20
    strategy = StrategyZombie
    senseRadius = Actor.senseRadius*0.7
    startingWeapons = [Bite]
    
class Soldier(Actor):
    appearance = SOLDIER
    maxSpeed = BASE_SPEED * SOLDIER_SPEED
    strategy = StrategySoldier
    startingWeapons = [Rifle, Punch]

class Civilian(Actor):
    appearance = CIVILIAN
    maxSpeed = BASE_SPEED * CIVILIAN_SPEED
    strategy = StrategyCivilian
    startingWeapons = [Punch]

class Corpse(Actor):
    appearance = CORPSE
    maxSpeed = 0
    killable = False
    strategy = None
    