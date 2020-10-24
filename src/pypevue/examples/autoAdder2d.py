#!/usr/bin/env python3
# -*- coding: utf-8 -*- -- jiw 15 Oct 2020

# Delaunay triangulations are developed for examples that use this
# plugin.  Among examples, it is used by variants of eg-auto-8-237 and
# eg-auto-test-2 for automatically making edges (cylinders) between
# posts.

# pypevu has two parameters related to automatic-edge generation:
# `autoMax`  - Not used here; is used in autoAdder1c
# `autoList` - Whether to list generated edges.  autoList=t says to
# list auto-edges; autoList=f says no.

from pypevue import Point, Cylinder, FunctionList as ref
#==============================================================
class Face:                     # Class for triangular faces
    def __init__(self, p1,p2,p3):
        self.p1, self.p2, self.p3 = p1, p2, p3
    @property    # t.get123 is the point numbers of triangle t
    def get123(self): return self.p1, self.p2, self.p3
    def __str__(t):   return f'({t.p1:3}, {t.p2:3}, {t.p3:3})'
    @property    # t.canon is a canonical signature for point#s of t
    def canon(self):  return tuple(set(self.get123))
#==============================================================
class Vert(Point):
    def __init__(self, p, num):
        self.x, self.y, self.z, self.num = p.x, p.y, p.z, num
#==============================================================
def autoAdder(fout):
    rlo = ref.LO
    cyls  = rlo.cyls            # List of cylinders
    posts = rlo.posts           # List of posts
    edgeList = rlo.edgeList     # List of edges
    nPosts = len(posts)
    clo = len(cyls) # Record how many cylinders are already processed
    # in this version punt color, thix, levels ...
    colo, thix, lev1, lev2 = 'B', 'p', 'c','c'

    # Make list of post locs in verts, recording original post numbers
    verts = [Vert(p.foot, pn) for pn, p in enumerate(posts)]
    print (f'verts has {len(verts)} points, ({verts[0]})...({verts[-1]})')
    tris = Triangulate(verts)  # Get Delaunay triangulation of verts
    print (f'tris has {len(tris)} faces, ({tris[0]})...({tris[-1]})')
    # Make cylinders for Delaunay edges (from low post# to high#)
    for f in tris:  # f is a Face in Delaunay triangulation (3 post #s)
        pvn = f.p3              # pvn is previous vert number
        for cvn in f.get123:    # cvn is current vert number
            va, vb = min(pvn,cvn),  max(pvn,cvn)
            pa, pb = verts[va].num, verts[vb].num
            if pa not in edgeList or pb not in edgeList[pa]:
                ref.addEdges(pa, pb, rlo)
                cyls.append(Cylinder(pa,pb, lev1, lev2, colo, thix, ref.endGap, 0,0))
    ref.writeCylinders(fout, clo, len(cyls), ref.autoList, 2)
#==============================================================
def Triangulate(pxy):
    #  Accepts a list pxy of Points in array pxy. Note, Triangulate
    #  mods pxy by sorting it and by adding 3 `super-triangle` points
    #  at end
    
    #  Returns a list tris of triangular Face elements, with vertices
    #  of each face in `clockwise` order.  CW may be ambiguous for
    #  folded 3D structures; do your own orientation if it matters.
    
    # The code in this half-3D routine was adapted from
    # triangulate.py, a 2D 22 Oct 2020 python version by James Waldby
    # of code in 2D Delauney triangulation programs by: Paul Bourke,
    # c, 1989; fjenett, java, 2005; Gregory Seidman, ruby, 2006.  See
    # links at http://paulbourke.net/papers/triangulate/

    pxy.sort(key=lambda p: p.x) # Sort points on ascending x coordinate
    # Allocate memory for the completeness list, flag for each triangle
    nv = len(pxy)
    trimax = 4 * nv           # Upper bound on resulting triangles count
    complete = [False]*trimax # No triangle is complete yet
    tris = [0]*trimax
    #  Find maximum and minimum vertex bounds, for calculation of
    #  bounding triangle (supertriangle)
    xmin, xmax = min(v.x for v in pxy), max(v.x for v in pxy)
    ymin, ymax = min(v.y for v in pxy), max(v.y for v in pxy)
    dx,  dy = xmax - xmin, ymax - ymin
    dmax = dx if dx > dy else dy
    xmid, ymid = (xmax + xmin) / 2.0, (ymax + ymin) / 2.0
    
    print (f'\n xmin:{xmin:0.2f}   xmax:{xmax:0.2f}   ymin:{ymin:0.2f}   ymax:{ymax:0.2f}  \n dx:{dx:0.2f}   dy:{dy:0.2f}   dmax:{dmax:0.2f}   xmid:{xmid:0.2f}   ymid:{ymid:0.2f}\n')
    
    #  Set up the supertriangle, a triangle to encompass all the sample
    #  points.  Its coordinates are added at the end of the vertex list
    #  and as the first triangle in the triangle list.
    pxy.append(Point(xmid - 20 * dmax, ymid - dmax))
    pxy.append(Point(xmid,        ymid + 20 * dmax))
    pxy.append(Point(xmid + 20 * dmax, ymid - dmax))
    print (f'Super-triangle: ({pxy[-3]}), ({pxy[-2]}), ({pxy[-1]})\n')
    tris[0] = Face(nv, nv+1, nv+2)
    complete[0] = False
    ntri = 1
    cache = {}
    #  Add points one by one into tris, the present state of mesh
    for i in range(nv):
        xp, yp = pxy[i].x, pxy[i].y
        #  Set up edge buffer.  If point (xp,yp) being added is inside
        #  circumcircle of some triangle T, then edges of T get put into
        #  edge buffer, and T gets removed from tris.
        j, nedge, edges = 0, 0, []  # edges are in class IEDGE
        while j < ntri:
            if complete[j]:
                j += 1; continue # Skip tests if triangle j already done
            threep = [pxy[p] for p in tris[j].get123]
            inside, xc, yc, rr = CircumCircle(xp, yp, threep, tris[j].canon, cache)
            if xc < xp and (xp-xc)*(xp-xc) > rr:
                complete[j] = True # Due to x-sorting of pxy, j is done
            if inside:             # Add 3 edges into edge buffer
                nedge += 3
                p1, p2, p3 = tris[j].get123
                edges.append((p1, p2))
                edges.append((p2, p3))
                edges.append((p3, p1))
                ntri -= 1
                tris[j] = tris[ntri]
                complete[j] = complete[ntri]
                j -= 1
                if not ntri: break
            j += 1

        # Tag [ie mark out] multiple edges [edges shared by different
        # triangles].  Note: if all triangles are specified
        # anticlockwise then all interior edges are opposite pointing
        # in direction, as tested for first.
        for j in range(nedge-1):
            for k in range(j+1, nedge):
                # 1-2, 2-1 case ...
                if edges[j][0]==edges[k][1] and edges[j][1]==edges[k][0]:
                    edges[j] = edges[k] = (-1,-1) # Remove jth & kth edges

                #  1-1, 2-2 case ... shouldn't need it, see above
                if edges[j][0]==edges[k][0] and edges[j][1]==edges[k][1]:
                    edges[j] = edges[k] = (-1,-1) # Remove jth & kth edges

        # Form new triangles for the current point.  Skipping over any
        # tagged edges.  All edges are arranged in clockwise order.
        for j in range(nedge):
            if edges[j][0] < 0 or edges[j][1] < 0:
                continue
            if ntri >= trimax: return None # c version returns status 4
            tris[ntri] = Face(edges[j][0], edges[j][1], i)
            complete[ntri] = False
            ntri += 1

    # Remove triangles with supertriangle vertices (triangles which
    # have a vertex numbered > nv)
    i = 0
    while i < ntri:
        if tris[i].p1 >= nv or tris[i].p2 >= nv or tris[i].p3 >= nv:
            ntri -= 1
            tris[i] = tris[ntri]
            i -= 1
        i += 1
 
    tris = tris[:ntri]
    return tris
#==============================================================
def CircumCircle3(p, threep, canon, cache):
    pass
#==============================================================
def CircumCircle2(xp, yp, threep, canon, cache):
    # Returns a four-tuple, (inside, xc, yc, rr) where `inside` is
    # True if point (xp,yp) is inside the circumcircle that points p1,
    # p2, p3 define.  `xc, yc` is circumcircle center.  `rr` is
    # squared radius r of circumcircle.  Points on edge of circle
    # register as inside it.  xc, yc, and r are obtained from cache if
    # possible.
    EPSILON = 1e-8              # (not specified in C program??)
    # Timings for tests of 1000, 2000, 4000, 8000 points:
    # 0.221, 0.598, 1.828, 5.924 seconds with caching
    # 0.273, 0.731, 2.210, 7.000 seconds without caching
    if canon in cache:
        xc, yc, rsqr = cache[canon]
        drsqr = (xp-xc)**2+(yp-yc)**2
        # Return true if point is in or on circumcircle
        return drsqr-rsqr < EPSILON, xc, yc, rsqr

    # Check for coincident points
    p1, p2, p3 = threep
    if abs(p1.y-p2.y) < EPSILON and abs(p2.y-p3.y) < EPSILON:
        return False,0,0,0

    if abs(p2.y-p1.y) < EPSILON:
        m2 = - (p3.x-p2.x) / (p3.y-p2.y)
        mx2 = (p2.x + p3.x)/2
        my2 = (p2.y + p3.y)/2
        xc = (p2.x + p1.x)/2
        yc = m2 * (xc - mx2) + my2
    elif abs(p3.y-p2.y) < EPSILON:
        m1 = - (p2.x-p1.x) / (p2.y-p1.y)
        mx1 = (p1.x + p2.x)/2
        my1 = (p1.y + p2.y)/2
        xc = (p3.x + p2.x)/2
        yc = m1 * (xc - mx1) + my1
    else:
        m1 = - (p2.x-p1.x) / (p2.y-p1.y)
        m2 = - (p3.x-p2.x) / (p3.y-p2.y)
        mx1 = (p1.x + p2.x)/2
        mx2 = (p2.x + p3.x)/2
        my1 = (p1.y + p2.y)/2
        my2 = (p2.y + p3.y)/2
        xc = (m1 * mx1 - m2 * mx2 + my2 - my1) / (m1 - m2)
        yc = m1 * (xc - mx1) + my1

    rsqr  = (p2.x-xc)**2 + (p2.y-yc)**2
    drsqr = (xp-xc)**2   + (yp-yc)**2
    # Cache the center and rsqr
    cache[canon] = (xc, yc, rsqr)
    # Return true if point is in or on circumcircle
    return drsqr-rsqr < EPSILON, xc, yc, rsqr
#==============================================================
def tell():
    return (autoAdder,)
