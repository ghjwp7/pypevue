#!/usr/bin/env python3

# jiw 26 Dec 2018
'''pypevu -- a program in the pypevue module, that generates OpenSCAD
code for tubes along selected edges between `posts` in a plane.  This
supports visualization of arrangements of edges in geodesic dome
structures, much like molecular stick-and-ball models, or like Tinker
Toys® models.'''

# This program processes a layout script and a cylinders script.  It
# generates an output file containing OpenSCAD code for 3D structures
# the scripts describe.  See `pypevu.dox.odt` for examples and
# details.  Note, pypevu may import from pypevue, makeIcosaGeo, and
# baseFuncs.  In a development environment, you may need to run the
# command "python3 -m site --user-site" and create a pypevue link in
# the directory it reports, eg ~/.local/lib/python3.6/site-packages
# (Also see bash scripts show-bin-lib-links and new-bin-lib-links).

#  *******  pypevu basics:  *******
#  A layout script tells where to locate posts.  It has entries with
#  type of pattern (polygon, rectangular grid, triangular grid),
#  numbers of corners, rows, or columns, and radius or spacing.

#  A cylinders script tells what post-to-post cylinders to make.  It
#  has entries with optional <color>, <diam>, <post>, and <level>
#  elements.  Each semicolon terminator invokes cylinder production.

# Optional parameters for this program are described in a table in
# pypevu.dox.odt, which tells how to specify parameter values endGap,
# postHi, pDiam, qDiam, SF, and numerous other params.  Parameter
# settings can appear on the command line as well as in =P lines of a
# scripts file.  A table in the documentation shows parameter names,
# parameter usage, and default values.

#  Note, an end gap is a small gap between a post and a cylinder end.
#  With endGap=3 default value, a gap of about 6 units is drawn
#  between the ends of cylinders meeting at the same point.  With
#  endGap=0, there'd be no gap.

# When modifying this code:
# (a) At outset (ie once only), at command prompt say:
#           SCF=pypevu.scad;  PYF=${SCF%.scad}.py
#           STF=${SCF%.scad}.stl; exec-on-change $PYF "python3 $PYF" &
#           echo $PYF, $SCF, $STF;  openscad $SCF &
#     [To avoid a 'Text file busy' shell error message, instead of
#      just saying  ./$PYF  the commands above use python to run $PYF]

#     [Bash script exec-on-change runs a command upon changes.  See
#      https://github.com/ghjwp7/plastics/blob/master/exec-on-change .
#      Or just run the program manually as needed.  When you are
#      working on a particular script S, you can replace the e-o-c
#      shown above with:    exec-on-change S "./pypevu f=S" &
#      which will run pypevu0 on S whenever you change the file S.]

# (b) After program changes that you want to see the effect of, save
#     the file.  The exec-on-change script will be informed of the
#     file change and will run $PYF.  Then [if openscad's `Design ->
#     Automatic Reload and Preview` option is on] openscad will see
#     that $SCF changed*, and re-render its image.

from sys import argv, exit, exc_info, stderr
import time, datetime
from math import sqrt, pi, cos, sin, asin, atan2
from pypevue import FunctionList, sssq
#---------------------------------------------------------
def setupData(c, readArgv = True):
    ref = FunctionList
    c.levels, c.thixx,  c.digits = 'abcde', 'pqrstuvw', '01234356789+-.'
    c.colorSet = {'G':'"Green"', 'Y':'"Yellow"', 'R':'"Red"', 'B':'"Blue"', 'C':'"Cyan"', 'M':'"Magenta"', 'W':'"White"', 'P':'[.5,0,.5]', 'A':'"Coral"'}
    c.colors = c.colorSet.keys()

    # Set initial values of main parameters
    c.pDiam,   c.qDiam,    c.dRatio   = 0.06, 0.02, sqrt(2)
    c.endGap,  c.postHi,   c.postDiam = 0.03, 0.16, c.qDiam
    c.f,       c.SF,    c.cylSegments = '', 100, 30
    c.paramTxt, c.postLabel= '', 'Bte' # Blue, size u, level e
    c.userCode = ''
    c.codeBase = f'pypevu.codeBase.scad' # SCAD functions for posts, cyls, etc
    c.scadFile = f'pypevu.scad'          # Name of scad output file
    c.postList = c.cylList = False # Control printing of post and cyl data
    c.Plugins, c.autoMax, c.autoList  = '', 0, True
    c.zSpread, c.zSize,   c.postAxial = False, 1, True
    c.userPar0 = c.userPar1 = c.userPar2 = '""'
    c.traceExec=False
    c.geoColors = 'YBRC'          # Colors for pentagons, rings, rays, seams
    c.script1 = '=P postDiam=.1 endGap=.05','=C Gpae 1,2;;;;1;Rea 1,2;;;;1;','=L C 0,0,0; P5,1,0;'
    if readArgv:
        for k in range(1,len(argv)):
            c.paramTxt = c.paramTxt + ' ' + argv[k]
        # Did we have exactly one parameter on the command line?
        if len(argv)==2 and not ('=' in c.paramTxt): # Is an '=' in it?
            c.paramTxt = ' f='+argv[1] # No. So prepend 'f='.

    c.userLocals = {}               # Initialize empty user-space dict
    exec(f'from pypevue import Point,Post,Layout,FunctionList\nref=FunctionList', c.userLocals)
#---------------------------------------------------------
def makePluginsList(ref):
    pll = ''
    for lin in list(ref.scripts) + [ref.paramTxt]: # For each line in script
        if lin.startswith('=P'):             # that starts with =P,
            for s in lin.split():            # split the line on white space.
                if s.startswith('Plugins='): # If it is a Plugins=args value,
                    pll = pll + ',' + s[8:]  # add args to the plugins list.
    return pll
#---------------------------------------------------------
def run():
    main(argv[1:])

def main(args):
    t0 = time.time()
    FunctionList.registrar('')
    ref = FunctionList
    setupData(ref) 
    ref.installParams([ref.paramTxt]) # Should set f, script-name parameter
    if ref.f == '':
        ref.scripts = ref.script1
    else:
        with open(ref.f) as fi:
            ref.scripts = fi.readlines()
    # If our command line or script names any plugins, get them registered
    FunctionList.registrar(makePluginsList(ref))
    
    ref.setClipAndRota(ref)   # Create LO and its clip1, clip2, rotavec vals
    ref.runScript(ref.scripts)    # Run selected script
    ref.setCodeFrontAndBack(ref)  # Set up beginning and ending SCAD code
    with open(ref.scadFile, 'w') as fout:
        ref.hookFront     (fout)
        fout.write(ref.frontCode)
        ref.hookPosts     (fout)
        ref.writePosts    (fout)
        ref.hookLabels    (fout)
        ref.writeLabels   (fout)
        ref.hookCylinders (fout)
        ref.writeCylinders(fout, 0, len(ref.LO.cyls), ref.cylList,
                           1 if ref.autoMax>0 else 3)
        ref.hookAdder     (fout)
        ref.autoAdder     (fout)
        ref.hookBack      (fout)
        fout.write(ref.backCode)
        ref.hookFinal    (fout)
    t1 = time.time()-t0
    print (f'For script "{ref.f}", pypevu wrote code to {ref.scadFile} at {ref.date} in {t1:0.3f} seconds')

if __name__ == '__main__':
    run()
