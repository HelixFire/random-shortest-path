import pygame, pygame.gfxdraw, pygame.image, pygame.font, time, math, stuff, sys
from pygame import ftfont as pygame_font
import numpy as np

"""
DONE
-added more debug text
-enhanced mouse input in preset mode (took way too long but id say its finished)
-i finally implemented a "search way" function, wich in future should display the shortest rout, but for now it just looks nice

TODO
-fix grid to proper size (smooth scale)
-draw nicer arrow
-add check box
-add text input
-update find_next
-create shortes path find algo
"""

def setup():
    global win, winsize, buttons, grids, arrow_mouse, font, sliders, mouse_pressed

    width, height = 800, 815
    winsize = (width, height)

    pygame.init()
    pygame.display.init()
    pygame_font.init()
    font = pygame_font.Font(None, 20)
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Cells")
    mouse_pressed = [False]*100

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
        stuff.Slider(win, 'prob', (width - 180, 50), (0, 1), 0.01, font, grids[0].probability)
    ]

    for grid in grids:
        grid.draw_grid()

    for button in buttons:
        button.draw()

    for slider in sliders:
        slider.draw()

    pygame.display.update()

def main():
    mouse_pos, mouse_pos_old = (0, 0), (0, 0)
    frame_time, frame_count, frame_times = 1, 1, [None] * 50
    mouse_delta = 0
    next_cell = (0,0)

    on = True
    while on:
        start_timer = time.perf_counter_ns()
        pygame.display.update()
        mouse_pos_old = mouse_pos
        mouse_pos = pygame.mouse.get_pos()

        if not mouse_pos == mouse_pos_old:
            mouse_delta = stuff.st(mouse_pos, mouse_pos_old)
        else:
            mouse_delta = 0

        for grid in grids:
            if grid.ongrid(mouse_pos):
                if grid.is_active:
                    if mouse_delta:
                        grid.draw_grid()
                        next_cell = grid.find_next(mouse_pos)
                        stuff.print_debug(font,win,grids,grid,next_cell[0])
                else:
                    grid.is_active = True
            else:
                if grid.is_active:
                    grid.is_active = False
                    grid.draw_grid()
                    stuff.print_debug(font,win,grids)

        if mouse_delta:
            for slider in sliders:
                slider.work(mouse_pos,mouse_pressed,grids)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button >= len(mouse_pressed):
                    pygame.quit()
                    pygame.font.quit()
                else:
                    mouse_pressed[event.button] = True

                for button in buttons:
                    button.click(mouse_pos, grids)
                for grid in grids:
                    grid.click(mouse_pos, event.button)
                    grid.alg()
                    grid.draw_grid()
                stuff.print_debug(font,win,grids)

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pressed[event.button] = False
                for button in buttons:
                    button.is_pressed = False
                    button.draw()

            if event.type == pygame.QUIT:
                on = False
                break

        stop_timer = time.perf_counter_ns()
        frame_time1 = stop_timer - start_timer

        if frame_count % (len(frame_times)+1) == 0:
            frame_time = sum(frame_times) / len(frame_times)
            stuff.print_fps(win,font,grids,frame_time)
            
        else:
            frame_times[(frame_count % len(frame_times)) - 1] = frame_time1

        frame_count += 1

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
