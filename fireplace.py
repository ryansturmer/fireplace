#!/usr/bin/python
import wx
from math import sqrt, pi, exp
import random

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

    def draw(self, dc):
        w,h = dc.GetSize()
        dc.SetBrush(wx.BLACK_BRUSH)
        dc.DrawRectangle(0,0,w,h)
        pw,ph = self.size
        cw, ch = int(float(w)/pw), int(float(h)/ph)
        j=0
        for row in range(ph):
            for col in range(pw):
                color = wx.Colour()
                cell = self.image[row][col]
                color.SetFromName(cell)
                dc.SetBrush(wx.Brush(color))
                dc.SetPen(wx.Pen(color))
                dc.DrawRectangle(cw*col, ch*row, cw, ch)
def rand():
    return 2*random.random()-1.0

CENTER1 = 0.5
CENTER2 = -0.5

def all_the_clamps(x, a,b):
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
def heights(cols, rows, sigma=1.0, center=0.0, max_height=1.0):
    MU = center
    A = 0.5*(sigma*sqrt(2*pi))
    B = MU
    C = sigma
    gauss = lambda x : A*exp(-((x-B)*(x-B))/(2*C*C))
    height = lambda col : int(max_height*rows*gauss(2*((float(col)/cols) - 0.5)))
    retval = []
    for i in range(cols):
        retval.append(height(i))
    return retval

def combine(a,b):
    return [ai+bi for ai,bi in zip(a,b)]

def gauss_fire(w,h, starting_point=None):
    global CENTER1,CENTER2
    SIGMA = 0.4
    #MU = rand()
    CENTER1 = all_the_clamps(CENTER1 + rand()/10.0, -0.75, 0.75)
    CENTER2 = all_the_clamps(CENTER2 + rand()/10.0, -0.75, 0.75)
    retval = starting_point or [['#000000' for i in range(w)] for j in range(h)]

    heights1 = heights(w,h,SIGMA,CENTER1, max_height=0.75)
    heights2 = heights(w,h,SIGMA,CENTER2, max_height=0.75)
    #heights2=[0]*w
    flame = combine(heights1,heights2)
    
    for col, height in enumerate(flame):

        for row in range(int(height*1.3) + random.choice(range(-2,3))):
            retval[int(h-row-1)][col] = '#660000'
        
        for row in range(height + random.choice(range(-1,2))):
            retval[int(h-row-1)][col] = '#ffcc00'

        for row in range(int(0.75*height) + random.choice(range(-1,2))):
            retval[int(h-row-1)][col] = '#ff9900'
        
        for row in range(int(0.25*height) + random.choice(range(-1,2))):
            retval[int(h-row-1)][col] = '#ffcc66'

    return retval

#DIMS = (48,48)
#DIMS = (32,32)
#DIMS = (16,16)
#DIMS = (24, 24)
DIMS = (16, 16)
FIRE_FUNCTION = gauss_fire
DARK = '#ff3300'
if __name__ == "__main__":
    app = wx.App(False)
    frame = wx.Frame(None)
    panel = PixelPanel(frame, DIMS)
    panel.set_image(FIRE_FUNCTION(*DIMS))
    panel.SetBackgroundColour(wx.RED)
    frame.SetSize((480,480))
    frame.SetTitle("Fireplace")
    frame.Show(True)
    
    def update_fire(evt):
        image = FIRE_FUNCTION(DIMS[0],DIMS[1])
        panel.set_image(image)
        panel.Refresh()
    timer = wx.Timer(panel)
    panel.Bind(wx.EVT_TIMER, update_fire, timer)
    timer.Start(100)
    
    app.MainLoop()
