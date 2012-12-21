'''
Created on Dec 20, 2012

@author: Grud
'''

from util import *
from tilemap import *

class PathFinder(object):
    '''
    Class for path finding in standard grid map
    Uses dynamic programming
    Assumes map is a member of tilemap.Map
    DP map is on the block level
    '''
    costs = {0: 1}
    blockedCost = 9999
    costsGrid = None
    valueGrid = None
    movesGrid = None
    
    def __init__(self, level=None, start=None, target=None, actor=None):
        '''
        Constructor
        '''
        self.level = level
        self.start = start
        self.target = target
        self.actor = actor
        if level:
            self.width, self.height = self.level.size
        if level and target:
            self.generatePaths()
    
    def getCost(self, block):
        if block in self.costs:
            return self.costs[block]
        return self.blockedCost

    def getMove(self, (x, y)):
        return self.movesGrid[y*self.width + x]

    def setMove(self, (x, y), move):
        self.movesGrid[y*self.width + x] = move
        
    def setCost(self, (x, y), cost):
        self.costsGrid[y*self.width + x] = cost

    def printGrid(self, grid):
        for i in range(self.height):
            print [c for c in grid[self.width*i:self.width*(i+1)]]
    
    def generatePaths(self):
        self.costsGrid = [self.blockedCost] * len(self.level.grid)
        self.movesGrid = [None for i in range(len(self.level.grid))]
        w, h = self.width, self.height
        self.setCost(self.target, 0)
        done = False
        while not done:
            done = True
            for x in range(w):
                for y in range(h):
                    mincost = self.getCost(self.level.getTile((x, y)))
                    cost = lowest = self.costsGrid[w*y + x]
                    for px in range(x-1, x+2):
                        for py in range(y-1, y+2):
                            if (0<=px<w) and (0<=py<h) and ((px==x) or (py==y)):
                                c = max(self.costsGrid[w*py + px] + self.getCost(self.level.getTile((px, py))),mincost)
                                        
                                if c < lowest:
                                    lowest = c
                                    dest = (px, py)
                    if lowest < cost:
                        self.setCost((x, y), lowest)
                        self.setMove((x, y), dest)
                        done = False
            #self.printGrid(self.level.grid)
            #self.printGrid(self.costsGrid)
            #self.printGrid(self.movesGrid)
            
        
    def setStart(self, start):
        self.start = start
        
    def setTarget(self, target):
        self.target = target
        
    def setLevel(self, level):
        self.level = level

    def setActor(self, actor):
        self.actor = actor
    
    def nextPoint(self, (x, y)):
        target = self.getMove((int(x/256), int(y/256)))
        if target:
            x, y = target
            return (x * BLOCKSIZE + BLOCKSIZE/2, y * BLOCKSIZE + BLOCKSIZE/2)
        

