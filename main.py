import pygame, pygame.gfxdraw, pygame.image, time, math, stuff, sys
from pygame import ftfont as pygame_font
import numpy as np

"""
DONE
-fixed path not dissaprearing when updating grid
-cleaned up "game cycle", moving stuff to stuff
-general cleanup (little bit)

TODO
-found out about operator overloading, gotta use that
-found out about good variable naming (_val: inner workings)
-edit button should toggle
-update grid when changing probability-slider
-fix grid to proper size (smooth scale)
-draw nicer arrow
-add check box
-add text input
-update find_next
-create shortes path find algo
"""
win, winsize, buttons, grids, arrow_mouse, font, sliders = 0,0,0,0,0,0,0 #this is the only way to fix this dang "undeclared var squiggle line" from the globally set variables, ive tried reinstalling language server

def setup():
    global win, winsize, buttons, grids, arrow_mouse, font, sliders

    width, height = 800, 815
    winsize = (width, height)

    pygame.init()
    pygame.display.init()
    pygame_font.init()
    font = pygame_font.Font(None, 20)
    win = pygame.display.set_mode(winsize)
    pygame.display.set_caption("Cells")

    button_pressed = pygame.image.load(r'pics\buttonpressed.png')
    button_unpressed = pygame.image.load(r'pics\buttonunpressed.png')

    grids = [
        stuff.Grid(win, (5, 5),     (600, 600), 20, 'main', 0.9),
        stuff.Grid(win, (5, 610),   (200, 200), 20, 'grid1'), 
        stuff.Grid(win, (210, 610), (200, 200), 20, 'grid2'), 
        stuff.Grid(win, (415, 610), (200, 200), 20, 'grid3') 
    ]

    buttons = [
        stuff.Button(win, (width - 80, 0),  button_pressed, button_unpressed, 'update'),
        stuff.Button(win, (width - 80, 40), button_pressed, button_unpressed, 'clear'),
        stuff.Button(win, (width - 80, 80), button_pressed, button_unpressed, 'edit'),
        stuff.Button(win, (width - 80, 120), button_pressed, button_unpressed, 'run'),
        stuff.Button(win, (width - 80, 180), button_pressed, button_unpressed, 'grid1'),
        stuff.Button(win, (width - 80, 220), button_pressed, button_unpressed, 'grid2'),
        stuff.Button(win, (width - 80, 260), button_pressed, button_unpressed, 'grid3')
    ]

    sliders = [
        stuff.Slider(win, 'cells', (width - 180, 10), (3, 30), 1, font, grids[0].cells),
        stuff.Slider(win, 'prob', (width - 180, 50), (0.5, 1), 0.01, font, grids[0].probability)
    ]

    for grid in grids:
        grid.draw_grid()

    for button in buttons:
        button.draw()

    for slider in sliders:
        slider.draw()

    pygame.display.update()

def main():
    mouse_pos, mouse_pos_old, mouse_delta = (0, 0), (0,0), 0
    frame_time, frame_count, frame_times, start_timer = 1, 1, [None] * 50, 0
    st =  stuff.tm('-')

    on = True
    while on:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                on = False
                break

            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos == mouse_pos_old:
                mouse_delta = 0
            else:
                mouse_delta = st(mouse_pos, mouse_pos_old)

            for button in buttons:
                button.handle(event,mouse_pos,grids)

            for slider in sliders:
                slider.handle(event,mouse_pos,grids)

            for grid in grids:
                out = grid.handle(event,mouse_pos,mouse_delta)
                if out:
                    stuff.print_debug(font,win,grids,grid,out[0])
        
        mouse_pos_old = mouse_pos

        stop_timer = time.perf_counter_ns()
        frame_time1 = stop_timer - start_timer
        start_timer = time.perf_counter_ns()

        if frame_count % (len(frame_times)+1) == 0:
            frame_time = sum(frame_times) / len(frame_times)
            stuff.print_fps(win,font,grids,frame_time)
        else:
            frame_times[(frame_count % len(frame_times)) - 1] = frame_time1

        frame_count += 1
        pygame.display.update()

if __name__ == "__main__":
    try:
        start_setup_ns = time.perf_counter_ns()
        setup()
        stop_setup_ns = time.perf_counter_ns()

        start_main_s = time.perf_counter()
        main()
        stop_main_s = time.perf_counter()

        time_setup_ms = (stop_setup_ns - start_setup_ns) / 10 ** 6
        time_main_s = stop_main_s - start_main_s
    except:
        print("\nUnexpected error:", sys.exc_info()[1])
        raise
    else:
        print(f'\nFinished without crash!\n\nDegub Times:')
        print(f'    setup: {int(time_setup_ms)}ms')
        print(f'    main: {int(time_main_s)}s\n')
