# import pygame as pg
import math
# pg.init()

# screen = pg.s
import curses
import random


# HEIGHT = 2
# WIDTH = 2
HEIGHT = 25
WIDTH = 18
WINDOW = None

DIR_ARR = [
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

class Tile:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.color_pair = 0

        self.solid = False

        self.lines = [
            '..','..','..'
        ]
        if random.randint(0, 100) > 70:
            self.lines = [
                'AA',
                'AA',
                'AA'
            ]


HIGHTLIGHT_POINTS = []


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


class MapGenerationConfig:
    def __init__(self):
        self.height = 10
        self.width = 10


def generate_map(config: MapGenerationConfig=None) -> tuple[list[list[Tile]], list[tuple[int, int]]]:
    if not config:
        config = MapGenerationConfig()

    result: list[list[Tile]] = []
    coords = []

    for i in range(config.height):
        a = []
        for j in range(config.width):
            a += [Tile(i, j)]
        result += [a]

    # generate start point
    # offset_y = config.height // 3
    # offset_x = config.width // 3
    start_point_loc = [
        config.height // 2,
        config.width // 2
    ]

    result[start_point_loc[0]][start_point_loc[1]].solid = True
    coords += [(start_point_loc[0], start_point_loc[1])]
    step_weight = 0.01

    offshoots_count = 3
    offshoots = []
    
    for i in range(offshoots_count):
        # [yloc, xloc, weight]
        o = [start_point_loc[0], start_point_loc[1], 0]
        offshoots += [o]
    count_thresh = 170
    count = 0
    while (len(offshoots)):
        for offshoot in offshoots:
            offshoot[2] += 1
            dir = random.choice(DIR_ARR[offshoot[0] % 2])
            newy = offshoot[0] + dir[0]
            newx = offshoot[1] + dir[1]
            
            if not (newy < 0 or newx < 0 or newy >= config.height or newx >= config.width):
                offshoot[0] = newy
                offshoot[1] = newx

                if not result[offshoot[0]][offshoot[1]].solid:
                    count += 1
                result[offshoot[0]][offshoot[1]].solid = True
                coords += [(offshoot[0], offshoot[1])]

            if count > count_thresh and random.randint(0, 100) < offshoot[2] * step_weight:
                offshoots.remove(offshoot)
    #     draw_map(WINDOW, result, 5, [0,0])
    #     WINDOW.refresh()
    #     # WINDOW.getch()
    #     curses.napms(20)
    # curses.flash()

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
    #     for i in range(bi, config.height - bi):
    #         result[i][bi] = False
    #         result[i][config.width - 1 - bi] = False
    #     for j in range(bi, config.width - bi):
    #         result[bi][j] = False
    #         result[config.height - 1 - bi][j] = False
    # for i in range(len(result)):
    #     line = result[i]
    #     for j in range(len(line)):
    #         if ( or ) and ( or ):
    #             result[i][j] = False

    return result, coords


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


def deferred_draw_tile(args):
    win = args['win']
    y = args['y']
    x = args['x']
    tile = args['tile']
    win.attron(curses.color_pair(tile.color_pair))
    basic_draw_sprite(win, y, x, tile)
    win.attroff(curses.color_pair(tile.color_pair))


def basic_draw_sprite(win, y, x, tile):
    for ii in range(len(SPRITE)):
        win.addstr(y + ii, x, SPRITE[ii])
    win.addstr(y + 1, x + 2, tile.lines[0])
    # win.addstr(y + 1, x + 2, str(tile['pos'][0]))
    win.addstr(y + 2, x + 2, tile.lines[1])
    # win.addstr(y + 2, x + 2, str(tile['pos'][1]))
    win.addstr(y + 3, x + 2, tile.lines[2])


def draw_sprite(win, y, x, tile, selected):
    if not tile.solid:
        return
    
    # win.attron(curses.color_pair(tile.color_pair))
    basic_draw_sprite(win, y, x, tile)
    
    if tile.color_pair != 0:
        defer_draw(deferred_draw_tile, {'win': win, 'y': y, 'x': x, 'tile': tile})
    # win.attroff(curses.color_pair(tile.color_pair))


    if not selected:
        return
    
    defer_draw(deferred_draw_tile, {'win': win, 'y': y, 'x': x, 'tile': tile})


def draw_map(win, map, xbase, pos):
    y = 0
    x = 0
    xdiff = xbase
    height = len(map)
    width = len(map[0])
    for i in range(height):
        x = xdiff
        for j in range(width):
            draw_sprite(win, y, x, map[i][j], pos[0] == i and pos[1] == j)
            x += len(SPRITE[0]) + 4
        xdiff = xbase - xdiff
        y += len(SPRITE) - 3


RESULT = {}
def main(stdscr: 'curses._CursesWindow'):
    global WINDOW
    WINDOW = stdscr
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_RED, 0)
    curses.init_pair(2, curses.COLOR_BLUE, 0)
    curses.init_pair(3, curses.COLOR_RED, 0)
    curses.init_pair(4, curses.COLOR_YELLOW, 0)
    curses.init_pair(5, curses.COLOR_MAGENTA, 0)
    curses.init_pair(6, curses.COLOR_GREEN, 0)
    config = MapGenerationConfig()
    config.height = HEIGHT
    config.width = WIDTH
    game_map, coords = generate_map(config)
    RESULT['map'] = game_map

    # find center
    # sumsy = [sum(line) for line in map]
    # sumsx = []
    # for j in range(len(map[0])):
    #     s = 0
    #     for i in range(len(map)):
    #         s += map[i][j]
    #     sumsx += [s]
    # sumsy += []

    # global CENTER_Y, CENTER_X
    y = sum([p[0] for p in coords]) // len(coords)
    x = sum([p[1] for p in coords]) // len(coords)

    # TODO move to center?

    # game_map[y][x].color_pair = 2

    num_of_players = 4
    angle = random.randint(0, 6)
    for playeri in range(num_of_players):
        yloc = y
        xloc = x
        ydiff = math.sin(angle)
        xdiff = math.cos(angle)
        last_loc = (yloc, xloc)
        while True:
            t = game_map[int(yloc)][int(xloc)]
            if t.solid:
                last_loc = (int(yloc), int(xloc))
                        
            yloc += ydiff
            xloc += xdiff
            if yloc < 0 or xloc < 0 or yloc >= config.height or xloc >= config.width:
                break
        t = game_map[last_loc[0]][last_loc[1]]
        t.color_pair = playeri + 3
        t.lines = [
            '  ',
            'MM',
            '  '
        ]
        # spread
        dirs = DIR_ARR[last_loc[0] % 2]
        for dir in dirs:
            locy = last_loc[0] + dir[0]
            locx = last_loc[1] + dir[1]
            if locy < 0 or locx < 0 or locy >= config.height or locx >= config.width:
                continue
            t = game_map[locy][locx]
            t.color_pair = playeri + 3
            t.lines = [
                '','',''
            ]

        angle += 2 * math.pi / num_of_players


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
        draw_map(stdscr, game_map, xbase, pos)

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
            if pos[0] >= config.height:
                pos[0] = config.height - 1
            pos[1] += diff[1]
            if pos[1] < 0:
                pos[1] = 0
            if pos[1] >= config.width:
                pos[1] = config.width - 1

        
        # clear
        stdscr.clear()

curses.wrapper(main)
rmap = RESULT['map']
for line in rmap:
    for t in line:
        print(t.color_pair, end=' ')
    print()

# num_of_players = 3
# for playeri in range(num_of_players):
#     angle = 0
#     yloc = y
#     xloc = x
#     for i in range(3):
#         yloc += math.sin(angle)
#         xloc += math.cos(angle)
#         try:
#             game_map[int(yloc)][int(xloc)].color_pair = playeri + 3
#         except Exception:
#             pass
#     angle += math.pi / num_of_players