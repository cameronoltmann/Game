'''
Created on Nov 11, 2012

@author: Grud
'''
import pygame
import pickle
import util

BLOCKSIZE = 256
TILE_OPEN = 0
TILE_WALL = 1

class MapTile(object):
    def __init__(self):
        pass
        
class Map(object):
    resourcePath = 'res/'
    '''
    classdocs
    '''
    def __init__(self, size=(20, 20), fill=TILE_OPEN, border=TILE_WALL):
        self.fill = fill
        self.wall = border
        self.setSize(size)
        self.clearMap()
        self.tilesRaw = None
        self.tiles = None
        self.scale = 1.0
        self.maxScale = 2.0
        self.minScale = 0.05
        self.setViewpoint(util.scaleCoords(self.getSize(), 0.5))
        self.setTileSize(BLOCKSIZE)
    
    def loadTiles(self, tileNames, tileSize=None):
        self.tileNames = list(tileNames)
        self.tilesRaw = [pygame.image.load(Map.resourcePath+tile) for tile in tileNames]
        self.tiles = [pygame.transform.scale(tile, (BLOCKSIZE, BLOCKSIZE)) for tile in self.tilesRaw]
        if tileSize:
            self.tileSize = tileSize
        self.setTileSize(self.tileSize)
        
    def setTileSize(self, tileSize):
        self.tileSize = tileSize
        if self.tiles:
            self.tilesScaled = [pygame.transform.scale(tile, (self.tileSize, self.tileSize)) for tile in self.tiles]

    def setViewpoint(self, pos):
        x, y = pos
        x = max(x, BLOCKSIZE/2)
        x = min(x, self.width*BLOCKSIZE - BLOCKSIZE/2)
        y = max(y, BLOCKSIZE/2)
        y = min(y, self.width*BLOCKSIZE - BLOCKSIZE/2)
        self.viewpoint = (x, y)
        return self.viewpoint

    def getViewpoint(self):
        return self.viewpoint
    
            
    def setSize(self, size):
        self.size = self.width, self.height = size
        self.clearMap()
    
    def getSize(self):
        return (self.width*BLOCKSIZE, self.height*BLOCKSIZE)
        
    def fillMap(self, fillWith):
        self.grid = [fillWith]*self.width*self.height
    
    def clearMap(self):
        self.fillMap(self.fill)
        # possibly take the boundary walls out later
        for i in range(self.width):
            self.grid[i] = self.wall
            self.grid[(self.height-1)*self.width + i] = self.wall
        for j in range(self.height):
            self.grid[self.width*j] = self.wall
            self.grid[self.width*j + self.width-1] = self.wall
    
    def transformToScreenspace(self, target, pos):
        x, y = pos
        centre = self.viewpoint
        xCentre, yCentre = centre
        viewCentre = viewXCentre, viewYCentre = (target.get_rect()[2]/2, target.get_rect()[3]/2)
        screenXPos = viewXCentre - ((xCentre-x) * self.tileSize/BLOCKSIZE)
        screenYPos = viewYCentre - ((yCentre-y) * self.tileSize/BLOCKSIZE)
        return (screenXPos, screenYPos)
    
    def transformToMapspace(self, target, pos):  
        x, y = pos
        centre = self.viewpoint
        xCentre, yCentre = centre
        viewCentre = viewXCentre, viewYCentre = (target.get_rect()[2]/2, target.get_rect()[3]/2)
        mapXPos = xCentre - ((viewXCentre-x) * BLOCKSIZE/self.tileSize)
        mapYPos = yCentre - ((viewYCentre-y) * BLOCKSIZE/self.tileSize)
        return (mapXPos, mapYPos)
    
    def render(self, target):
        centre = self.viewpoint
        xCentre, yCentre = centre
        mapSize = mapWidth, mapHeight = self.getSize()
        r = l, t, w, h = target.get_rect()
        viewCentre = viewXCentre, viewYCentre = (w/2, h/2)
        viewSize = viewWidth, viewHeight = (w, h)
        xMin = max(xCentre-viewXCentre/self.scale, 0)
        yMin = max(yCentre-viewYCentre/self.scale, 0)
        xMax = min(xCentre+viewXCentre/self.scale, mapWidth-1)
        yMax = min(yCentre+viewYCentre/self.scale, mapHeight-1)
        leftBlock, topBlock = self.tileByPos((xMin, yMin))
        rightBlock, bottomBlock = self.tileByPos((xMax, yMax))
        self.setTileSize
        target.fill((0,0,0))
        for y in range(topBlock, bottomBlock+1):
            for x in range(leftBlock, rightBlock+1):
                self.renderTile(target, (x, y))

    def renderTile(self, target, tile):
        centre = self.viewpoint
        x, y = tile
        tileULC = util.scaleCoords(tile, BLOCKSIZE)
        tileScreenULC = self.transformToScreenspace(target, tileULC)
        tileRect = pygame.rect.Rect(tileScreenULC, (self.tileSize, self.tileSize))
        target.blit(self.tilesScaled[self.grid[x+y*self.width]],tileRect)
        
                
    def setScale(self, scale):
        if self.minScale <= scale <= self.maxScale and scale != self.scale:
            self.scale = scale
            self.setTileSize(int(BLOCKSIZE*scale))
        return self.scale
        

    def fitTo(self, width, height):
        maxTileWidth = width/self.width
        maxTileHeight = height/self.height 
        maxTileSize = min(maxTileWidth, maxTileHeight)
        mw = self.width*maxTileSize
        mh = self.height*maxTileSize
        return pygame.Rect((width-mw)/2, (height-mh)/2, mw, mh)

    def tileByViewportPos(self, (x, y)):
        if -1<x<self.width*self.tileSize and -1<y<self.height*self.tileSize:
            return (x/self.tileSize, y/self.tileSize)
        
    def tileByPos(self, (x, y)):
        if -1<x<self.width*BLOCKSIZE and -1<y<self.height*BLOCKSIZE:
            return (int(x/BLOCKSIZE), int(y/BLOCKSIZE))
        
    def setTile(self, (x, y), fill):
        self.grid[y*self.width+x] = fill
        
    def get_tile(self, (x, y)):
        return self.grid[y*self.width+x]
        
    @classmethod
    def load(cls, filename):
        data = pickle.load(open(Map.resourcePath+filename, 'rb'))
        m = Map()
        for name, value in data.iteritems():
            setattr(m, name, value)
        m.setSize(m.size)
        m.grid = data['grid']
        m.filename = filename
        m.loadTiles(m.tileNames)
        return m
        
    def save(self, filename=None):
        if filename:
            self.filename = filename
        '''
        data = {'fill': self.fill,
                'wall': self.wall,
                'size': self.size,
                'tileSize': self.tileSize,
                'grid': self.grid,
                'tileNames': self.tileNames,
                }
        '''
        data = self.__dict__
        del data['tiles']
        del data['tilesRaw']
        del data['tilesScaled']
        pickle.dump(data, open(Map.resourcePath+self.filename, 'wb'))

