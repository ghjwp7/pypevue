#!/usr/bin/env python3
# -*- coding: utf-8 -*- -- jiw 15 Oct 2020

# This pypevu plugin develops Delaunay triangulations.  Is used by
# variants of eg-auto-8-237 and eg-auto-test-2 for automatically
# making edges (cylinders) between posts.

# pypevu has two parameters related to automatic-edge generation:
# `autoMax`  - Not used here; is used in autoAdder1c
# `autoList` - Whether to list generated edges.  autoList=t says to
# list auto-edges; autoList=f says no.
from math import sqrt
from pypevue import Point, Cylinder, FunctionList as ref
from nearby.delaunay import Vert, Triangulate
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
    # Get Delaunay triangulation of verts
    sverts, tris, cache = Triangulate(verts)
    print (f'tris has {len(tris)} faces, ({tris[0]})...({tris[-1]})')
    # Make cylinders for Delaunay edges (from low post# to high#)
    for f in tris:  # f is a Face in Delaunay triangulation (3 post #s)
        if f.canon in cache:
            ctr, rr = cache[f.canon]
            if rr>(ref.autoMax**2)/4:
                fout.write(f'  *translate([{ctr}]) sphere(r={sqrt(rr):0.2f}); // {ref.autoMax}\n')
        pvn = f.p3              # pvn is previous vert number
        for cvn in f.get123:    # cvn is current vert number
            pa, pb = verts[pvn].num, verts[cvn].num
            #print (f'Cyl gen:  test  pvn {pvn}, cvn {cvn} ie pa {pa}, pb {pb}')
            pa, pb = min(pa,pb),  max(pa,pb)
            if pa not in edgeList or pb not in edgeList[pa]:
                if (verts[pvn]-verts[cvn]).mag() < ref.autoMax:
                    #print (f'Posts {pa},{pb} are {(verts[pvn]-verts[cvn]).mag()} apart.')
                    ref.addEdges(pa, pb, rlo)
                    cyls.append(Cylinder(pa,pb, lev1, lev2, colo, thix, ref.endGap, 0,0))
                else: print (f'Posts {pa},{pb} are {(verts[pvn]-verts[cvn]).mag()} apart')
            pvn = cvn
    ref.writeCylinders(fout, clo, len(cyls), ref.autoList, 2)
#==============================================================
def tell():
    return (autoAdder,)
