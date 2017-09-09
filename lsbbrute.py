#!/usr/bin/python
#-*- coding:utf-8 -*-

import sys

import cv2.cv as cv
import filesig

def is_ascii(c):
    return 32 <= ord(c) < 127

def get_ascii_per(s):
    '''return percentage of 'printable' ascii char in s'''
    return (reduce(lambda acc,x: acc+(1 if x else 0),[ is_ascii(x) for x in s])*100)/len(s)

def nsplit(s, n):
    '''Split a list into sublists of size "n"'''
    return [s[k:k+n] for k in xrange(0, len(s), n)]

def bit_to_bytes_string(s):
    ''' Join all the bit together to recreate the string'''
    return ''.join([chr(int(x,2)) for x in nsplit(s, 8)])

class LSBBruteForcer():
    def __init__(self, im):
        self.image = im
        self.save_match = True                    #Save the dump when a sig match     
        self.ascii_threshold = 30                 #Threshold of ascii chars
        self.ignore_sigs = ["\xff","\xff\xff\xff\xff"] #Avoid generating too much false positive
        
    def get_rotated(self,im=None):
        ''' Return a list of the fourth possible image rotation '''
        l= []
        tmp_im = self.image if im is None else im
        l.append(tmp_im) #Add the file without rotation
        for i in range(3):
          im_rot = cv.CreateImage((tmp_im.height,tmp_im.width), tmp_im.depth, tmp_im.channels)
          cv.Transpose(tmp_im,im_rot)
          cv.Flip(im_rot,im_rot,flipMode=1)
          l.append(im_rot)
          tmp_im = im_rot
        return l

    def get_separated_channels(self):
        ''' Split the channels of an image '''
        b = cv.CreateImage(cv.GetSize(self.image),self.image.depth, 1)
        g = cv.CloneImage(b)
        r = cv.CloneImage(b)
        cv.Split(self.image, b, g, r, None)
        return [b,g,r]

    def get_shuffled_channels(self):
        ''' Create a list of images with all channels combination '''
        b,g,r = self.get_separated_channels()
        l = []
        for x,y,z in [(r,g,b),(r,b,g),(g,r,b),(g,b,r),(b,g,r),(b,r,g)]:
            merged = cv.CreateImage(cv.GetSize(self.image), 8, 3)
            cv.Merge(x, y, z, None, merged)
            l.append(merged)
        return l

    def brute_single(self, im=None, **kwargs):
        ''' Iterate the various list and modes to find file signature '''
        im = self.image if im is None else im
        for bit_mode in ["msb","lsb"]:
            for iter_mode in ["line","column"]:
                for read_mode in ["straight","reverse"]:
                    kwargs["bitmode"] = bit_mode
                    kwargs["itermode"] = iter_mode
                    kwargs["readmode"] = read_mode
                    s=""
                    if iter_mode == "line":
                        s = ''.join([cv.GetRow(im,x).tostring() for x in range(im.height)])
                    else:
                        s = ''.join([cv.GetCol(im,x).tostring() for x in range(im.width)])
                    mask = 128 if bit_mode == "msb" else 1
                    bitstring = ''.join([str(0 if (ord(c) & mask) == 0 else 1) for c in s ])
                    bytestring = bit_to_bytes_string(bitstring)
                    final = bytestring if read_mode == "straight" else bytestring[::-1]
                    self.analyse(final, **kwargs)

    def analyse(self, s, **kwargs):
        ''' Method in charge to find matches with signatures '''
        self.print_status(**kwargs)
        if filesig.is_known(s):
            for match in filesig.get_match(s):
                sig = match['signature']
                if sig not in self.ignore_sigs:
                    print("description %s\t extension:%s\tcategory:%s\tsignature:%s"%(match['description'],match['extension'],match['category'],match['signature']))
                    if self.save_match:
                        f = open(self.to_name(**kwargs),"wb")
                        f.write(s)
                        f.close()
        if get_ascii_per(s) >= self.ascii_threshold:
            print("ASCII match > "+str(self.ascii_threshold)+"%")

    def to_name(self, **kwargs):
        ''' Just create an name (when dumping hidden files) '''
        infos = kwargs["rot"] if kwargs.has_key("rot") else "unknown"
        infos += "_"+(kwargs["color"] if kwargs.has_key("color") else "unknown")
        infos += "_"+(kwargs["bitmode"] if kwargs.has_key("bitmode") else "unknown")
        infos += "_"+(kwargs["itermode"] if kwargs.has_key("itermode") else "unknown")
        infos += "_"+(kwargs["readmode"] if kwargs.has_key("readmode") else "unknown")
        return infos

    def print_status(self, **kwargs):
        infos = "rot:"+(kwargs["rot"] if kwargs.has_key("rot") else "unknown")
        infos += " color:"+(kwargs["color"] if kwargs.has_key("color") else "unknown")
        infos += " mode:"+(kwargs["bitmode"] if kwargs.has_key("bitmode") else "unknown")
        infos += " Iter:"+(kwargs["itermode"] if kwargs.has_key("itermode") else "unknown")
        infos += " way:"+(kwargs["readmode"] if kwargs.has_key("readmode") else "unknown")
        print(infos)

    def brute_all(self):
        order = ["blue","green","red","RGB","RBG","GRB","GBR","BGR","BRG"]
        for color, img in zip(order, self.get_separated_channels()+self.get_shuffled_channels()):
            for rot,img_r in zip(["0","90","180","260"],self.get_rotated(img)):
                self.brute_single(img_r,**{"rot":rot,"color":color})

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("./brute.py filename")
        sys.exit(1)
    else:
        try:
            img = cv.LoadImage(sys.argv[1])
            brute = LSBBruteForcer(fn)
            brute.brute_all()
            sys.exit(0)
        except IOError:
            print("Image type not handled")
            sys.exit(1)