#!/usr/bin/env python

""" make_poly.py script to generate deflected polygon images and
kaleidoscopic images (a series of overlaid polygons).
Polygons are deflected according to the algorithm described
by Miyashita.   Useful for creating a large number of unique
abstract stimuli. """


# Definitions --
# Kaleido = overlaid set of 'poly's which are randomly deflected polygons
#   Each overlaid 'poly' should be smaller than the previous to avoid hiding it
#   This doesn't always work due to the randomness of making a 'poly'
#
# Poly = randomly deflected polygon for making unique memory stimuli
#   The algorithm starts with a random simple shape: triangle, square, pentagon, hexagon
#   A 'deflection' involved finding the mid point of a side and randomly moving it in or
#   out a random number of degrees of deflection.
#   Note that this doubles the number of sides on each iteration
#   After all the sides are defined, the polygon is 'filled' to make a shape
#   The fill color is randomly selected (or possibly kept constant over a set of shapes)


# 12/5/2013 -- 4AFC images for Implicit Recognition project
# 8/2015    -- Code clean up for useability

__version__="Make_poly.py v.2.1 PJR Aug 2015"

import Image, ImageDraw, random, math, datetime, string, re
    

def random_color():
    """ Generate a random (R,G,B) tuple where at least one
    color is >128 (so it's not too dark)."""
    
    r=g=b=0
    while r<128 and b<128 and g<128:
        r=int(random.random()*256)
        g=int(random.random()*256)
        b=int(random.random()*256)
    return (r,g,b)


class poly:
    init_square=[-100,-100,-100,100,100,100,100,-100]
    init_pentagon=[0,-100,-95,-31,-56,81,56,81,95,-31]
    init_hexagon=[0,-100,-87,-50,-87,50,0,100,87,50,87,-50]

    def __init__(self,poly_type,scale,size,color,num_deflect,pv_list=[],deflect_list=[],deflect_size=20):
        (self.x, self.y)=size
        self.color=color
        self.cx=self.x/2
        self.cy=self.y/2
        self.deflects=[]
        self.deflect_size=deflect_size

        if poly_type=='r':
            self.init=random.choice(['s','p','h'])
        else:
            self.init=poly_type

        if  self.init=='s':
            self.pv=poly.init_square[0:]
        elif self.init=='p':
            self.pv=poly.init_pentagon[0:]
        elif self.init=='h':
            self.pv=poly.init_hexagon[0:]

        self.nv=len(self.pv)/2

        # Scale the initial polygon to the screen size & scale
        self.cx=self.x/2
        self.cy=self.y/2
        self.scale=scale
        for i in range(0,len(self.pv)):
            self.pv[i]=self.pv[i]*scale
            if i%2==0:
                self.pv[i]=self.pv[i]+self.cx
            else:
                self.pv[i]=self.pv[i]+self.cy
        
        if pv_list==[]:
            self.recurse(num_deflect,deflect_list)
        else:
            self.pv=[]
            for i in pv_list:
                self.pv.append(i)
            self.deflects=[]
            for i in deflect_list:
                self.deflects.append(i)
        self.nv=len(self.pv)/2       
              
    def distort(self,source_poly,distance):
        for i in range(0,len(source_poly.deflects)):
            deflection=source_poly.deflects[i]
            angle=(deflection + random.uniform(distance/2,distance)*random.choice([-1,1]))
            self.deflect(angle)
            
    def draw(self,im):
        im.polygon(self.pv,fill=self.color)

    def deflect(self,angle=0):
        # spread points
        for i in range((self.nv*2),0,-2):
            self.pv.insert(i,0)
            self.pv.insert(i,0)
        self.pv.insert(len(self.pv),self.pv[0])
        self.pv.insert(len(self.pv),self.pv[1])
        self.nv=len(self.pv)/2

        # deflect midpoints
        # This produces random deflection angles
        if angle==0:
            ga=random.uniform(-1*self.deflect_size,self.deflect_size)
            # ga=100
        else:
            # This produces a specific deflection angle
            ga=angle
            # print ga    
        self.deflects.append(ga)
        for i in range(1,self.nv,2):
            mx=(self.pv[(i-1)*2]+self.pv[(i+1)*2])/2
            my=(self.pv[(i-1)*2+1]+self.pv[(i+1)*2+1])/2
            dx=self.pv[(i+1)*2]-self.pv[(i-1)*2]
            dy=self.pv[(i+1)*2+1]-self.pv[(i-1)*2+1]
            theta=math.atan2(dy,dx)
            self.pv[i*2]=mx+ga*math.sin(theta)
            self.pv[i*2+1]=my-ga*math.cos(theta)
        del self.pv[len(self.pv)-2:len(self.pv)]
        self.nv=len(self.pv)/2

        #check for off-screen points
        for i in range(0,len(self.pv)):
            if self.pv[i]<0:
                self.pv[i]=0;
            elif i%2==0:
                if self.pv[i]>=self.x:
                    self.pv[i]=self.x-1
            elif self.pv[i]>=self.y:
                self.pv[i]=self.y-1
                
    def recurse(self,n,deflect_list=[]):
        for i in range(0,n):
            if deflect_list:
                self.deflect(deflect_list[i])
            else:
                self.deflect()

    def print_size(self):
        mx=0
        my=0
        for i in range(0,self.nv*2,2):
            if abs(self.pv[i]-self.cx)>mx:
                mx=abs(self.pv[i]-self.cx)
            if abs(self.pv[i+1]-self.cy)>my:
                my=abs(self.pv[i+1]-self.cy)
        print "Scale %f, max X %d, max Y %d " % (self.scale,mx,my)
        

    def desc(self):
        print "Image size (%d,%d), Scale: %f " % (self.x,self.y,self.scale)
        print "Color ",self.color," init_shape %s, nv %d" % (self.init,self.nv)
        print "Deflections: ",self.deflects

    def save_txt(self,output_file):
        output_file.write("DEFLECTS:\n")
        for i in self.deflects:
            output_file.write("%s, " % i)
        output_file.write("\n\n")
        output_file.write("PV:\n")
        for i in self.pv:
            output_file.write('%s,' % i)
        output_file.write('\n\n***\n')

    def textDesc(self):
        s="DEFLECTS: "
        for i in self.deflects:
            s=s+"%s, " % i
        s=s+"\nPV: "
        for i in self.pv:
            s=s+'%s,' % i
        s=s+'\n***\n'
        return s

                    
class kaleido:
    def __init__(self):
        # these variables hold the kaleido vertex information
        self.deflects=[]
        self.pvs=[]
        self.polyList=[]
            
    def make(self,poly_type,size,npoly,num_deflect,scale,zoom,deflect_size,color_list=[]):
        self.deflect=num_deflect
        self.scale=scale
        self.npoly=npoly
        self.init=poly_type
        self.size=size
        self.zoom=zoom
        self.colors=color_list
        self.scale=scale
        self.deflect_size=deflect_size
        
        # if color list is not set, then make them random
        if self.colors==[]:
            for i in range(0,npoly):
                self.colors.append(random_color())
        else:
            print "*** color set:", self.colors
            
        curr_scale=self.scale
        # Generate a new kaleido
        if verbose:
            print "New kaleido:", self.npoly, self.colors
        for i in range(0,self.npoly):
            self.polyList.append(poly(self.init,curr_scale,self.size,self.colors[i],num_deflect,deflect_size=self.deflect_size))
            curr_scale=curr_scale*self.zoom
    # end create kaleido
    
    def copy(self,prototype,distort):
        if verbose:
            print "Copying kaleido"
        self.npoly=prototype.npoly
        self.init=prototype.init
        self.size=prototype.size
        self.zoom=prototype.zoom
        self.scale=prototype.scale
        self.colors=prototype.colors
        self.deflect_size=prototype.deflect_size

        # Create a distortion of a the source polygon
        curr_scale=self.scale
        for i in range(0,self.npoly):
            # first create a 0-deflect polygon:
            self.polyList.append(poly(self.init,curr_scale,self.size,self.colors[i],0))
            # then use the copy_from & distort parameters to make deflections
            self.polyList[-1].distort(prototype.polyList[i],distort)            
            curr_scale=curr_scale*self.zoom
       
    def resize(self,gdist):
        "Resize the whole image to the given frame"
        cx=self.polyList[0].cx
        cy=self.polyList[0].cy
        max_x=min_x=cx
        max_y=min_y=cy
        for p in self.polyList:
            for i in range(0,p.nv):
                if p.pv[i*2]>max_x:
                    max_x=p.pv[i*2]
                if p.pv[i*2]<min_x:
                    min_x=p.pv[i*2]
                if p.pv[i*2+1]>max_y:
                    max_y=p.pv[i*2+1]
                if p.pv[i*2+1]<min_y:
                    min_y=p.pv[i*2+1]
        adist=max(max_x-cx,cx-min_x,max_y-cy,cy-min_y)
        sf=gdist/adist
        #print sf,adist,gdist,max_x,min_x,max_y,min_y
        for p in self.polyList:
            for i in range(0,p.nv):
                p.pv[i*2]=(p.pv[i*2]-cx)*sf+cx
                p.pv[i*2+1]=(p.pv[i*2+1]-cy)*sf+cy


    def draw(self,im):
        for p in self.polyList:
            p.draw(im)

    def desc(self):
        num=1
        for p in self.polyList:
            print "Poly ",num
            p.desc()
            num=num+1
            
    def print_size(self):
        print "%d polygons" % self.npoly
        for p in self.polyList:
            p.print_size()

    def similarity(self,other):
        self.r=0.0
        for p in range(0,len(self.polyList)):
            for a in range(0,len(self.polyList[p].deflects)):
                difference=self.polyList[p].deflects[a]-\
                             other.polyList[p].deflects[a]
                self.r=self.r+difference*difference ### Squares the difference
        # No need to print, since it's saved in self.r
        #print "SUM OF SQUARES:"
        print self.r

    def save_img(self,num=1):
        surface=Image.new('RGB',size)
        im=ImageDraw.Draw(surface)
        self.draw(im)
        if self.distort==0:
            self.descriptive_filename="%s_%dp_%dnd_%dnv" % (self.init,self.npoly,self.deflect,self.polyList[0].nv)
        else:
            self.descriptive_filename="%s_%dp_%dnv_%d" % (self.init,self.npoly,self.polyList[0].nv, self.r)

        surface.save("%s-%d.jpg" % \
                     (self.descriptive_filename,num))
    
    def textDesc(self):
        s="poly_type=%s;size=%s;npoly=%s;deflect=%s;scale=%s;zoom=%s;colors=%s\n" % (self.init, self.size, self.npoly , len(self.polyList[0].deflects), self.scale, self.zoom, self.colors )
        for p in self.polyList:
            s=s+p.textDesc()
        return s
        
    def save_txt(self,suffix=1):
        f=open("%s-%s.kdf" % (self.descriptive_filename, suffix),"w")
        f.write("poly_type=%s;size=%s;npoly=%s;deflect=%s;scale=%s;zoom=%s;colors=%s\n" % (self.init, self.size, self.npoly , len(self.polyList[0].deflects), self.scale, self.zoom, self.colors ))
        f.write("***\n")
        for p in self.polyList:
            p.save_txt(f)
        f.write("\n")
        f.close()

    def load_fromfile(self,filename):
        self.filename=filename
        self.f=open(filename)
        self.p=self.f.read()
        self.f.close()
        parse_options=re.compile("poly_type=(\S);size=\((\d*),\s(\d*)\);npoly=(\d);deflect=(\d);scale=(\d*.\d*);zoom=(\d*.\d*);colors=\[\((\d*),\s(\d*),\s(\d*)\),\s\((\d*),\s(\d*),\s(\d*)\)\]")
        self.preoptions=parse_options.findall(self.p)
        self.options=self.preoptions[0]
        self.init=self.options[0]
        self.size=(int(self.options[1]), int(self.options[2]))
        self.npoly=int(self.options[3])
        self.deflect=int(self.options[4])
        self.scale=string.atof(self.options[5])
        self.zoom=string.atof(self.options[6])
        self.colors=[(int(self.options[7]),int(self.options[8]),int(self.options[9])), (int(self.options[10]),int(self.options[11]),int(self.options[12]))]

        pattern='DEFLECTS:\n(-*\d*.\d*)'
        for i in range(0, self.deflect-1):
            pattern=pattern + ',\s(-*\d*.\d*)'
        parse_deflects=re.compile(pattern)
        parse_pvs=re.compile("PV:\n(\S*)\n")

        pv_list=parse_pvs.findall(self.p)
        deflect_list=parse_deflects.findall(self.p)

        self.polyList=[]
        for i in range(0,self.npoly):
            self.polyList.append(poly(self.init,self.scale,self.size,self.colors[i],0,
                                      map(string.atof,string.split(pv_list[i],',')[:-1]),
                                      map(string.atof,deflect_list[i])))

class StimulusSet:
    # For holding a collection of kaleido's
    def __init__(self,num_images=1,canvas_size=(640,480)):       
        # number of images, sisters (and distance), color set style
        self.numImages=num_images
        self.make_sister=False
        self.canvasSize=canvas_size
        self.fixedColor=False
        self.kaleidoList={}
        
    def add_sisters(self,sister_distance=20,num_sisters=1):
        self.makeSisters=True
        self.numSisters=num_sisters
        self.sisterDistance=sister_distance
        
    def fix_color(self,color_list=[]):
        self.fixedColor=True
        self.colorScheme=color_list
    
    def set_kaleido(self,poly_type,npoly,scale,zoom,num_deflect,deflect_size):
        # kaleido creation parameters
        self.polyType=poly_type        # starting shape
        self.nPoly=npoly               # number of overlaid polygons
        self.scale=scale               # initial size scaling parameter
        self.zoom=zoom                 # size of overlaid polygons
        self.numDeflect=num_deflect    # Number of polygon deflections, increases complexity
        self.deflectSize=deflect_size  # Magnitude of the line deflection, larger increases complexity

    def fix_size(self):
        # Fixes to fill the image canvas
        gdist=min((self.canvasSize[0]/2),(self.canvasSize[1]/2))
        if verbose:
            print "Fixing size at",gdist
        for k in self.kaleidoList.keys():
            self.kaleidoList[k].resize(gdist)
        return

    def make_set(self,output_stem,extension='.png',verbose=True):
        if verbose:
            print "Size=(%d,%d), Scale=%f, Zoom=%f, Poly=%d, Deflect=(%d, %d)" % \
                (self.canvasSize[0],self.canvasSize[1],self.scale,self.zoom,self.nPoly,self.numDeflect,self.deflectSize)
            if self.fixedColor:
                print "Color scheme held constant"
    
        for i in range(0,self.numImages):
            k=kaleido()
            if self.fixedColor:  # pass color information                
                k.make(self.polyType,self.canvasSize,self.nPoly,self.numDeflect,self.scale,self.zoom,deflect_size=self.deflectSize,color_list=self.colorScheme)
            else:
                k.make(self.polyType,self.canvasSize,self.nPoly,self.numDeflect,self.scale,self.zoom,deflect_size=self.deflectSize,color_list=[])
            if self.makeSisters:
                fn="%s%03d_sis1%s" % (output_stem,i+1,extension)
                self.kaleidoList[fn]=(k)
                for j in range(self.numSisters):
                    sk=kaleido()
                    sk.copy(k,self.sisterDistance)
                    fn="%s%03d_sis%d%s" % (output_stem,i+1,j+2,extension)
                    self.kaleidoList[fn]=sk
            else:
                fn="%s%03d%s" % (output_stem,i+1,extension)
                self.kaleidoList[fn]=(k)

     
    def write_images(self,overwrite=True):
        for k in self.kaleidoList.keys():
            surface=Image.new('RGB',self.canvasSize)
            im=ImageDraw.Draw(surface)
            self.kaleidoList[k].draw(im)
            surface.save(k)
            
    def log_generation(self,logfile,overwrite=True):
        f=open(logfile,'w')
        f.write("Run on %s\n" % datetime.datetime.now().isoformat())
        f.write("Poly_type: %s\n" % self.polyType)
        f.write("nPoly: %s\n" % self.nPoly)
        f.write("Scale: %s\n" % self.scale)
        f.write("Zoom: %s\n" % self.zoom)
        f.write("Num_deflect: %s\n" % self.numDeflect)
        f.write("Deflect_size: %s\n" % self.deflectSize)
        if self.makeSisters:
            f.write("Sisters: %d\n" % self.numSisters)
            f.write("Sisters_deflection: %d\n" % self.sisterDistance)
        f.write("Image List:\n")
        for k in self.kaleidoList.keys():
            f.write("%s\n" % k)
        f.write("Kaleido parameters:\n")
        for k in self.kaleidoList.keys():
            f.write("%s\n" % k)
            f.write("%s\n" % self.kaleidoList[k].textDesc())
        f.close()
         

##########################

verbose=True

# Reset random number generator
random.seed()

S=StimulusSet(num_images=10,canvas_size=(800,800))
S.set_kaleido(poly_type='r',npoly=3,scale=1.5,zoom=0.7,num_deflect=4,deflect_size=90)
S.add_sisters(sister_distance=10,num_sisters=3)
S.make_set('kaleido')
S.fix_size()
S.write_images(overwrite=True)
S.log_generation('kaleido.log',overwrite=True)






