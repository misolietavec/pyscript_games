# Inspired by Mats Lund:
# https://github.com/CoderMats/breakout 
# Completely rewritten

import js
from pyodide.ffi import create_proxy
p5 = js.window


WIDTH =  640    # canvas  width
HEIGHT = 400    # canvas height
P_WIDTH =  50   # paddle halfwidth
P_HEIGHT = 8    # paddle halfheight
B_ROWS = 5      # bricks, number of rows
B_COLS = 10     # bricks, number of columns
B_MARGINS = 15  # margins for bricks (bottom, side)
BALL_DIAM = 10  # diameter of ball
FPS = 20        # frames per second

# block width, height, total space
b_width = (WIDTH - 2 * B_MARGINS) // B_COLS
b_height = 40  
b_gap = 15      # gap between blocks

# constants, helper variables
bw2 = b_width // 2 
bh2 = b_height // 2
dw = (b_width - b_gap) // 2
dh = (b_height - b_gap) // 2
r = BALL_DIAM // 2    # ball diameter
y_paddle = HEIGHT - 30

cell_colors = {1:"green" , 2:"blue" , 3:"red" , 4:"yellow"}

game = None

def setup():
    global game
    p5.createCanvas(WIDTH, HEIGHT, p5.P2D)
    p5.rectMode(p5.CENTER)
    p5.frameRate(FPS)
    p5.noCursor()
    game = Game()

def new_game():
    global game
    new_level = game.level + int(game.blocks_gone)
    game = Game(level=new_level)
        
def draw(*args):
    global game
    if game.blocks_gone:
        new_game()    
    if p5.keyIsPressed:
        if (p5.keyCode == p5.RIGHT_ARROW) and (not game.game_over):  # Move right
            game.paddle.x = min(game.paddle.x + 12, WIDTH - P_WIDTH) 
        elif (p5.keyCode == p5.LEFT_ARROW) and (not game.game_over): # Move left
            game.paddle.x = max(game.paddle.x - 12, P_WIDTH)
        elif (p5.key == ' '):
            new_game()
    game.update()
    p5.requestAnimationFrame(create_proxy(draw))        

class Ball(object):
    def __init__(self,level=1):
        # ball velocity
        self.vel = p5.createVector(3 + int(1.5 * level),-3 - int(1.5 * level))
        xp = WIDTH // 2 + int(p5.random(-P_WIDTH - 40,P_WIDTH + 40))
        yp = y_paddle - P_HEIGHT // 2 - r - 1      
        self.pos = p5.createVector(xp,yp)                   # ball position

    def update(self):
        self.pos.add(self.vel)    
        if (self.pos.x >= WIDTH or self.pos.x <= 0):  
            self.vel.x = -self.vel.x
        if (self.pos.y <= 0):
            self.vel.y = -self.vel.y

class Game(object):
    def __init__(self,level=1):
        self.paddle = p5.createVector(WIDTH // 2, HEIGHT - 30)
        self.level = level
        self.ball = Ball()
        self.score = 0 
        self.blocks = [int(p5.random(1.5,4.5)) for k in  range(B_ROWS * B_COLS)]
        self.game_over = False
        self.blocks_gone = False
        # x, y positions of block centers
        self.centers = [((i % B_COLS) * b_width + B_MARGINS + bw2,
                         b_height * (i // B_COLS) + B_MARGINS + bh2) 
                         for i in range(B_ROWS * B_COLS)]

    def update_ball(self):
        self.ball.update()
        px, py = self.paddle.x, self.paddle.y
        if ((px - P_WIDTH -r) <= self.ball.pos.x
             <= (px + P_WIDTH + r) and 
            (py - P_HEIGHT - r <= self.ball.pos.y 
             <= py - P_HEIGHT)):
            # ball is hitting paddle rectangle, reverse y_speed
            self.ball.vel.y = -self.ball.vel.y
            self.score = self.score + 1
        p5.fill(100,100,200)
        p5.ellipse(self.ball.pos.x, self.ball.pos.y, BALL_DIAM, BALL_DIAM)

            
    def update_paddle(self):
        p5.fill(0,255,0)
        p5.rect(self.paddle.x, self.paddle.y, 2 * P_WIDTH, 2* P_HEIGHT)
        if (self.ball.pos.y >= HEIGHT):
            p5.fill(255) 
            p5.textSize(40)
            p5.textAlign(p5.CENTER)
            p5.text("Game over", WIDTH // 2, HEIGHT // 2 + 40)
            self.game_over = True 
    
    def update_texts(self):            
        p5.background(25)
        p5.noStroke()
        # Set fill color to white
        p5.fill(255)
        # Display score
        p5.textSize(16)
        p5.textAlign(p5.RIGHT)
        p5.text("Score", 80, HEIGHT - 6)
        p5.textAlign(p5.LEFT)
        p5.text(self.score, 90, HEIGHT - 6)
        # text("Frames: %.1f" %frameRate(), 130, HEIGHT - 6) 
        # Display level
        p5.textAlign(p5.RIGHT)
        p5.text("Level", WIDTH - 50, HEIGHT - 6)
        p5.textAlign(p5.LEFT)
        p5.text(self.level, WIDTH - 40, HEIGHT - 6)

    def update_blocks(self):
        self.blocks_gone = True
        # Loop through all the potential blocks
        collide = False

        for i in range(B_ROWS * B_COLS):
            # Check if we have that block
            if (self.blocks[i]):
                x_cent, y_cent = self.centers[i]
                self.blocks_gone = False
                    
                if not collide:
                    bx, by = self.ball.pos.x, self.ball.pos.y     
                    # check bounce on top/bottom
                    if ((x_cent - dw - r < bx < x_cent + dw + r) and 
                        ((y_cent + dh < by < y_cent + dh + r) or 
                        (y_cent -dh - r < by < y_cent - dh))):
                        self.blocks[i] = 0
                        self.ball.vel.y = -self.ball.vel.y
                        self.score = self.score + 5
                        collide = True
                     
                    # check bounce on left/right
                    if ((y_cent - dh - r < by < y_cent + dh + r) and 
                        ((x_cent + dw < bx < x_cent + dw + r) or 
                        (x_cent - dw -r < bx < x_cent - dw))):
                        self.blocks[i] = 0
                        self.ball.vel.x = -self.ball.vel.x
                        self.score = self.score + 5
                        collide = True
            if collide:
                break
                    
    def draw_blocks(self):
        for i in range(B_ROWS * B_COLS):
            if (self.blocks[i]):
                p5.fill(cell_colors[self.blocks[i]])
                x_cent, y_cent = self.centers[i]
                p5.rect(x_cent, y_cent, 2 * dw, 2 * dh)
                        
    def update(self):
        self.update_texts()
        self.update_ball()
        self.update_paddle()
        self.update_blocks()    
        self.draw_blocks()
        
setup()
p5.requestAnimationFrame(create_proxy(draw))                  
