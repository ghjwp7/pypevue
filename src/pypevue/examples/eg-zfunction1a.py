#!/usr/bin/python3
# -*- mode: python;  coding: utf-8 -*-

'''Make 3D points for trying triangulation functionality & timing'''

# Example of use:
#     ./eg-zfunction1a.py 90 4 2 1 2 4 && pypevu xyz

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

def makeBaseData(ngrid=24, edgew=5, params=[3, 2.3, 7, 0.7], smooth=1):
    '''Make a square grid of points, with zero z values at all points;
    evaluate some parametric functions to set some non-zero z values;
    then relax it a few iterations.    '''
    trapi, sqMul, tadd, tmul = params
    def fx(t): return cos(t)
    def fy(t): return sin(t*sqrt(t/2.3))
    def fv(t): return fx(t+tadd)
    def fw(t): return fy(t*tmul)

    scell = ngrid+2*edgew;  sstep = 2/ngrid;  snil = scell//2
    #print (scell, sstep, snil)
    cells = [0]*scell
    for i in range(scell):
        cells[i] = [0]*scell

    tn = int(trapi*ngrid*ngrid);  tstep = trapi*pi/tn
    #print (tn, tstep, tn*tstep, tn*tstep/pi)
    for k in range(tn):
        t = k*tstep
        for fa, fb in ((fx,fy),(fv,fw)):
            ix = max(0,min(scell-1, int(fa(t)/sstep+snil)))
            iy = max(0,min(scell-1, int(fb(t)/sstep+snil)))
            cells[iy][ix] += 1
            #print (f'{t:6.3f}  fa {fa(t):6.3f}  fb {fb(t):6.3f}  ix {ix:2}  iy {iy:2}')

    # Smooth via some relaxation sweeps
    for sweepn in range(smooth):
        for k in range(scell):
            for j in range(1,scell-1):
                t = sum(cells[k][l] for l in (j-1,j,j+1))
                a = t//3
                cells[k][j-1] = cells[k][j+1] = a
                cells[k][j] = t-2*a
        for k in range(scell):
            for j in range(1,scell-1):
                t = sum(cells[l][k] for l in (j-1,j,j+1))
                a = t//3
                cells[j-1][k] = cells[j+1][k] = a
                cells[j][k] = t-2*a

    # Output x,y,z values, except where cellss have equal neighbors
    nout = 0
    with open('xyz', 'w') as f:
        # Make autoMax non-zero so writeCylinders doesn't close module
        f.write('=P Plugins=examples.autoAdder3e\n=P postHi=.4     postDiam=.4   autoList=f   pDiam=.3  autoMax=1\n=L C ')
        for j in range(scell-1):
            for k in range(scell-1):
                if cells[j][k] != cells[j+1][k] and cells[j][k] != cells[j][k+1]:
                    f.write(f'{j} {k} {cells[j][k]} ')
                    nout += 1
        f.write(';\n=C Bpbb 0 0;\n')
    return nout
    
#--------------------------------------------------------------
if __name__ == '__main__':
    from sys import argv
    arn = 0
    arn+=1; ngrid = int(argv[arn])   if len(argv)>arn else 20
    arn+=1; trapi = float(argv[arn]) if len(argv)>arn else 3
    arn+=1; sqMul = float(argv[arn]) if len(argv)>arn else 2.3
    arn+=1; tadd  = float(argv[arn]) if len(argv)>arn else 7
    arn+=1; tmul  = float(argv[arn]) if len(argv)>arn else 0.7
    arn+=1; smoot = int(argv[arn])   if len(argv)>arn else 1
    nout = makeBaseData(ngrid, params=[trapi, sqMul, tadd, tmul], smooth=smoot)
    print (f'Wrote {nout} coordinates to file')
