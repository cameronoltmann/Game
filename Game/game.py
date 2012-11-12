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

logging.getLogger().setLevel('DEBUG')
pygame.init()

size = width, height = 1024, 768#640, 480 #tuple(pygame.display.list_modes()[0])
speed = [2, 2]
black = 0, 0, 0
RED = (255, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode(size) #(size, pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.HWSURFACE)
clock = pygame.time.Clock()


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super(Ball, self).__init__()
        self.speed = [random.randrange(4), random.randrange(4)]
        self.image = pygame.image.load('ball.gif')
        self.rect = self.image.get_rect()

    def update(self):
        self.rect = self.rect.move(self.speed)
        if self.rect.left < 0 or self.rect.right > width:
            self.speed[0] = -self.speed[0]
        if self.rect.top <0 or self.rect.bottom > height:
            self.speed[1] = -self.speed[1]



        
balls = pygame.sprite.RenderPlain([Ball() for i in range(100)])
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))
try:
    level = tilemap.Map.load('map.p')
    logging.info(level)
except:
    level = tilemap.Map()
    level.filename = 'map.p'
    level.load_tiles(['tile0.jpg', 'tile1.jpg'])
map_offset=level.fit(width, height)
level.render(background,(map_offset[0], map_offset[1]))
framecount=0
start_time=time.time()
edit_mode = False
system_font = pygame.font.SysFont("None", 16)
drawing = False
done = False
while not done:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            map_pos = (event.pos[0]-map_offset[0], event.pos[1]-map_offset[1])
            map_tile = level.tile_by_pos(map_pos)
        if event.type == pygame.QUIT:
            done = True
            level.save()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKQUOTE:
                edit_mode = not edit_mode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if map_tile:
                if edit_mode and event.button==1:
                    if level.get_tile(map_tile) == level.fill:
                        drawing = level.wall+100
                    else:
                        drawing = level.fill+100
                    level.set_tile(map_tile, drawing-100)
                    level.render_tile(background, map_tile, map_offset)
        elif event.type == pygame.MOUSEBUTTONUP:
            if map_tile and event.button==1:
                drawing = False
        elif event.type == pygame.MOUSEMOTION:
            if map_tile and drawing:
                level.set_tile(map_tile, drawing-100)
                level.render_tile(background, map_tile, map_offset)
                    

        
    
    #screen.fill(black)
    cursor_pos = pygame.mouse.get_pos()
    map_pos = (cursor_pos[0]-map_offset[0], cursor_pos[1]-map_offset[1])
    map_tile = level.tile_by_pos(map_pos)
    screen.blit(background, (0, 0))
    if edit_mode:
        screen.blit(system_font.render("Edit", 0, (255,0,0)), (0,0))
        cursor_color=RED
    else:
        cursor_color=GREEN
    if map_tile:
        tile_rect = pygame.rect.Rect(map_offset[0]+map_tile[0]*level.tile_size,
                     map_offset[1]+map_tile[1]*level.tile_size,
                     level.tile_size,
                     level.tile_size)
        pygame.draw.rect(screen, cursor_color, tile_rect, max((level.tile_size/16,1)))
    #balls.update()
    #balls.draw(screen)
    pygame.display.flip()
    framecount += 1
    cur_time = time.time()
    elapsed = cur_time-start_time
    if elapsed>=1:
        logging.info("FPS: %f" % (framecount/elapsed))
        start_time=cur_time
        framecount=0
        