#!/usr/bin/env python3
# -*- mode: python -*-

# objReader.py, a plugin to read point and face data from a Wavefront
# OBJ file # (a 3D-structures file format) - jiw 9 Oct 2020 Ref:
# <https://www.fileformat.info/format/wavefrontobj/egff.htm>

# This program defines a data structure class (ObjFileData) and
# several methods (objReadFile, objManyPoly, objOnePoly, objFatPoly)
# that load or process data into or from an ObjData item.

# Usage: To incorporate this code into pypevue, in command line
# parameters or in an `=P` line of a script, say
# `Plugins=examples.objReader`.

# See example eg-objfile2b for an example of how to use the methods
# below.  That example has lines like "=P Plugins=examples.objReader2"
# and "=A ref.objFileCalls=((ref.objFatPoly, 'slabs.obj', 3),
# (ref.objManyPoly, 'slabs.obj', 2), (ref.objOnePoly, 'slabs.obj',
# 1))", with the =P line to incorporate this code into pypevue, and
# the =A line to tell hookback() which methods to call, with file
# names and scale factors.  [When an =A line is processed, pypevu's
# output file is not yet available for the obj*Poly routines to write
# to; thus the level of indirection.]  When hookback() is called, it
# will try to call any methods listed in ref.objFileCalls, supplying
# them with given values for `filename` and `scalefactor` parameters.
# [You can use hookBack as defined here to call other methods, whether
# related to OBJ files or not, so long as your methods comply with a
# parameter set like (fout, scalefactor=1, filename=None).  Or, copy
# hookBack() into your own code and modify parameter sets and the
# objFileCalls name and content as you like.]

# Limitation: This code primarily handles v and f lines that appear in
# .obj files.  These specify vertex and face data.  (See Ref.)  It
# recognize `g` group and `usemtl` material lines, saving their values
# in lists in an ObjFileData.  [Later versions of methods might use
# those values to set colors, eg, `usemtl green` to change the color
# of following items to green.  However, not all material tags are
# colors.]

# Method objReadFile reads data from a specified .obj file, storing it
# in an instance of ObjFileData.  Methods objManyPoly, objOnePoly,
# objFatPoly produce OpenSCAD code as follows.

# objManyPoly: makes one flat 'polyhedron' for each face read in.
# objOnePoly:  makes one polyhedron with all faces read in.
# objFatPoly:  makes 3D structure, of given thickness, per face. (*)

# (*) Let F1 stand for the polygonal shape specified by any given f
# line from the file.  F1 forms one surface of a polyhedron.  F2, a
# flat face congruent to F1, is offset from it by a given thickness t.
# The direction of offset that objFatPoly uses is (v1 x v2) where v1
# and v2 are the first two edges of F1.  Rectangles of width t close
# the edges of the space between F1 and F2.

from math import sqrt, pi, cos, sin, asin, atan2, degrees
from pypevue import ssq, sssq, rotate2, isTrue, Point
from pypevue import FunctionList as ref
from re import sub
#---------------------------------------------------------
class ObjFileData:
    def __init__(self):
        self.fileName = None
        self.verts = []         # v Vertex list
        self.faces = []         # f Face list
        self.stuff = []         # u usemtl data, (face#, uname) pairs
        self.group = []         # g group data,  (face#, gname) pairs
        self.linesIn  = 0       # count of lines read from file
        self.nDrops = 0         # count of non-comment dropped lines
        self.drops = ''         # string of dropped lines
#---------------------------------------------------------
def objReadFile(fn, scalefac, tellCounts=True):
    '''Read data from file fn, scale it by scale factor, & return an ObjFileData.'''
    #  Strip outer quotes, if any, from the .obj file name
    fn = sub('^"|"$', '', fn)
    #print (f'objReadFile says fn is {fn} and sf is {scalefac}')
    result = ObjFileData()
    result.fileName = fn
    with open(fn) as fin:
        lin = 0; skipped = []
        while (token := fin.readline()):
            lin += 1
            token = sub('/[/0-9]*', '', token)
            parts = token.split()
            if token.startswith('v '):    # vertex command
                p = Point(*[float(u) for u in parts[1:]])
                p.scale(scalefac)
                result.verts.append(p)  
            elif token.startswith('f '):    # face command
                f = list(int(u)-1 for u in parts[1:])
                result.faces.append(f)            
            elif token.startswith('#') or token=='' or token=='\n':
                pass # ignore comments and empty lines
            elif token.startswith('usemtl'):
                result.stuff.append((len(result.faces), parts[1]))
            elif token.startswith('g'):
                result.group.append((len(result.faces), parts[1]))
            else:
                skipped.append(lin) # Add lin to list of dropped lines
    result.linesIn = lin
    result.nDrops  = len(skipped)
    result.drops   = ' '.join(str(t) for t in skipped)
    if tellCounts:
        print (f"Obtained {len(result.verts)} vertices and {len(result.faces)} faces from {result.linesIn} lines in file {result.fileName}")
        print (f"Skipped {result.nDrops} lines (#{result.drops[:40]}...) of the {result.linesIn} lines in file")
    return result
#---------------------------------------------------------
def objOnePoly(fout, objData=None, thickness=1, scalefactor=1, filename=None):
    '''Write OpenSCAD code for one polyhedron, with thin faces for an OBJ file'''
    if filename:
        objData = objReadFile(filename, scalefactor)
    pl = ', '.join(f'[{v}]' for v in objData.verts)
    tl = ', '.join(str(f) for f in objData.faces)
    fout.write(f'// objOnePoly (... {filename} ...) produces:\n')
    fout.write(f'polyhedron(points=[{pl}],\n   faces=[{tl}]);\n\n')
    return objData
#---------------------------------------------------------
def objManyPoly(fout, objData=None, thickness=1, scalefactor=1, filename=None):
    '''Write OpenSCAD code for many 'polyhedrons', one per thin face'''
    if filename:
        objData = objReadFile(filename, scalefactor)
    fout.write(f'// objManyPoly (... {filename} ...) produces:\n')
    verts = objData.verts
    for f in objData.faces:
        pl = ', '.join(f'[{verts[i]}]' for i in f)
        tl = ', '.join(str(i) for i in range(len(f)))
        fout.write(f'polyhedron(points=[\n   {pl}],\n   faces=[[{tl}]]);\n')
    fout.write(f'\n')
    return objData
#---------------------------------------------------------
def objFatPoly(fout, objData=None, thickness=1, scalefactor=1, filename=None):
    '''Write OpenSCAD code for individual thick faces for an OBJ file'''
    if filename:
        objData = objReadFile(filename, scalefactor)
    fout.write(f'// objFatPoly (... {filename} ...) produces:\n')
    verts = objData.verts
    for f in objData.faces:
        # Compute normal to face, using its first 3 vertices
        v0, v1, v2 = verts[f[0]], verts[f[1]], verts[f[2]]
        vnorm = (v0-v1) & (v2-v1)       # v0-v1 cross v2-v1
        vmag = vnorm.mag()
        if vmag < 1e-6:  vmag=1   # Any value>0 works ok in this case
        vnorm.scale(thickness/vmag)     # scale its thickness
        fout.write(f'// For face {f},  vnorm = {vnorm}\n')
        pl = ', '.join(f'[{verts[i]}]' for i in f)
        tl = ', '.join(f'[{verts[i]+vnorm}]' for i in f)
        fout.write(f'polyhedron(points=[\n    {pl},\n    {tl}],\n')
        nv = len(f)
        pl = ', '.join(str(i) for i in range(nv))
        tl = ', '.join(str(i) for i in range(nv,2*nv))
        fout.write(f'faces=[[{pl}], [{tl}]')
        vp = nv-1          # Set previous vertex for wrap-around
        for i in range(nv):
            fout.write(f', [{vp}, {i}, {nv+i}, {nv+vp}]')
            vp = i
        fout.write(f']);\n\n')
    return objData
#---------------------------------------------------------
def hookBack(fout):
    '''If objFileCalls is properly defined, call methods with params.'''
    #print (f'hookBack(fout)')
    try:
        for meth,fname,scale in ref.objFileCalls:
            try:
                print(f'objFileCalls invokes {meth}({fname})')
                meth(fout, filename=fname, scalefactor=scale)
            except:
                print(f'objFileCalls fails for {meth}({fname})')
    except:
        print(f'objFileCalls fails in hookBack')
#---------------------------------------------------------
def tell(): return (hookBack, objReadFile, objManyPoly, objOnePoly, objFatPoly)
#---------------------------------------------------------
if __name__ == '__main__':
    objReadFile('box.obj', 1)
