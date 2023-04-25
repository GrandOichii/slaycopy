# import pygame as pg

# pg.init()

# screen = pg.s
import curses
import random


# HEIGHT = 2
# WIDTH = 2
HEIGHT = 25
WIDTH = 18
WINDOW = None

CORRECTIONS = [
    {
        'template': [
            [False, False],
            [True, False],
            [False, False],
        ],
        'correction': [
            [True, True],
            [True, True],
            [True, True],
        ]
    },
    {
        'template': [
            [False, False],
            [True, True],
            [True, False],
        ],
        'correction': [
            [True, True],
            [True, True],
            [True, True],
        ]
    },
    {
        'template': [
            [False, False],
            [True, True],
            [False, True],
        ],
        'correction': [
            [True, True],
            [True, True],
            [True, True],
        ]
    },
    {
        'template': [
            [False],
            [True],
            [False],
        ],
        'correction': [
            [True],
            [True],
            [True],
        ]
    },
    {
        'template': [
            [False, True],
            [True, False]
        ],
        'correction': [
            [True, True],
            [True, True]
        ]
    }
]


def matches(map, template, posy, posx):
    for i in range(len(template)):
        line = template[i]
        for j in range(len(line)):
            y = i + posy
            if y >= len(map):
                return False
            x = j + posx
            if x >= len(map[0]):
                return False
            if line[j] != map[y][x]:
                return False
    return True


def reverse_matches(map, template, posy, posx):
    newt = []
    for line in template:
        newt += [line[::-1]]
    return matches(map, newt, posy, posx)


def replace(map, correction, posy, posx):
    for i in range(len(correction)):
        line = correction[i]
        for j in range(len(line)):
            y = i + posy
            x = j + posx
            map[y][x] = line[j]


def reverse_replace(map, correction, posy, posx):
    newt = []
    for line in correction:
        newt += [line[::-1]]
    replace(map, newt, posy, posx)


def generate_map() -> list[list]:
    result = []

    for i in range(HEIGHT):
        a = []
        for j in range(WIDTH):
            a += [False]
        result += [a]

    # generate start point
    offset_y = HEIGHT // 3
    offset_x = WIDTH // 3
    start_point_loc = [
        random.randint(offset_y, HEIGHT-offset_y),
        random.randint(offset_x, WIDTH-offset_x),
    ]

    result[start_point_loc[0]][start_point_loc[1]] = True
    step_weight = 0.01

    offshoots_count = 3
    offshoots = []
    dir_arr = [
        [
            [-2, 0],
            [-1, +1],
            [+1, +1],
            [+2, 0],
            [+1, 0],
            [-1, 0]
        ],
        [
            [-2, 0],
            [-1, 0],
            [+1, 0],
            [+2, 0],
            [+1, -1],
            [-1, -1],
        ]
    ]
    for i in range(offshoots_count):
        # [yloc, xloc, weight]
        o = [start_point_loc[0], start_point_loc[1], 0]
        offshoots += [o]
    count_thresh = 170
    count = 0
    while (len(offshoots)):
        for offshoot in offshoots:
            offshoot[2] += 1
            dir = random.choice(dir_arr[offshoot[0] % 2])
            newy = offshoot[0] + dir[0]
            newx = offshoot[1] + dir[1]
            
            if not (newy < 0 or newx < 0 or newy >= HEIGHT or newx >= WIDTH):
                offshoot[0] = newy
                offshoot[1] = newx
                if not result[offshoot[0]][offshoot[1]]:
                    count += 1
                result[offshoot[0]][offshoot[1]] = True
            if count > count_thresh and random.randint(0, 100) < offshoot[2] * step_weight:
                offshoots.remove(offshoot)
        draw_map(WINDOW, result, 5, [0,0])
        WINDOW.refresh()
        # WINDOW.getch()
        curses.napms(20)
    curses.flash()

    # correct missing pieces
    # for correction in CORRECTIONS:
    #     corr = correction['correction']
    #     template = correction['template']
    #     # theight = len(template)
    #     # twidth = len(template[0])
    #     for i in range(0, len(result)):
    #         line = result[i]
    #         for j in range(0, len(line)):
    #             if matches(result, template, i, j):
    #                 draw_map(WINDOW, result, 5, [0,0])
    #                 WINDOW.getch()
    #                 replace(result, corr, i, j)
    #                 draw_map(WINDOW, result, 5, [0,0])
    #                 WINDOW.getch()
    #             if reverse_matches(result, template, i, j):
    #                 draw_map(WINDOW, result, 5, [0,0])
    #                 WINDOW.getch()
    #                 reverse_replace(result, corr, i, j)
    #                 draw_map(WINDOW, result, 5, [0,0])
    #                 WINDOW.getch()

    # cut the borders
    # border_width = 2
    # for bi in range(border_width):
    #     for i in range(bi, HEIGHT - bi):
    #         result[i][bi] = False
    #         result[i][WIDTH - 1 - bi] = False
    #     for j in range(bi, WIDTH - bi):
    #         result[bi][j] = False
    #         result[HEIGHT - 1 - bi][j] = False
    # for i in range(len(result)):
    #     line = result[i]
    #     for j in range(len(line)):
    #         if ( or ) and ( or ):
    #             result[i][j] = False

    return result


SPRITE = [
    '  --  ',
    '/    \\',
    '      ',
    '\\    /',
    '  --  ',
]


DEFERED_DRAW = []


def defer_draw(func, args):
    global DEFERED_DRAW
    DEFERED_DRAW += [{
        'func': func,
        'args': args
    }]


def draw_selected(args):
    win = args['win']
    y = args['y']
    x = args['x']
    win.attron(curses.color_pair(1))
    basic_draw_sprite(win, y, x)
    win.attroff(curses.color_pair(1))


def basic_draw_sprite(win, y, x):
    for ii in range(len(SPRITE)):
        win.addstr(y + ii, x, SPRITE[ii])


def draw_sprite(win, y, x, sprite_info):
    if not sprite_info['tile']:
        return
    basic_draw_sprite(win, y, x)
    if sprite_info['tile']:
        win.addstr(y + 1, x + 2, f'aa')
        win.addstr(y + 1, x + 2, str(sprite_info['pos'][0]))
        win.addstr(y + 2, x + 2, 'aa')
        win.addstr(y + 2, x + 2, str(sprite_info['pos'][1]))
        win.addstr(y + 3, x + 2, 'aa')

    if not sprite_info['selected']:
        return
    
    defer_draw(draw_selected, {'win': win, 'y': y, 'x': x})


def draw_map(win, map, xbase, pos):
    y = 0
    x = 0
    xdiff = xbase
    for i in range(HEIGHT):
        x = xdiff
        for j in range(WIDTH):
            draw_sprite(win, y, x, {'tile': map[i][j], 'selected': pos[0] == i and pos[1] == j, 'pos': [i, j]})
            x += len(SPRITE[0]) + 4
        xdiff = xbase - xdiff
        y += len(SPRITE) - 3

RESULT = {}
def main(stdscr: 'curses._CursesWindow'):
    global WINDOW
    WINDOW = stdscr
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_RED, 0)
    map = generate_map()
    RESULT['map'] = map

    pos = [0, 0]

    key_map = {
        curses.KEY_UP: [-1, 0],
        curses.KEY_DOWN: [1, 0],
        curses.KEY_LEFT: [0, -1],
        curses.KEY_RIGHT: [0, 1],
    }

    while True:
        # draw
        xbase = 5
        draw_map(stdscr, map, xbase, pos)
            # y += len(SPRITE)
        # draw defered
        global DEFERED_DRAW
        for defered in DEFERED_DRAW:
            defered['func'](defered['args'])
        DEFERED_DRAW = []
        # refresh
        stdscr.refresh()
        # input
        command = stdscr.getch()
        if command == ord('q'):
            break
        if command in key_map:
            diff = key_map[command]
            pos[0] += diff[0]
            if pos[0] < 0:
                pos[0] = 0
            if pos[0] >= HEIGHT:
                pos[0] = HEIGHT - 1
            pos[1] += diff[1]
            if pos[1] < 0:
                pos[1] = 0
            if pos[1] >= WIDTH:
                pos[1] = WIDTH - 1

        
        # clear
        stdscr.clear()

curses.wrapper(main)
rmap = RESULT['map']
for line in rmap:
    for t in line:
        print((1 if t else 0), end=' ')
    print()