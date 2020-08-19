.. -*- mode: rst -*-
=======
pypevue
=======


The pypevu program (in pypevue package and module) allows easy drawing
of "posts and pipes" figures.  It interprets drawing-scripts for
figures, and produces files of OpenSCAD code representing the figures.


Description
===========

Figures to be drawn are made up of cylinders (pipes) connected between
locations in space (posts).  This paradigm is useful for drawing
diagrams of geodesic domes.

The rest of this file briefly describes software requirements; running
the program; getting pypevu to run automatically, or OpenSCAD to
update automatically, when you change a source file; and how to create
software plugins.

**For details about how to write scripts, see LibreOffice file
pypevu.dox.odt or PDF file pypevu.dox.pdf** in the docs subdirectory.
For script-file examples, see examples/eg-* files (ie, files in the
examples subdirectory, with names that begin with "eg-").

Software requirements
=====================

To use the program, you need to have python3 installed on your system
and also should have openscad installed.  Install pypevu using [in
future] pip3 or [at moment] by copying files pypevu.py, __init__.py,
baseFuncs.py, makeIcosaGeo.py into a directory called pypevue.  Get a
script file for the object you wish to make, and say pypevu f=<sf>
where <sf> is the script file name.  (If pypevu or the pypevue module
isn't found, run ./new-bin-lib-links in the pypevue directory.) After
pypevu runs, view the 3D result via a command like openscad pypevu.scad .

Running the program
=====================
  
When you run the program to process a script, it will write SCAD code
to a file (by default, to pypevu.scad). For example, you might say

     ./pypevu.py  f=eg-pentagon-script

which will produce pypevu.scad based on that script, and then you
might say

     openscad pypevu.scad &

which will cause OpenSCAD to read pypevu.scad and display the created
figure.

Automatic updates in OpenSCAD 
=====================
  
If OpenSCAD's `Design -> Automatic Reload and Preview` option is on,
then once you've started OpenSCAD as above, it will notice whenever
pypevu.scad changes, and will re-render the image.

Automatically running pypevu on script file changes 
=====================
From https://github.com/ghjwp7/plastics/blob/master/exec-on-change
obtain the exec-on-change shell script (and its requirements).  Then a
command like that below will automatically run pypevu whenever file
"myscriptfile" changes.  Then OpenSCAD will see that pypevu.scad
changed, and will re-render.

     exec-on-change myscriptfile  './pypevu f=myscriptfile' &

Other comments (about running the program) appear at the beginning of
pypevu.py.

How to create software plugins
=====================
  
Pypevu supports plugins, allowing individual functions used by pypevu
processing to be replaced.  Thus, one can customize pypevu output
without modifying pypevu itself.  To create a plugin, create a Python
module or modules.  (See examples autoHelper.py and twoHelper.py,
which have plugins for examples/eg-auto-test-2 and
examples/eg-two-rings, respectively).  In your script or on the
command line, set parameter Plugins to a list of module names, in the
order you want the modules processed.  If there are several Plugins
settings, their module lists are concatenated together in the order of
appearance, ending with Plugins settings from the command line.
Plugin modules that are not mentioned in a Plugins parameter setting
do not get loaded or used.

For example, if you want to use one plugin module, myPI (or, file
myPI.py in pypevue), you would say "Plugins=myPI" among parameter
settings.  If you had two plugin modules to load, myAxi and myBio, you
could say "Plugins=myAxi,myBio", or "Plugins=myBio,myAxi", or
"Plugins=myBio Plugins=myAxi", etc.  If some function, say
"CrucialOp(z5)" is defined in both of myAxi and myBio, then in the
first case the one from myBio is used, and in the other cases, the one
from myAxi is used.  In short, later-mentioned modules take
precedence.
  
User functions vs Base functions
=====================
  
Functions defined with plugin modules can be *user functions* or *base
functions*.

**Base functions** (functions with names as listed in the tell()
statement at the end of baseFuncs.py) control how pypevu gets and
treats its inputs and how it produces its output.  To change intrinsic
functionality of some part of the program, copy the relevant function
from baseFuncs.py into your own module, and modify it to produce what
you need in your own application.  If you change any base function
calling sequences, change all uses for consistency.  If you want to
call an original base function from your substitute for it, import it
from baseFuncs and refer to it via the import.  For example, a
substitute for addEdge could import the base version of addEdge via
"from pypevue.baseFuncs import addEdge as baseAddEdge" and could call
it via "baseAddEdge(v,w, layout)" or similar.

**User functions** have names not equal to any base function name; a
function is a user function if it isn't a base function.  Call user
functions via U codes in layout sections.  For example, if "U mything
1,2,4;" appears in a layout section, pypevu will issue `mything(1.0,
2.0, 4.0)` at that point in its processing.  The function will be
called with as many numerical parameters as the U code gives it. Note,
`mything()` should be well-defined.  For example, if mything() code
(like `def mything(someargs): ...`) is in myPI.py, use `=P
Plugins=myPI` in your script, and in myPI.py also say `def tell():
return (mything,)`.  Via proper imports, user functions can access
pypevu data structures.  For examples see `examples/userfuncs1.py`.

[ *In a future release, calls within arithmetic sections of a script
will be supported in a simpler form, like `ref.mything(paramlist)`,
vs the present form, like `ref.uDict['mything'](paramlist)`* ]


Note
====

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
