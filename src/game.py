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



class Game():
    resource_path = 'res/'
    
    def __init__(self, **kwargs):
        pygame.init()
        self.size = pygame.display.list_modes()[0]
        self.mode = 0
        self.resource_path = 'res/'
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.width, self.height = self.size
        self.screen = pygame.display.set_mode(self.size, self.mode)
        self.clock = pygame.time.Clock()
        Game.resource_path = self.resource_path
        Actor.setInit(**{'resource_path': Game.resource_path})
        self.Setup()

    def Quit(self):
        self.level.save()


    def Render(self):
        cursor_pos = pygame.mouse.get_pos()
        map_pos = (cursor_pos[0]-self.map_offset[0], cursor_pos[1]-self.map_offset[1])
        map_tile = self.level.tile_by_pos(map_pos)
        self.screen.blit(self.background, (0, 0))
        if self.edit_mode:
            self.screen.blit(self.system_font.render("Edit", 0, (255,0,0)), (0,0))
            cursor_color=RED
        else:
            cursor_color=GREEN
        if map_tile:
            tile_rect = pygame.rect.Rect(self.map_offset[0]+map_tile[0]*self.level.tile_size,
                         self.map_offset[1]+map_tile[1]*self.level.tile_size,
                         self.level.tile_size,
                         self.level.tile_size)
            pygame.draw.rect(self.screen, cursor_color, tile_rect, max((self.level.tile_size/16,1)))
        #self.balls.update()
        #self.balls.draw(self.screen)
        pygame.display.flip()
        
    def GameLoop(self):
        while not self.done:
            self.clock.tick(60)
        
            for event in pygame.event.get():
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    map_pos = (event.pos[0]-self.map_offset[0], event.pos[1]-self.map_offset[1])
                    map_tile = self.level.tile_by_pos(map_pos)
                if event.type == pygame.QUIT:
                    self.done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKQUOTE:
                        self.edit_mode = not self.edit_mode
                    elif event.key ==pygame.K_ESCAPE:
                        self.done = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if map_tile:
                        if self.edit_mode and event.button==1:
                            if self.level.get_tile(map_tile) == self.level.fill:
                                self.drawing = self.level.wall+100
                            else:
                                self.drawing = self.level.fill+100
                            self.level.set_tile(map_tile, self.drawing-100)
                            self.level.render_tile(self.background, map_tile, self.map_offset)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if map_tile and event.button==1:
                        self.drawing = False
                elif event.type == pygame.MOUSEMOTION:
                    if map_tile and self.drawing:
                        self.level.set_tile(map_tile, self.drawing-100)
                        self.level.render_tile(self.background, map_tile, self.map_offset)
            self.Render()
            self.framecount += 1
            cur_time = time.time()
            elapsed = cur_time-self.start_time
            if elapsed>=1:
                logging.info("FPS: %f" % (self.framecount/elapsed))
                self.start_time=cur_time
                self.framecount=0
        # Exit game
        self.Quit()


    def Setup(self):
        self.balls = pygame.sprite.RenderPlain([Ball() for i in range(100)])
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        logging.info('Resource path: %s' % self.resource_path)
        tilemap.Map.resource_path = self.resource_path
        try:
            self.level = tilemap.Map.load('map.p')
            logging.info(self.level)
        except:
            self.level = tilemap.Map()
            self.level.filename = 'map.p'
            self.level.load_tiles(['tile0.jpg', 'tile1.jpg'])
        self.map_offset=self.level.fit(self.width, self.height)
        self.level.render(self.background,(self.map_offset[0], self.map_offset[1]))
        self.framecount=0
        self.start_time=time.time()
        self.edit_mode = False
        self.system_font = pygame.font.SysFont("None", 16)
        self.drawing = False
        self.done = False
        self.GameLoop()
        