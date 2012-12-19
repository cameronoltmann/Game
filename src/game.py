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
    debugMode = True
    beacon = None
    
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
            self.screen.blit(self.systemFont.render('Edit', 0, RED), (5,20))
            cursor_color=RED
        #else:
        #    cursor_color=GREEN
        if mapTile and self.editMode:
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
        if not self.editMode:
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

    def mapLocByPos(self, pos):
        '''
        Return map coordinates of screen coordinates
        '''
        if self.mapPortRect.collidepoint(pos):
            pos = (pos[0]-self.mapPortRect[0], pos[1]-self.mapPortRect[1])
            mapPos = self.level.transformToMapspace(self.mapPort, pos)
            return mapPos
        
    def mapTileByPos(self, pos):
        '''
        Return map tile corresponding to screen coordinates
        '''
        '''
        if self.mapPortRect.collidepoint(pos):
            pos = (pos[0]-self.mapPortRect[0], pos[1]-self.mapPortRect[1])
            mapPos = self.level.transformToMapspace(self.mapPort, pos)
        '''
        mapPos = self.mapLocByPos(pos)
        if mapPos:
            return self.level.tileByPos(mapPos)

    def generateMob(self, mob):
        w, h = self.level.getSize()
        loc = Loc(0, 0)
        m = mob()
        while not self.level.isClear(loc):
            loc = Loc(random.randrange(w), random.randrange(h))
            print loc
            m.loc = loc
        if self.beacon:
            m.targetLoc = self.beacon.loc
        self.level.addMob(m)

    def generateMobs(self):
        for mob in self.level.mobs:
            mob.effects = []
            mob.leavesCorpse = None
            mob.die()
        self.beacon = None
        logging.debug('generating mobs')
        s = NUM_SOLDIERS/2+int(random.random()*NUM_SOLDIERS)
        c = NUM_CIVILIANS/2+int(random.random()*NUM_CIVILIANS)
        z = NUM_ZOMBIES/2+int(random.random()*NUM_ZOMBIES)
        mobs = [Soldier] * s + [Civilian] * c + [Zombie] * z
        for mob in mobs:
            self.generateMob(mob)

    def handleEvents(self):
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
                    self.replay = True
                    self.done = True
                elif event.key == pygame.K_d:
                    Game.debugMode = not Game.debugMode
                elif event.key == pygame.K_m:
                    self.generateMobs()
                elif event.key == pygame.K_z:
                    self.generateMob(Zombie)
                elif event.key == pygame.K_x:
                    self.generateMob(Soldier)
                elif event.key == pygame.K_c:
                    self.generateMob(Civilian)
                
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
                    if self.editMode:
                        if event.button==1:
                            if self.level.getTile(mapTile) == TILE_OPEN:
                                self.drawing = TILE_WALL+100
                            else:
                                self.drawing = TILE_OPEN+100
                            self.level.setTile(mapTile, self.drawing-100)
                            self.level.renderTile(self.mapPort, mapTile)
                    else:
                        if event.button==1:
                            l = x, y = self.mapLocByPos(event.pos)
                            targetLoc = Loc(x, y)
                            if self.beacon:
                                self.beacon.moveTo(targetLoc)
                            else:
                                self.beacon = Beacon(self.level, targetLoc)
                            for s in self.level.friendlies:
                                s.targetLoc = self.beacon.loc
                        elif event.button==3:
                            if self.beacon:
                                for s in self.level.friendlies:
                                    s.targetLoc = None
                                self.beacon.die()
                                self.beacon = None
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouseState[event.button] = False
                if mapTile and event.button==1:
                    self.drawing = False
            elif event.type == pygame.MOUSEMOTION:
                if mapTile and self.drawing:
                    self.level.setTile(mapTile, self.drawing-100)
                    self.level.renderTile(self.mapPort, mapTile)

    def scroll(self):
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

    def loopTimer(self):
        self.framecount += 1
        curTime = time.time()
        elapsed = curTime-self.startTime
        shortCount = curTime-self.frameTime
        if shortCount>=1:
            self.fps = self.framecount/elapsed
            #self.startTime=curTime
            self.frameTime = curTime
        
    def gameOver(self):
        if not self.editMode and ((self.fc + self.nc == 0) or (self.zc == 0)):
            self.idlecount += 1
        else:
            self.idlecount = 0
        if self.idlecount>IDLE_TIME:
            return True
        return False
        
    def gameLoop(self):
        self.replay = False
        while not self.done:
            self.clock.tick(60)
            self.handleEvents()
            self.scroll()
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
            self.loopTimer()
            if self.gameOver():
                self.replay = True
                self.done = True
                
        # Exit game
        self.quit()
        return self.replay

    def setup(self):
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
            self.level = Map((20, 20))
            self.level.game = self
            self.level.filename = 'map.p'
            self.level.loadTiles(['tile0.png', 'tile1.png'])
            self.level.loadActors(['blip.png', 'zombie.png', 'soldier.png', 'civilian.png', 'corpse.png'])
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
        self.editMode = True
        self.systemFont = pygame.font.SysFont("None", 16)
        self.drawing = False
        self.done = False
        