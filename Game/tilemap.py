'''
Created on Nov 11, 2012

@author: Grud
'''
import pygame

resource_path='res/'
import pickle

class Map(object):
    '''
    classdocs
    '''
    def __init__(self, size=(20, 20), tile_size=32, fill=0, wall=1):
        self.fill = fill
        self.wall = wall
        self.set_size(size)
        self.clear_map()
        self.tiles_raw = None
        self.set_tile_size(tile_size)
    
    def load_tiles(self, tile_names, tile_size=None):
        self.tile_names = list(tile_names)
        self.tiles_raw = [pygame.image.load(resource_path+tile) for tile in tile_names]
        if tile_size:
            self.tile_size = tile_size
        self.set_tile_size(self.tile_size)
        
    def set_tile_size(self, tile_size):
        self.tile_size = tile_size
        if self.tiles_raw:
            self.tiles = [pygame.transform.scale(tile, (self.tile_size, self.tile_size)) for tile in self.tiles_raw]

    def set_size(self, size):
        self.size = self.width, self.height = size
        self.clear_map()
    
    def get_size(self):
        return (self.width*self.tile_size, self.height*self.tile_size)
        
    def fill_map(self, fill_with):
        self.grid = [fill_with]*self.width*self.height
    
    def clear_map(self):
        self.fill_map(self.fill)
        # possibly take the boundary walls out later
        for i in range(self.width):
            self.grid[i] = self.wall
            self.grid[(self.height-1)*self.width + i] = self.wall
        for j in range(self.height):
            self.grid[self.width*j] = self.wall
            self.grid[self.width*j + self.width-1] = self.wall
    
    def render(self, target, pos=(0,0)):
        left, top = pos
        t_rect = pygame.rect.Rect(0, 0, self.tile_size, self.tile_size)
        for y in range(self.height):
            t_rect.top = y*self.tile_size+top
            for x in range(self.width):
                t_rect.left = x*self.tile_size+left
                target.blit(self.tiles[self.grid[x+y*self.width]],t_rect)

    def render_tile(self, target, tile, pos=(0,0)):
        x, y = tile
        left = tile[0]*self.tile_size + pos[0]
        top = tile[1]*self.tile_size + pos[1]  
        t_rect = pygame.rect.Rect(left, top, self.tile_size, self.tile_size)
        target.blit(self.tiles[self.grid[x+y*self.width]],t_rect)
        
                
    def fit(self, width, height):
        max_tile_width = width/self.width
        max_tile_height = height/self.height 
        self.set_tile_size(min((max_tile_width, max_tile_height)))
        m_w, m_h = self.get_size()
        return ((width-m_w)/2, (height-m_h)/2)

    def tile_by_pos(self, (x, y)):
        if -1<x<self.width*self.tile_size and -1<y<self.height*self.tile_size:
            return (x/self.tile_size, y/self.tile_size)
        
    def set_tile(self, (x, y), fill):
        self.grid[y*self.width+x] = fill
        
    def get_tile(self, (x, y)):
        return self.grid[y*self.width+x]
        
    '''@classmethod
    def load(cls, filename):
        m = pickle.load(open(resource_path+filename, 'rb'))
        m.filename = filename
        return m
        
    def save(self, filename=None):
        if filename:
            self.filename = filename
        pickle.dump(self, open(resource_path+self.filename, 'wb'))
    '''

    @classmethod
    def load(cls, filename):
        data = pickle.load(open(resource_path+filename, 'rb'))
        m = Map()
        for name, value in data.iteritems():
            setattr(m, name, value)
        m.filename = filename
        m.load_tiles(m.tile_names)
        return m
        
    def save(self, filename=None):
        if filename:
            self.filename = filename
        data = {'fill': self.fill,
                'wall': self.wall,
                'size': self.size,
                'tile_size': self.tile_size,
                'grid': self.grid,
                'tile_names': self.tile_names,
                }
        pickle.dump(data, open(resource_path+self.filename, 'wb'))

