#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Besides making this directory represent a module, __init__ provides
some utility functions (ssq, sssq, rotate2, isTrue) and defines
classes for plugins and for pypevue data structures:

1,2.  Classes Point and IcosaGeoPoint are data structures for points
in space.  Point has (x,y,z) data for one point, plus several methods
that treat the coordinates as a point or a vector.  IcosaGeoPoint adds
to that several data items useful when working with points on an
icosahedron or a typical geodesic dome.

3,4.  Classes Post and Cylinder are data structures for individual
posts and cylinders, plus methods for access, string representations,
etc

5.  Class Layout is a data structure for assemblies of posts and
cylinders, plus base points, origin points, and edge lists.

6.  Class FunctionList, with its registrar() and clear() methods,
supports plugins.  The tell() function at the end of this file is an
example of a tell() method as needed in a plugin.'''

# This section (next 8 lines) is for PyScaffold
from pkg_resources import get_distribution, DistributionNotFound
try:
    dist_name = 'pypevue'
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound

from math import sin, cos, sqrt
#==================== Utility functions ==========================
def ssq(x,y,z):    return x*x + y*y + z*z
def sssq(x,y,z):   return sqrt(ssq(x,y,z))
#------------------------------------------
def rotate2(a,b,theta):
    st = sin(theta)
    ct = cos(theta)
    return  a*ct-b*st, a*st+b*ct
#------------------------------------------
def isTrue(x):
    '''Return false if x is None, or False, or an empty string, or a
    string beginning with f, F, N, or n.  Else, return True.    '''
    return not str(x)[:1] in 'fFNn'

#==========1===========Point=========================
class Point:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    def scale(self, s):
        self.x = s*self.x
        self.y = s*self.y
        self.z = s*self.z
    def scalexy(self, s):
        self.x = s*self.x
        self.y = s*self.y
    def inner(self, q):         # Inner product of two 3-vectors
        return (self.x*q.x + self.y*q.y + self.z*q.z)
    def cross(self, q):         # cross product of the two 3-vectors
        return (self.y*q.z - self.z*q.y, self.z*q.x - self.x*q.z, self.x*q.y - self.y*q.x)
    def norm(self):
        mag = sssq(self.x, self.y, self.z)
        return (self.x / mag, self.y / mag, self.z / mag)
    def diff(self, q):
        return (self.x-q.x, self.y-q.y, self.z-q.z)
    def add(self, q):
        return (self.x+q.x, self.y+q.y, self.z+q.z)
    def mag(self):
        return sssq(self.x, self.y, self.z)
    def str(self, places):
        x,y,z = (round(k,places) for k in (self.x, self.y ,self.z))
        return f'{x}, {y}, {z}'
    def __str__( self):  return self.str(3)
    def __repr__(self):  return self.str(8)
    def __lt__(a, b):     # To sort points in x,y,z order
        return (a.x < b.x) or (a.x == b.x and a.y < b.y) or (a.x == b.x and a.y == b.y and a.z <= b.z)

#==========2===========================================


#==========3==========Post=============================
class Post:
    def __init__(self, foot, top=0, diam=0, hite=0, yAngle=0, zAngle=0, num=0, data=0):
        self.foot = foot
        self.top  = top
        self.diam = diam
        self.hite = hite
        self.yAngle = yAngle
        self.zAngle = zAngle
        self.num  = num
        self.data = data 
    def __str__( self):
        return f'Post {self.num} ({self.foot}) ({self.top}) {round(self.yAngle,1)} {round(self.zAngle,1)}  '
    def __repr__(self):  return self.__str__()

#==========4==========Cylinder=========================
class Cylinder:
    def __init__(self, post1, post2, lev1, lev2, colo, thix, gap, data=0, num=0):
        diam = FunctionList.thickLet(thix)
        self.put9 (post1, post2, lev1, lev2, colo, diam, gap, data, num)
        
    def get9(self):
        return self.post1, self.post2, self.lev1, self.lev2, self.colo, self.diam, self.gap, self.data, self.num
    
    def put9(self, post1, post2, lev1, lev2, colo, diam, gap, data, num):
        self.post1, self.post2 = post1, post2
        self.lev1,  self.lev2  = lev1,  lev2
        self.colo,  self.diam  = colo,  diam
        self.gap,   self.data  = gap,   data
        self.num = num
        
    def __str__( self):
        return f'Cylinder {self.num} ({self.post1},{self.post2}) {self.colo}{self.diam:0.2f}{self.lev1}{self.lev2} {round(self.gap,2)}'
    def __repr__(self):  return self.__str__()

#==========5==========Layout===========================
class Layout:
    def __init__(self, BP=Point(0,0,0), OP=Point(0,0,0),
                 posts=[], cyls=[],  edgeList={}):
        self.BP = BP  # Current basepoint value
        self.OP = OP  # Origin point of net
        self.posts = posts
        self.cyls  = cyls
        self.edgeList = edgeList
    def get4(self):
        return  self.BP, self.OP, self.posts, self.cyls
    def __str__( self):
        return f'Layout: BP({self.BP})  OP({self.OP});  {len(self.posts)} posts, {len(self.cyls)} cyls'

#==========6==========FunctionList=====================
class FunctionList:
    # The next lines initialize dicts for correspondences between
    # functions and function names.
    fNames = [] # names of base-level functions
    fDict  = {} # dictionary with fDict[name] = function with given name
    fTotal = [] # Raw list of function spec triples, (name, func, module)
    # Next, the same things but for user-function plugins:
    uNames = [];    uDict = {};    uTotal = [] 
    
    def registrar(pll):
        '''Load plugins, either from baseFuncs (if plugins list pll is empty)
        or from files listed in pll.  Eg, if pll is "abc,def,," then
        registrar will get plugins from files abc.py and def.py.  A
        plugin mentioned in multiple files will be taken from the
        last-registered file.  '''
        import pypevue.baseFuncs, inspect, importlib
        ref = FunctionList
        #print (f'Registrar pll = {pll}')
        if pll=='':
            ref.fDict, ref.uDict = {}, {}
            # baseFuncs will give us a complete list of base-level functions
            fs = pypevue.baseFuncs.tell()
            for f in fs: # Make canonical list of fixed function names
                ref.fDict[f.__name__] = f
            ref.fNames = sorted(ref.fDict.keys())
            ref.loaded = ['baseFuncs']
        else:
            finn = [fn for fn in pll.split(',') if fn != '']            
            #print (f'Registrar pll = {pll}, finn = {finn}')
            for toImp in finn:
                m = importlib.import_module(toImp) # m is a module
                mkeys = [obj for obj, pred in inspect.getmembers(m)]
                # If the module contains a `tell` object, try calling it.
                if 'tell' in mkeys:
                    try: 
                        for f in m.tell(): # Add functions from tell() into ref.fDict{}
                            name = f.__name__ # Get the function name
                            if name in ref.fNames:
                                ref.fDict[name] = f
                            else:
                                ref.uDict[name] = f
                        ref.loaded.append(toImp)
                    except AttributeError:
                        print (f"Calling `tell` for {toImp} failed")
            print (f"Registrar got functions from {', '.join(ref.loaded)}")

        # Set class variables for all plugin functions
        ref.uNames = sorted(ref.uDict.keys())
        for n in ref.fNames: setattr(ref, n, ref.fDict[n])
        for n in ref.uNames: setattr(ref, n, ref.uDict[n])

    def clear():
        # To make changes to a dome which uses plugins while still
        # running the same process, have to clear out old plugins
        ref = FunctionList
        ref.fNames = [] # names of base-level functions
        ref.fDict  = {} # dictionary with fDict[name] = function with given name
        ref.fTotal = [] # Raw list of function spec triples, (name, func, module)
        # Do the same for user-function plugins:
        ref.uNames = [];    ref.uDict = {};    ref.uTotal = []


def tell():                     # Example of a tell() function ...
    '''A tell() function returns a list or tuple of functions.  Each
    program in this directory should contain a tell() function, by
    which pypevu discovers functions to use as addons or overrides of
    its own fixed functions.  Functions not listed in a tell will be
    ignored by pypevu and not used as addons or overrides.  If an
    unqualified user function name is in several tell's, the one from
    the highest-lexing module will be used.  Note, registrar does not
    call this example.    '''
    def whatFunc(layout): # Functions can be module level or local, etc
        return None
    return (someFunc, whatFunc)
# For user functions, pypevu provides one argument, a layout.
def someFunc(layout): return otherstuff(layout, 4, 3)
