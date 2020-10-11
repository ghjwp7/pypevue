# -*- mode: python -*-

# objReader.py, a plugin to read point and face data from a Wavefront
# OBJ file # (a 3D-structures file format)  - jiw 9 Oct 2020
# Ref: <https://www.fileformat.info/format/wavefrontobj/egff.htm>

# Usage: To incorporate this code into pypevue, in command line
# parameters or in an `=P` line of a script, say
# `Plugins=examples.objReader`.  To tell it which .obj file to read,
# say `userPar2="f"` (replacing f with appropriate .obj file name).
# If no .obj file name is specified, name will default to box.obj.

# Limitation: This code handles v and f lines (specifying vertex and
# face data) that appear in .obj files (see Ref) and ignores others.

# Method: This replaces the `hookBack()` method (a `pass`) with code
# that reads data from a specified .obj file.  It keeps vertex and
# face data locally (rather than adding it into pypevu's post or
# cylinder data structures).  Then, for each face that was read in, it
# writes code for one 3D polyhedron.  See following example.
# polyhedron(points=[[241.037, -77.8, -84.111], [240.731, -97.498,
# -80.509], [229.245, -87.185, -88.24]], faces=[[0, 1, 2]] ); .  For
# this example, `f 3 4 2` appeared in an OBJ file.  The coordinates of
# OBJ-file vertices 3, 4, and 2 are listed in the points[] array, in
# that order, so that the faces[] array can refer to them as points 0,
# 1, and 2.

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
        lin = 0; skipped = []; nskipped = 0
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
                nskipped += 1
                if len(skipped) < 34:
                    skipped.append(lin)
    print (f"Skipped {nskipped} lines (#{' '.join(str(i) for i in skipped)}...) of the {lin} lines in OBJ file")
    nverts = len(verts)
    
    # Scale the vertices
    for i in range(nverts):
        verts[i].scale(ref.SF)

    # Write OpenSCAD code for faces
    for f in faces:
        pl = ', '.join(f'[{verts[i]}]' for i in f)
        fout.write(f'polyhedron(points=[{pl}],   ')
        pl = ', '.join(str(i) for i in range(len(f)))
        fout.write(f'faces=[[{pl}]] );\n')

#---------------------------------------------------------
def tell(): return (hookBack,)
#---------------------------------------------------------
