'''
Created on Nov 11, 2012

@author: Grud
'''
import pygame
import pickle
import time
from util import *
from constants import *

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
        self.tiles = []
        self.actors = []
        self.mobs = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.friendlies = pygame.sprite.Group()
        self.neutrals = pygame.sprite.Group()
        self.visible = pygame.sprite.Group()
        self.mobOffset = Loc(0, 0)
        self.mobSize = Loc(0, 0)
        self.scale = 1.0
        self.maxScale = 2.0
        self.minScale = 0.05
        self.setViewpoint(scaleCoords(self.getSize(), 0.5))
        self.setTileSize(BLOCKSIZE)
    
    def loadTiles(self, tileNames, tileSize=None):
        self.tileNames = list(tileNames)
        self.tilesRaw = [pygame.image.load(Map.resourcePath+tile) for tile in tileNames]
        self.tiles = [pygame.transform.scale(tile, (BLOCKSIZE, BLOCKSIZE)) for tile in self.tilesRaw]
        if tileSize:
            self.tileSize = tileSize
        self.setTileSize(self.tileSize)

    def loadActors(self, actorNames):
        self.actorNames = list(actorNames)
        self.actorsRaw = [pygame.image.load(Map.resourcePath+actor) for actor in self.actorNames]
        self.actors = [pygame.transform.scale(actor, (ACTORSIZE, ACTORSIZE)) for actor in self.actorsRaw]
        self.setActorSize(self.actorSize)
        
    def canMoveTo(self, actor, loc):
        if isinstance(loc, Loc):
            x, y = loc.loc
        else:
            x, y = loc
        if ACTORSIZE<x<self.width*BLOCKSIZE-ACTORSIZE\
            and ACTORSIZE<y<self.height*BLOCKSIZE-ACTORSIZE\
            and actor.canTraverse((x,y)):
                return True
        return False

    def resizeImages(self, images, size):
        return [pygame.transform.scale(image, (size, size)) for image in images]
    
    def setTileSize(self, tileSize):
        self.tileSize = tileSize
        logging.debug('tileSize: %s' % tileSize)
        self.setActorSize(self.tileSize*ACTORSIZE/BLOCKSIZE)
        if self.tiles:
            self.tilesScaled = self.resizeImages(self.tiles, tileSize)
        else:
            logging.debug('self.actors doesn\'t exist!')
        
    def setActorImage(self, actor):
        actor.image = self.actorsScaled[actor.appearance]

    def setActorSize(self, size):
        self.actorSize = size
        self.mobSize = Loc(self.actorSize, self.actorSize)
        self.mobOffset = -self.mobSize/2.0
        logging.debug('mobSize: %s' % self.mobSize)
        if self.actors:
            self.actorsScaled = self.resizeImages(self.actors, size)
            for mob in self.mobs:
                self.setActorImage(mob)
                #mob.image = self.actorsScaled[mob.appearance]

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

    def isInRange(self, viewer, target, range):
        return viewer.loc.distanceTo(target.loc)<=range

    def getVisibleMobs(self, viewers = None):
        visible = []
        if not viewers:
            viewers = self.friendlies
        for v in viewers:
            for m in self.mobs:
                if self.isInRange(v, m, v.senseRadius):
                    visible.append(m)
        return visible

    def setVisible(self, visible):
        self.visible.empty()
        self.visible.add(visible)
                    
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
    
    def renderMobs(self, target, mobs=None):
        if not mobs:
            mobs = self.mobs
        for mob in mobs.sprites():
            mob.rect = pygame.Rect((self.mobOffset+self.transformToScreenspace(target, mob.loc.loc)).loc, self.mobSize.loc)
            #logging.debug('%s = %s' % (mob.loc, mob.rect))
        #mobs.draw(target)
        self.visible.draw(target)
        #self.friendlies.draw(target)
        
    def render(self, target):
        mapSize = mapWidth, mapHeight = self.getSize()
        xMin, yMin = self.transformToMapspace(target, (0, 0))
        xMax, yMax = self.transformToMapspace(target, target.get_rect()[2:])
        xMin = max(xMin, 0)
        yMin = max(yMin, 0)
        xMax = min(xMax, mapWidth-1)
        yMax = min(yMax, mapHeight-1)
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
        tileULC = scaleCoords(tile, BLOCKSIZE)
        tileScreenULC = self.transformToScreenspace(target, tileULC)
        tileRect = pygame.rect.Rect(tileScreenULC, (self.tileSize, self.tileSize))
        target.blit(self.tilesScaled[self.grid[x+y*self.width]],tileRect)
        
                
    def setScale(self, scale):
        if self.minScale <= scale <= self.maxScale and scale != self.scale:
            self.scale = scale
        self.setTileSize(int(BLOCKSIZE*self.scale))
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
        
    def getTile(self, (x, y)):
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
        m.loadActors(m.actorNames)
        for mob in m.mobs:
            mob.level = m
        return m
        
    def save(self, filename=None):
        t0 = time.time()
        if filename:
            self.filename = filename
        data = self.__dict__
        del data['tiles']
        del data['tilesRaw']
        del data['tilesScaled']
        del data['actors']
        del data['actorsRaw']
        del data['actorsScaled']
        for mob in self.mobs:
            mob.image = None
        pickle.dump(data, open(Map.resourcePath+self.filename, 'wb'))
        t1 = time.time()
        logging.debug('Level saved in %f seconds' % (t1-t0))

