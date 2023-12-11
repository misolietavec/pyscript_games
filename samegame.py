import js
from pyodide.ffi import create_proxy
p5 = js.window

NROWS =  10      # numer of brick rows 
NCOLS =  20      # number of brick columns
NCOLORS = 4      # 1 .. 5
B_WIDTH = 50     # brick width
FPS = 30         # frames per second
C_WIDTH =  NCOLS * B_WIDTH # canvas width
C_HEIGHT = NROWS * B_WIDTH # canvas height 

game = None
canvas = None

def setup():
    global game, canvas
    canvas = p5.createCanvas(C_WIDTH, C_HEIGHT, p5.P2D)
    canvas.mousePressed(create_proxy(mousePressed))
    p5.rectMode(p5.CENTER)
    p5.frameRate(FPS)
    game = SameGame()
    

def draw(*args):
    global game
    game.plotBoard()
    p5.requestAnimationFrame(create_proxy(draw))

                
def inCell(x,y):
    return (int(x) // (B_WIDTH + 1), int(y) // (B_WIDTH + 1))

def inCanvas(x,y):
    return  (0 <=  x <= C_WIDTH) and (0 <= y <= C_HEIGHT)

def mousePressed(event):
    global game
    x, y = p5.mouseX, p5.mouseY
    i, j = inCell(x,y)
    if (0 <= i < game.nc) and (0 <= j < game.nr):
        if not game.alone(i,j):
            game.floodfill(i,j)
            game.fall_all()

def PyKeyTyped(event):
    global game
    if event.key == "n":
        game = SameGame()
    elif event.key in ("3","4","5"):
        colors = int(event.key)    
        game = SameGame(ncolors=colors)

p5.keyTyped = create_proxy(PyKeyTyped)        

         
cell_colors = {0:"black", 1:"green", 2:"blue", 
               3:"red", 4:"yellow", 5:"magenta"}

def cells(colors_only=False,ncolors=NCOLORS):
    ycent = B_WIDTH // 2
    pos =    [[0] * NROWS for col in range(NCOLS)]
    colors = [[0] * NROWS for col in range(NCOLS)]  
    # store cell centers coordinates and colors, columnwise
    for row in range(NCOLS):
        xcent = -B_WIDTH // 2
        for col in range(NROWS):   
            xcent += B_WIDTH
            pos[row][col] = (ycent,xcent)
            colors[row][col] = int(p5.random(1, ncolors + 1))
        ycent += B_WIDTH
    if not colors_only:    
        return pos, colors
    return colors

class SameGame:
    def __init__(self,nr=NROWS, nc=NCOLS, ncolors=NCOLORS, 
                 colors=None, pos=None, score=0, score_diff=0, 
                 empty_cols = None, to_fill=None,score_corr=0):
        self.nr = nr
        self.nc = nc
        self.ncolors = ncolors
        self.to_fill = set()
        self.score = score
        self.score_diff = score_diff
        self.score_corr = score_corr
        self.empty_cols = []
        self.pos, self.colors = cells(ncolors=ncolors) 
        
    def plotBoard(self):
        for row in range(NROWS):
            for col in range(NCOLS):
                xc, yc = self.pos[col][row]   
                p5.fill(cell_colors[self.colors[col][row]])
                p5.rect(xc,yc,B_WIDTH,B_WIDTH)
                
        p5.fill(255)
        p5.textSize(20)
        p5.textAlign(p5.RIGHT)
        p5.text("Score: %d" %self.score, 130, C_HEIGHT - 6)

        if self.endGame():
            if not self.score_corr: 
                self.score_correction()
                self.score_corr = True
            self.compactLeft()
            p5.textSize(36)
            p5.textAlign(p5.CENTER)
            p5.text("End of Game",C_WIDTH // 2, C_HEIGHT // 2 - 10)

    def neighbours(self,i,j):
        possible = [(i-1,j),(i+1,j),(i,j-1),(i,j+1)]
        
        return [p for p in possible if (0 <= p[0] < self.nc) 
                                   and (0 <= p[1] < self.nr)]
    
    def alone(self,i,j):
        # i -column, j - row
        color = self.colors[i][j]
        res = True
        if color == 0:
            return True
        for k,l in self.neighbours(i,j):
            if self.colors[k][l] == color:
                res = False
                break
        return res        
    
    def floodfill(self, i, j,color=None):        
        if color == None:
            self.to_fill = set()
            if self.colors[i][j]:
                color = self.colors[i][j]
            if self.alone(i,j):
                return 
        if self.colors[i][j] == color:
            self.colors[i][j] = 0
            self.to_fill.add(i)
            self.score_diff += 1
        else:
            return
        for k,l in self.neighbours(i,j):
            self.floodfill(k,l,color=color)

    def fall_column(self,col):
        if sum(self.colors[col]) == 0:
            self.empty_cols.append(col)
            return
        colored = []
        for row in range(self.nr):
            cc = self.colors[col][row]
            if cc:
                colored.append(cc)
        lc = len(colored)
        new_col = [0] *(self.nr - lc) + colored
        self.colors[col] = new_col         
                        
    def compactLeft(self):
        if self.empty_cols == []:
            return 
        for c in sorted(self.empty_cols,reverse=True): 
            for cindex in range(c,self.nc-1):
                    self.colors[cindex] = self.colors[cindex + 1]
            self.colors[self.nc-1] = [0] * self.nr
        self.empty_cols = []
          
    def fall_all(self):
        if self.to_fill == []:
            self.score_diff = 0
            return
        for col in self.to_fill:
            self.fall_column(col)
        self.compactLeft()
        nscore = self.score_diff - 1    
        self.score += (nscore * nscore)
        self.score_diff = 0
            
    def endGame(self):
        return sum([self.alone(i,j) for i in range(self.nc) 
                    for j in range(self.nr)]) == self.nr * self.nc

    def score_correction(self):
        rem = sum(bool(self.colors[c][r]) for c in range(self.nc) 
                                          for r in range(self.nr)) 
        if rem == 0:
            self.score += 1000
        else:
            self.score -= (rem-1)*(rem-1)

setup()
p5.requestAnimationFrame(create_proxy(draw))
