'''
Created on Nov 11, 2012

@author: Grud
'''
import pygame
import pickle
import time
from util import *
from constants import *
from actor import *

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
        self.friendlies = pygame.sprite.Group()
        self.neutrals = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.other = pygame.sprite.Group()
        self.visible = pygame.sprite.Group()
        self.mobOffset = Loc()
        self.mobSize = Loc()
        self.scale = 1.0
        self.maxScale = 2.0
        self.minScale = 0.05
        self.setViewpoint(scaleCoords(self.getSize(), 0.5))
        self.setTileSize(BLOCKSIZE)
        self.game = None
    
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

    def isClear(self, loc):
        if isinstance(loc, Loc):
            x, y = loc.loc
        else:
            x, y = loc
        if BLOCKSIZE+ACTORSIZE<x<self.width*BLOCKSIZE-(ACTORSIZE+BLOCKSIZE)\
            and BLOCKSIZE+ACTORSIZE<y<self.height*BLOCKSIZE-(ACTORSIZE+BLOCKSIZE):
                return self.getTile(self.tileByPos((x, y)))==TILE_OPEN

    def canMoveTo(self, actor, loc):
        if isinstance(loc, Loc):
            x, y = loc.loc
        else:
            x, y = loc
        '''
        if BLOCKSIZE+ACTORSIZE<x<self.width*BLOCKSIZE-(ACTORSIZE+BLOCKSIZE)\
            and BLOCKSIZE+ACTORSIZE<y<self.height*BLOCKSIZE-(ACTORSIZE+BLOCKSIZE)\
            and actor.canTraverse((x,y)):
                return True
        '''
        if actor.canTraverse((x,y)):
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
        self.mobSize = Loc((self.actorSize, self.actorSize))
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
    
    def blocksVision(self, tile):
        return True if (tile == TILE_WALL) else False

    def losGridCellsStrict(self, viewerLoc, targetLoc):
        x0, y0 = viewerLoc
        x1, y1 = targetLoc
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        ix = 1 if x0 < x1 else -1
        iy = 1 if y0 < y1 else -1
        e = 0
        for i in range(dx+dy):
            yield (x0, y0)
            e1 = e + dy
            e2 = e - dx
            if abs(e1)<abs(e2):
                x0 += ix
                e = e1
            else:
                y0 += iy
                e = e2
    
    def losGridCells(self, viewerLoc, targetLoc):
        x0, y0 = viewerLoc
        x1, y1 = targetLoc
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        ix = 1 if x0 < x1 else -1
        iy = 1 if y0 < y1 else -1
        e = 0
        for i in range(dx+dy):
            yield (x0, y0)
            e1 = e + dy
            e2 = e - dx
            e3 = e + dy - dx
            m = min((abs(e1), abs(e2), abs(e3)))
            if m == abs(e1):
                x0 += ix
                e = e1
            elif m == abs(e2):
                y0 += iy
                e = e2
            else:
                x0 += ix
                y0 += iy
                e = e3     

    def isVisible(self, viewer, target, strict = False):
        if strict:
            losFunc = self.losGridCellsStrict
        else:
            losFunc = self.losGridCells
        x1, y1 = viewer.loc.loc
        l1 = int(x1)/BLOCKSIZE, int(y1)/BLOCKSIZE
        x2, y2 = target.loc.loc
        l2 = int(x2)/BLOCKSIZE, int(y2)/BLOCKSIZE
        for cell in losFunc(l1, l2):
            if self.blocksVision(self.getTile(cell)):
                return False
        return True

    def getVisibleMobs(self, viewers = None, mobs = None, strict = False):
        visible = []
        if viewers == None:
            viewers = self.friendlies
        if mobs == None:
            mobs = self.mobs
        for v in viewers:
            for m in mobs:
                if math.hypot(v.loc.x-m.loc.x, v.loc.y-m.loc.y)<=v.senseRadius:
                    if self.isVisible(v, m, strict):
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
        return (int(screenXPos), int(screenYPos))
    
    def transformToMapspace(self, target, pos):  
        x, y = pos
        centre = self.viewpoint
        xCentre, yCentre = centre
        viewCentre = viewXCentre, viewYCentre = (target.get_rect()[2]/2, target.get_rect()[3]/2)
        mapXPos = xCentre - ((viewXCentre-x) * BLOCKSIZE/self.tileSize)
        mapYPos = yCentre - ((viewYCentre-y) * BLOCKSIZE/self.tileSize)
        return (mapXPos, mapYPos)
    
    def addMob(self, mob):
        mob.level = self
        self.mobs.add(mob)
        self.setActorImage(mob)
        if mob.__class__.__name__ == 'Soldier':
            self.friendlies.add(mob)
        elif mob.__class__.__name__ == 'Civilian':
            self.neutrals.add(mob)
        elif mob.__class__.__name__ == 'Zombie':
            self.enemies.add(mob)
        else:
            self.other.add(mob)
        
    def sortMobs(self):
        self.friendlies.empty()
        self.neutrals.empty()
        self.enemies.empty()
        for mob in self.mobs:
            self.addMob(mob)

    def renderMobs(self, target, mobs=None):
        if not mobs:
            mobs = self.mobs
        for mob in mobs.sprites():
            mob.rect = pygame.Rect((self.mobOffset+self.transformToScreenspace(target, mob.loc.loc)).loc, self.mobSize.loc)
        #self.visible.draw(target)
        self.other.draw(target)
        self.neutrals.draw(target)
        self.enemies.draw(target)
        self.friendlies.draw(target)
        
        target.lock()
        for s in self.visible:
            for h in s.highlight:
                pygame.draw.circle(target, h[0], self.transformToScreenspace(target, s.loc.loc), max(int(h[1]*self.scale), h[2]), h[2])
        target.unlock()
        
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
    def load(cls, filename, game):
        data = pickle.load(open(Map.resourcePath+filename, 'rb'))
        m = Map()
        for name, value in data.iteritems():
            setattr(m, name, value)
        m.setSize(m.size)
        m.grid = data['grid']
        m.filename = filename
        m.game = game
        m.loadTiles(m.tileNames)
        m.loadActors(m.actorNames)
        for mob in m.mobs:
            mob.level = m
        return m
        
    def save(self, saveMobs=False, filename=None):
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
        del data['game']
        for mob in self.mobs:
            mob.image = None
        if not saveMobs:
            self.mobs = pygame.sprite.Group()
            del data['other']
            self.sortMobs()
        out = open(Map.resourcePath+self.filename, 'wb')
        pickle.dump(data, out)
        out.close()
        t1 = time.time()
        logging.debug('Level saved in %f seconds' % (t1-t0))

