#!/usr/bin/env python3
# -*- coding: utf-8 -*- -- jiw 15 Oct 2020

# This pypevu plugin develops Delaunay triangulations.  Is used by
# variants of eg-auto-8-237 and eg-auto-test-2 for automatically
# making edges (cylinders) between posts.  autoAdder3e was adapted
# from autoAdder2d by adding tests for 6NN nearest neighbor edges
# being included in Delaunay triangulations.  Let nbr(u) be the set of
# neighbors of u.  For each 6NN graph edge a-b not included among DT
# edges, code looks for DT edge c-d, with c, d in intersect(nbr(a),
# nbr(b)).  If length(c,d) > length(a,b) we remove c-d and replace it
# with a-b.  Note, this prelim version of autoAdder3e doesn't treat
# sets of common neighbors with more than 2 members.  (Geometrically
# unlikely in 2D; easy to find in 3D solid figures...)

# pypevu has two parameters related to automatic-edge generation:
# `autoMax`  - Used in test of whether to visualize circumcenters
# `autoList` - Whether to list generated edges.  autoList=t says to
# list auto-edges; autoList=f says no.
from math import sqrt
from pypevue import Point, Cylinder, FunctionList as ref
from nearby.delaunay import Vert, Triangulate
from nearby.kNN import PNN, doAMethod
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
    npoints = len(posts)
    def canon(j,k):             # Canonical reference for edge j-k
        return min(j,k)*npoints + max(j,k)
    def decanon(t):
        return t//npoints, t%npoints
    # Make list of post locs in verts, recording original post numbers
    verts  = [Vert(p.foot, pn) for pn, p in enumerate(posts)]
    print (f'verts has {len(verts)} points, ({verts[0]})...({verts[-1]})')
    # Get Delaunay triangulation of verts
    sverts, tris, cache = Triangulate(verts)
    print (f'tris has {len(tris)} faces, ({tris[0]})...({tris[-1]})')
    # Make DT edges dict and edges lists
    DTedges = {};  DTedgels = [0]*npoints
    for f in tris: # Make arrows to verts of faces
        cornerNums = f.get123      # Get triple of vert indices
        p = sverts[cornerNums[-1]]
        for kq in cornerNums:
            q = sverts[kq]
            DTedges[canon(p.num,q.num)] = 1
            if not DTedgels[p.num]:
                DTedgels[p.num] = []
            DTedgels[p.num].append(q.num)
            p = q
    for k in range(npoints):
        DTedgels[k] = set(DTedgels[k])
    # Make NN data and NN edges list; via list of PNN points in orig order
    # PNN.kNN needs to be set before we call doAMethod
    PNN.kNN = 1                           # We want exactly 1 nearest nbr
    PNN.kNN = 6                           # Actually, we want more than that
    Nverts = [PNN(p.foot.x,p.foot.y,p.foot.z) for p in posts] # PNN has .BSF[] for each point
    doAMethod(Nverts)
    NNedges = {}
    for jp, p in enumerate(Nverts):
        for kq in p.nBSF:
            NNedges[canon(jp,kq)] = 1
    #print(f'DTedges has {len(DTedges)} entries and NNedges has {len(NNedges)} entries, {[decanon(k) for k in sorted(NNedges.keys())]}')

    # Find edges that are in NN but not in DT
    for ne in NNedges:
        if not ne in DTedges:
            ea, eb = decanon(ne)
            dab = (Nverts[ea]-Nverts[eb]).mag2()
            nbrs = DTedgels[ea].intersection(DTedgels[eb])
            if len(nbrs) == 2:
                ec, ed = nbrs
                dcd = (Nverts[ec]-Nverts[ed]).mag2()
                # To get list of possible changes change 0 to nonzero
                if 0: print (f'Verts {ea}, {eb} at d^2 = {dab:0.3f}  Common neighbors: {nbrs} at d^2 = {dcd:0.3f}')
                if dab < dcd: # Install NN link a-b in place of DT link c-d
                    del DTedges[canon(ec,ed)]
                    DTedgels[ec].discard(ed)
                    DTedgels[ed].discard(ec)
                    DTedges[canon(ea,eb)] = 1
                    DTedgels[ea].add(eb)
                    DTedgels[eb].add(ea)
            elif len(nbrs) > 2:
                print(f'Not handling Verts {ea}, {eb}:  Too many common neighbors, {nbrs}')

    # Make cylinders for Delaunay edges (from low post# to high#)
    for e in sorted(DTedges.keys()):
        pa, pb = decanon(e)
        if pa not in edgeList or pb not in edgeList[pa]:
            ref.addEdges(pa, pb, rlo)
            cyls.append(Cylinder(pa,pb, lev1, lev2, colo, thix, ref.endGap, 0,0))
    ref.writeCylinders(fout, clo, len(cyls), ref.autoList, 2)
#==============================================================
def tell():
    return (autoAdder,)
