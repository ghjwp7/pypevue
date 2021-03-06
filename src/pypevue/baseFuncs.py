#!/usr/bin/env python3
'''Base functions for pypevu.py, a program that generates OpenSCAD
code for tubes along selected edges between `posts` in a plane.  This
supports visualization of arrangements of edges in geodesic dome
structures. -- jiw March 2020...'''

from sys import argv, exit, exc_info, stderr
import datetime
from math import sqrt, cos, sin, asin, atan2, pi, radians, degrees
from pypevue import ssq, sssq, rotate2, isTrue
from pypevue import Point, Post, Cylinder, Layout, FunctionList

#---------------------------------------------------------
def arithmetic(line, xTrace):
    # Remove =A and any leading whitespace, to avoid indentation error
    ref = FunctionList
    code = line.lstrip()
    if xTrace:   print (f'Code to exec:  {code}')
    try:
        if code:    # have we got any user-code?
            exec (code, ref.userLocals)   # yes, try to execute it
    except SystemExit:
        exit(0)             # allow code to exit
    except Exception:       # catch normal exceptions
        er = exc_info()
        print(f'Got error:  `{er[1]}`   from code:  `{code.strip()}`')
#---------------------------------------------------------
# Compute coords of a letter-point on post p
def levelAt(lev, p):
    ref = FunctionList
    a = (ord(lev)-ord(ref.levels[0]))/(len(ref.levels)-1) # Get portion-of-post
    b = 1-a                                       # Get unused portion
    pf, pt = p.foot, p.top
    return Point(round(b*pf.x+a*pt.x, 2), round(b*pf.y+a*pt.y, 2), round(b*pf.z+a*pt.z, 2))

def thickLet(thix):
    ref = FunctionList
    if type(thix)==float:
        return thix       # If thix is already real, return as is
    if thix=='p':
        return ref.SF*ref.pDiam
    else: # diameters q, r, s, t... scale geometrically
        expo = max(0, ord(thix)-ord('q'))
        return round(ref.SF * ref.qDiam * pow(ref.dRatio, expo), 2)

def addEdge(v,w, layout):
    if v in layout.edgeList:
        if w not in layout.edgeList[v]:
            layout.edgeList[v].append(w)
    else:
        layout.edgeList[v] = [w]

def addEdges(v,w, layout):
    ref = FunctionList
    ref.addEdge(v,w,layout); ref.addEdge(w,v,layout)
#---------------------------------------------------------
def generatePosts(code, numberTexts, func):
    '''Modify layout LO according to provided code and numbers'''
    ref = FunctionList
    B = ref.LO.BP
    bx, by, bz = B.x, B.y, B.z
    nn = len(numberTexts)
    Lots = 99999
    
    def getNums(j, k): # Get list of values from list of number strings
        nums = []
        try:
            if j > nn or nn > k :
                raise ValueError;
            for ns in numberTexts:
                nums.append(float(ns))
        except ValueError:
            print (f'Anomaly: code {code}, {numberTexts} has wrong count or format')
            return None
        return nums

    def postAt(x,y,z): ref.LO.posts.append(Post(Point(x,y,z)))
    
    if code=='B':               # Set base point, BP
        nums = getNums(3,3)     # Need exactly 3 numbers
        if nums:   ref.LO.BP = Point(*nums);  return

    if code=='C':               # Create a collection of posts
        nums = getNums(3,Lots) # Need at least 3 numbers
        if nums:
            while len(nums) >= 3:
                postAt(nums[0]+bx,  nums[1]+by, nums[2]+bz)
                nums = nums[3:]
            if len(nums)>0:
                print (f'Anomaly: code {code}, {numberTexts} has {nums} left over')
            return

    if code=='D':      # Remove specified posts and references to them
        nums = getNums(1,Lots)     # Accept 1 or more numbers
        if not nums: return
        lopo = ref.LO.posts;  nlop = len(lopo)
        nums = [int(x) for x in sorted(nums)]
        error = f'{nums[0]} < 0' if nums[0] < 0 else (f'{nums[-1]} >= {nlop}' if nums[-1] >= nlop else None)
        if error:
            print (f'Error: List of post numbers for =L D code has an out-of-range value; {error} -- terminating.')
            exit(0)

        print (f'=  From {nlop} posts, deleting {len(nums)} of them: {nums}')
        # If we knew nums were distinct, we'd say polout = [0]*(nlop-len(nums))
        nin, nout, ninf, polout = 0, 0, nlop+13, [0]*nlop
        nums.append(ninf)
        transi = {} # Init post-number translation table
        # Copy posts, deleting some while making translation table
        for k in range(nlop):
            if k == nums[nin]:
                transi[k] = ninf;  nin += 1
            else:
                polout[nout] = lopo[k]
                transi[k] = nout;  nout += 1
        
        # We've deleted some posts; install into layout
        del lopo;  ref.LO.posts = polout[:nout]
        # Remove obsolete post numbers from cylinders list
        locy = ref.LO.cyls;   cylout = []
        for c in locy:
            if not(c.post1 in nums or c.post2 in nums):
                c.post1 = transi[c.post1]
                c.post2 = transi[c.post2]
                cylout.append(c)
        del locy;  ref.LO.cyls = cylout
        # If we wanted autoAdder to work ok after a D operation, at this
        # point we would clean up LO.edgeList.  But maybe we don't care...
        return

    # This exclude-edge code is not so efficient but is good enough
    # for removing handfuls of edges, eg for doors or windows in
    # geodesics.
    #def edgecode(e,f): return max(e,f) + 262144*min(e,f)
    def edgecode(e,f): return max(e,f) + 1000*min(e,f)
    if code=='E':               # Exclude edges -- remove some cylinders
        nums = getNums(1,Lots)     # Accept 1 or more numbers
        if not nums: return  
        pairs = [(int(x),int(y)) for x,y in zip(nums[::2],nums[1::2])]
        print (f'To remove: {pairs}')
        pairs = [edgecode(x,y) for x,y in pairs]
        drops = [];   locy = ref.LO.cyls
        for k in range(len(locy)):
            c = locy[k]
            if edgecode(c.post1, c.post2) in pairs:
                drops.append(k)
        if drops:
            drops.reverse()
            for k in drops: del locy[k]
        else:
            print (f'=  Error: None of edges {nums} found')
        return
        
    if code=='G':               # Create geodesic posts and cylinders
        from pypevue.makeIcosaGeo import genIcosahedron
        nums = getNums(2,2)     # Need exactly 2 numbers
        if not nums: return
        geoFreq, geoScale = int(round(nums[0])), nums[1]
        elo = Layout(posts=[], cyls=[],  edgeList={}) # Init an empty layout
        rlo = ref.LO
        # Rotation in following is not yet as advertised -- ie is normalizer not opt
        genIcosahedron(elo, geoFreq, rlo.clip1, rlo.clip2, rlo.rotavec.y, rlo.rotavec.z)
        epo = elo.posts;  eel = elo.edgeList;  nLoPo = len(rlo.posts)
        # Scale the generated posts by given scale; and copy to LO
        for p in epo:
            p.scale(geoScale)
            rlo.posts.append(Post(p))
        # Generate sets of cylinders in various colors.
        colorTrans = {'Y':ref.geoColors[0], 'B':ref.geoColors[1], 'R':ref.geoColors[2], 'C':ref.geoColors[3] }
        for co in ('Y', 'B', 'R', 'C'):
            for j in sorted(eel.keys()):
                for k in sorted(eel[j]):
                    if j<k:   # Both of j,k and k,j are in the list
                        p, q = epo[j], epo[k]
                        oB = p.rank == q.rank
                        oY = p.nnbrs==5 or q.nnbrs==5
                        oC = p.dupl>1 and q.dupl>1 and not (oB or oY)
                        oR = not (oB or oY or oC)
                        if (co=='B' and oB and not oY) or (co=='Y' and oY) or (co=='R' and oR) or (co=='C' and oC):
                            cyl = Cylinder(j+nLoPo,k+nLoPo, 'c', 'c', colorTrans[co], 'p', ref.endGap, 0, 0)
                            rlo.cyls.append(cyl)
        return
        
    if code=='H':               # Create a clip box (particularly for geodesics)
        nums = getNums(6,6)     # Need exactly 6 numbers        
        if nums:
            ref.LO.clip1 = Point(*nums[:3]);
            ref.LO.clip2 = Point(*nums[3:]);
        return
        
    if code=='L':               # Create a line of posts
        nums = getNums(4,4)     # Need exactly 4 numbers
        if nums:
            n, dx, dy, dz = int(nums[0]), nums[1], nums[2], nums[3]
            x, y, z = bx, by, bz
            for k in range(n):
                postAt(x+dx, y+dy, z+dz)
            return

    if code=='O':               # Set origin point, OP
        nums = getNums(3,3)     # Need exactly 3 numbers
        if nums:   ref.LO.OP = Point(*nums);  return

    if code=='P':               # Create a polygon of posts        
        nums = getNums(3,3)     # Need exactly 3 numbers
        if nums:
            n, r, a0 = int(nums[0]), nums[1], nums[2]
            theta = 2*pi/n
            x, y = rotate2(r, 0, radians(a0)) # a0 in degrees
            for post in range(n):
                postAt(bx+x, by+y, bz)
                x, y = rotate2(x, y,theta)
            return
    
    if code in 'RT':            # Create an array of posts
        nums = getNums(4,4)     # Need exactly 4 numbers
        if nums:
            r, c, dx, dy = int(nums[0]), int(nums[1]), nums[2], nums[3]
            y, z = by, bz
            for rr in range(r):
                x, roLen = bx, c
                # For odd rows of triangular arrays, offset the row
                if code=='T' and (rr&1)==1:
                    x, roLen = bx - dx/2, c+1
                for cc in range(roLen):
                    postAt(x,y,z)
                    x += dx
                y += dy
            return
    if code=='U':               # Call a function
        f = ref.uDict[func](*getNums(0,Lots))
    return                      # We might fail or fall thru
#===============================================
def scriptPost(ss, prePost):
    ref = FunctionList
    codes = 'BCDEGHILOPRSTU'
    pc, code, numbers, glom = '?', '?', prePost.data, ''
    getGlom = False
    for cc in ss:   # Process characters of script
        # Add character to number, or store a number, or what?
        if getGlom:
            if getGlom > 1:
                if cc==' ' or cc==';':
                    getGlom = 0
                else: glom = glom + cc
            else:
                if cc != ' ':
                    getGlom = 2;
                    glom = cc
        if pc == '#':       # Set or use a simple variable
            if code=='?':   # If between codes, store post count
                ref.userLocals[cc] = len(ref.LO.posts)
            else: # Substitute simple value into list of numbers
                numbers.append(ref.userLocals[cc])
        elif cc in ref.digits:
            num = num + cc if pc in ref.digits else cc
        elif pc in ref.digits:
            numbers.append(num) # Add number to list of numbers
        # Process a completed entry, or start a new entry?
        if cc==';':
            ref.generatePosts(code, numbers, glom)
            code = '?'
        elif cc in codes:
            pc, code, numbers, glom = '?', cc, [], ''
            getGlom = 1 if code=='U' else 0
        pc = cc             # Prep to get next character
    prePost.data = numbers
    return
#=========================================================
def scriptCyl(ss, preCyl):
    ref = FunctionList
    post1, post2, lev1, lev2, colo, thix, gap, nonPost, num = preCyl.get9()
    mode = 0                    # mode 0 = comments at start
    pc, code = '?', '?'
    for cc in ss:            
        if pc == '#':       # Insert a simple variable's value
            post1, post2 = post2, ref.userLocals[cc]
            nonPost = False
        elif cc in ref.colors: colo = cc
        elif cc in ref.thixx: thix  = cc
        elif cc in ref.levels:
            lev1, lev2 = lev2, cc
        elif cc in ref.digits:
            if pc in ref.digits:  post2 = post2 + cc
            else:             post1, post2 = post2, cc
            nonPost = False
        elif cc=='/':
            lev1, lev2 = lev2, lev1
        elif cc==';':
            p1, p2 = int(post1), int(post2)
            if nonPost:
                p1, p2 = p1+1, p2+1
                post1, post2 = str(p1), str(p2)
            num = len(ref.LO.cyls)
            cyl = Cylinder(p1, p2, lev1, lev2, colo, thix, gap, 0, num)
            ref.LO.cyls.append(cyl)
            addEdges(p1, p2, ref.LO) # Add edges p1,p2 and p2,p1 to edges list
            nonPost = True
        pc = cc
    preCyl.put9(post1, post2, lev1, lev2, colo, thix, gap, nonPost, num)
    return preCyl
#===============================================
def runScript(scripts):
    '''Process scripts (a list of lines) line by line'''
    ref = FunctionList
    preCyl = Cylinder(0, 1, 'c','c', 'G', 'p', ref.endGap, True, 0)
    #print (f'runScript: preCyl = {preCyl}  preCyl.gap={preCyl.gap}  ref.endGap={ref.endGap}')
    prePost = Post(0, data=[])
    mode = 0                    # mode 0 = comments at start
    numbers = []
    for line in scripts:
        l1, l2, ss, ll = line[:1], line[:2], line[2:], line
        if   l2=='=C': mode = 'C'; ll=ss # Cylinders
        elif l2=='=L': mode = 'L'; ll=ss # Layout
        
        elif l2=='=P':
            # Process current line of params, and let command params
            # in paramTxt override if necessary
            ref.installParams((ss, ref.paramTxt));
            continue
        elif l2=='=A':          # Process Arithmetic line
            ref.arithmetic(ss, ref.traceExec);
            continue
        elif l1=='=':           # Process comment line
            continue
        
        if   mode == 'L':       # Process Posts line
            ref.scriptPost(ll, prePost)
        elif mode == 'C':       # Process Cylinders line
            preCyl.gap = ref.endGap
            ref.scriptCyl (ll, preCyl)
#===============================================
def postTop(p, OP):   # Given post p, return loc. of post top
    ref = FunctionList
    x, y, z = p.foot.x, p.foot.y, p.foot.z # Location of post foot
    ox, oy, oz = (x, y, z-99) if ref.postAxial else (OP.x, OP.y, OP.z)
    u = ref.SF*ref.postHi       # Distance from p to post-top
    v = sssq(x-ox, y-oy, z-oz)  # Distance from p to origin point
    if v>0.01:
        a, b = (u+v)/v, -u/v    # Extrapolation ratios a + b = 1
        tx, ty, tz = a*x+b*ox, a*y+b*oy, a*z+b*oz
    else:
        tx, ty, tz = x, y, z+u  # Fallback if p ~ OP
    siny = min(1, max(-1, (tz-z)/u)) # Don't let rounding error shut us down
    yAxisAngle = degrees(pi/2 - asin(siny))
    zAxisAngle = degrees(atan2(ty-y, tx-x))
    #yAxisAngle = (pi/2 - asin(siny)) * 180/pi
    #zAxisAngle = atan2(ty-y, tx-x) * 180/pi
    #zt =  atan2(ty-y, tx-x) * 180/pi
    #print (f'postTop  diff zangle: {zt-zAxisAngle:6.6e}   zt {zt}   zA {zAxisAngle}')
    return Point(tx,ty,tz), round(yAxisAngle,2), round(zAxisAngle,2)
#===============================================
def writePosts(fout):
    ref = FunctionList
    try:
        ref.LO.OP.scale(ref.SF) # Get ready to orient the posts: scale the OP
    except:
        print ('In exception, dir(ref): ', [x for x in dir(PD) if not x.startswith('__')])
    # Scale the set of posts, and compute their tops and angles 
    pHi, pDi = ref.SF*ref.postHi, ref.SF*ref.postDiam
    for k, p in enumerate(ref.LO.posts):
        p.num = k
        if isTrue(ref.zSpread):
            zrat = 2/(1+p.foot.z/ref.zSize) # assumes z centers at z==0
            p.foot.scalexy(zrat)
        p.foot.scale(ref.SF)
        if isTrue(ref.postList):
            print (f'p{k:<2}=Point( {p.foot})')
        p.diam, p.hite = pDi, pHi
        p.top, p.yAngle, p.zAngle = ref.postTop(p, ref.LO.OP)

    fout.write('''
module onePost (diam, hi, yA, zA, px, py, pz)
  translate (v=[px, py, pz]) rotate(a=[0, yA, zA])
      cylinder(d=diam, h=hi);
module makePosts() {
''')
    # The onePost calls in following should match params in above def.
    for p in ref.LO.posts:
        fout.write(f'''  onePost({p.diam}, {p.hite}, {p.yAngle:7.3f}, {p.zAngle:7.3f},   {p.foot.x:1.2f}, {p.foot.y:1.2f}, {p.foot.z:1.2f} );
''')
    fout.write('}\n')           # close the module

#===============================================
def writeLabels(fout):
    ref = FunctionList
    if not isTrue(ref.postLabel):
        fout.write('module makeLabels() {}\n') # Make an empty module
        return
    cName = ref.colorSet['B']
    thik  = ref.thickLet('t')
    for cc in ref.postLabel:
        if cc in ref.colors: cName = ref.colorSet[cc]
        if cc in ref.thixx:  thik  = ref.thickLet(cc)
    fout.write(f'''module oneLabel (offset, yA, txt, lx, ly, lz) 
  translate (v=[lx+offset, ly+offset, lz+offset])
    rotate([0, yA, 0]) color(c={cName}) text(size={thik:0.3f}, text=txt);
module makeLabels() {'{'}\n''')
    for p in ref.LO.posts:
        lxyz  = ref.levelAt('e', p)
        for cc in ref.postLabel:
            if cc in ref.levels: lxyz  = ref.levelAt(cc, p)
        fout.write(f'''  oneLabel({p.diam/3:0.3f}, {p.yAngle:0.3f}, "{str(p.num)}",  {str(lxyz)});\n''')
    fout.write('}\n')           # close the module

#==================================================
def writeCylinders(fout, clo, chi, listIt, startFin):
    '''Write openSCAD code to generate pipes between posts.  We process
    from cylinder clo to chi-1, printing cylinder data if listIt is
    true.  Integer startFin controls whether module prefix and suffix
    code is written.  0=neither, 1=prefix, 2=suffix, 3=both    '''
    ref = FunctionList
    posts = ref.LO.posts
    nPosts = len(posts)
    if startFin & 1:
        fout.write('''module oneCyl(diam, cylLen, rota, trans, colo)
    translate (v=trans) rotate(a=rota)
      color(c=colo) cylinder(d=diam, h=cylLen);
module makeCylinders() {\n''')

    for nCyl in range(clo, chi):
        cyl = ref.LO.cyls[nCyl]     # Draw this cylinder
        post1, post2, lev1, lev2, colo, thix, gap, data, num = cyl.get9()
        gap = ref.SF*gap            # gap needs scaling
        p1, p2 = min(post1,nPosts-1), min(post2,nPosts-1)
        try:
            pp, qq = posts[p1], posts[p2]
        except:
            print (f'Fatal Error with p1= {p1},   p2= {p2},  nPosts {nPosts}')
            exit(0)
        p = ref.levelAt(lev1, pp)
        q = ref.levelAt(lev2, qq)
        qmp = q.diff(p)
        L = round(max(0.1, qmp.mag()), 2) # Round L to 2 places
        cName = ref.colorSet[colo]
        alpha = gap/L
        cc = p + alpha * qmp    # Add scaled qmp to p
        cylNum= 1000*p1 + p2
        if isTrue(listIt):
            print (f'Make {cyl}  L {L:2.2f}  {cName}')
        # Use min/max to avoid exception from dz/L numerical error
        ##yAngle = round(degrees(pi/2 - asin(min(1, max(-1, dz/L)))), 2)
        ##zAngle = round(degrees(atan2(dy, dx)), 2)
        yAngle = round(degrees(pi/2 - asin(min(1, max(-1, qmp.z/L)))), 2)
        zAngle = round(degrees(atan2(qmp.y, qmp.x)), 2)
        fout.write(f'''  oneCyl ({cyl.diam:0.3f}, {L-2*gap:0.3f}, [0, {yAngle:0.3f}, {zAngle:0.3f}], [{cc.x:0.3f}, {cc.y:0.3f}, {cc.z:0.3f}], {cName});\n''')

    if startFin & 2:
        fout.write('}\n')           # close the module
#-------------------------------------------------------------
def autoAdder(fout):
    '''Stub for auto-adding cylinders, which happens via a plug-in'''
    pass
#-------------------------------------------------------------
def installParams(script):
    '''Given a script line or lines that are Parameter-setting lines, this
    treats variable names and value settings, like "var1=val1
    var2=val2 var3=val3 ...".  It converts the values to numeric
    forms, and stores them in globals() dict.  Notes: White space is
    taboo within a var=val item. Variables specified multiple times
    will be overwritten each time with each value enduring until
    overwritten.  Plugins settings are pre-processed via
    makePluginsList() as well as here. '''
    ref = FunctionList
    for parTxt in script:
        plist = parTxt.split()       # Split the list on white space
        for vev in plist:
            p = pq = vev.split('=')  # Split each equation on = sign
            q, ok = '', False
            if len(pq)==2:
                p, q = pq
                if p in dir(ref):
                    t, v = type(getattr(ref, p)), q
                    try:
                        if   t==int:   v = int(q);     ok=True
                        elif t==float: v = float(q);   ok=True
                        elif t==bool:  v = isTrue(q);  ok=True
                        elif t==str:   v = q;          ok=True
                    except:  pass
            if ok: setattr(ref,p,v)
            else: 
                print (f'Parameter-setting fail for "{parTxt}" in {script}')
#-------------------------------------------------------------
def setClipAndRota(c):
    '''Set empty layout and set defaults for geodesic-dome clipping box
    corners and rotation vector    '''    
    c.LO = Layout()  # Start an empty layout.
    c.LO.clip1   =  Point(-2,-2,-0.01)
    c.LO.clip2   = Point(2,2,2)
    phi = (1+sqrt(5))/2;   r = sqrt(2+phi)
    # Set default Z rotation to 0 instead of -18, so that FRA2 works
    # ok in makeIcosaGeo genIcosahedron()
    c.LO.rotavec = Point(0, degrees(asin(phi/r)), 0) # X,Y,Z rotations
#-------------------------------------------------------------
def setCodeFrontAndBack(c):
    c.date = datetime.datetime.today().strftime('%Y-%m-%d  %H:%M:%S')
    # Find out if there's userCode to be included:
    includer = f'include <{c.userCode}>;' if c.userCode else '//'
    c.frontCode = f'''// File {c.scadFile}, generated  {c.date}
// by pypevu.py from script "{c.f}"
$fn = {c.cylSegments};
userPar0 = {c.userPar0};
userPar1 = {c.userPar1};
userPar2 = {c.userPar2};
{includer}
'''
    c.backCode = '''
union() {
  makePosts();
  makeLabels();
  makeCylinders();
}
'''
#-------------------------------------------------------------
# Hook functions -- To let user modify data or
# output before each step of the output process
def hookFront (fout): pass
def hookPosts (fout): pass
def hookLabels(fout): pass
def hookCylinders(fout): pass
def hookAdder (fout): pass
def hookBack  (fout): pass
def hookFinal (fout): pass
#-------------------------------------------------------------

def tell():
    return (addEdge, addEdges, arithmetic, autoAdder, generatePosts,
            installParams, levelAt, postTop, runScript, scriptCyl,
            scriptPost, setClipAndRota, setCodeFrontAndBack, thickLet,
            writeCylinders, writeLabels, writePosts,
            hookFront, hookPosts, hookLabels, hookCylinders,
            hookAdder, hookBack,  hookFinal)
