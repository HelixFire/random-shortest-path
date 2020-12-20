import random, time, pygame, pygame.gfxdraw, pygame.font, math
import numpy as np
from pygame import ftfont as pygame_font

colors = {
    'black'         : (0,0,0),
    'white'         : (255,255,255),
    'lightgrey'     : (191,191,191),
    'grey'          : (127,127,127),
    'darkgrey'      : (64,64,64),
    'red'           : (255,0,0),
    'lightred'      : (255,100,100),
    'darkred'       : (100,0,0),
    'green'         : (0,255,0),
    'lightgreen'    : (100,255,100),
    'darkgreen'     : (0,100,0),
    'blue'          : (0,0,255),
    'lightblue'     : (100,100,255),
    'darkblue'      : (0,0,100),
    'yellow'        : (200,200,0),
    'lightyellow'   : (255,255,100),
    'darkyellow'    : (100,100,0),
}

class Grid:
    def __init__(self,win,corner,size,cells,id,probability=0.95):
        self.win = win #surface
        self.corner = corner   #tuple
        self.size = size   #tuple
        self.cells = cells #int
        self.id = id    #string

        self.endcorner = at(corner,size) #tuple
        self.probability = probability   #float
        self.data = rand_bool_grid((cells,cells),probability)    #2d np list
        self.step_size = int(size[0]/cells) #int
        self.cell_size = (self.step_size,self.step_size)    #tuple
        self.is_active = False  #bool

        error_x = int((size[0]-cells*self.step_size)/2)  
        error_y = int((size[1]-cells*self.step_size)/2)
        self.e_corner = at(corner,(error_x,error_y)) #tuple
        self.e_size = mt(self.cell_size,(cells,cells))   #tuple
        self.rects = self.get_rects()   #list

    def draw_grid(self):
        for y in range(self.cells):
            for x in range(self.cells):
                self.draw_data((x,y))
        
    def draw_data(self,index):
        if self.data[index[1]][index[0]] == 1:
            color = colors['black']
            f_color = colors['white']
        elif self.data[index[1]][index[0]] == 0:
            color = colors['white']
            f_color = colors['black']
        elif self.data[index[1]][index[0]] == 2:
            color = colors['darkgreen']
            f_color = colors['white']
                
        rect = self.rects[self.cells*index[1]+index[0]]

        pygame.draw.rect(self.win,color,rect,0)
        pygame.draw.rect(self.win,f_color,rect,1)

    def find_next(self,pos):
        idx = self.get_cell_index(pos)
        next_cell = find_next(self.data,idx)
        pos_cell = self.get_cell_pos(next_cell)

        return[next_cell,pos_cell]

    def rand(self):
        self.data = rand_bool_grid((self.cells,self.cells),self.probability)

    def ongrid(self,pos):
        inside_x = pos[0] > self.e_corner[0] and pos[0] < self.e_corner[0]+self.e_size[0]
        inside_y = pos[1] > self.e_corner[1] and pos[1] < self.e_corner[1]+self.e_size[1]
        if inside_x and inside_y:
            return True
        else:   return False

    def get_cell_pos(self,index):
        if index == False:
            posx,posy = at(self.corner,dt(self.size,(2,2)))
        else:
            posx = int(self.e_corner[0] + int(self.step_size/2) + index[0] * self.step_size)
            posy = int(self.e_corner[1] + int(self.step_size/2) + index[1] * self.step_size)
        return (posx,posy)

    def get_cell_index(self,pos):
        ix = int((pos[0]-self.e_corner[0])/self.step_size)
        iy = int((pos[1]-self.e_corner[1])/self.step_size)
        return(ix,iy)

    def click(self,pos):
        rect = pygame.Rect(self.corner,self.size)

        if pygame.Rect.collidepoint(rect,pos):
            return True
        else:
            return False

    def get_rects(self):
        celloffset = dt(self.cell_size,(2,2))

        def midpoints():
            for x in range(self.cells**2):
                xoff = x%self.cells * self.step_size
                yoff = int(x/self.cells) * self.step_size
                yield at(at(self.e_corner,(xoff,yoff)),celloffset)

        rects = []
        for point in midpoints():
            corner = st(point,celloffset)
            rects.append(pygame.Rect(corner,self.cell_size))

        return rects

class Button:
    def __init__(self,win,corner,size,color,name='none'):
        self.win = win #surface
        self.corner = corner   #tuple
        self.size = size   #tuple
        self.color = color #tuple
        self.name = name   #string
        
        self.padding = dt(self.size,(5,5))
        self.is_active = False

    def draw_button(self,color):
        rect = pygame.Rect(self.corner,self.size)

        pygame.draw.rect(self.win,colors['light'+color],rect,0)
        pygame.draw.rect(self.win,colors['darkgrey'],rect,2)

        rect = pygame.Rect.inflate(rect,-self.padding[0],-self.padding[1])

        pygame.draw.rect(self.win,colors[color],rect,0)
        pygame.draw.rect(self.win,colors['darkgrey'],rect,1)

    def draw(self):
        if self.is_active:
            self.draw_button(self.color)
        else:
            if self.name == 'quit':
                color = 'red'
            elif self.name == 'update':
                color = 'green'
            else:
                color = 'grey'
            self.draw_button(color)

    def click(self,pos):
        rect = pygame.Rect(self.corner,self.size)

        if pygame.Rect.collidepoint(rect,pos):
            return True
        else:
            return False

class Arrow:
    def __init__(self,win,spos,epos,color=colors['red']):
        self.win = win
        self.spos = spos
        self.epos = epos
        self.color = color

    def draw(self):
        pygame.draw.line(self.win, self.color, self.spos, self.epos, 5)
    
    def drawgrid(self,grid):
        diff = self.get_lengh()
        points = list(range(int(diff)))
        lpt = (diff,diff)
        delta = dt(st(self.spos,self.epos),lpt)
        offset = at(grid.e_corner,self.epos)

        for x in points:
            point = at(mt(delta,(x,x)),self.epos)
            for rect in grid.rects:
                if pygame.Rect.collidepoint(rect,point):
                    grid.drawdata(grid.get_cell_index(point))

        pygame.draw.line(self.win, self.color, self.spos, self.epos, 5)
  
    def get_angle(self):
        dx = self.spos[0]-self.epos[0]
        dy = 0-(self.spos[1]-self.epos[1])

        if dx == 0:
            dx = -0.0001
        angle = math.atan(abs(dy)/abs(dx))

        angle *= 180/math.pi

        if dx < 0 and dy == 0:
            angle = 180
        elif dx < 0 and dy > 0:
            angle = 90-angle+90
        elif dx < 0 and dy < 0:
            angle += 180
        elif dx > 0 and dy < 0:
            angle = 90-angle+270

        angle %= 360

        return int(angle)

    def get_lengh(self):
        d = st(self.spos,self.epos)
        return (d[0]**2+d[1]**2)**0.5

def clear_debug(grids,win,color=colors['black']):
    winsize = pygame.Surface.get_size(win)
    pygame.gfxdraw.box(win,(grids[3].endcorner[0]+2,winsize[1]-210,winsize[0],winsize[1]),color)

def clear_screen(win):
    pygame.gfxdraw.box(win,pygame.Surface.get_rect(win),colors['black'])

def table(y_len, x_len, y_zero, x_zero):
    a = np.zeros((y_len,x_len))
    b = np.zeros((y_len,x_len))

    for y in range(-y_zero, y_len - y_zero):
        a[y + y_zero] = abs(y)

    for x in range(-x_zero, x_len - x_zero):
        b[:, [x + x_zero]] = abs(x)

    return np.sqrt(np.square(a)+np.square(b))

def index_gen(size_y, size_x, y_zero, x_zero):
        len_table = table(size_y, size_x, y_zero, x_zero)

        for x in range(size_y*size_x):
            idx = len_table.argmin()

            yield idx
        
            y = int(idx/size_x)
            len_table[y][idx-y*size_x] = 2*size_x

def find_next(grid, pos):
    size = len(grid[0])
    for index in index_gen(len(grid), size, pos[1], pos[0]):
        y_idx = int(index/size)
        x_idx = index - size * y_idx
        
        if grid[y_idx][x_idx]:
            return  (x_idx,y_idx)
    return False

def rand_bool_grid(size, p = 0.95):
        return np.random.choice([0,1], size, p=[p, 1-p])

def at(a,b):
    return (a[0]+b[0],a[1]+b[1])

def st(a,b):
    return (a[0]-b[0],a[1]-b[1])

def mt(a,b):
    return (a[0]*b[0],a[1]*b[1])

def dt(a,b):
    return (a[0]/b[0],a[1]/b[1])
