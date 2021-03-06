'''
Created on Nov 12, 2012

@author: Grud
'''

import random
import math
import pygame
from pygame.locals import *

from game import *
from tilemap import *
from util import *
from constants import *

class Attack(object):
    range = ACTORSIZE
    damage = 1.0
    delay = 120
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
            self.owner.addHighlight(GREEN, self.range, int(self.damage))
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
    delay = 90

class Incubate(Attack):
    range = 0
    damage = 0
    delay = 300
    countdown = delay

    def attack(self, target):
        if self.ready() and self.canHit(target):
            target.die()
            target.level.mobs.add(Zombie(target.level, target.loc))

class Infection(Attack):
    range = 0
    damage = 0.5
    delay = 50
    special = Incubate
    condition = ON_DEATH
    
    def onKill(self, target):
        target.addEffect(Incubate())

class Bite(Attack):
    range = ACTORSIZE
    damage = 1.5
    delay = 120
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
        if random.random()>actor.consistency:
            impulse = Loc().addVector(actor.direction-math.pi/2+random.random()*math.pi, random.random()*.1)
            actor.addImpulse(impulse)
    
class StrategyChase(Strategy):
    @classmethod
    def think(cls, actor):
        if actor.target:
            if actor.loc.distanceTo(actor.target.loc)>ACTORSIZE/2:
                impulse = Loc().addVector(actor.loc.directionTo(actor.target.loc), actor.riled/MAX_RILED)
                actor.addImpulse(impulse)

class StrategyAttackNearestZombie(Strategy):
    @classmethod
    def think(cls, actor):
        for weapon in actor.weapons:
            if weapon.ready():
                visibleMobs = actor.level.getVisibleMobs([actor], actor.level.enemies.sprites(), True)
                zombieDistance = 1e+10
                nearestZombie = None
                for mob in visibleMobs:
                    if  isinstance(mob, Zombie):
                        if actor.loc.distanceTo(mob.loc)<zombieDistance:
                            nearestZombie = mob
                            zombieDistance = actor.loc.distanceTo(mob.loc)
                if nearestZombie:
                    weapon.attack(nearestZombie)
        
class StrategyHuddle(Strategy):
    @classmethod
    def think(cls, actor):
        #if isinstance(actor, (Soldier, Civilian)):
        if (actor.level.friendlies in actor.groups()) or (actor.level.neutrals in actor.groups()): 
            friendlies = actor.level.getVisibleMobs([actor], actor.level.friendlies.sprites() + actor.level.neutrals.sprites())
        #elif isinstance(actor, Zombie):
        elif (actor.level.enemies in actor.groups()):
            friendlies = actor.level.getVisibleMobs([actor], actor.level.enemies.sprites())
        else:
            return
        friendlies = list(set(friendlies) - set((actor,)))
        crowdFactor = math.sqrt(len(friendlies)) * actor.senseRadius
        impulse = Loc()
        for mob in friendlies:
            distance = actor.loc.distanceTo(mob.loc)
            direction = actor.loc.directionTo(mob.loc)
            away = direction + math.pi
            if distance<ACTORSIZE:
                impulse = impulse.addVector(away, ACTORSIZE/max(distance, 1))
            impulse = impulse.addVector(direction, (distance*mob.bravery)/(crowdFactor*actor.bravery))
        actor.addImpulse(impulse)
        
class StrategyFlee(Strategy):
    @classmethod
    def think(cls, actor):
        if (actor.level.friendlies in actor.groups()) or (actor.level.neutrals in actor.groups()): 
            enemies = actor.level.getVisibleMobs([actor], actor.level.enemies)
        elif (actor.level.enemies in actor.groups()):
            enemies = actor.level.getVisibleMobs([actor], actor.level.friendlies.sprites() + actor.level.neutrals.sprites())
        else:
            return
        impulse = Loc()
        actor.fleeing = False
        for mob in enemies:
            distance = actor.loc.distanceTo(mob.loc)
            if distance<actor.senseRadius/actor.bravery:
                impulse = impulse.addVector(actor.loc.directionTo(mob.loc)+math.pi, actor.senseRadius/actor.bravery/max(actor.loc.distanceTo(mob.loc)/2, 1))
                actor.fleeing = True
        actor.addImpulse(impulse)

class StrategyAvoidWalls(Strategy):
    @classmethod
    def think(cls, actor):
        impulse = Loc()
        x, y = actor.loc.loc
        xi = x % BLOCKSIZE
        yi = y % BLOCKSIZE
        bs = BLOCKSIZE
        if not actor.canTraverse((x-BLOCKSIZE, y-BLOCKSIZE)):
            impulse = impulse.addVector(math.pi*1.5, (bs-yi) * WALL_PHOBIA/2)
            impulse = impulse.addVector(math.pi*0, (bs-xi) * WALL_PHOBIA/2)
        if not actor.canTraverse((x, y-BLOCKSIZE)):
            impulse = impulse.addVector(math.pi*1.5, (bs-yi) * WALL_PHOBIA)
        if not actor.canTraverse((x+BLOCKSIZE, y-BLOCKSIZE)):
            impulse = impulse.addVector(math.pi*1.5, (bs-yi) * WALL_PHOBIA/2)
            impulse = impulse.addVector(math.pi*1, xi * WALL_PHOBIA/2)
        if not actor.canTraverse((x+BLOCKSIZE, y)):
            impulse = impulse.addVector(math.pi*1, xi * WALL_PHOBIA)
        if not actor.canTraverse((x-BLOCKSIZE, y+BLOCKSIZE)):
            impulse = impulse.addVector(math.pi*.5, yi * WALL_PHOBIA/2)
            impulse = impulse.addVector(math.pi*0, (bs-xi) * WALL_PHOBIA/2)
        if not actor.canTraverse((x, y+BLOCKSIZE)):
            impulse = impulse.addVector(math.pi*.5, yi * WALL_PHOBIA)
        if not actor.canTraverse((x+BLOCKSIZE, y+BLOCKSIZE)):
            impulse = impulse.addVector(math.pi*1, xi * WALL_PHOBIA/2)
            impulse = impulse.addVector(math.pi*.5, yi * WALL_PHOBIA/2)
        if not actor.canTraverse((x-BLOCKSIZE, y)):
            impulse = impulse.addVector(math.pi*0, (bs-xi) * WALL_PHOBIA)
        if impulse != Loc():
            actor.addImpulse(impulse)

class StrategyCivilian(Strategy):
    @classmethod
    def think(cls, actor):
        StrategyAttackNearestZombie.think(actor)
        StrategyHuddle.think(actor)
        StrategyFlee.think(actor)
        StrategyAvoidWalls.think(actor)
        if not actor.fleeing:
            StrategyRandom.think(actor)

class StrategyMoveToTarget(Strategy):
    @classmethod
    def think(cls, actor):
        if actor.targetLoc:
            path = actor.level.game.path
            target = path.nextPoint(actor.loc.loc)
            if target:
                x, y = target
                target = Loc((x, y))
            else:
                target = actor.targetLoc
            impulse = target-actor.loc
            impulse = impulse * actor.obedience / actor.loc.distanceTo(target) # Normalize impulse
            actor.addImpulse(impulse)
    
class StrategySoldier(Strategy):
    @classmethod
    def think(cls, actor):
        StrategyMoveToTarget.think(actor)
        StrategyAttackNearestZombie.think(actor)
        StrategyHuddle.think(actor)
        StrategyFlee.think(actor)
        StrategyAvoidWalls.think(actor)

class StrategyZombie(Strategy):
    @classmethod
    def think(cls, actor):
        actor.updateTargetDistance()
        visibleMobs = actor.level.getVisibleMobs([actor], actor.level.friendlies.sprites() + actor.level.neutrals.sprites())
        visibleTargets = 0
        for mob in visibleMobs:
            if actor.loc.distanceTo(mob.loc)<actor.targetDistance*.66:
                actor.setTarget(mob)
            visibleTargets += 1
        visibleZombies = actor.level.getVisibleMobs([actor], actor.level.enemies)
        impulse = Loc()
        if visibleTargets:
            actor.rile()
        else:
            actor.target = None
        for mob in visibleZombies:
            if mob is not actor:
                actor.rile(mob.riled)
                distance = actor.loc.distanceTo(mob.loc)
                direction = actor.loc.directionTo(mob.loc)
                away = direction+math.pi
                if distance<ACTORSIZE*2:
                    impulse = impulse.addVector(away, ACTORSIZE/max(distance, 1)**2)
                if not visibleTargets:
                    if mob.riled:
                        impulse = impulse.addVector(actor.loc.directionTo(mob.loc), actor.maxSpeed*.1*actor.riled/MAX_RILED)
                        impulse = impulse.addVector(mob.direction, actor.maxSpeed*.1*actor.riled/MAX_RILED)
                        if actor.level.game.debugMode:
                            actor.addHighlight(GRAY1)
        if impulse.loc != (0, 0):
            actor.addImpulse(impulse)
        if actor.target:
            for weapon in actor.weapons:
                weapon.attack(actor.target)
            StrategyChase.think(actor)
        if not actor.riled:
            StrategyRandom.think(actor)
            if actor.speed>actor.maxSpeed/5:
                actor.speed *= .98

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
    strategy = None
    target = None
    fear = None
    health = 10
    killable = True
    range = 64
    damage = 3
    delay = 60
    startingWeapons = None
    target = None
    targetLoc = None
    targetDistance = 1e+15
    thinkInterval = 10
    thinkCount = 0
    highlight = []
    distanceMoved = 0
    riled = 0
    fleeing = False
    bravery = 1.0
    obedience = 1.0
    leavesCorpse = 'Corpse'
    
    def __init__(self, level = None, loc = None):
        super(Actor, self).__init__()
        self.blendmode = BLEND_MIN
        self.setMap(level)
        self.loc = self.lastLoc = loc
        self.speed = 0.0
        self.direction = 0.0
        self.weapons = []
        self.effects = []
        if self.leavesCorpse:
            self.leavesCorpse = globals()[self.leavesCorpse]
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
        if self.leavesCorpse:
            body = self.leavesCorpse(self.level, self.loc)
            for effect in self.effects:
                if effect.condition == ON_DEATH:
                    effect.onKill(body)
        self.kill()
        
    def damage(self, weapon):
        if self.killable:
            self.addHighlight(RED, ACTORSIZE*.8, max(int(weapon.damage*2), 1))
            self.health -= weapon.damage
            if self.health<=0:
                logging.debug('A %s died of %s' % (self.__class__.__name__, weapon.__class__.__name__))
                self.die()
    
    def setMap(self, level):
        self.level = level
        if level:
            level.addMob(self)

    def moveTo(self, loc):
        if self.level.canMoveTo(self, loc):
            self.distanceMoved = self.loc.distanceTo(loc)
            self.loc = loc
            return True
        return False
    
    def move(self, direction, speed):
        self.lastLoc = self.loc
        if self.moveTo(self.loc.addVector(direction, speed)):
            return True
        quadrant = int((direction / (2*math.pi)) * 4)
        nextDir = quadrant*2*math.pi/4
        if self.moveTo(self.loc.addVector(nextDir, speed)):
            self.direction = nextDir + random.random()*(nextDir-self.direction)
            return True
        quadrant += 1
        nextDir = quadrant*2*math.pi/4
        if self.moveTo(self.loc.addVector(quadrant*2*math.pi/4, speed)):
            self.direction = nextDir + random.random()*(nextDir-self.direction)
            return True
    
    def updateTargetDistance(self):
        if self.target:
            self.targetDistance = self.loc.distanceTo(self.target.loc)
        else:
            self.targetDistance = 1e+15

    def setTarget(self, target):
        self.target = target
        self.updateTargetDistance()
    
    def tick(self):
        if self.thinkCount:
            self.thinkCount -= 1
            return False
        return True

    def rile(self, r=MAX_RILED+RILE_FACTOR):
        if r>self.riled+RILE_FACTOR:
            self.riled = self.maxRiled

    def calm(self):
        self.riled = max(self.riled-DEC_RILED, 0)
            
    def update(self):
        self.updateTargetDistance()
        if not self.target:
            self.calm()
        self.maxRiled = min(self.riled+INC_RILED, MAX_RILED)
        if self.strategy:
            self.strategy.think(self)
        self.move(self.direction, self.speed)
        for weapon in self.weapons:
            weapon.tick()
        for effect in self.effects:
            if effect.ready():
                effect.attack(self)
            effect.tick()
        if self.riled:
            if self.level.game.debugMode:
                self.addHighlight(WHITE, self.riled*ACTORSIZE*.25/MAX_RILED, 0)
        
    def canTraverse(self, loc):
        if isinstance(self, Beacon):
            return True
        if self.level.getTile(self.level.tileByPos(loc)) == TILE_WALL:
            return False
        return True
    
    def addHighlight(self, color = GRAY, radius = None, width = 1):
        if radius == None:
            radius = self.senseRadius
        if radius:
            self.highlight.append((color, radius, width))
    
    def addImpulse(self, impulse):
        impulse = impulse.addVector(self.direction, self.speed)
        self.direction, self.speed = Loc().getVector(impulse)
        self.speed = min(self.speed, self.maxSpeed)

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
    bravery = 2.5
    obedience = 2.5

class Civilian(Actor):
    appearance = CIVILIAN
    maxSpeed = BASE_SPEED * CIVILIAN_SPEED
    strategy = StrategyCivilian
    startingWeapons = [Punch]

class Corpse(Actor):
    appearance = CORPSE
    maxSpeed = 0
    killable = False
    leavesCorpse = None
    
class Beacon(Actor):
    maxSpeed = 0
    killable = False
    leavesCorpse = None