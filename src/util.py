'''
Created on Nov 11, 2012

@author: Grud
'''

import math
import logging

def addCoords(a, b):
    return (a[0]+b[0], a[1]+b[1])

def scaleCoords(pos, scale):
    return (pos[0]*scale, pos[1]*scale)

class Loc():
    '''
    basic two-dimensional coordinate class
    - overload addition/subtraction, and multiplication/division(scaling)
    '''
    def __init__(self, x=0, y=0):
        self.loc = self.x, self.y = x, y
    
    def __repr__(self):
        return '(%s, %s)' % (self.x, self.y)
    
    def __add__(self, other):
        if isinstance(other, Loc):
            return Loc(self.x+other.x, self.y+other.y)
        return Loc(self.x+other[0], self.y+other[1])
    
    def __sub__(self, other):
        return Loc(self.x-other.x, self.y-other.y)
    
    def __neg__(self):
        return Loc(-self.x, -self.y)
    
    def __mul__(self, factor):
        return Loc(self.x*factor, self.y*factor)
    
    def __div__(self, factor):
        return Loc(float(self.x/factor), float(self.y/factor))
    
    def __eq__(self, other):
        if isinstance(other, Loc):
            return self.loc==other.loc
        return self.loc == other 

    def addVector(self, direction, magnitude):
        x = math.cos(direction)*magnitude
        y = math.sin(direction)*magnitude
        return self+(x, y)
        
    def distance(self, other):
        #return math.sqrt((self.x-other.x)**2 + (self.y-other.y)**2)
        return math.hypot(self.x-other.x, self.y-other.y)
 
