'''
Created on Nov 11, 2012

@author: Grud
'''

import math
import logging

from functools import update_wrapper

def decorator(d):
    "Make function d a decorator: d wraps function fn."
    def _d(fn):
        return update_wrapper(d(fn), fn)
    update_wrapper(_d, d)
    return d

@decorator
def memo(f):
    """Decorator that caches return value for each call to f(args).
    Then when called again with same args, returns cached value."""
    cache = {}
    def _f(*args):
        try:
            return cache[args]
        except KeyError:
            cache[args] = result = f(*args)
            return result
        except TypeError:
            # some element can't be a dict key
            return f(args)
    return _f


def addCoords(a, b):
    return (a[0]+b[0], a[1]+b[1])

def scaleCoords(pos, scale):
    return (pos[0]*scale, pos[1]*scale)





class Loc():
    '''
    basic two-dimensional coordinate class
    - overload addition/subtraction, and multiplication/division(scaling)
    '''
    def __init__(self, loc = (0, 0)):
        self.loc = self.x, self.y = loc
    
    def __repr__(self):
        return '(%s, %s)' % (self.x, self.y)
    
    def __add__(self, other):
        if isinstance(other, Loc):
            return Loc((self.x+other.x, self.y+other.y))
        return Loc((self.x+other[0], self.y+other[1]))
    
    def __sub__(self, other):
        return Loc((self.x-other.x, self.y-other.y))
    
    def __neg__(self):
        return Loc((-self.x, -self.y))
    
    def __mul__(self, factor):
        return Loc((self.x*factor, self.y*factor))
    
    def __div__(self, factor):
        return Loc((float(self.x/factor), float(self.y/factor)))
    
    def __eq__(self, other):
        if isinstance(other, Loc):
            return self.loc==other.loc
        return self.loc == other 

    def addVector(self, direction, magnitude):
        x = math.cos(direction)*magnitude
        y = -math.sin(direction)*magnitude
        return self+(x, y)
        
    def getVector(self, other):
        return [self.directionTo(other), self.distanceTo(other)] 
         
    def distanceTo(self, other):
        return math.hypot(self.x-other.x, self.y-other.y)
 
    def directionTo(self, other):
        x, y = other.x-self.x, other.y-self.y
        y = -y
        if x==0:
            x = 1e-15
        angle = math.atan(y/x)
        if x<0:
            if y<0:
                angle -= math.pi
            else:
                angle += math.pi
        return angle 

    @classmethod
    def fromVector(cls, direction, magnitude):
        return Loc(magnitude*math.cos(direction), -magnitude*math.sin(direction))
