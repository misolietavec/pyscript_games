import js
from pyodide.ffi import create_proxy
p5 = js.window

from py_p5 import *

x = 50
y = 100
rad = 6

vx = 5
vy = 6

WIDTH = 640
HEIGHT = 400
FPS = 60

def setup():
    createCanvas(WIDTH, HEIGHT)
    frameRate(FPS)

def draw(*args):
    global x, y, vx, vy
    
    background(220)
    fill(0, 255, 0)
    ellipse(x, y, 2 * rad)

    x += vx
    y += vy
  
    if (x + rad >= WIDTH or x - rad <= 0):
        vx = -vx
    
    if (y + rad >= HEIGHT or y - rad <= 0):
        vy = -vy
    requestAnimationFrame(create_proxy(draw))

setup()
requestAnimationFrame(create_proxy(draw))

