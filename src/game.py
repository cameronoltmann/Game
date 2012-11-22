'''
Created on Nov 11, 2012

@author: Cameron Oltmann
'''

import sys
import pygame
import random
import logging
import time
import tilemap
import util
from actors import *


BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ZOOMFACTOR = 1.2
SCROLLSPEED = 1.5

class Game():
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
        if self.editMode:
            self.screen.blit(self.systemFont.render("Edit", 0, (255,0,0)), (0,0))
            cursor_color=RED
        else:
            cursor_color=GREEN
        if mapTile:
            tileULC = util.scaleCoords(mapTile, tilemap.BLOCKSIZE)
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
                            if self.level.get_tile(mapTile) == tilemap.TILE_OPEN:
                                self.drawing = tilemap.TILE_WALL+100
                            else:
                                self.drawing = tilemap.TILE_OPEN+100
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
                self.mapViewpoint = self.level.setViewpoint(util.addCoords(self.mapViewpoint, (xMove, yMove)))
                self.level.render(self.mapPort)
            
            self.render()
            self.framecount += 1
            curTime = time.time()
            elapsed = curTime-self.startTime
            if elapsed>=1:
                logging.info("FPS: %f" % (self.framecount/elapsed))
                self.startTime=curTime
                self.framecount=0
        # Exit game
        self.quit()

    def setup(self):
        #self.balls = pygame.sprite.RenderPlain([Ball() for i in range(100)])
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(BLACK)
        logging.info('Resource path: %s' % self.resourcePath)
        tilemap.Map.resourcePath = self.resourcePath
        try:
            self.level = tilemap.Map.load('map.p')
            logging.info(self.level)
        except:
            self.level = tilemap.Map((50, 50), tilemap.TILE_WALL)
            self.level.filename = 'map.p'
            self.level.loadTiles(['tile0.jpg', 'tile1.jpg'])
            self.level.loadActors(['zombie.png', 'civilian.png', 'civilian.png'])
        self.mapPortRect = self.level.fitTo(self.width, self.height)
        mapSize = mapWidth, mapHeight = self.level.getSize()
        self.mapViewScale = (1.0*self.mapPortRect[2]/mapWidth)
        self.level.setScale(self.mapViewScale)
        self.mapViewpoint = self.level.getViewpoint()
        logging.info("Scale: %s" % self.mapViewScale)
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
        