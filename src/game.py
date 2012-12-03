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
    fps = 0
    idlecount = 0
    play = True
    debugMode = False
    
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
        self.bannerFont = pygame.font.Font(self.resourcePath+'drip.ttf', 48)
        Game.resourcePath = self.resourcePath
        Actor.setInit(**{'resourcePath': Game.resourcePath})
        # Initialize input state
        self.keyState={}
        self.mouseState={}
        while self.play:
            self.setup()
            self.play = self.gameLoop()

    def quit(self):
        self.level.save()


    def render(self):
        mapTile = self.mapTileByPos(pygame.mouse.get_pos())
        self.screen.blit(self.background, (0, 0))
        self.level.renderMobs(self.mapPortOverlay)
        if Game.debugMode:
            self.screen.blit(self.systemFont.render('Debug', 1, RED), (5, 5))
        if self.editMode:
            self.screen.blit(self.systemFont.render('Edit', 1, RED), (5,20))
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
        # Display UI
        self.screen.blit(self.systemFont.render('FPS: %s' % round(self.fps, 1), 1, WHITE), (self.width-60, 5))
        self.screen.blit(self.systemFont.render('S: %s' % self.fc, 1, GREEN), (self.width-45, 20))
        self.screen.blit(self.systemFont.render('C: %s' % self.nc, 1, GRAY1), (self.width-45, 35))
        self.screen.blit(self.systemFont.render('Z: %s' % self.zc, 1, RED), (self.width-45, 50))
        # Display banner
        bannerTop = self.height/2
        if self.fc+self.nc == 0:
            bannerText = 'NO HUMANS SURVIVE'
            bannerColor = RED
            bannerSize = x, y = self.bannerFont.size(bannerText)
            self.screen.blit(self.bannerFont.render(bannerText, 1, bannerColor), ((self.width-x)/2, bannerTop))
            bannerTop += y+5
        if self.zc == 0:
            bannerText = 'NO ZOMBIES REMAIN'
            bannerColor = GREEN
            bannerSize = x, y = self.bannerFont.size(bannerText)
            self.screen.blit(self.bannerFont.render(bannerText, 1, bannerColor), ((self.width-x)/2, bannerTop))
            bannerTop += y+5
        pygame.display.flip()
        for mob in self.level.mobs:
            mob.highlight = []

    def mapTileByPos(self, pos):
        '''
        Return map tile corresponding to screen coordinates
        '''
        if self.mapPortRect.collidepoint(pos):
            pos = (pos[0]-self.mapPortRect[0], pos[1]-self.mapPortRect[1])
            mapPos = self.level.transformToMapspace(self.mapPort, pos)
            return self.level.tileByPos(mapPos)
        
    def gameLoop(self):
        replay = False
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
                    elif event.key == pygame.K_ESCAPE:
                        self.done = True
                    elif event.key == pygame.K_r:
                        replay = True
                        self.done = True
                    elif event.key == pygame.K_d:
                        Game.debugMode = not Game.debugMode
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
                #self.level.setVisible(self.level.getVisibleMobs(self.level.friendlies))
                self.level.setVisible(self.level.mobs)
            else:
                self.level.setVisible(self.level.mobs)
            self.fc = len(self.level.friendlies)
            self.nc = len(self.level.neutrals)
            self.zc = len(self.level.enemies)
            self.render()
            self.framecount += 1
            curTime = time.time()
            elapsed = curTime-self.startTime
            shortCount = curTime-self.frameTime
            if shortCount>=1:
                #logging.debug("FPS: %f" % (self.framecount/elapsed))
                self.fps = self.framecount/elapsed
                #self.startTime=curTime
                self.frameTime = curTime
            if (self.fc + self.nc == 0) or (self.zc == 0):
                self.idlecount += 1
            else:
                self.idlecount = 0
            if self.idlecount>IDLE_TIME:
                replay = True
                self.done = True
                
        # Exit game
        self.quit()
        return replay

    def setup(self):
        #self.balls = pygame.sprite.RenderPlain([Ball() for i in range(100)])
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(BLACK)
        logging.debug('Resource path: %s' % self.resourcePath)
        Map.resourcePath = self.resourcePath
        try:
            self.level = Map.load('nomap.p')
            #self.level = Map.load('map.p')
            logging.debug(self.level)
        except IOError:
            logging.debug('Generating map')
            self.level = Map((10+random.randrange(30), 10+random.randrange(30)))
            self.level.game = self
            logging.debug('Map size: %s x %s' % (self.level.width, self.level.height))
            self.level.filename = 'map.p'
            self.level.loadTiles(['tile0.png', 'tile1.png'])
            self.level.loadActors(['blip.png', 'zombie.png', 'soldier.png', 'civilian.png', 'corpse.png'])
            logging.debug('generating mobs')
            validMinX, validMaxX = (BLOCKSIZE+ACTORSIZE, self.level.width*BLOCKSIZE-(BLOCKSIZE+ACTORSIZE))
            validRangeX = validMaxX - validMinX  
            validMinY, validMaxY = (BLOCKSIZE+ACTORSIZE, self.level.height*BLOCKSIZE-(BLOCKSIZE+ACTORSIZE))
            validRangeY = validMaxY - validMinY  
            s = NUM_SOLDIERS/2+int(random.random()*NUM_SOLDIERS)
            c = NUM_CIVILIANS/2+int(random.random()*NUM_CIVILIANS)
            z = NUM_ZOMBIES/2+int(random.random()*NUM_ZOMBIES)
            self.level.mobs = pygame.sprite.Group([Civilian(self.level, Loc(random.random()*validRangeX + validMinX, random.random()*validRangeY + validMinY)) for i in range(c)])
            self.level.mobs.add([Soldier(self.level, Loc(random.random()*validRangeX + validMinX, random.random()*validRangeY + validMinY)) for i in range(s)])
            self.level.mobs.add([Zombie(self.level, Loc(random.random()*validRangeX + validMinX, random.random()*validRangeY + validMinY)) for i in range(z)])
            self.level.sortMobs()
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
        self.startTime=self.frameTime=time.time()
        self.editMode = False
        self.systemFont = pygame.font.SysFont("None", 16)
        self.drawing = False
        self.done = False
        