import math

import cv2
import numpy as np
from sc2.ids.unit_typeid import UnitTypeId


async def intel(bot):
    game_data = np.zeros(
        (bot.game_info.map_size[1], bot.game_info.map_size[0], 3), np.uint8)

    for unit in bot.units().ready:
        pos = unit.position
        cv2.circle(game_data, (int(pos[0]), int(pos[1])), int(
            unit.radius*8), (255, 255, 255), math.ceil(int(unit.radius*0.5)))

    for unit in bot.enemy_units:
        pos = unit.position
        cv2.circle(game_data, (int(pos[0]), int(pos[1])), int(
            unit.radius*8), (125, 125, 125), math.ceil(int(unit.radius*0.5)))

    try:
        line_max = 50
        mineral_ratio = bot.minerals / 1500
        if mineral_ratio > 1.0:
            mineral_ratio = 1.0

        vespene_ratio = bot.vespene / 1500
        if vespene_ratio > 1.0:
            vespene_ratio = 1.0

        population_ratio = bot.supply_left / bot.supply_cap
        if population_ratio > 1.0:
            population_ratio = 1.0

        plausible_supply = bot.supply_cap / 200.0

        worker_weight = len(bot.units(UnitTypeId.PROBE)) / \
            (bot.supply_cap-bot.supply_left)
        if worker_weight > 1.0:
            worker_weight = 1.0

        cv2.line(game_data, (0, 19), (int(line_max*worker_weight),
                 19), (250, 250, 200), 3)  # worker/supply ratio
        cv2.line(game_data, (0, 15), (int(line_max*plausible_supply), 15),
                 (220, 200, 200), 3)  # plausible supply (supply/200.0)
        cv2.line(game_data, (0, 11), (int(line_max*population_ratio), 11),
                 (150, 150, 150), 3)  # population ratio (supply_left/supply)
        cv2.line(game_data, (0, 7), (int(line_max*vespene_ratio),
                 7), (210, 200, 0), 3)  # gas / 1500
        cv2.line(game_data, (0, 3), (int(line_max*mineral_ratio),
                 3), (0, 255, 25), 3)  # minerals minerals/1500
    except Exception as e:
        print(str(e))

    # flip horizontally to make our final fix in visual representation:
    grayed = cv2.cvtColor(game_data, cv2.COLOR_BGR2GRAY)
    bot.flipped = cv2.flip(grayed, 0)
    resized = cv2.resize(bot.flipped, dsize=None, fx=2, fy=2)
    cv2.imshow(str('VISUALIZACAO'), resized)
    cv2.waitKey(1)
