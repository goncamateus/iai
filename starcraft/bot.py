import sc2
from sc2 import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

from visualization import intel


class GoncaBot(sc2.BotAI):

    NAME: str = "GoncaBot"
    """This bot's name"""
    RACE: Race = Race.Protoss
    """This bot's Starcraft 2 race.
    Options are:
        Race.Terran
        Race.Zerg
        Race.Protoss
        Race.Random
    """

    def __init__(self):
        super().__init__()
        self.proxy_built = False

    async def on_start(self):
        print("Game started")
        # Do things here before the game starts

    async def on_step(self, iteration):
        # Populate this function with whatever your bot should do!
        await self.distribute_workers()
        await self.structures_preparation()
        await self.units_preparation()
        await self.attack()
        await intel(self)

    async def structures_preparation(self):
        await self.build_pylons()
        await self.build_gateway()
        await self.build_assimilators()
        await self.build_cyber_core()
        await self.build_four_gates()
        await self.chrono_boost()
        await self.warpgate_research()

    async def units_preparation(self):
        await self.build_workers()
        await self.train_stalker()
        await self.warp_stalkers()

    async def build_workers(self):
        nexus = self.townhalls.ready.random
        if self.can_afford(UnitTypeId.PROBE) \
            and nexus.is_idle \
                and self.workers.amount < self.townhalls.amount*22:
            nexus.train(UnitTypeId.PROBE)

    async def build_pylons(self):
        nexus = self.townhalls.ready.random
        pos = nexus.position.towards(self.enemy_start_locations[0], 10)
        can_build = self.supply_left < 3
        can_build = can_build and self.already_pending(UnitTypeId.PYLON) == 0
        can_build = can_build and self.can_afford(UnitTypeId.PYLON)
        if can_build:
            await self.build(UnitTypeId.PYLON, near=pos)

        if self.structures(UnitTypeId.GATEWAY).amount == 4 \
                and not self.proxy_built \
                and self.can_afford(UnitTypeId.PYLON):
            pos = self.game_info.map_center.towards(
                self.enemy_start_locations[0], 20)
            await self.build(UnitTypeId.PYLON, near=pos)
            self.proxy_built = True

    async def build_gateway(self):
        can_build = self.structures(UnitTypeId.PYLON).ready
        can_build = can_build and not self.structures(UnitTypeId.GATEWAY)
        can_build = can_build and self.can_afford(UnitTypeId.GATEWAY)
        if can_build:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.GATEWAY, near=pylon)

    async def build_assimilators(self):
        if self.structures(UnitTypeId.GATEWAY):
            for nexus in self.townhalls.ready:
                vgs = self.vespene_geyser.closer_than(15, nexus)
                for vg in vgs:
                    if not self.can_afford(UnitTypeId.ASSIMILATOR):
                        break
                    worker = self.select_build_worker(vg.position)
                    if worker is None:
                        break
                    if not self.gas_buildings \
                            or not self.gas_buildings.closer_than(1, vg):
                        worker.build(UnitTypeId.ASSIMILATOR, vg)
                        worker.stop(queue=True)

    async def build_cyber_core(self):
        any_pylon = self.structures(UnitTypeId.PYLON).ready
        if any_pylon:
            gateway = self.structures(UnitTypeId.GATEWAY).ready
            if gateway:
                if not self.structures(UnitTypeId.CYBERNETICSCORE):
                    can_afford = self.can_afford(UnitTypeId.CYBERNETICSCORE)
                    already_building = self.already_pending(
                        UnitTypeId.CYBERNETICSCORE) == 0
                    if can_afford and already_building:
                        pylon = any_pylon.random
                        await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)

    async def train_stalker(self):
        for gateway in self.structures(UnitTypeId.GATEWAY).ready:
            can_afford = self.can_afford(UnitTypeId.STALKER)
            if can_afford and gateway.is_idle:
                gateway.train(UnitTypeId.STALKER)

    async def build_four_gates(self):
        if self.structures(UnitTypeId.GATEWAY).amount < 4:
            can_build = self.structures(UnitTypeId.PYLON).ready
            can_build = can_build and self.can_afford(UnitTypeId.GATEWAY)
            if can_build:
                pylon = self.structures(UnitTypeId.PYLON).ready.random
                await self.build(UnitTypeId.GATEWAY, near=pylon)

    async def chrono_boost(self):
        if self.structures(UnitTypeId.PYLON):
            nexus = self.townhalls.ready.random
            if not self.structures(UnitTypeId.CYBERNETICSCORE).ready \
                    and self.structures(UnitTypeId.PYLON).amount > 0:
                if nexus.energy >= 50:
                    nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
            elif nexus.energy >= 50:
                cyber_core = self.structures(
                    UnitTypeId.CYBERNETICSCORE).ready.random
                nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, cyber_core)

    async def warpgate_research(self):
        can_boost = self.structures(UnitTypeId.CYBERNETICSCORE).ready
        can_boost = can_boost and self.can_afford(AbilityId.RESEARCH_WARPGATE)
        can_boost = can_boost and self.already_pending(
            UpgradeId.WARPGATERESEARCH) == 0
        if can_boost:
            cyber_core = self.structures(
                UnitTypeId.CYBERNETICSCORE).ready.random
            cyber_core.research(UpgradeId.WARPGATERESEARCH)

    async def attack(self):
        stalkers = self.units(UnitTypeId.STALKER)
        stalker_count = stalkers.amount
        pylons = self.structures(UnitTypeId.PYLON).ready
        if pylons:
            proxy = pylons.closest_to(self.enemy_start_locations[0])
            proxy_pos = proxy.position.random_on_distance(3)

        for stalker in stalkers.ready.idle:
            if stalker_count > 15:
                stalker.attack(self.enemy_start_locations[0])
            else:
                stalker.attack(proxy_pos)

    async def warp_stalkers(self):
        for warpgate in self.structures(UnitTypeId.WARPGATE).ready:
            abilities = await self.get_available_abilities(warpgate)
            proxy = self.structures(UnitTypeId.PYLON).ready.closest_to(
                self.enemy_start_locations[0])
            if AbilityId.WARPGATETRAIN_STALKER in abilities \
                    and self.can_afford(UnitTypeId.STALKER):
                pos = proxy.position.random_on_distance(3)
                warpgate.warp_in(UnitTypeId.STALKER, position=pos)

    async def micro(self):
        stalkers = self.units(UnitTypeId.STALKER)
        enemy_location = self.enemy_start_locations[0]
        pylons = self.structures(UnitTypeId.PYLON).ready
        if pylons:
            pylon = pylons.closest_to(enemy_location)
            for stalker in stalkers:
                if stalker.weapon_cooldown == 0:
                    stalker.attack(enemy_location)
                else:
                    stalker.move(pylon)

    def on_end(self, result):
        print("Game ended.")
        # Do things here after the game ends
