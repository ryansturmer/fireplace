#!/usr/bin/python
import wx
from math import sqrt, pi, exp
import random

def name2rgb(name):
    name = name.strip(' #')
    r = int(name[0:2],16)
    g = int(name[2:4],16)
    b = int(name[4:6],16)
    return r,g,b

COLOR1 = name2rgb('#000066') 
COLOR2 = name2rgb('#00ccff')
COLOR3 = name2rgb('#0099ff')
COLOR4 = name2rgb('#66ccff')

class PixelPanel(wx.Panel):
    def __init__(self, parent, size):
        self.size = size
        wx.Panel.__init__(self, parent, -1)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.i = 0 
    def set_image(self, image):
        self.image = image

    def on_size(self, evt):
        self.Refresh()
        evt.Skip()

    def on_paint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        self.draw(dc)
        if self.i < 20:
            self.save(dc, 'fire_%05d.png' % self.i)
        self.i+=1

    def save(self, dc, filename):
        # based largely on code posted to wxpython-users by Andrea Gavana 2006-11-08
        size = dc.Size

        bmp = wx.EmptyBitmap(size.width, size.height)

        memDC = wx.MemoryDC()

        memDC.SelectObject(bmp)

        memDC.Blit( 0, # Copy to this X coordinate
            0, # Copy to this Y coordinate
            size.width, # Copy this width
            size.height, # Copy this height
            dc, # From where do we copy?
            0, # What's the X offset in the original DC?
            0  # What's the Y offset in the original DC?
            )

        memDC.SelectObject(wx.NullBitmap)

        img = bmp.ConvertToImage()
        img.SaveFile(filename, wx.BITMAP_TYPE_PNG)

    def draw(self, dc):
        w,h = dc.GetSize()
        dc.SetBrush(wx.BLACK_BRUSH)
        dc.DrawRectangle(0,0,w,h)
        pw,ph = self.size
        cw, ch = int(float(w)/pw), int(float(h)/ph)
        j=0
        for row in range(ph):
            for col in range(pw):
                cell = self.image[row][col]
                color = wx.Colour(*cell)
                dc.SetBrush(wx.Brush(color))
                dc.SetPen(wx.Pen(color))
                dc.DrawRectangle(cw*col, ch*row, cw, ch)
def rand():
    return 2*random.random()-1.0

def all_the_clamps(x, a,b):
    if x < a:
        return a
    if x > b:
        return b
    return x

def combine(a,b):
    return [ai+bi for ai,bi in zip(a,b)]

class GaussBurner(object):
    def __init__(self, w,h,starting_point=None,sigma=0.4,center1=0.5,center2=-0.5):
        self.w = w
        self.h = h
        self.starting_point = starting_point
        self.center1 = center1
        self.center2 = center2
        self.retval = starting_point or [[(0,0,0) for i in range(w)] for j in range(h)]
        self.sigma = sigma

    def blank(self):
        for i in range(self.h):
            for j in range(self.w):
                self.retval[i][j] = self.starting_point[i][j] if self.starting_point else (0,0,0)

    def clamp(self, x, a,b):
        if x < a:
            return a
        if x > b:
            return b
        return x

    # center: -1.0 to 1.0 (far left to far right)
    # max_height: Maximum hight (0 to 100% of rows)
    # cols: number of columns in the fire
    # rows: number of rows in the fire
    # sigma: science factor - try 1.0
    def heights(self, center=0.0, max_height=1.0):
        MU = center
        A = 0.5*(self.sigma*sqrt(2*pi))
        B = MU
        C = self.sigma
        gauss = lambda x : A*exp(-((x-B)*(x-B))/(2*C*C))
        height = lambda col : int(max_height*self.h*gauss(2*((float(col)/self.w) - 0.5)))
        retval = []
        for i in range(self.w):
            retval.append(height(i))
        return retval


    def burn(self):
        
        self.blank()

        self.center1 = self.clamp(self.center1 + rand()/10.0, -0.75, 0.75)
        self.center2 = self.clamp(self.center2 + rand()/10.0, -0.75, 0.75)
        
        heights1 = self.heights(self.center1, max_height=0.75)
        heights2 = self.heights(self.center2, max_height=0.75)
        flame = combine(heights1,heights2)
        
        for col, height in enumerate(flame):

            for row in range(int(height*1.3) + random.choice(range(-2,3))):
                self.retval[int(self.h-row-1)][col] = COLOR1
            
            for row in range(height + random.choice(range(-1,2))):
                self.retval[int(self.h-row-1)][col] = COLOR2

            for row in range(int(0.75*height) + random.choice(range(-1,2))):
                self.retval[int(self.h-row-1)][col] = COLOR3
            
            for row in range(int(0.25*height) + random.choice(range(-1,2))):
                self.retval[int(self.h-row-1)][col] = COLOR4

        return self.retval

burner = GaussBurner(16,16)

if __name__ == "__main__":
    app = wx.App(False)
    frame = wx.Frame(None)
    panel = PixelPanel(frame, (burner.w,burner.h))
    panel.set_image(burner.burn())
    
    frame.SetSize((16,16))
    frame.SetTitle("Fireplace")
    frame.Show(True)
    
    def update_fire(evt):
        image = burner.burn() 
        panel.set_image(image)
        panel.Refresh()
    
    timer = wx.Timer(panel)
    panel.Bind(wx.EVT_TIMER, update_fire, timer)
    timer.Start(100)
    
    app.MainLoop()
