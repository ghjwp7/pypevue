#!/usr/bin/python3
# -*- mode: python;  coding: utf-8 -*-

'''Make 3D points for trying triangulation functionality & timing'''

# Some examples of use:
#     ./eg-zrough3e.py 50 2 1   0 2    3 && pypevu xyz
#     ./eg-zrough3e.py 50 2 1   2 2    3 && pypevu xyz
#     ./eg-zrough3e.py 12 2 1.5 0 1    3 && pypevu xyz
#     ./eg-zrough3e.py 50 2 1   0 1.15 3 && pypevu xyz

# The __main__ portion of this file accepts five parameter values that
# control x-y grid size and the parametric functions fx, fy, fv, fw
# that produce x,y coordinates at which to make z values.  Then it
# calls makeBaseData() to write an x-y-z data set to file xyz, plus
# brief headers and footers making xyz suitable for input to pypevue.

# In makeBaseData, for t values in the range from 0 to pi*trapi, we
# evaluate (fx(t),fy(t)) and increase by 1 the raw z value in a cell
# near that location.  Similarly for (fv(t),fw(t)).  After raw z
# values have been set, one or more smoothing steps are made.  Then
# x,y,z values are written to file xyz for each cell whose z value
# differs from cell at right and cell below.

from math import sqrt, pi, sin, cos

def makeBaseData(ngrid, edgew, paramsets, smooth):
    '''Make a square grid of points, zeroed at all points; evaluate some
    parametric functions in (-1,1)x(-1,1) to set some cells non-zero;
    then relax cell values for a few iterations.    '''

    # Init all cells to zero, including edge-banding cells
    snil  = edgew + ngrid//2  # Zero is at center of banded grid
    edgeu = edgew + ngrid     # Upper edge of grid
    scell = 2*snil + 1        # Want odd cell count for smoothing
    sstep = 2/ngrid           # x or y step per cell with (-1,1) range
    zc = [0]*scell
    for i in range(scell):    # Initialize all the z cells to 0
        zc[i] = [0]*scell

    for params in paramsets:  # Each tuple in paramsets has 4 values
        trapi, tpow, tadd, tmul = params
        ntvals = int(trapi*ngrid*ngrid)
        tstep = trapi*pi/ntvals
        def fx(t): return cos(t)
        def fy(t): return sin(tmul*(t**tpow)+tadd)
        #def fy(t): return sin(t)
        print (f'Processing t from 0 to {trapi}*pi in {ntvals} steps;  tpow {tpow}, tmul {tmul}, tadd {tadd}')
        for k in range(ntvals):
            t = k*tstep
            ix = snil+int(fx(t)/sstep)
            iy = snil+int(fy(t)/sstep)
            if edgew <= ix <= edgeu and  edgew <= iy <= edgeu:
                zc[ix][iy] += 1

    # "Smooth" via some relaxation sweeps
    x = y = j = k = 1; dj=dk=1
    # Both ranges are odd in size so a cell's x,y differs each sweep
    print (f'scell {scell}   edgew {edgew}   edgeu {edgeu}')
    print (f'sweep    j     k     x     y   tot   qot')
    for sweepn in range(smooth):
        dj, dk = -dk, dj
        for aj in range(1,scell-1):
            j = aj if dj>0 else scell-1-aj
            for ak in range(1,scell-1):
                k = ak if dk>0 else scell-1-ak
                x, y = -y, x    # Gen.  -+  --  +-  ++  sequence
                # Kernel has 1 diagonal nbr and 2 opposite adjacent
                tot = zc[j][k] + zc[j+x][k+y] + zc[j-x][k] + zc[j][k-y]
                qot = tot//4
                if qot:
                    zc[j+x][k+y] = zc[j-x][k] = zc[j][k-y] = qot
                    zc[j][k] = tot-3*qot
                if qot<0 and (j>edgeu or k>edgeu) :
                    print (f'{sweepn:4}  {j:4}  {k:4}  {x:4}  {y:4}  {tot:4}  {qot:4}')
    # Output x,y,z values, except where zc's have equal neighbors
    nout = 0
    with open('xyz', 'w') as f:
        # Make autoMax non-zero so writeCylinders doesn't close module
        f.write('=P Plugins=examples.autoAdder3e\n=P postHi=.4     postDiam=.4   autoList=f   pDiam=.3  autoMax=1\n=L C ')
        for j in range(1,scell-1):
            for k in range(1,scell-1):
                if zc[j][k] != zc[j+1][k] and zc[j][k] != zc[j][k+1] or zc[j][k] != zc[j-1][k] and zc[j][k] != zc[j][k-1]:
                    f.write(f'{j} {k} {zc[j][k]} ')
                    nout += 1
        f.write(';\n=C Bpbb 0 0;\n')
    return nout
    
#--------------------------------------------------------------
if __name__ == '__main__':
    from sys import argv
    arn = 0
    arn+=1; ngrid = int(argv[arn])   if len(argv)>arn else 20
    arn+=1; trapi = float(argv[arn]) if len(argv)>arn else 2
    arn+=1; tpow  = float(argv[arn]) if len(argv)>arn else 1
    arn+=1; tadd  = float(argv[arn]) if len(argv)>arn else 0
    arn+=1; tmul  = float(argv[arn]) if len(argv)>arn else 1
    arn+=1; smoot = int(argv[arn])   if len(argv)>arn else 4
    nout = makeBaseData(ngrid, 10, [(trapi, tpow, tadd, tmul)], smoot)
    print (f'Wrote {nout} coordinates to file')
