import random, time, pygame, pygame.gfxdraw, pygame.font, math
from pygame import ftfont as pygame_font
import numpy as np

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
        self.is_active = False  #bool
        self.in_edit = False #bool

    def draw_grid(self):
        self.rects = self.get_rects()
        pd = (3,3)
        corner = st(self.corner,pd)
        size = at(self.size,at(pd,pd))
        pygame.gfxdraw.box(self.win,(corner,size),colors['black'])

        for y in range(self.cells):
            for x in range(self.cells):
                self.draw_data((x,y))
        
    def draw_data(self,index):
        if self.data[index[1]][index[0]] == 0:
            color = colors['white']
            f_color = colors['black']
        elif self.data[index[1]][index[0]] == 1:
            color = colors['black']
            f_color = colors['white']
        elif self.data[index[1]][index[0]] == 2:
            color = colors['darkgreen']
            f_color = colors['white']
        elif self.data[index[1]][index[0]] == 3:
            color = colors['darkred']
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
        self.in_edit = False

    def ongrid(self,pos):
        inside_x = pos[0] > self.e_corner[0] and pos[0] < self.e_corner[0]+self.e_size[0]
        inside_y = pos[1] > self.e_corner[1] and pos[1] < self.e_corner[1]+self.e_size[1]
        if inside_x and inside_y:   return True
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

    def click(self,pos,button):
        rect = pygame.Rect(self.corner,self.size)
        if pygame.Rect.collidepoint(rect,pos):
            i = self.get_cell_index(pos)
            data = self.data[i[1]][i[0]]
            no_start = type(self.get_start())==bool
            no_end = type(self.get_end())==bool

            if self.in_edit:            #edit mode
                if button == 1:     #left click
                    set_table = {
                        0 : [data==1],
                        1 : [data==0, data==2, data==3]}
                    for x in set_table:
                        if any(set_table[x]):
                            self.data[i[1]][i[0]] = x

                elif button == 2:   #middle click
                    self.data[i[1]][i[0]] = 0

                elif button == 3:   #right click
                    set_table = {
                        3 : [(data == 0 and no_end),(data == 1 and no_end),(data == 2 and no_end)],
                        2 : [(data == 0 and no_start),(data == 1 and no_start),(data == 3 and no_start)],
                        0 : [(data == 3),(data == 2 and not no_end)]}
                    for x in set_table:
                        if any(set_table[x]):
                            self.data[i[1]][i[0]] = x

            else:                       #preset mode
                if button == 1:     #left click
                    set_table = {
                        0 : [(data == 2)],
                        2 : [(data == 0 or data == 3),(no_start)]}
                    for x in set_table:
                        if all(set_table[x]):
                            self.data[i[1]][i[0]] = x

                elif button == 2:   #middle click
                    if any([data==0, data==2, data==3]):
                        self.data[i[1]][i[0]] = 0

                elif button == 3:   #right click
                    set_table = {
                        0 : [(data == 3)],
                        3 : [(data == 0 or data == 2),(no_end)]}
                    for x in set_table:
                        if all(set_table[x]):
                            self.data[i[1]][i[0]] = x

            if data-self.data[i[1]][i[0]]:
                self.draw_data(i)
        #if anyone reads this, tell me if theres a better way to assert functions to mouse inputs with respect to what is being clicked on

    def get_rects(self):
        self.step_size = int(self.size[0]/self.cells)
        error_x = int((self.size[0]-self.cells*self.step_size)/2)  
        error_y = int((self.size[1]-self.cells*self.step_size)/2)
        self.e_corner = at(self.corner,(error_x,error_y))
        self.cell_size = (self.step_size,self.step_size)
        self.e_size = mt(self.cell_size,(self.cells,self.cells))
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

    def clear(self):
        self.data = np.zeros((self.cells,self.cells)).tolist()
        self.in_edit = True

    def get_cells(self):
        c = 0
        cells = []

        for x in self.data:
            if x == 1:
                cells.append((c%self.cells,int(c/self.size)))
            c += 1

        return cells

    def get_start(self):
        try:
            return np.array(self.data).flatten().tolist().index(2)
        except:
            return False

    def get_end(self):
        try:
            return np.array(self.data).flatten().tolist().index(3)
        except:
            return False

class Button:
    def __init__(self,win,corner,image,image_unpressed,name):
        self.win = win  #surface
        self.corner = corner    #tuple
        self.image = image  #pygame.image
        self.image_unpressed = image_unpressed  #pygame.image
        self.name = name    #string
        
        self.padding = 5
        self.size = self.image.get_size()
        self.end_corner = at(self.corner,self.size)
        self.is_pressed = False

    def draw(self):
        pygame.gfxdraw.box(self.win,(self.corner,self.size),colors['black'])
        if self.is_pressed:
            image = self.image
        else:
            image = self.image_unpressed
        self.win.blit(image,self.corner)

        textpos = at(self.corner,(10,20))
        pygame_font.Font(None,30).render_to(
            self.win,
            textpos,
            self.name,
            colors['white'],
            None,
            size=30)

    def click(self,pos,grids):
        rect = pygame.Rect(self.corner,self.size)
        if pygame.Rect.collidepoint(rect,pos):
            self.is_pressed = True
            self.draw()

            if self.name == 'quit':
                pygame.quit()
                pygame.font.quit()
                on = False

            if self.name == 'update':
                grids[0].rand()
                grids[0].draw_grid()

            if self.name == 'clear':
                grids[0].clear()
                grids[0].draw_grid()

            if self.name == 'edit':
                grids[0].in_edit = True

            if 'grid' in self.name:
                idx = int(self.name.replace('grid',''))
                grids[idx].cells = grids[0].cells
                grids[idx].data = grids[0].data
                grids[idx].draw_grid()
        
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

class Slider:
    def __init__(self,win,name,corner,range,step_size,font,state = None):
        self.win = win  #pygame.surface
        self.name = name    #string
        self.corner = corner  #tuple (x,y)
        self.num_range = range  #tuple (min,max)
        self.step_size = step_size  #int
        self.font = font

        self.size = (80,20)
        self.state = state

    def draw(self):
        def clear(color=colors['black']):
            corner = st(self.corner,(4,0))
            size = at(self.size,(8,20))
            pygame.gfxdraw.box(self.win,(corner,size),color)

        def draw_line(color=colors['white']):
            corner = at(self.corner,(0,self.size[1]/2-2))
            size = (self.size[0],4)
            pygame.gfxdraw.box(self.win,(corner,size),color)

        def draw_slider(color=colors['red']):
            if self.state == None:
                self.state = self.num_range[0]

            px_step = self.size[0] / (self.num_range[1]-self.num_range[0])
            step = self.state-self.num_range[0]
            sliderpos = self.corner[0] + step * px_step
            corner = (sliderpos-4,self.corner[1])
            size = (8,self.size[1])
            pygame.gfxdraw.box(self.win,(corner,size),color)

        def draw_text():
            text = f'{self.name} = {self.state}'
            textpos = at(self.corner,(0,self.size[1]+13))
            self.font.render_to(self.win,textpos,text,colors['white'],None,size=20)

        clear()
        draw_line()
        draw_slider()
        draw_text()
        
    def get_nums(self):
        start = self.num_range[0]
        stop = self.num_range[1]+self.step_size
        step = self.step_size
        dp = self.step_size**-1
        return (np.arange(start,stop,step)*dp).astype(int)/dp
        
    def work(self,pos,mouse_pressed,grids):
        rect = pygame.Rect(self.corner,at(self.size,(1,0)))
        if pygame.Rect.collidepoint(rect,pos) and mouse_pressed[1]:
            step_px = (self.num_range[1]-self.num_range[0]) / self.size[0]
            nums = self.get_nums()
            state = self.state
            self.state = min(nums, key=lambda x:abs(x-((pos[0]-self.corner[0]) * step_px) - self.num_range[0]))
            
            if state-self.state:
                self.draw()

                if self.name == 'cells':
                    grids[0].cells = int(self.state)
                    grids[0].rand()
                    grids[0].draw_grid()

                if self.name == 'prob':
                    grids[0].probability = self.state
                    grids[0].draw_grid()

def clear(win,grids,buttons,color=colors['black']):
    winsize = pygame.Surface.get_size(win)
    x = grids[-1].endcorner[0]+2
    y = grids[-1].corner[1]-2
    pygame.gfxdraw.box(win,(x,y,winsize[0],winsize[1]),color)

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
        return np.random.choice([0,1], size, p=[p, 1-p]).tolist()

def print_debug(font,win,grid,grids,arrow,next_cell=False):
    winsize = pygame.Surface.get_size(win)

    text = f'Name: {grid.id}'
    textpos = (grids[3].endcorner[0]+10, winsize[1]-90)
    font.render_to(win,textpos,text,colors['white'],None,size=25)
                        
    distance = int(arrow.get_lengh()/grid.step_size*100)/100
    text = f'Distance: {distance}'
    textpos = (grids[3].endcorner[0]+10, winsize[1]-70)
    font.render_to(win,textpos,text,colors['white'],None,size=25)
                        
    text = f'Angle: {arrow.get_angle()}°'
    textpos = (grids[3].endcorner[0]+10, winsize[1]-50)
    font.render_to(win,textpos,text,colors['white'],None,size=25)
                        
    if next_cell == False :
        text = f'no cell in grid'
    else:
        text = f'Closest Cell: ({next_cell[0]+1}|{grid.cells-next_cell[1]})'
    textpos = (grids[3].endcorner[0]+10, winsize[1]-30)
    font.render_to(win,textpos,text,colors['white'],None,size=25)

    if grid.in_edit:
        text = f'Edit Mode'
        textpos = (grids[3].endcorner[0]+10, winsize[1]-10)
        font.render_to(win,textpos,text,colors['red'],None,size=25)

def at(a,b):
    return (a[0]+b[0],a[1]+b[1])

def st(a,b):
    return (a[0]-b[0],a[1]-b[1])

def mt(a,b):
    return (a[0]*b[0],a[1]*b[1])

def dt(a,b):
    return (a[0]/b[0],a[1]/b[1])

def print_fps(win,font,grids,frame_time):
    text = f'{int(1 / (frame_time / 10 ** 9))} fps'
    textpos = (grids[3].endcorner[0] + 20, grids[3].corner[1] + 10)
    font.render_to(win, textpos, text, colors['white'], None, size=20)