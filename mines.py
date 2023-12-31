import js
from pyodide.ffi import create_proxy
p5 = js.window

from random import randint

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

NCOLS  = 10
NROWS  = 10
NMINES = 10
CELLSIZE = 60
WIDTH =  NCOLS * CELLSIZE + CELLSIZE // 2 + 1
HEIGHT = NROWS * CELLSIZE + CELLSIZE // 2 + 1

top_grid = None
base_grid = None
cover = None
flag = None
tiles = None

def setup():
    global top_grid, base_grid, cover, flag, tiles
    top_grid  = setup_empty_grid(NCOLS, NROWS, 1)
    base_grid = setup_empty_grid(NCOLS, NROWS, 0)
    populate_grid(NMINES, NCOLS, NROWS)
    count_mines()
    canvas = p5.createCanvas(WIDTH, HEIGHT)
    canvas.mousePressed(create_proxy(mousePressed))
    cover = Actor('cover')
    flag  = Actor('flag')
    tiles = {0: Actor('blank'), 1: Actor('one'), 2: Actor('two'),
             3: Actor('three'), 4: Actor('four'),5: Actor('five'),
             6: Actor('six'), 7: Actor('seven'), 8: Actor('eight'),
             'M': Actor('mine')}

def draw(*args):
    p5.requestAnimationFrame(create_proxy(draw))
    ypos = -CELLSIZE
    for row in range(NROWS):
        ypos += CELLSIZE
        xpos = -CELLSIZE 
        for col in range(NCOLS):
            xpos += CELLSIZE
            gridpos = base_grid[row][col]
            tiles[gridpos].x,tiles[gridpos].y = xpos, ypos
            tiles[gridpos].draw()
    ypos = -CELLSIZE
    for row in range(NROWS):
        ypos += CELLSIZE
        xpos = -CELLSIZE 
        for col in range(NCOLS):
            xpos += CELLSIZE
            if top_grid[row][col] == 1:
                cover.x, cover.y = xpos, ypos
                cover.draw()
            elif top_grid[row][col] == 'F':
                flag.x, flag.y = xpos, ypos
                flag.draw()

def mousePressed(event):
    col, row = p5.mouseX // CELLSIZE, p5.mouseY // CELLSIZE
    if not ((0 <= col < NCOLS) and (0 <= row < NROWS)):
        return
    if p5.mouseButton == p5.LEFT:
        if top_grid[row][col] != 'F':
            top_grid[row][col] = 0
            if base_grid[row][col] == 0:
                edge_detection(col, row)
    elif p5.mouseButton == p5.CENTER:
        if top_grid[row][col] == 1:
            top_grid[row][col] = 'F'
        elif top_grid[row][col] == 'F':
            top_grid[row][col] = 1


def setup_empty_grid(NCOLS, NROWS, filler):
    grid = [[filler] * NCOLS for rows in range(NROWS)]
    return grid

def populate_grid(NMINES, NCOLS, NROWS):
    global base_grid
    for mine in range(NMINES):
        col, row = randint(0, NCOLS - 1), randint(0,NROWS - 1)
        while base_grid[row][col] == 'M':
            col, row = randint(0, NCOLS - 1), randint(0,NROWS - 1)
        base_grid[row][col] = 'M'

def count_mines():
    global base_grid
    for r in range(NROWS):
        for c in range(NCOLS):
            if base_grid[r][c] != 'M':
                neighbors = [(c - 1, r - 1), (c, r - 1), (c + 1, r - 1),
                             (c - 1, r),                     (c + 1, r),
                             (c - 1, r + 1), (c, r + 1), (c + 1, r + 1)]
                for nx, ny in neighbors:
                    try:
                        if ny >= 0 and nx >= 0 and base_grid[ny][nx] == 'M':
                            base_grid[r][c] += 1
                    except IndexError:
                        pass


def edge_detection(col, row):
    zeros = [(col, row)]
    for c, r in zeros:
        top_grid[r][c] = 0
        neighbors = [(c - 1, r - 1), (c, r - 1), (c + 1, r - 1),
                     (c - 1, r    ),             (c + 1, r    ),
                     (c - 1, r + 1), (c, r + 1), (c + 1, r + 1)]
        for nx, ny in neighbors:
            try:
                if ny >= 0 and nx >= 0:
                    if base_grid[ny][nx] == 0 and top_grid[ny][nx] == 1:
                        if top_grid[ny][nx] != 'F':
                            top_grid[ny][nx] = 0
                        if (nx, ny) not in zeros:
                            zeros.append((nx, ny))
                    else:
                        if top_grid[ny][nx] != 'F':
                            top_grid[ny][nx] = 0

            except:
                pass

setup()
p5.requestAnimationFrame(create_proxy(draw))
