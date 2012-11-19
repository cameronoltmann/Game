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
from actors import *


BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ZOOMFACTOR = 1.2


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
            tile_rect = pygame.rect.Rect(self.mapPortRect[0]+mapTile[0]*self.level.tileSize,
                         self.mapPortRect[1]+mapTile[1]*self.level.tileSize,
                         self.level.tileSize,
                         self.level.tileSize)
            pygame.draw.rect(self.screen, cursor_color, tile_rect, max((self.level.tileSize/16,1)))
        #self.balls.update()
        #self.balls.draw(self.screen)
        pygame.display.flip()

    def mapTileByPos(self, pos):
        '''
        Return map tile corresponding to screen coordinates
        '''
        mapPos = (pos[0]-self.mapPortRect[0], pos[1]-self.mapPortRect[1])
        return self.level.tileByViewportPos(mapPos)
        
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
                    if mapTile:
                        if event.button == 4: # wheel up
                            self.mapViewScale = self.level.setScale(self.mapViewScale*ZOOMFACTOR)
                            self.level.render(self.mapPort, self.mapViewCentre, self.mapViewScale)
                        elif event.button == 5: # wheel down
                            self.mapViewScale = self.level.setScale(self.mapViewScale/ZOOMFACTOR)
                            self.level.render(self.mapPort, self.mapViewCentre, self.mapViewScale)
                        if self.editMode and event.button==1:
                            if self.level.get_tile(mapTile) == self.level.fill:
                                self.drawing = self.level.wall+100
                            else:
                                self.drawing = self.level.fill+100
                            self.level.setTile(mapTile, self.drawing-100)
                            self.level.renderTile(self.mapPort, mapTile, self.mapViewCentre)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouseState[event.button] = False
                    if mapTile and event.button==1:
                        self.drawing = False
                elif event.type == pygame.MOUSEMOTION:
                    if mapTile and self.drawing:
                        self.level.setTile(mapTile, self.drawing-100)
                        self.level.renderTile(self.mapPort, mapTile, self.mapViewCentre)
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
            self.level = tilemap.Map()
            self.level.filename = 'map.p'
            self.level.loadTiles(['tile0.jpg', 'tile1.jpg'])
        self.mapPortRect = self.level.fit(self.width, self.height)
        mapSize = mapWidth, mapHeight = self.level.getSize()
        self.mapViewScale = (1.0*self.mapPortRect[2]/mapWidth)
        self.level.setScale(self.mapViewScale)
        self.mapViewCentre = (mapWidth/2, mapHeight/2)
        logging.info("Scale: %s" % self.mapViewScale)
        self.mapPort = self.background.subsurface(self.mapPortRect)
        self.level.render(self.mapPort, self.mapViewCentre, self.mapViewScale)
        self.framecount=0
        self.startTime=time.time()
        self.editMode = False
        self.systemFont = pygame.font.SysFont("None", 16)
        self.drawing = False
        self.done = False
        self.gameLoop()
        