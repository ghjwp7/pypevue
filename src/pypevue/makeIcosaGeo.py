#!/usr/bin/env python3
# jiw - 29 Feb 2020 - 1 July 2020 - 

# This generates geodesic dome point coordinates and edges.
# Clipping-box parameters allow some control over how much of the
# sphere is generated.  The orientation of the icosahedron has two
# controls: z angle and y angle rotation.  To see an example, try
# (from the pypevue directory within the source tree) the first of the
# next two lines; or after proper installation somewhere on the
# system, the second line, to get a pypevu.scad file:

#       ./makeIcosaGeo.py > t1-v; ./pypevu.py f=t1-v
#         makeIcosaGeo > t1-v;  pypevu f=t1-v

from pypevue import  ssq, sssq, Point, IcosaGeoPoint, Layout, FunctionList
from pypevue.baseFuncs import addEdges
from math import sqrt, pi, sin, cos, atan2, radians, degrees

def genTriangleK (layout, K, v0, v1, v2, pn):
    def genPoint(p, q, r):
        x = (p*v0.x + q*v1.x + r*v2.x)/K
        y = (p*v0.y + q*v1.y + r*v2.y)/K
        z = (p*v0.z + q*v1.z + r*v2.z)/K
        t = sssq(x,y,z)         # t = distance to origin
        layout.posts.append(IcosaGeoPoint(x/t,y/t,z/t, K))
        if pn-ro <= re:  addEdges(pn, pn-ro,   layout)        
        if pn-ro > rbp:  addEdges(pn, pn-ro-1, layout)        
        if pn    >  rb:  addEdges(pn, pn-1,    layout)
        return pn+1

    # Triangulate the face with corners v0,v1,v2; stepping row by row
    # from point v0 toward v1 (hence decreasing a, increasing b), and
    # in each row stepping across from the v0-v1 side toward the v0-v2
    # side (hence decreasing e, increasing f).  Neighbor tracking
    # looks to the left and looks up both left and right.  rb tracks
    # beginning of current row.  rbp and re track beginning and end of
    # previous row.  Frequency = K.
    rbp = rb = pn+2; re = -1;  ro=0
    a,b,c = K, 0, 0;     pn=genPoint(a,b,c)
    rbp = re = pn; rb = pn
    for ro in range(1,1+K):
        a -= 1;  b += 1; pn=genPoint(a,b,c)
        e,f = b,c
        for co in range(ro):
            e -= 1;  f += 1; pn=genPoint(a,e,f)
        rbp = rb; re = pn-1; rb = pn

# See if point p is in box with corners given by elements of clip1, clip2
def pointInBox (p, clip1, clip2):
    xlo, xhi = min(clip1.x, clip2.x), max(clip1.x, clip2.x)
    ylo, yhi = min(clip1.y, clip2.y), max(clip1.y, clip2.y)
    zlo, zhi = min(clip1.z, clip2.z), max(clip1.z, clip2.z)
    return xlo <= p.x <= xhi and ylo <= p.y <= yhi and zlo <= p.z <=zhi

def CCW(p):    # To sort points by descending z and clockwise about z
    return -round(p.z*100000)-atan2(p.y,p.x)/8
def FRA(p):    # To sort points by rank from 0 and clockwise about z
    return p.rank - atan2(p.y,p.x)/8

# sortRZ -- To sort points by rank from 0 and clockwise about z always
# starting a new rank on an icosahedron edge.  Note: this only works
# with zAngle == 0, so if you want this to work, don't rotate.
def sortRZ(p, Vfreq):
    angle = atan2(p.y,p.x) #angle from -pi to +pi (-180deg to 180deg)
    # our vertical edge 0 point is at 180 degrees.  If a rounding error occurs, this could
    # become -180 degrees.  Adjust the value to make sure this does not happen
    tweak = (2*pi) / (Vfreq * 5) / 4
    angle -= tweak
    if angle < -pi:
        angle += 2*pi
    if Vfreq < p.rank <= Vfreq * 2: # our 0 edge is on a ~36deg angle
        # each segment makes an approximate angle of 360 / number of segments around the dome
        # each rank has a number of segments offset from the center, e.g. 0.5, 1, 1.5, 2, ...
        segAngle = 2*pi / (Vfreq * 5)
        segsOffset = ((p.rank - Vfreq) / 2)
        angle += segAngle * segsOffset
    elif p.rank > Vfreq * 2:
        # the center line is offset by half a pentagon segment (360/10)
        angle += (2*pi) / 10
    if angle > pi:
        angle -= 2*pi
    sortVal = p.rank - angle/8  # Divide angle by a number > 2*pi
    return sortVal

def dedupClip(phase, layi, layo, clip1, clip2, Vfreq = 1):
    '''Given list of points via layi, return de-duplicated and clipped
    list etc'''
    L  = layi.posts
    # eps should be smaller than actual point to point distances,
    # but larger than possible floating point rounding error.
    # For example, .001 is too big to work ok at freq=36.
    eps = 0.00001   # Good enough for freq 36, where .001 is too big
    pprev = Point(9e9, 8e8, 7e7)
    for n, p in enumerate(L): p.dex = n
    L.sort(key = CCW if phase==1 else lambda p: sortRZ(p, Vfreq))
    transi = {} # Make node-number translation table for merged points
    if phase==1:
        for p in L:  p.dupl = 1 # how many duplicates of point
    for p in L:
        me = p.dex; del p.dex
        if pointInBox (p, clip1, clip2):
            if ssq(*(p.diff(pprev))) > eps:
                layo.posts.append(p)
            elif phase==1: pprev.dupl += 1
            transi[me] = len(layo.posts)-1
        else:          # p is out-of-box; remove its edge evidence
            nbrs = layi.edgeList[me]
            for nbr in nbrs:    # Get rid of all refs to me
                layi.edgeList[nbr].remove(me)
            del layi.edgeList[me] # Get rid of me
        pprev = p
        
    # Translate all edge numbers in the edgeList to merge points
    el = layi.edgeList
    for i in el.keys():
        v = transi[i]
        for j in el[i]:
            w = transi[j]
            addEdges(v, w, layo)

def genIcosahedron(layin, Vfreq, clip1, clip2, rotay, rotaz):
    '''Generate points and edges for triangulated icosahedral faces.
    Rotate basic icosahedron faces about y by ry degrees, and about z
    by rz degrees. Use genTriangleK to triangulate feasible faces at
    frequency K=Vfreq.  Use dedupClip to discard corners outside of box
    clip1, clip2.  Ref: "Geodesic Domes", by Tom Davis - a pdf file -
    pp. 5-10 ; and note, "The vertices of an icosahedron centered at
    the origin with an edge-length of 2 and a circumradius of sqrt(phi
    +2) ~ 1.9 are described by circular permutations of (0, ±1, ±ϕ)
    where ϕ = 1 + √5/2 is the golden ratio", from
    https://en.wikipedia.org/wiki/Regular_icosahedron#Cartesian_coordinates
    '''
    phi = (1+sqrt(5))/2
    cornerNote = 'oip ojp ojq oiq  poi qoi qoj poj  ipo jpo jqo iqo'
    facesNote = 'aij ajf afb abe aei bfk bkl ble cdh chl clk ckg cgd dgj dji dih elh ehi fjg fgk'
    corr1 = {'o':0, 'i':1, 'j':-1, 'p':phi, 'q':-phi}
    corners = [Point(corr1[i], corr1[j], corr1[k]) for i,j,k in cornerNote.split()]
    # Rotate corners by rz, ry degrees. See:
    # https://en.wikipedia.org/wiki/Rotation_matrix#General_rotations
    ry, rz = radians(rotay), radians(rotaz)
    sa, ca, sb, cb = sin(rz), cos(rz), sin(ry), cos(ry)
    rox = Point(ca*cb,  -sa,  ca*sb)
    roy = Point(sa*cb,   ca,  sa*sb) # Set up x,y,z rows
    roz = Point(-sb,      0,  cb)    #   of Z,Y rotation matrix
    oa = ord('a')
    # Init empty layouts for local use (ie before deduplication)
    laylo1 = Layout(posts=[], cyls=[],  edgeList={})
    laylo2 = Layout(posts=[], cyls=[],  edgeList={})
    # Now make faces, and triangulate those that look feasible
    for i,j,k in facesNote.split():
        pp, qq, rr = corners[ord(i)-oa], corners[ord(j)-oa], corners[ord(k)-oa]
        # Rotate each of the pp, qq, rr faces in space by Z and Y degrees
        p = Point(rox.inner(pp), roy.inner(pp), roz.inner(pp))
        q = Point(rox.inner(qq), roy.inner(qq), roz.inner(qq))
        r = Point(rox.inner(rr), roy.inner(rr), roz.inner(rr))
        # Now maybe triangulate this face if any of its corners are in
        # box.  (When box & face intersection is strictly inside the
        # face we mess up and don't process it.  Oh well.)
        if pointInBox(p,clip1,clip2) or pointInBox(q,clip1,clip2) or pointInBox(r,clip1,clip2):
            pn = len(laylo1.posts)
            genTriangleK (laylo1, Vfreq, p, q, r, pn)
            #print (f'=   {len(laylo1.posts):3} posts after face {i}{j}{k}')
        else:
            #print (f'=   {len(laylo1.posts):3} posts after face {i}{j}{k} skipped')
            pass
    # Have done all faces.  Now dedup & clip laylo and copy points into layin
    dedupClip(1, laylo1, laylo2, clip1, clip2)
    #print (f'=  Made {len(laylo2.posts)} posts for geodesic with frequency {Vfreq}')
    
    # Find ranks, or number of rows down from rank-0 center point.
    po = laylo2.posts; elo = laylo2.edgeList;  infin = Vfreq*20
    for k,p in enumerate(po):
        p.num=k;   p.pa = p.pb = p.rank = infin  # Set stuff large
    if len(po): po[0].rank = 0
    for p in po:
        p.nnbrs = len(elo[p.num])
        for dq in elo[p.num]:
            q = po[dq]
            if 1+p.rank < q.rank: # Is p the new pop of q?
                q.pa, q.pb, q.rank = p.num, p.num, 1+p.rank
            elif p.rank < q.rank: # Is p the new mom of q?
                q.pb = p.num
    dedupClip(2, laylo2, layin, clip1, clip2, Vfreq)

    #add face, step, stepInRank
    po = layin.posts; rank = -1; stepsPerFace = [0,0];
    for p in po:
        if p.rank != rank:
            rank = p.rank; faceIdx = 0; step = 0; stepInRank = 0
            if rank == 0:
                faces = p.topFaces
                stepsPerFace[0] = 0
            elif rank == Vfreq * 2:
                faces = p.bottomFaces
                stepsPerFace[0] = Vfreq
            elif rank == Vfreq + 1:
                faces = p.midFaces
                stepsPerFace = [Vfreq-1,1]
            elif rank <= Vfreq:
                stepsPerFace[0] += 1
            elif rank < Vfreq * 2:
                stepsPerFace[0] -= 1
                stepsPerFace[1] += 1
            else:
                stepsPerFace[0] -= 1

        #print(f'TMPDEBUG faces {faces}, faceIdx {faceIdx}')
        p.face = faces[faceIdx]
        p.step = step
        p.stepInRank = stepInRank
        step += 1
        stepInRank += 1
        #print(p)
        if rank <= Vfreq or rank >= Vfreq * 2:
            if step == stepsPerFace[0]:
                faceIdx += 1; step = 0
        else:
            idx = faceIdx % 2
            if step == stepsPerFace[idx]:
                faceIdx += 1; step = 0

# 3 Aug 2020: jiw removed code from "if __name__ == '__main__'" to end
# of file as no longer relevant
