import js
from pyodide.ffi import create_proxy
p5 = js.window


def colliderect(im1,im2):
    x1,y1, w1, h1 = im1.x,im1.y,im1.img.width,im1.img.height
    x2,y2, w2, h2 = im2.x,im2.y,im2.img.width,im2.img.height
    return ((x1 < x2 + w2) and (y1 < y2 + h2) and
            (x1 + w1 > x2) and (y1 + h1 > y2))


def load_image(img_file, im_dir="images",ext="png"):
    img = p5.loadImage("%s/%s.%s" %(im_dir,img_file,ext))    
    return img

     
class Actor:
    def __init__(self,img,x=0,y=0):
        self.img = load_image(img)
        self.x = x
        self.y = y

    def draw(self):
        p5.image(self.img,self.x,self.y)
     
WIDTH =  400
HEIGHT = 708
                 
# These constants control the difficulty of the game
GAP = 130
GRAVITY = 0.3
FLAP_STRENGTH = 6.5
SPEED = 3

background, bird, pipe_top, pipe_bottom = None, None, None, None
bird1, bird2, birddead = None, None, None

def setup():
    global background, bird, pipe_top, pipe_bottom, bird1, bird2, birddead
    p5.createCanvas(WIDTH, HEIGHT)
    p5.noCursor()
    bird = Actor("bird1",75,200)
    bird.score = 0
    bird.dead = False
    bird.vy = 0
    gap_y = int(p5.random(200, HEIGHT - 200))
    pipe_top = Actor("top")
    pipe_top.x, pipe_top.y = WIDTH, gap_y - GAP // 2 - 500
    pipe_bottom = Actor("bottom")
    pipe_bottom.x, pipe_bottom.y = WIDTH, gap_y + GAP // 2
    background = load_image("background")
    bird1 = load_image("bird1")
    bird2 = load_image("bird2")
    birddead = load_image("birddead")
    p5.image(background,0, 0)
    bird.draw()
    pipe_top.draw()
    pipe_bottom.draw()

def draw(*args):
    p5.image(background, 0, 0)
    update_pipes()
    update_bird()
    bird.draw()
    pipe_top.draw()
    pipe_bottom.draw()
    p5.fill(255)
    p5.textSize(24)
    p5.text("Score: %d" %bird.score, WIDTH-140, 30)
    p5.requestAnimationFrame(create_proxy(draw))
    
def keyPressed():
    if p5.keyIsPressed:
        if not bird.dead:
            bird.vy = -FLAP_STRENGTH

def reset_pipes(create=False):
    gap_y = int(p5.random(200, HEIGHT - 200))
    # anchor - left bottom
    pipe_top.x, pipe_top.y = WIDTH, gap_y - GAP // 2 - pipe_top.img.height
    pipe_bottom.x, pipe_bottom.y = WIDTH, gap_y + GAP // 2
           

def update_pipes():
    pipe_top.x -= SPEED
    pipe_bottom.x -= SPEED
    if (pipe_top.x  < 0):
        reset_pipes()
        if not bird.dead:
            bird.score += 1

def update_bird():
    keyPressed()
    uy = bird.vy
    bird.vy += GRAVITY
    bird.y += (uy + bird.vy) / 2
    bird.x = 75

    if not bird.dead:
        if bird.vy < -3:
            bird.img = bird2
        else:
            bird.img = bird1

    if colliderect(bird,pipe_top) or colliderect(bird,pipe_bottom):
        bird.dead = True
        bird.img = birddead
 
    if not (0 < bird.y < HEIGHT + 12):
        bird.y = 200
        bird.dead = False
        bird.score = bird.vy = 0
        reset_pipes()

setup()
p5.requestAnimationFrame(create_proxy(draw))
