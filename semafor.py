import js
from pyodide.ffi import create_proxy
p5 = js.window

from random import choice
fill = p5.fill
ellipse = p5.ellipse

WIDTH =  400
HEIGHT = 300
FPS =  30        # pocet ramcov (obrazkov) za sekundu
CAS =  5.04      # cas (sec), po ktory svieti ta ista kombinacia farieb
SVET_DIAM = 50   # svetlo, priemer
SEM_WIDTH  = 80
SEM_HEIGHT = 200
SEM_X = WIDTH  // 2 
SEM_Y = HEIGHT // 2

svetla = None
cas = 0.0

def setup():
    global svetla, cas 
    p5.createCanvas(WIDTH, HEIGHT)
    p5.frameRate(FPS)
    p5.rectMode(p5.CENTER)
    svetla = choice(farby)    
    kresli_semafor(svetla)
    
def draw(*args):
    p5.requestAnimationFrame(create_proxy(draw))
    uprav_cas()
    kresli_semafor(svetla)
    
     
# =======================================================

farby = [('red', 'orange', None), (None, None, 'green'),
         ('red', 'orange', 'green'),(None, 'orange', None),
         ('red', None, None)]
         
def kresli_semafor(svetla):
    p5.background(230)
    p5.fill('gray') 
    p5.rect(SEM_X, SEM_Y, SEM_WIDTH, SEM_HEIGHT)
         
    r, o, g = svetla
    if r: fill(r); ellipse(SEM_X, SEM_Y - SEM_HEIGHT / 3.5, SVET_DIAM)
    if o: fill(o); ellipse(SEM_X, SEM_Y, SVET_DIAM)
    if g: fill(g); ellipse(SEM_X, SEM_Y + SEM_HEIGHT / 3.5, SVET_DIAM)
    p5.fill(0)
    p5.textSize(24)
    p5.textAlign(p5.CENTER)
    p5.text("%d" %int(cas), WIDTH // 2, HEIGHT-18)
        
def uprav_cas():
    global cas, svetla
    if  cas > CAS:
        cas = 0.
        svetla = choice(farby)     
    cas += (1 / FPS)
        
setup()
p5.requestAnimationFrame(create_proxy(draw))
