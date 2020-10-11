#!/bin/sh

# Make Euler-Formula calculation for 3D assembly of posts and
# cylinders listed in specified file, or in pypevu.scad if no file is
# specified.

FI=${1:-pypevu.scad}

# Compute number of edges (cylinders), subtracting 1 for "module oneCyl"
e=$((`grep oneCyl $FI |wc -l`-1))

# Compute number of vertices (posts), subtracting 1 for "module onePost"
v=$((`grep onePost $FI |wc -l`-1))

# Compute number of faces, from formula  V-E+F = 2 in 3D
f=$(($e-$v+2))

printf "$FI has %d edges, %d vertices, so %d faces\n" $e $v $f
