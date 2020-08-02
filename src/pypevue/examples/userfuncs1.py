# Helper code for use by eg-user-funcs1 example.  The spirally(k, t,
# xs, ys, zs) function calculates a set of 2*k post locations along t
# turns of a sort-of-spiral beginning at the current base location,
# and inserts the posts into a drawing by calls to generatePosts(),
# with x-y-z scale factors xs, ys, zs.  jiw 1 Aug 2020

from math import sin, cos, pi
from pypevue import FunctionList as ref
#-------------------------------------------------------------
def spirally(k=8, turns=0.5, xs=.2, ys=.5, zs=.5):
    rSide, lSide, k = [], [], int(k)
    da = turns*2*pi/k
    B = ref.LO.BP
    bx, by, bz = B.x/ref.SF, B.y/ref.SF, B.z/ref.SF
    print (f'In spirally:  k {k:3}  turns {turns}  xs {xs}  ys {ys}  zs {zs}  BP {B}')
    for i in range(k):
        u = 1
        for v in (bx + xs*i, by + ys*sin(da*i), bz + zs*cos(da*i)):
            rSide.append(v)
            lSide.append(u*v); u=-1
    ref.generatePosts('C', rSide+lSide, None)
    return k
#-------------------------------------------------------------
def tell():
    return (spirally,)
