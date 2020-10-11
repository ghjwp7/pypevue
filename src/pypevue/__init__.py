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
    '''3D (x,y,z) points or vectors, with methods and overloaded operators.

    Methods include scale, scalexy, inner, cross, norm (a unit
    vector), mag (scalar magnitude), diff, add.

    Overloaded operators are + - * & as follows, where u, v are
    vectors and s is a scalar:

    u + v   Vector sum of u and v
    u - v   Vector difference, u-v
    u * v   Dot or inner product (a scalar), equal to u.dot(v)
    u & v   Cross product, u x v, a vector,  equal to u.cross(v)
    s * v   Scalar times vector (scaled vector)
            (Note, v * s is not supported)

    '''
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z        
    def __add__(self, v):
        '''Vector sum, self + v'''
        return Point(self.x+v.x, self.y+v.y, self.z+v.z)
    def __sub__(self, v):
        '''Vector difference, u-v'''
        return Point(self.x-v.x, self.y-v.y, self.z-v.z)
    def __mul__(self, v):
        '''Scalar, dot product of self with argument q'''
        return self.x*v.x + self.y*v.y + self.z*v.z
    def __rmul__(self, s):
        '''s * v is a scaled vector, s times self'''
        return Point(s*self.x, s*self.y, s*self.z)
    def __and__(self, v):
        '''Vector cross product, self cross v'''
        return Point(self.y*v.z - self.z*v.y, self.z*v.x - self.x*v.z, self.x*v.y - self.y*v.x)
    def __getitem__(self, key):
        '''Return x, y, or z for indices 0, 1, 2'''
        if key<2:
            if key: return self.y
            else: return self.x
        if key>2: raise IndexError
        else: return self.z
    
    def add(self, q):
        '''Return a vector sum, self + arg'''
        return self + q
    def diff(self, q):
        '''Vector difference'''
        return self - q
    def inner(self, q):
        '''Scalar inner product of self with vector q'''
        return self * q
    def cross(self, q):
        '''Vector cross product, self cross q'''
        return self & q
    
    def mag(self):
        '''Return magnitude of vector self; equal to sqrt(s dot s')'''
        return sssq(self.x, self.y, self.z)
    def mag2(self):
        '''Square of magnitude of vector self; equal to s dot s' '''
        return ssq(self.x, self.y, self.z)
    def norm(self):
        '''Return a unit vector, aligned with self; or (0,0,0)'''
        mag = sssq(self.x, self.y, self.z)
        if mag == 0: return Point(0, 0, 0)
        return Point(self.x / mag, self.y / mag, self.z / mag)
    
    def scale(self, s):         # 
        '''Scale self in place, with argument = scale factor s'''
        self.x = s*self.x;  self.y = s*self.y;  self.z = s*self.z
    def scalexy(self, s):       # (s*self.x, s*self.y,  self.z)
        '''Scale the x and y components of self, in place.'''
        self.x = s*self.x;  self.y = s*self.y

    # For more information about nutation and precession, see eg
    # https://demonstrations.wolfram.com/EulerAnglesPrecessionNutationAndSpin/
    # Generally, if we have an item projecting from the side of a
    # post, precession is that item's angular position about the axis
    # of the post when the post is in position, and nutation is the
    # angle between the post's axis and the item's axis
    def nutation(self, q):
        '''Let s = self; let d = q-s = vector from s to q; and let p = plane
        that's tangent at point s to the sphere of which vector s is a
        radius.  Return angle (in degrees) between d and p.  Reference:
        https://www.superprof.co.uk/resources/academic/maths/analytical-geometry/distance/angle-between-line-and-plane.html        '''
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
        plInnerQP = pl.inner(q-p)
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
        '''Return shortest distance from self to the plane with normal pl
        '''
        return self.inner(pl.norm())

    def projectionOnPlane(self, pl):
        '''Find projection of self onto plane with normal pl
        '''
        plNorm = pl.norm()
        pPerpMag = self.inner(plNorm)
        plNorm.scale(pPerpMag)
        pPerp = plNorm
        return self.diff(pPerp)

    def angle(self, q):
        '''Return angle (in degrees) between vector self and vector q
        '''
        try:
            angleCos = self.inner(q) / (self.mag() * q.mag())
        except ZeroDivisionError as e:
            angleCos = -1
        angleCos = min(1, max(-1, angleCos))
        return degrees(acos(angleCos))

    def precession(self, q, show=False):
        '''Return angle (in radians) from the plane created by the tangent
        line to the circle on the sphere at height z and the origin,
        to the vector from this point to q.  Reference:
        https://www.youtube.com/watch?v=Zbiclnu2IlU @ 14:50 min:sec '''
        p = self
        if show: print(f'in precession() with p ({p}), q ({q})')

        # we need to remove the effects of the nutation angle on the precession angle
        # define the plane tangent to the sphere at p
        pltsNorm = Point(2*p.x, 2*p.y, 2*p.z).norm()
        nut = radians(self.nutation(q))

        # Find the component of q-p perpendicular to the tangent plane of the sphere at p
        qMpMag = (q-p).mag()
        pltsMag = sin(nut)*qMpMag
        pqPerp = pltsMag * pltsNorm
        m = qMpMpqPerp = (q-p)-pqPerp
        qProj = p+m
        
        if show:
            qProj = p+qMpMpqPerp
            nutCheck = radians(self.nutation(qProj))
            ### print may need fix for some tmp vars refactored out
            print(f'  pltsNorm ({pltsNorm}), nutation {degrees(nut):1.2f}deg, qMp ({qMp}), qMpMag {qMpMag:1.2f}, pltsMag = {pltsMag:1.2f}, pqPerp = ({pqPerp}), qMpMpqPerp = ({qMpMpqPerp}), qProj ({qProj}),  nutCheck {degrees(nutCheck):1.2f}deg (should be 0)')

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
            pltc = 2*pl
            if show: print(f'  tangent vector ({tv}), points on tangent line: p ({p}), t ({t}), pltc ({pltc})')

        angle = self._angleLineSlopeToPlane(pltc, m)
        pXpltc = p & pltc  # p cross pltc
        if show: print(f'  raw angle {degrees(angle):1.2f}deg, pltc.inner(qProj) {pltc.inner(qProj)}, tv.inner(qProj) {tv.inner(qProj)}, pXpltc.inner(qProj) {pXpltc.inner(qProj)}')
        # adjust the positive acute angle based on what quadrant it is in
        if pltc*qProj >= 0:  # 0-180 degrees since pltc dot qProj >= 0
            if pXpltc*qProj > 0:  # >90 since pXpltc dot qProj > 0
                angle = pi - angle
        else:  # 180-360
            if pXpltc*qProj < 0:  # >270 since pXpltc dot qProj < 0
                angle = pi - angle
            angle += pi           # fix quadrant in >270 case
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
                try:
                    m = importlib.import_module(toImp) # m is a module
                    mkeys = [obj for obj, pred in inspect.getmembers(m)]
                except ModuleNotFoundError:
                    print (f'**Error** Registrar fail for <{toImp}>')
                    next
                # If the module contains a `tell` object, try calling it.
                if 'tell' in mkeys:
                    try:  # Add functions from tell() into ref.fDict{}
                        for f in m.tell():
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
