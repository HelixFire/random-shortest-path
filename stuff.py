import random, time, pygame, pygame.gfxdraw, pygame.font, math, copy
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
        self.corner = corner #tuple
        self.size = size #tuple
        self.cells = cells #int
        self.id = id #string

        self.endcorner = at(corner,size) #tuple
        self.probability = probability #float
        self.data = rand_bool_grid((cells,cells),probability) #2d np list
        self.is_active = False #bool
        self.in_edit = False #bool
        self.arrows = []

    def handle(self,event,mouse_pos,mouse_delta):
        if self.ongrid(mouse_pos):
            if self.is_active and mouse_delta:
                return self.find_next(mouse_pos)
            elif not self.is_active and mouse_delta:
                self.is_active = True
        else:
            if self.is_active:
                self.is_active = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.click(mouse_pos, event.button)

    def alg(self):
        """
            grid: 2d list with int
            arrows: list with Arrow
            self.get_start() returns [(y_idx,x_idx),...]
            self.get_end() returns [(y_idx,x_idx),...]
        """
        self.arrows.clear()
        grid = copy.deepcopy(self.data)

        try:
            start = self.get_start()[-1]
            end_cell = self.get_end()[-1]
        except:
            return
        
        on = True
        while on:
            grid[start[1]][start[0]] = 0
            end = findnext(grid,start)
            if end:
                self.arrows.append(Arrow(self.win,self.get_cell_pos(start),self.get_cell_pos(end)))
                a = Arrow(self.win,self.get_cell_pos(start),self.get_cell_pos(end))
                a.draw()
                start = end
            else:
                on = False
            
        self.arrows.append(Arrow(self.win,self.get_cell_pos(start),self.get_cell_pos(end_cell)))

    def find_next(self,pos):
        def _findnext(grid,pos):
            def index_gen(size):
                for x in range(size[0]*size[1]):
                    idx = len_table.argmin()
                    yield idx
                    len_table[idx//size[1]][idx%size[1]] = 2*size[1]

            def table(size,zero):
                a = np.zeros(size)
                b = np.zeros(size)
                for y in range(-zero[1],0):
                    a[y + zero[1]] = abs(y)
                for x in range(-zero[0],0):
                    b[:, [x + zero[0]]] = abs(x)
                return np.sqrt(np.square(a)+np.square(b))

            if not any(any(row) for row in self.data):
                return False

            size = (len(grid),len(grid[0]))
            len_table = table(size,pos)
            size = (len(grid),len(grid[0]))

            for index in index_gen(size):
                x_idx = index%size[1]
                y_idx = index//size[1]

                if grid[y_idx][x_idx]:
                    return (x_idx,y_idx)

            return False

        idx = self.get_cell_index(pos)
        next_cell = _findnext(self.data,idx)
        pos_cell = self.get_cell_pos(next_cell)
        return [next_cell,pos_cell]

    def rand(self):
        self.data = rand_bool_grid((self.cells,self.cells),self.probability)
        self.in_edit = False

    def ongrid(self,pos):
        rect = pygame.Rect(self.corner,self.size)
        if pygame.Rect.collidepoint(rect,pos):
            return True
        else: return False

    def click(self,pos,button):
        if self.ongrid(pos):
            i = self.get_cell_index(pos)
            data = self.data[i[1]][i[0]]
            no_start = type(self.get_start())==bool
            no_end = type(self.get_end())==bool
            start = self.get_start()
            end = self.get_end()

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
                        3 : [data==0 and no_end,    data==1 and no_end,     data==2 and no_end],
                        2 : [data==0 and no_start,  data==0 and not no_end,   data==3 and no_start],
                        0 : [data==3 and not no_start, data==2 and not no_end]}
                    for x in set_table:
                        if any(set_table[x]):
                            self.data[i[1]][i[0]] = x

            else:                       #preset mode
                if button == 1:     #left click
                    set_table = {
                        0 : [data==2],
                        2 : [data==0 or data==3]}
                    for x in set_table:
                        if all(set_table[x]):
                            self.data[i[1]][i[0]] = x

                elif button == 2:   #middle click
                    if any([data==0, data==2, data==3]):
                        self.data[i[1]][i[0]] = 0

                elif button == 3:   #right click
                    set_table = {
                        0 : [data==3],
                        3 : [data==0 or data==2]}
                    for x in set_table:
                        if all(set_table[x]):
                            self.data[i[1]][i[0]] = x

            if type(self.get_start()) != bool:  #this is to reset old start/end cells for preset mode
                if len(self.get_start()) > 1:       #if there is no start cell, output from get_start will be False, causing a TypeError
                    self.data[start[0][1]][start[0][0]] = 0
            if type(self.get_end()) != bool:
                if len(self.get_end()) > 1:
                    self.data[end[0][1]][end[0][0]] = 0
            
        self.alg()
        self.draw_grid()
        #if anyone reads this, tell me if theres a better way to assert functions to mouse inputs with respect to what is being clicked on

    def clear(self):
        self.data = np.zeros((self.cells,self.cells)).astype(int).tolist()
        self.in_edit = True

    def draw_grid(self,index=False):
        if index:
            self.draw_data(index)
        else:
            self.rects = self.get_rects()
            pd = (3,3)
            corner = st(self.corner,pd)
            size = at(self.size,at(pd,pd))
            pygame.gfxdraw.box(self.win,(corner,size),colors['black'])

            for y in range(self.cells):
                for x in range(self.cells):
                    self.draw_data((x,y))
            
            for arrow in self.arrows:
                arrow.draw()
        
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

    def get_rects(self):
        self.step_size = self.size[0]//self.cells
        error_x = (self.size[0]-self.cells*self.step_size)//2
        error_y = (self.size[1]-self.cells*self.step_size)//2
        self.e_corner = at(self.corner,(error_x,error_y))
        self.cell_size = (self.step_size,self.step_size)
        self.e_size = mt(self.cell_size,(self.cells,self.cells))
        celloffset = dt(self.cell_size,(2,2))

        def midpoints():
            for x in range(self.cells**2):
                xoff = x%self.cells * self.step_size
                yoff = x//self.cells * self.step_size
                yield at(at(self.e_corner,(xoff,yoff)),celloffset)

        rects = []
        for point in midpoints():
            corner = st(point,celloffset)
            rects.append(pygame.Rect(corner,self.cell_size))

        return rects

    def get_cells(self):
        c,cells = 0,[]
        for x in np.array(self.data).flatten().tolist():
            if x == 1:
                cells.append((c%self.cells,c//self.cells))
            c += 1
        return cells

    def get_cell_pos(self,index):
        if index == False:
            posx,posy = at(self.corner,dt(self.size,(2,2)))
        else:
            posx = self.e_corner[0] + self.step_size//2 + index[0] * self.step_size
            posy = self.e_corner[1] + self.step_size//2 + index[1] * self.step_size
        return (posx,posy)

    def get_cell_index(self,pos):
        ix = (pos[0]-self.e_corner[0])//self.step_size
        iy = (pos[1]-self.e_corner[1])//self.step_size
        return (ix,iy)

    def get_start(self):
        c,out = 0,[]
        for x in np.array(self.data).flatten().tolist():
            if x == 2:
                out.append((c%self.cells,c//self.cells))
            c+=1
        if len(out) == 0:
            return False
        else: return out

    def get_end(self):
        c,out = 0,[]
        for x in np.array(self.data).flatten().tolist():
            if x == 3:
                out.append((c%self.cells,c//self.cells))
            c+=1
        if len(out) == 0:
            return False
        else: return out

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

    def handle(self,event,mouse_pos,grids):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.click(mouse_pos, grids)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_pressed = False
            self.draw()

    def draw(self):
        pygame.gfxdraw.box(self.win,(self.corner,self.size),colors['black'])
        if self.is_pressed:
            image = self.image
        else:
            image = self.image_unpressed
        self.win.blit(image,self.corner)

        textpos = at(self.corner,(10,25))
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

            if self.name == 'run':
                grids[0].alg()
                
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
        offset_x = 0
        start = 0
        pygame.draw.line(self.win, self.color, self.spos, self.epos, 3)

        x = math.cos(self.get_angle()[1]+0.35)*25
        y = math.sin(self.get_angle()[0]+0.35)*25
        start = (y,x)
        pygame.draw.line(self.win, self.color, at(start,self.epos), self.epos, 3)

        x = math.cos(self.get_angle()[1]-0.35)*25
        y = math.sin(self.get_angle()[0]-0.35)*25
        start = (y,x)
        pygame.draw.line(self.win, self.color, at(start,self.epos), self.epos, 3)


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
        dx = self.epos[0]-self.spos[0]
        dy = self.epos[1]-self.spos[1]

        if not dx:
            dx -= 0.000000000001

        rad = math.atan(dy/dx)-math.pi/2
        angle = rad * 180/math.pi
        
        if dx > 0 and dy > 0:
            angle += 180
        elif dx > 0 and dy < 0:
            angle += 180
        elif dx < 0 and dy > 0:
            angle += 360
        
        return (int(angle),rad)
        
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
        self.pressed = False

    def handle(self,event,mouse_pos,grids):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hitbox(mouse_pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed = False
        
        if self.pressed:
            step_px = (self.num_range[1]-self.num_range[0]) / self.size[0]
            state = self.state
            self.state = min(self.get_nums(), key=lambda x:abs(x-((mouse_pos[0]-self.corner[0]) * step_px) - self.num_range[0]))

            if state-self.state:
                self.draw()

                if self.name == 'cells':
                    grids[0].cells = int(self.state)
                    grids[0].rand()

                if self.name == 'prob':
                    grids[0].probability = self.state
                
                grids[0].arrows.clear()
                grids[0].draw_grid()

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

    def hitbox(self,pos):
        rect = pygame.Rect(self.corner,at(self.size,(1,0)))
        if pygame.Rect.collidepoint(rect,pos):
            return True
        else:
            return False

    def get_nums(self):
        start = self.num_range[0]
        stop = self.num_range[1]+self.step_size
        step = self.step_size
        dp = self.step_size**-1
        return (np.arange(start,stop,step)*dp).astype(int)/dp

def rand_bool_grid(size, p = 0.95):
        return np.random.choice([0,1], size, p=[p, 1-p]).tolist()

def print_debug(font,win,grids,grid=False,next_cell=False):
    def main():
        pygame.gfxdraw.box(win,(corner,winsize),colors['black'])

        start_cell(grid)
        end_cell(grid)
        amt_cells(grid)
        name(grid)
        mode(grid)

    def start_cell(grid):
        if type(grid.get_start())==list:
            text = f'Start Cell: ({grid.get_start()[0][0]+1}|{grid.get_start()[0][1]+1})'
            textpos = (grids[3].endcorner[0]+10, winsize[1]-150)
            font.render_to(win,textpos,text,colors['green'],None,size=25)
    
    def end_cell(grid):
        if type(grid.get_end())==list:
            text = f'End Cell: ({grid.get_end()[0][0]+1}|{grid.get_end()[0][1]+1})'
            textpos = (grids[3].endcorner[0]+10, winsize[1]-130)
            font.render_to(win,textpos,text,colors['red'],None,size=25)

    def amt_cells(grid):
        if len(grid.get_cells()):
            text = f'Cell amount: {len(grid.get_cells())}'
        else:
            text = f'No cells on'
        textpos = (grids[3].endcorner[0]+10, winsize[1]-110)
        font.render_to(win,textpos,text,colors['white'],None,size=25)

    def name(grid):
        text = f'Name: {grid.id}'
        textpos = (grids[3].endcorner[0]+10, winsize[1]-90)
        font.render_to(win,textpos,text,colors['white'],None,size=25)

    def dist(arrow):
        distance = int(arrow.get_lengh()/grid.step_size*100)/100
        text = f'Distance: {distance}'
        textpos = (grids[3].endcorner[0]+10, winsize[1]-70)
        font.render_to(win,textpos,text,colors['white'],None,size=25)

    def angle(arrow):
        text = f'Angle: {arrow.get_angle()}'
        textpos = (grids[3].endcorner[0]+10, winsize[1]-50)
        font.render_to(win,textpos,text,colors['white'],None,size=25)

    def closest(next_cell):
        if next_cell:
            text = f'Closest Cell: ({next_cell[0]+1}|{next_cell[1]+1})'
        else:
            text = f'No cell on'
        textpos = (grids[3].endcorner[0]+10, winsize[1]-30)
        font.render_to(win,textpos,text,colors['white'],None,size=25)

    def mode(grid):
        if grid.in_edit:
            text = f'Edit Mode'
            textpos = (grids[3].endcorner[0]+10, winsize[1]-10)
            font.render_to(win,textpos,text,colors['lightblue'],None,size=25)

    winsize = pygame.Surface.get_size(win)
    corner = (grids[-1].endcorner[0],grids[-1].corner[1])

    if grid==False:
        grid = grids[0]
        main()
    else:
        main()
        #dist(arrow)
        #angle(arrow)
        closest(next_cell)

def print_fps(win,font,grids,frame_time):
    textpos = (grids[3].endcorner[0] + 20, grids[3].corner[1]-5)
    size = (80,20)
    corner = st(textpos,(5,15))
    pygame.gfxdraw.box(win,(corner,size),colors['black'])
    text = f'{int(1/(frame_time / 10 ** 9))} fps'
    font.render_to(win, textpos, text, colors['white'], None, size=20)

def at(a,b):
    return (a[0]+b[0],a[1]+b[1])

def st(a,b):
    return (a[0]-b[0],a[1]-b[1])

def mt(a,b):
    return (a[0]*b[0],a[1]*b[1])

def dt(a,b):
    return (a[0]/b[0],a[1]/b[1])

def tm(operator):
    if operator == '+':
        return lambda a,b: (a[0]+b[0],a[1]+b[1])
    elif operator == '-':
        return lambda a,b: (a[0]-b[0],a[1]-b[1])
    elif operator == '*':
        return lambda a,b: (a[0]*b[0],a[1]*b[1])
    elif operator == '/':
        return lambda a,b: (a[0]/b[0],a[1]/b[1])

def findnext(grid,pos):
    def index_gen(size):
        for x in range(size[0]*size[1]):
            idx = len_table.argmin()
            yield idx
            len_table[idx//size[1]][idx%size[1]] = 2*size[1]

    def table(size,zero):
        a = np.zeros(size)
        b = np.zeros(size)
        for y in range(-zero[1],0):
            a[y + zero[1]] = abs(y)
        for x in range(-zero[0],0):
            b[:, [x + zero[0]]] = abs(x)
        return np.sqrt(np.square(a)+np.square(b))
            
    size = (len(grid),len(grid[0]))
    len_table = table(size,pos)
    size = (len(grid),len(grid[0]))

    for index in index_gen(size):
        x_idx = index%size[1]
        y_idx = index//size[1]

        if grid[y_idx][x_idx] == 1:
            return  (x_idx,y_idx)

    return False
