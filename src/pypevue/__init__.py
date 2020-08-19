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

from math import asin, sin, cos, sqrt, pi, radians, acos, degrees
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
    '''3D (x,y,z) points or vectors, with associated methods scale,
    scalexy, inner, cross, norm (a unit vector), mag (scalar
    magnitude), diff, add.  Also
    '''
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    def scale(self, s):         # s*self
        self.x = s*self.x
        self.y = s*self.y
        self.z = s*self.z
    def scalexy(self, s):       # (s*self.x, s*self.y,  self.z)
        self.x = s*self.x
        self.y = s*self.y
    def inner(self, q):         # Inner product, self * q
        return (self.x*q.x + self.y*q.y + self.z*q.z)
    def cross(self, q):         # Cross product, self x q
        return (self.y*q.z - self.z*q.y, self.z*q.x - self.x*q.z, self.x*q.y - self.y*q.x)
    def norm(self):             # unit vector along vector  self
        mag = sssq(self.x, self.y, self.z)
        if mag == 0: return (0, 0, 0)
        return (self.x / mag, self.y / mag, self.z / mag)
    def diff(self, q):          # difference of vectors:  self - q
        return (self.x-q.x, self.y-q.y, self.z-q.z)
    def add(self, q):           # sum of vectors:  self + q
        return (self.x+q.x, self.y+q.y, self.z+q.z)
    def mag(self):              # magnitude of vector
        return sssq(self.x, self.y, self.z)

    def nutation(self, q):
        ''' 
        Angle from the tangent plane of the sphere at this point, 
        to the vector from this point to q.
        https://www.superprof.co.uk/resources/academic/maths/analytical-geometry/distance/angle-between-line-and-plane.html 
        '''
        # use p for the point of this class
        p = self
        # define the plane tangent to the sphere at p
        pl = Point(2*p.x, 2*p.y, 2*p.z)
        # the vector corresponding to the slope from p to q
        m = Point(q.x-p.x, q.y-p.y, q.z-p.z)
        # find the angle between the line and the plane
        angle = self._angleLineSlopeToPlane(pl, m)

        # determine if q is below or above the plane so we know the sign(+-) of the angle
        # https://math.stackexchange.com/questions/7931/point-below-a-plane
        # If v is the vector that points 'up' and p0 is some point on your plane, and finally p is the point that might be below the plane, compute the dot product v⋅(p−p0). This projects the vector to p on the up-direction. This product is {−,0,+} if p is below, on, above the plane, respectively. 
        qpDiff = q.diff(p)
        qpDiff = Point(qpDiff[0], qpDiff[1], qpDiff[2])
        plInnerQP = pl.inner(qpDiff)
        if plInnerQP < 0:
            angle = -angle
        return degrees(angle)

    def _angleLineSlopeToPlane(self, plane, lineSlope, show=False):
        '''Return the angle (in radians) between a plane (defined by a
        3-vector normal to the plane at the origin) and a 3D line
        through the origin (defined by three slopes).  Reference:
        https://www.superprof.co.uk/resources/academic/maths/analytical-geometry/distance/angle-between-line-and-plane.html        '''
        
        if show: print(f'in angleLineSlopeToPlane() with plane ({plane}), line ({lineSlope})')
        pl = plane
        m = lineSlope         
        # The following dot product (inner product) is proportional to
        # the cosine of the angle between two vectors; one of them being
        # the normal vector of the plane
        plInnerM = abs(pl.inner(m))      
        plMag = pl.mag()  # magnitude of plane's normal vector
        mMag = m.mag()    # magnitude of vector of slopes        
        # Normalize the dot product to the magnitude of the two vectors.
        # Because the plane's normal is normal to the plane, we want
        # arcsine rather than arccosine 
        if show: print(f'  plInnerM {plInnerM:1.2f},  plMag {plMag:1.2f}, mMag {mMag:1.2f}, plInnerM / (plMag * mMag) {plInnerM / (plMag * mMag)}')
        sinOfAngle = plInnerM / (plMag * mMag)
        sinOfAngle = min(1, max(0, sinOfAngle))
        angle = asin(sinOfAngle)
        if show: print(f'  returning angle {degrees(angle):1.2f}deg')
        return angle

    def distanceToPlane(self, pl):
        '''
        return the shortest distance from myself to the plane pl
        '''
        pln = pl.norm()
        plNorm = Point(pln[0], pln[1], pln[2])
        return self.inner(plNorm)

    def projectionOnPlane(self, pl):
        '''
        find the projection of this vector onto a plane
        '''
        pln = pl.norm()
        plNorm = Point(pln[0], pln[1], pln[2])
        pPerpMag = self.inner(plNorm)
        plNorm.scale(pPerpMag)
        pPerp = plNorm
        return self.diff(pPerp)

    def angle(self, q):
        '''
        angle between vector me and another vector q
        '''
        try:
            angleCos = self.inner(q) / (self.mag() * q.mag())
        except ZeroDivisionError as e:
            angleCos = -1
        angleCos = max(-1, angleCos)
        angleCos = min(1, angleCos)
        return degrees(acos(angleCos))

    def precession(self, q, show=False):
        '''
        Angle from the plane created by the tangent line to the circle on the sphere at height z and the origin, 
        to the vector from this point to q.
        https://www.youtube.com/watch?v=Zbiclnu2IlU @ 14:50 min:sec
        '''
        p = self
        if show: print(f'in precession() with p ({p}), q ({q})')

        # we need to remove the effects of the nutation angle on the precession angle
        # define the plane tangent to the sphere at p
        plts = Point(2*p.x, 2*p.y, 2*p.z) # plane of tangent sphere
        pltsn = plts.norm()
        pltsNorm = Point(pltsn[0], pltsn[1], pltsn[2])
        nut = radians(self.nutation(q))

        #find the component of q-p perpendicular to the tangent plane of the sphere at p
        qMp = q.diff(p)
        qMp = Point(qMp[0], qMp[1], qMp[2])
        qMpMag = qMp.mag()
        pltsMag = sin(nut)*qMpMag 
        pqPerp = Point(pltsNorm.x*pltsMag, pltsNorm.y*pltsMag, pltsNorm.z*pltsMag)
        aa = qMp.diff(pqPerp)
        m = qMpMpqPerp = Point(aa[0], aa[1], aa[2])
        aa = p.add(m)
        qProj = Point(aa[0], aa[1], aa[2])
        if show:
            aa = p.add(qMpMpqPerp)
            qProj = Point(aa[0], aa[1], aa[2]) # PROBLEM!!!
            nutCheck = radians(self.nutation(qProj))
            print(f'  plts ({plts}), pltsNorm ({pltsNorm}), nutation {degrees(nut):1.2f}deg, qMp ({qMp}), qMpMag {qMpMag:1.2f}, pltsMag = {pltsMag:1.2f}, pqPerp = ({pqPerp}), qMpMpqPerp = ({qMpMpqPerp}), qProj ({qProj}),  nutCheck {degrees(nutCheck):1.2f}deg (should be 0)')

        dx = 0.1
        if (-dx < self.x < dx) and (-dx < self.y < dx):
            # we are at the top center, define the plane as the y-axis
            pltc = Point(0,1,0)
            tv = Point(1,0,p.z)
        else:
            # find the plane which is formed by the line tangent to the circle on
            # the sphere with z = p.z and the origin.
            tv = Point(-p.y, p.x, 0) #vector in direction of tangent line
            t = Point(p.x + tv.x, p.y + tv.y, p.z) # point on the tangent line
            pl = p.cross(t)
            pltc = Point(2*pl[0], 2*pl[1], 2*pl[2]) # plane of tangent to cicle
            if show: print(f'  tangent vector ({tv}), points on tangent line: p ({p}), t ({t}), pltc ({pltc})')

        angle = self._angleLineSlopeToPlane(pltc, m)
        aa = p.cross(pltc)
        pXpltc = Point(aa[0], aa[1], aa[2])
        if show: print(f'  raw angle {degrees(angle):1.2f}deg, pltc.inner(qProj) {pltc.inner(qProj)}, tv.inner(qProj) {tv.inner(qProj)}, pXpltc.inner(qProj) {pXpltc.inner(qProj)}')
        # adjust the positive acute angle based on what quadrant it is in
        if pltc.inner(qProj) >= 0:
            # 0-180 degrees
            if pXpltc.inner(qProj) > 0:
                # >90
                angle = pi - angle
        else:
            # 180-360
            if pXpltc.inner(qProj) < 0:
                # >270
                angle = pi - angle
            angle += pi
        if angle >= 2*pi:
            angle -= 2*pi
        if show: print(f'  returning angle {degrees(angle):1.2f}deg')
        return degrees(angle)

    #=====  Point:  display & comparison methods  =====
    def str(self, places):
        x,y,z = (round(k,places) for k in (self.x, self.y ,self.z))
        return f'{x}, {y}, {z}'
    def __str__( self):  return self.str(3)
    def __repr__(self):  return self.str(8)
    def __lt__(a, b):     # To sort points in x,y,z order
        return (a.x < b.x) or (a.x == b.x and a.y < b.y) or (a.x == b.x and a.y == b.y and a.z <= b.z)



#==========2==========IcosaGeoPoint(Point)=============
class IcosaGeoPoint(Point):
    facess = [(1,2,3,4,5), (6,7,8,9,10,11,12,13,14,15), (16,17,18,19,20)]
    def __init__(self, x, y, z, freq, rank = None, face = None, step = None, stepInRank = None, num=None, nnbrs = None, dupl = None):
        super().__init__(x,y,z)
        self.freq = freq
        self.rank = rank
        self.face = face
        self.step = step
        self.stepInRank = stepInRank
        self.num = num
        self.nnbrs = nnbrs #the number of struts connected to this node
        self.dupl = dupl

    @property
    def stepsInRank(self):
        if self.rank <= self.freq:
            steps = self.rank * 5
        elif self.rank <= 2 * self.freq:
            steps = self.freq * 5
        else:
            steps = (self.freq - (self.rank - self.freq * 2)) * 5
        return steps

    @property
    def topFaces(self):
        return self.facess[0]
    @property
    def midFaces(self):
        return self.facess[1]
    @property
    def bottomFaces(self):
        return self.facess[2]
    @property
    def botFaces(self):
        return self.facess[2]
    @property
    def radius(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)

    def __repr__(self):
        return f'num {self.num}, rank {self.rank}, face {self.face}, step {self.step}, nnbrs {self.nnbrs}, dupl {self.dupl}, coords ({self.x:1.2f}, {self.y:1.2f}, {self.z:1.2f})'
    def __str__(self):
        return f'{self.num}, {self.rank}, {self.face}, {self.step}, {self.nnbrs}, {self.dupl}, {self.x:1.2f}, {self.y:1.2f}, {self.z:1.2f}'

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
