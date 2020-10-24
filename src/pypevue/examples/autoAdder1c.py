#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This code is used by variants of eg-auto-8-237 and eg-auto-test-2
# that are examples to demonstrate automatically making edges
# (cylinders) between posts.  When the distance between two posts is
# small enough, a cylinder is developed for that pair of posts.

# pypeVue's automatic-edge algorithm is simple-minded.  It merely
# generates all edges with lengths not exceeding a cutoff limit,
# autoMax.  If autoMax is overly large, edges may be generated that
# are not part of a valid triangulation.  It might generate edges that
# cross.

# Parameters that control this version of autoAdder:

# `autoMax` is the maximum length generated edges can have.  Its
# default value is 0, which suppresses edge generation.

# `autoList` says whether to list automatically-generated edges.
# autoList=f says to not list auto-edges.  autoList=t would list them.

from pypevue import FunctionList as ref, Cylinder
#----------------------------------------------------------------
def autoAdder(fout):    # See if we need to auto-add cylinders
    rlo = ref.LO
    cyls  = rlo.cyls            # List of cylinders
    posts = rlo.posts           # List of posts
    edgeList = rlo.edgeList     # List of edges
    nPosts = len(posts)
    clo = len(cyls) # Record how many cylinders are already processed
    # in this version punt color, thix, levels ...
    colo, thix, lev1, lev2 = 'B', 'p', 'c','c'
            
    cutoff = ref.autoMax
    if cutoff > 0:     # See if any way for any more edges
        print (f'In auto-add, cutoff distance autoMax is {cutoff:7.3f}')
        cutoff2 = cutoff*cutoff
        for pn in range(nPosts):
            p = posts[pn].foot
            for qn in range(1+pn, nPosts):
                q = posts[qn].foot
                t = p-q
                if abs(t.x) > cutoff or abs(t.y) > cutoff:
                    continue
                d2 = t*t        # mag^2 of p-q
                if d2 > cutoff2: continue
                if pn not in edgeList or qn not in edgeList[pn]:
                    ref.addEdges(pn, qn, rlo)
                    cyls.append(Cylinder(pn,qn, lev1, lev2, colo, thix, ref.endGap, 0,0))
        ref.writeCylinders(fout, clo, len(cyls), ref.autoList, 2)
#----------------------------------------------------------------
def tell():
    return (autoAdder, )
