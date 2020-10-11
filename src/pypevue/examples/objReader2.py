# -*- mode: python -*-

# objReader.py, a plugin to read point and face data from a Wavefront
# OBJ file # (a 3D-structures file format) - jiw 9 Oct 2020 Ref:
# <https://www.fileformat.info/format/wavefrontobj/egff.htm>

# This program defines a data structure (ObjData) and several methods
# (objReadFile, objManyPoly, objOnePoly, objFatPoly) that load or
# process data into or from an ObjData item.

# Usage: To incorporate this code into pypevue, in command line
# parameters or in an `=P` line of a script, say
# `Plugins=examples.objReader`.  To get data from a .obj file, in a
# pypevue script say something like `=A ` (fix this)

# arithmetic line (an =A line)
 
# To tell it which .obj file to read,
# say `userPar2=f` (replacing f with appropriate .obj file name).  If
# no .obj file name is specified, name will default to box.obj.

# Limitation: This code primarily handles v and f lines that appear in
# .obj files.  These specify vertex and face data.  (See Ref.)  A
# later version will recognize `usemtl` lines and use them to set
# colors.  For example, `usemtl green` will change the color of
# following items to green.  Not all material tags are recognized,
# which can result in arbitrary color settings.

# Method: This replaces the `hookBack()` method (a `pass`) with code
# that reads data from a specified .obj file.  It keeps vertex and
# face data locally (rather than adding it into pypevu's post or
# cylinder data structures).  Then it produces code for one 3D
# polyhedron per face read in.  Let F stand for the polygonal shape
# specified by a certain f line from the file.  F forms one surface of
# the polyhedron.  An opposite surface is congruent to F, offset by a
# thickness t.  The direction of offset is (v1 x v2) where v1 and v2
# are the first two edges of F.  Thickness t is a fraction h of RMS
# edge length, over all faces in the file.  For example, if there are
# 28 edges of specified faces and the total of squared lengths is
# 23548 units, t = sqrt(23548/28)*h = 29*h = 1.45.  The default value
# of h is 1/20.  Note, shared edges count multiple times.

from math import sqrt, pi, cos, sin, asin, atan2, degrees
from pypevue import ssq, sssq, rotate2, isTrue, Point
from pypevue import FunctionList as ref
from re import sub
#---------------------------------------------------------
def hookBack(fout):
    # Is a file name given?
    fn = ref.userPar2 if ref.userPar2 else 'box.obj'
    fn = sub('^"|"$', '', fn)   # Strip outer quotes if any
    verts = []
    faces = []
    with open(fn) as fin:
        lin = 0; skipped = []
        while (token := fin.readline()):
            lin += 1
            if token.startswith('v '):    # vertex command
                x,y,z = [float(u) for u in token[2:].split()]
                verts.append(Point(x, y, z))    
            elif token.startswith('f '):    # face command
                f = []
                token = sub('/[/0-9]*', '', token)
                for u in token[2:].split():
                    f.append(int(u)-1) # Make list of corners of face
                faces.append(f)
            
            elif token.startswith('#') or token=='' or token=='\n':
                pass # ignore comments and empty lines
            else:
                #print (f"Skipping line {lin} of OBJ file: {token}")
                if len(skipped) < 34:
                    skipped.append(lin)
    print (f"Skipped lines {' '.join(str(i) for i in skipped)}... of OBJ file")
    nverts = len(verts)
    
    # Scale the vertices and get total of edge lengths
    for i in range(nverts):
        verts[i].scale(ref.SF)
    totalssq = nsides = 0
    for f in faces:        # f is an index number of a vertex
        m = f[-1] if f[-1]<nverts else 0
        for n in f:
            nsides += 1
            nl = n if n<nverts else m
            if 0<=nl<nverts and 0<=m<nverts:
                totalssq += (verts[nl]-verts[m]).mag2()
            else: print(f'Bad vertex numbers?  {nl} {m} from {f}')
            m = nl
    hfactor = 0.05
    thik = sqrt(totalssq/nsides)*hfactor
    print (f'nsides={nsides}   totalssq={totalssq}   hfactor={hfactor}   thik={thik}')

    # Write OpenSCAD code for faces
    for f in faces:
        v0, v1, v2 = verts[0], verts[1], verts[2]
        vnorm = (v0-v1) & (v2-v1) # v0-v1 cross v2-v1
        vnorm.scale(thik/vnorm.mag())
        pl = ', '.join(f'[{verts[i]}]' for i in f)
        tl = ', '.join(f'[{verts[i]+vnorm}]' for i in f)
        #fout.write(f'polyhedron(points=[{pl},\n           {tl}],\n')
        fout.write(f'polyhedron(points=[{pl}],\n')
        nv = len(f)
        pl = ', '.join(str(i) for i in range(nv))
        tl = ', '.join(str(i) for i in range(nv,2*nv))
        #fout.write(f'faces=[[{pl}], [{tl}],')
        #fout.write(f'[0, 1, {nv+1}, {nv}] ] );\n')
        fout.write(f'faces=[[{pl}]] );\n')

#---------------------------------------------------------
def tell(): return (hookBack,)
#---------------------------------------------------------