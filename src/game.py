'''
Created on Nov 11, 2012

@author: Cameron Oltmann
'''

import sys
import random
import logging
import time
import pygame
from pygame.locals import *

from util import *
from actor import *
from constants import *
from tilemap import *


class Game(object):
    resourcePath = 'res/'
    
    def __init__(self, **kwargs):
        pygame.init()
        self.size = pygame.display.list_modes()[0]
        self.mode = 0
        self.resourcePath = 'res/'
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.width, self.height = self.size
        self.screen = pygame.display.set_mode(self.size, self.mode)
        self.clock = pygame.time.Clock()
        Game.resourcePath = self.resourcePath
        Actor.setInit(**{'resourcePath': Game.resourcePath})
        # Initialize input state
        self.keyState={}
        self.mouseState={}
        self.setup()

    def quit(self):
        self.level.save()


    def render(self):
        mapTile = self.mapTileByPos(pygame.mouse.get_pos())
        self.screen.blit(self.background, (0, 0))
        self.level.renderMobs(self.mapPortOverlay)
        if self.editMode:
            self.screen.blit(self.systemFont.render("Edit", 0, (255,0,0)), (0,0))
            cursor_color=RED
        else:
            cursor_color=GREEN
        if mapTile:
            tileULC = scaleCoords(mapTile, BLOCKSIZE)
            screenULC = self.level.transformToScreenspace(self.mapPort, tileULC)
            tile_rect = pygame.rect.Rect(screenULC[0],
                         screenULC[1],
                         self.level.tileSize,
                         self.level.tileSize)
            pygame.draw.rect(self.mapPortOverlay, cursor_color, tile_rect, max((self.level.tileSize/8,2)))
        #self.balls.update()
        #self.balls.draw(self.screen)
        pygame.display.flip()

    def mapTileByPos(self, pos):
        '''
        Return map tile corresponding to screen coordinates
        '''
        if self.mapPortRect.collidepoint(pos):
            pos = (pos[0]-self.mapPortRect[0], pos[1]-self.mapPortRect[1])
            mapPos = self.level.transformToMapspace(self.mapPort, pos)
            return self.level.tileByPos(mapPos)
        
    def gameLoop(self):
        while not self.done:
            self.clock.tick(60)
        
            for event in pygame.event.get():
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    self.mouseState['pos'] = event.pos
                    mapTile = self.mapTileByPos(event.pos)
                if event.type == pygame.QUIT:
                    self.done = True
                elif event.type == pygame.KEYDOWN:
                    self.keyState[event.key]=True
                    if event.key == pygame.K_BACKQUOTE:
                        self.editMode = not self.editMode
                    elif event.key ==pygame.K_ESCAPE:
                        self.done = True
                elif event.type == pygame.KEYUP:
                    self.keyState[event.key] = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouseState[event.button] = True
                    if self.mapPortRect.collidepoint(event.pos):
                        if event.button == 4: # wheel up
                            self.mapViewScale = self.level.setScale(self.mapViewScale*ZOOMFACTOR)
                            self.level.render(self.mapPort)
                        elif event.button == 5: # wheel down
                            self.mapViewScale = self.level.setScale(self.mapViewScale/ZOOMFACTOR)
                            self.level.render(self.mapPort)
                    if mapTile:
                        if self.editMode and event.button==1:
                            if self.level.getTile(mapTile) == TILE_OPEN:
                                self.drawing = TILE_WALL+100
                            else:
                                self.drawing = TILE_OPEN+100
                            self.level.setTile(mapTile, self.drawing-100)
                            self.level.renderTile(self.mapPort, mapTile)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouseState[event.button] = False
                    if mapTile and event.button==1:
                        self.drawing = False
                elif event.type == pygame.MOUSEMOTION:
                    if mapTile and self.drawing:
                        self.level.setTile(mapTile, self.drawing-100)
                        self.level.renderTile(self.mapPort, mapTile)
            xMove = yMove = 0
            if self.keyState.get(pygame.K_LEFT):
                xMove -= SCROLLSPEED/self.mapViewScale
            if self.keyState.get(pygame.K_UP):
                yMove -= SCROLLSPEED/self.mapViewScale
            if self.keyState.get(pygame.K_RIGHT):
                xMove += SCROLLSPEED/self.mapViewScale
            if self.keyState.get(pygame.K_DOWN):
                yMove += SCROLLSPEED/self.mapViewScale
            if xMove or yMove:
                self.mapViewpoint = self.level.setViewpoint(addCoords(self.mapViewpoint, (xMove, yMove)))
                self.level.render(self.mapPort)
            if not self.editMode:
                self.level.mobs.update()
                self.level.setVisible(self.level.getVisibleMobs(self.level.friendlies))
            else:
                self.level.setVisible(self.level.mobs)
            self.render()
            self.framecount += 1
            curTime = time.time()
            elapsed = curTime-self.startTime
            if elapsed>=1:
                logging.debug("FPS: %f" % (self.framecount/elapsed))
                self.startTime=curTime
                self.framecount=0
        # Exit game
        self.quit()

    def setup(self):
        #self.balls = pygame.sprite.RenderPlain([Ball() for i in range(100)])
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(BLACK)
        logging.debug('Resource path: %s' % self.resourcePath)
        Map.resourcePath = self.resourcePath
        try:
            self.level = Map.load('map.p')
            logging.debug(self.level)
        except IOError:
            logging.debug('Generating map')
            self.level = Map((20, 20))
            self.level.filename = 'map.p'
            self.level.loadTiles(['tile0.png', 'tile1.png'])
            self.level.loadActors(['blip.png', 'zombie.png', 'soldier.png', 'civilian.png'])
            logging.debug('generating mobs')
            validMin, validMax = (BLOCKSIZE+ACTORSIZE, self.level.width*BLOCKSIZE-(BLOCKSIZE+ACTORSIZE))
            validRange = validMax - validMin  
            self.level.mobs = pygame.sprite.Group([Civilian(self.level, Loc(random.random()*validRange + validMin, random.random()*validRange + validMin)) for i in range(5)])
            self.level.mobs.add([Soldier(self.level, Loc(random.random()*validRange + validMin, random.random()*validRange + validMin)) for i in range(5, 10)])
            self.level.mobs.add([Zombie(self.level, Loc(random.random()*validRange + validMin, random.random()*validRange + validMin)) for i in range(10, 20)])
            self.level.enemies = pygame.sprite.Group([mob for mob in self.level.mobs if isinstance(mob, Zombie)])
            self.level.friendlies = pygame.sprite.Group([mob for mob in self.level.mobs if isinstance(mob, Soldier)])
            self.level.neutrals = pygame.sprite.Group([mob for mob in self.level.mobs if isinstance(mob, Civilian)])
            logging.debug('%s %s %s %s' % (len(self.level.mobs), len(self.level.enemies), len(self.level.friendlies), len(self.level.neutrals)))
        self.mapPortRect = self.level.fitTo(self.width, self.height)
        mapSize = mapWidth, mapHeight = self.level.getSize()
        self.mapViewScale = (1.0*self.mapPortRect[2]/mapWidth)
        logging.debug('Setting map scale')
        self.level.setScale(self.mapViewScale)
        self.mapViewpoint = self.level.getViewpoint()
        logging.debug("Scale: %s" % self.mapViewScale)
        self.mapPort = self.background.subsurface(self.mapPortRect)
        self.mapPortOverlay = self.screen.subsurface(self.mapPortRect)
        self.level.render(self.mapPort)
        self.framecount=0
        self.startTime=time.time()
        self.editMode = False
        self.systemFont = pygame.font.SysFont("None", 16)
        self.drawing = False
        self.done = False
        self.gameLoop()
        