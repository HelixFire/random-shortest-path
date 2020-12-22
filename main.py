import pygame, pygame.gfxdraw, pygame.image, pygame.font, time, math, stuff
from pygame import ftfont as pygame_font
import numpy as np

"""
TODO
-draw nicer arrow
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
    mouse_pressed = [False, False, False]

    button_pressed = pygame.image.load(r'pics\buttonpressed.png')
    button_unpressed = pygame.image.load(r'pics\buttonunpressed.png')

    grids = [
        stuff.Grid(win, (5, 5), (600, 600), 20, 'main', 0.9),  # main
        stuff.Grid(win, (5, 610), (200, 200), 20, 'grid1'),  # 1st save
        stuff.Grid(win, (210, 610), (200, 200), 20, 'grid2'),  # 2nd save
        stuff.Grid(win, (415, 610), (200, 200), 20, 'grid3')  # 3rd save
    ]

    buttons = [
        stuff.Button(win, (width - 80, 0), button_pressed, button_unpressed, 'update'),
        stuff.Button(win, (width - 80, 40), button_pressed, button_unpressed, 'clear'),
        stuff.Button(win, (width - 80, 80), button_pressed, button_unpressed, 'grid1'),
        stuff.Button(win, (width - 80, 120), button_pressed, button_unpressed, 'grid2'),
        stuff.Button(win, (width - 80, 160), button_pressed, button_unpressed, 'grid3'),
    ]

    sliders = [
        stuff.Slider(win, 'cells', (width - 180, 10), (1, 30), 1, font),
        stuff.Slider(win, 'prob', (width - 180, 50), (0, 1), 0.01, font)
    ]

    arrow_mouse = stuff.Arrow(win, (0, 0), (0, 0))

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
    next_cell = 0

    on = True
    while on:
        start_timer = time.perf_counter_ns()
        pygame.display.update()
        stuff.clear(win, grids, buttons)
        mouse_pos_old = mouse_pos
        mouse_pos = pygame.mouse.get_pos()

        if not mouse_pos == mouse_pos_old:
            mouse_delta = stuff.st(mouse_pos, mouse_pos_old)
        else:
            mouse_delta = 0

        text = f'{int(1 / (frame_time / 10 ** 9))} fps'
        textpos = (grids[3].endcorner[0] + 20, grids[3].corner[1] + 10)
        font.render_to(win, textpos, text, stuff.colors['white'], None, size=20)

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

                    stuff.print_debug(font, win, grid, grids, arrow_mouse, next_cell)
                else:
                    grid.is_active = True
            else:
                if grid.is_active:
                    grid.is_active = False
                    grid.draw_grid()

        for slider in sliders:
            slider.work(mouse_pos,mouse_pressed,grids)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pressed[event.button-1] = True
                for button in buttons:
                    button.click(mouse_pos, grids)

                for grid in grids:
                    grid.click(mouse_pos, event.button)

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pressed[event.button-1] = False
                for button in buttons:
                    button.is_pressed = False
                    button.draw()

            if event.type == pygame.QUIT:
                on = False
                break

        stop_timer = time.perf_counter_ns()
        frame_time1 = stop_timer - start_timer

        if not frame_count % (len(frame_times) + 1) == 0:
            frame_times[(frame_count % len(frame_times)) - 1] = frame_time1
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

    time_setup_ms = (stop_setup_ns - start_setup_ns) / 10 ** 6
    time_main_s = stop_main_s - start_main_s

    print(f'\nFinished without crash!\n\nDegub Times:')
    print(f'    setup: {int(time_setup_ms)}ms')
    print(f'    main: {int(time_main_s)}s\n')
