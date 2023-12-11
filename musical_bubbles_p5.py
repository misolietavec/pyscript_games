import js
from pyodide.ffi import create_proxy
p5 = js.window
Envelope = p5.Envelope
Oscillator = p5.Oscillator
js = p5.js

# Port to pyscript by Ben Alkov, 2022-07
# Oscillator sound added by Andrew Hannum, 2022-07

import math

# Not strictly necessary, but seeing naked e.g. `document`, `window`, etc. really bothers me
import js
import random
from pyodide.ffi import create_proxy

NUM_BALLS = 10
SPRING = 0.9
GRAVITY = 0.03
FRICTION = -0.9
BALLS = []
HEIGHT = 400
WIDTH = 720

p5js = js.window

class Ball():
    def __init__(self, x, y, dia):
        self.x = x
        self.y = y
        self.diameter = dia
        self.vx = 0
        self.vy = 0
        self.osc = js.Oscillator.new()
        self.osc.freq(p5js.midiToFreq(random.choice([61, 63, 65, 68, 70])))
        self.env = js.Envelope.new(0.1, 0.1, 0.1, 0.1)
        self.osc.amp(self.env)
        self.osc.start()

    def collide(self):
        for other_ball in [b for b in BALLS if b is not self]:
            dx = other_ball.x - self.x
            dy = other_ball.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            min_dist = other_ball.diameter / 2 + self.diameter / 2
            if (distance < min_dist):
                angle = math.atan2(dy, dx)
                targetX = self.x + math.cos(angle) * min_dist
                targetY = self.y + math.sin(angle) * min_dist
                ax = (targetX - other_ball.x) * SPRING
                ay = (targetY - other_ball.y) * SPRING
                self.vx -= ax
                self.vy -= ay
                other_ball.vx += ax
                other_ball.vy += ay
                self.env.play()

    def move(self):
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy
        if self.x + self.diameter / 2 > WIDTH:
            self.x = WIDTH - self.diameter / 2
            self.vx *= FRICTION
        elif self.x - self.diameter / 2 < 0:
            self.x = self.diameter / 2
            self.vx *= FRICTION

        if self.y + self.diameter / 2 > HEIGHT:
            self.y = HEIGHT - self.diameter / 2
            self.vy *= FRICTION
        elif (self.y - self.diameter / 2 < 0):
            self.y = self.diameter / 2
            self.vy *= FRICTION

    def display(self):
        p5js.ellipse(self.x, self.y, self.diameter, self.diameter)


# These are named per convention: js doesn't know anything about them

def setup():
    global BALLS

    p5js.createCanvas(WIDTH, HEIGHT)
    BALLS = [Ball(p5js.random(WIDTH), p5js.random(HEIGHT), p5js.random(30, 70))
             for _ in range(NUM_BALLS)]
    p5js.noStroke()
    p5js.fill(255, 204)
    p5js.background(0)


def draw(*args):
    p5js.background(0)
    for ball in BALLS:
        ball.collide()
        ball.move()
        ball.display()
    p5js.requestAnimationFrame(create_proxy(draw))


setup()
p5js.requestAnimationFrame(create_proxy(draw))
