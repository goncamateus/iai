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
import random


def random_pos():
    y = random.randint(0, 360)
    x = random.randint(0, 640)
    position = PVector(x, y)
    return position


def is_hit(obj1, obj2, o_width, o_height):
    dist_y = abs(obj1.y - obj2.y)
    hit_y = dist_y < 1+o_height/2
    dist_x = abs(obj1.x - obj2.x)
    hit_x = dist_x < 1+o_width/2
    return hit_y and hit_x

def is_hit_sand(water, obj):
    return is_hit(water, obj, 200, 100)


def is_hit_water(water, obj):
    return is_hit(water, obj, 200, 200)


def is_hit_fruit(fruit, obj):
    return is_hit(fruit, obj, 10, 10)


def is_hit_obstacles(obstacles, fruit):
    hits = list()
    for pos, (wid, hei) in obstacles:
        hits.append(is_hit(pos, fruit, wid, hei))
    return True in hits


def draw_obstacle(obstacle, wid, hei):
    fill(0)
    stroke(127)
    strokeWeight(2)
    rect(obstacle.x-wid/2, obstacle.y-hei/2, wid, hei)


def draw_sand(sand_pos):
    fill(216, 204, 125)
    stroke(127)
    strokeWeight(2)
    rect(sand_pos.x-100, sand_pos.y-50, 200, 100)


def draw_water(water_pos):
    fill(98, 237, 255)
    stroke(127)
    strokeWeight(2)
    rect(water_pos.x-100, water_pos.y-100, 200, 200)


def draw_fruit(fruit_pos):
    fill(175, 80, 248)
    stroke(127)
    strokeWeight(2)
    ellipse(fruit_pos.x, fruit_pos.y, 10, 10)


def draw_text():
    textSize(32)
    text("Frutas comidas em " + str(steps) + " steps: "  + str(points), 10, 30)
    fill(0, 102, 153)


def setup():
    global v, points, obstacles, sands, water, fruit, steps
    size(640, 360)
    v = Vehicle(0, 0)
    points = 0
    steps = 0
    sands = [PVector(100, height-50), PVector(width/2, 50)]
    water = PVector(width-100, height-100)
    obs_pos = [PVector(120, 100), PVector(width/2, height/2), PVector(320+200, 200)]
    obs_params = [(20, 120), (80, 80), (160, 20)]
    obstacles = zip(obs_pos, obs_params)
    fruit = random_pos()
    while is_hit_obstacles(obstacles, fruit):
        fruit = random_pos()


def draw():
    global v, points, obstacles, sands, water, fruit, steps
    background(158, 236, 136)
    draw_water(water)
    for sand in sands:
        draw_sand(sand)
    for pos, (wid, hei) in obstacles:
        draw_obstacle(pos, wid, hei)

    # Call the appropriate steering behaviors for our agents
    power_percent = 1.0
    if is_hit_water(water, v.position):
        power_percent *= 0.1
    if is_hit_sand(sands[0], v.position):
        power_percent *= 0.5
    if is_hit_sand(sands[1], v.position):
        power_percent *= 0.5
    if is_hit_obstacles(obstacles, v.position):
        power_percent *= 0
    if is_hit_fruit(fruit, v.position):
        points += 1
        fruit = random_pos()
        while is_hit_obstacles(obstacles, fruit):
            fruit = random_pos()

    draw_fruit(fruit)
    v.arrive(fruit)
    v.update(power_percent)
    v.display()
    draw_text()
    steps += 1
