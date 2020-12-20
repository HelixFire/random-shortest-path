import pygame, pygame.gfxdraw, pygame.image, pygame.font, time, math, stuff
from pygame import ftfont as pygame_font
import numpy as np

"""
TODO
-implement png buttons
-update find_next
-create shortes path find algo
"""

def setup():
    global win,winsize,buttons,grids,arrow_mouse,font

    width,height = 800,815
    winsize = (width,height)

    pygame.init()
    pygame.display.init()
    pygame_font.init()
    win = pygame.display.set_mode((width,height))
    pygame.display.set_caption("Cells")

    cells = 20

    grids = [
        stuff.Grid(win,(5,5),     (600,600),  cells,  'main', 0.995),   #main
        stuff.Grid(win,(5,610),   (200,200),  cells,  'grid1'),       #1st save
        stuff.Grid(win,(210,610), (200,200),  cells,  'grid2'),       #2nd save
        stuff.Grid(win,(415,610), (200,200),  cells,  'grid3')        #3rd save
    ]

    buttons = [
        stuff.Button(win,(width-105,5),     (100,75),'green','update'),
        stuff.Button(win,(width-105,85),    (100,75),'blue','start'),
        stuff.Button(win,(width-105,185),   (100,75),'blue','grid1'),
        stuff.Button(win,(width-105,265),   (100,75),'blue','grid2'),
        stuff.Button(win,(width-105,345),   (100,75),'blue','grid3'),
        ]

    arrow_mouse = stuff.Arrow(win,grids[1].corner,(0,0))
    font = pygame_font.Font(None,20)

    for grid in grids:
        grid.draw_grid()

    for button in buttons:
        button.draw()

    pygame.display.update()

def main():
    global win,buttons,grids,arrow_mouse,font

    mouse_pos,mouse_pos_old = (0,0),(0,0)
    frame_time,frame_times,frame_count = 1,[None]*50,1
    mouse_delta = 0
    next_cell = 0

    on = True
    while on:
        start_timer = time.perf_counter_ns()
        pygame.display.update()
        stuff.clear_debug(grids,win)

        mouse_pos_old = mouse_pos
        mouse_pos = pygame.mouse.get_pos()

        if not mouse_pos == mouse_pos_old:
            mouse_delta = stuff.st(mouse_pos,mouse_pos_old)
        else:
            mouse_delta = 0

        text = f'{int(1/(frame_time/10**9))} fps'
        textpos = (grids[3].endcorner[0]+20, grids[3].corner[1]+10)
        font.render_to(win,textpos,text,stuff.colors['white'],None,size=20)

        for button in buttons:
    	    button.draw()

        for grid in grids:
            if grid.ongrid(mouse_pos):
                if grid.is_active:
                    if mouse_delta:
                        grid.draw_grid()
                        new_cell = grid.find_next(mouse_pos)
                        next_cell = new_cell[0]
                            
                        arrow_mouse.spos = mouse_pos
                        arrow_mouse.epos = new_cell[1]
                        arrow_mouse.draw()

                    text = f'Name: {grid.id}'
                    textpos = (grids[3].endcorner[0]+10, winsize[1]-90)
                    font.render_to(win,textpos,text,stuff.colors['white'],None,size=20)
                        
                    distance = int(arrow_mouse.get_lengh()/grid.step_size*100)/100
                    text = f'Distance: {distance}'
                    textpos = (grids[3].endcorner[0]+10, winsize[1]-70)
                    font.render_to(win,textpos,text,stuff.colors['white'],None,size=20)
                        
                    text = f'Angle: {arrow_mouse.get_angle()}°'
                    textpos = (grids[3].endcorner[0]+10, winsize[1]-50)
                    font.render_to(win,textpos,text,stuff.colors['white'],None,size=20)
                        
                    if next_cell == False :
                        text = f'no cell in grid'
                    else:
                        text = f'Closest Cell: ({next_cell[0]+1}|{grid.cells-next_cell[1]})'
                    textpos = (grids[3].endcorner[0]+10, winsize[1]-30)
                    font.render_to(win,textpos,text,stuff.colors['white'],None,size=20)

                else:
                    grid.is_active = True
            else:
                if grid.is_active:
                    grid.is_active = False
                    grid.draw_grid()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.click(mouse_pos):
                        button.is_active = True

                        if button.name == 'quit':
                            pygame.quit()
                            pygame.font.quit()
                            on = False
                            break

                        if button.name == 'update':
                            grids[0].rand()
                            grids[0].draw_grid()

                        if 'grid' in button.name:
                            idx = int(button.name.replace('grid',''))
                            grids[idx].data = grids[0].data
                            grids[idx].draw_grid()

                for grid in grids:
                    if grid.click(mouse_pos):
                        idx = grid.get_cell_index(mouse_pos)
                        if grid.data[idx[1]][idx[0]] == 0:
                            grid.data[idx[1]][idx[0]] = 2
                        elif grid.data[idx[1]][idx[0]] == 2:
                            grid.data[idx[1]][idx[0]] = 0
                    grid.draw_grid()

            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    button.is_active = False

            if event.type == pygame.QUIT:
                on = False
                break
        
        stop_timer = time.perf_counter_ns()
        frame_time1 = stop_timer - start_timer

        if not frame_count%(len(frame_times)+1) == 0:
            frame_times[(frame_count%len(frame_times))-1] = frame_time1
        else:
            frame_time = sum(frame_times) / len(frame_times)
        
        frame_count += 1

if __name__ == "__main__":
    start_setup_ns = time.perf_counter_ns()
    setup()
    stop_setup_ns = time.perf_counter_ns()

    start_main_s = time.perf_counter()
    main()
    stop_main_s = time.perf_counter()

    time_setup_ms = (stop_setup_ns-start_setup_ns)/10**6
    time_main_s = stop_main_s-start_main_s

    print(f'\nFinished without crash!\n\nDegub Times:')
    print(f'    setup: {int(time_setup_ms)}ms')
    print(f'    main: {int(time_main_s)}s\n')
