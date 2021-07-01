# The Nature of Code
# Daniel Shiffman
# http://natureofcode.com

# Seeking "vehicle" follows the mouse position

# Implements Craig Reynold's autonomous steering behaviors
# One vehicle "seeks"
# See: http://www.red3d.com/cwr/

# Equipe
# Jose Faustino Macedo de Souza, Mateus Machado, Tu Chin Hung

from Vehicle import Vehicle
from PriorityQueue import PriorityQueue
import random
from copy import deepcopy
import time
import sys
import math


def random_pos():
    y = random.randint(0, 15)
    x = random.randint(0, 25)
    return (x, y)


def get_vehicle_tile(pos):
    global v_tile
    tile_x = floor(pos.x/25)
    tile_y = floor(pos.y/25)
    v_tile = (tile_x, tile_y)
    return tile_x, tile_y


def on_object(pos):
    if pos is None:
        pos = v.position
    tile_x, tile_y = get_vehicle_tile(pos)
    return mapa[tile_y][tile_x]


def in_game(pos):
    x = 0 < pos.x < width
    y = 0 < pos.y < height
    return x and y


def draw_text():
    textSize(32)
    text("Frutas comidas : " + str(points), 10, 30)
    fill(0, 102, 153)


def draw_tiles():
    for y in range(len(mapa)):
        for x in range(len(mapa[y])):
            m_color = m_green
            if mapa[y][x] == 100:
                m_color = (0, 0, 0)
            elif mapa[y][x] == 10:
                m_color = m_blue
            elif mapa[y][x] == 5:
                m_color = m_yellow
            fill(*m_color)
            stroke(127)
            strokeWeight(1)
            rect(x*25, y*25, 25, 25)
            if mapa[y][x] == -1:
                m_color = (175, 80, 248)
                fill(*m_color)
                stroke(127)
                strokeWeight(1)
                ellipse(12.5+x*25, 12.5+y*25, 20, 20)

def draw_res():
    for x, y in ori_res[:-1]:
        m_color = (255, 197, 192)
        fill(*m_color)
        stroke(127)
        strokeWeight(1)
        ellipse(12.5+x*25, 12.5+y*25, 20, 20)

def draw_visited():
    for x, y in visited[:-1]:
        m_color = (149, 86, 80)
        fill(*m_color)
        stroke(127)
        strokeWeight(1)
        ellipse(12.5+x*25, 12.5+y*25, 20, 20)


def set_map():
    global mapa, ori_mapa
    mapa = []
    for y in range(16):
        linha = []
        for x in range(26):
            linha.append(1)
        mapa.append(linha)

    # Areias
    for y in range(1, 8):
        for x in range(8, 22):
            mapa[y][x] = 5
    for y in range(11, 16):
        for x in range(11):
            mapa[y][x] = 5

    # Agua
    for y in range(11, 16):
        for x in range(16, 26):
            mapa[y][x] = 10

    # Obstaculos
    for x in range(7):
        mapa[7][x] = 100
    for y in range(1, 7):
        mapa[y][6] = 100
    for x in range(7, 12):
        mapa[10][x] = 100
    for y in range(11, 16):
        mapa[y][11] = 100
    for x in range(15, 20):
        mapa[10][x] = 100
    for y in range(11, 16):
        mapa[y][15] = 100
    for y in range(8):
        mapa[y][18] = 100
    for x in range(18, 25):
        mapa[8][x] = 100

    ori_mapa = deepcopy(mapa)


def set_fruit_pos():
    global mapa, fruit
    mapa = deepcopy(ori_mapa)
    fruit = random_pos()
    while mapa[fruit[1]][fruit[0]] == 100 or fruit == v_tile:
        fruit = random_pos()
    mapa[fruit[1]][fruit[0]] = -1


def get_fruit_pvector():
    x = fruit[0]*25
    y = fruit[1]*25
    return PVector(x+12.5, y+12.5)


def get_target(tile):
    x = tile[0]*25
    y = tile[1]*25
    return PVector(x+12.5, y+12.5)


def get_neighbours(tile):
    neighbours = []
    if tile[1]-1 >= 0 and mapa[tile[1]-1][tile[0]] < 11:
        # pra cima
        neighbours.append((tile[0], tile[1]-1))
    if tile[0]+1 < 26 and mapa[tile[1]][tile[0]+1] < 11:
        # pra direita
        neighbours.append((tile[0]+1, tile[1]))
    if tile[1]+1 < 16 and mapa[tile[1]+1][tile[0]] < 11:
        # pra baixo
        neighbours.append((tile[0], tile[1]+1))
    if tile[0]-1 >= 0 and mapa[tile[1]][tile[0]-1] < 11:
        # pra esquerda
        neighbours.append((tile[0]-1, tile[1]))
    return neighbours


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidian(a, b):
    return sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def glutony(a, b):
    return 0


def heuristic(goal, next):
    return abs(manhattan(goal, next) - euclidian(goal, next))


def a_star():
    global res, visited, ori_res
    start = get_vehicle_tile(v.position)
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = dict()
    cost_so_far = dict()
    came_from[start] = None
    cost_so_far[start] = 0
    res = [fruit]
    visited = []

    while not frontier.empty():
        current = frontier.getf()
        visited.append(current)
        if current == fruit:
            break

        for next in get_neighbours(current):
            new_cost = cost_so_far[current] + mapa[next[1]][next[0]]
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(fruit, next)
                frontier.put(next, priority)
                came_from[next] = current
    last = came_from[fruit]
    res.append(last)
    while last != start:
        last = came_from[last]
        res.append(last)
    res.reverse()
    ori_res = deepcopy(res)


def setup():
    # deixa 26 x 16 tiles
    global v, points, mapa, m_green, m_blue, m_yellow, res
    size(650, 400)
    m_green = (158, 236, 136)
    m_blue = (98, 237, 255)
    m_yellow = (216, 204, 125)
    points = 0
    set_map()
    v = Vehicle(12.5, 12.5)
    get_vehicle_tile(v.position)
    set_fruit_pos()
    res = a_star()


def draw():
    global v, points, mapa, fruit, ori_mapa, res
    background(158, 236, 136)
    obj = on_object(None)
    if obj == 5:
        time.sleep(0.2)
    if obj == 10:
        time.sleep(0.5)
        power_percent = 0.1
    else:
        time.sleep(0.05)

    if obj < 0:
        set_map()
        get_vehicle_tile(v.position)
        set_fruit_pos()
        points += 1
    if res:
        target = get_target(res[0])
        res = res[1:]
    else:
        a_star()
        target = v.position

    v.arrive(target)
    next_pos = v.position + v.desired
    if in_game(next_pos) and on_object(next_pos) < 11:
        v.position.add(v.desired)

    draw_tiles()
    draw_visited()
    draw_res()
    v.display()
    draw_text()
    
