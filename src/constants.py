'''
Created on Nov 23, 2012

@author: Grud
'''

## Map constants
BLOCKSIZE = 256
ACTORSIZE = 128
TILE_OPEN = 0
TILE_WALL = 1

## Actor constants
# Appearances
ACTOR = 0
ZOMBIE = 1
SOLDIER = 2
CIVILIAN = 3
CORPSE = 0
# Abilities & Behaviour
SENSE_RADIUS = BLOCKSIZE*6
BASE_SPEED = 4.0
ZOMBIE_SPEED = 1.0
SOLDIER_SPEED = 1.0
CIVILIAN_SPEED = 0.9
WALL_PHOBIA = 1.0/16
# Attack constnats
ON_HIT = 1
ON_DEATH = 2

## Game constants
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ZOOMFACTOR = 1.2
SCROLLSPEED = 1.5

