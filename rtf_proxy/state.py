import asyncio
import time
import json
import io
import math
import struct
from collections import defaultdict



TOLERATE = 20  # AOE memory


class State:
    def __init__(self, is_test=False):
        self.counter = 0
        self.stats = defaultdict(int)
        self.mypos = [0, 0]
        self.me = None
        self.safe = True
        self.kill = False
        self.enemies = {}
        self.expected_dmg = 0
        self.is_test = is_test
        self.log = io.StringIO() if is_test else open('messages.log', 'w')
        self.aoe = {'time': 0, 'dmg': 0}
        self.hp_delta = 0
        self.prev_damage = 0
        self.burst_value = 0
        self.defence = 0
        self.damage_diff = []

    async def burst(self, dmg):
        await asyncio.sleep(self.burst_time)
        self.burst_value = max(0, self.burst_value - dmg)

    reserve_hp = 20
    burst_time = 0.5
    use_defence = False

    def calc_burst(self, dmg):
        self.prev_damage = dmg
        self.burst_value += dmg
        print(f'Received damage: {dmg} [Burst: {self.burst_value}]')
        if not self.is_test:
            asyncio.create_task(self.burst(dmg))
        if (self.hp - self.reserve_hp) < self.burst_value + dmg:
            print(f'Close due burst: {self.burst_value} + {dmg} VS {self.hp}')
            self.close()

    def add_expected_dmg(self, dmg):
        if self.use_defence:
            self.expected_dmg += (dmg * 0.85 - self.defence) + dmg * 0.15
        else:
            self.expected_dmg += dmg

        if not self.hp_safe:
            print(f'Not safe hp {self.hp} => {self.expected_dmg}')
            self.close()

    def set_new_me(self, new_me):
        if self.me:
            self.process_expected_dmg(self.me.dct, new_me.dct)
        self.me = new_me

    def update_me_dct(self, new_dct):
        self.process_expected_dmg(self.me.dct, new_dct)
        self.hp_delta = new_dct.get('hp', self.hp) - self.hp
        self.me.dct.update(new_dct)

    def process_expected_dmg(self, old_dct, new_dct):
        if ('hp' in new_dct or 'mp' in new_dct) and old_dct:
            old_hp = old_dct['hp']
            new_hp = new_dct.get('hp', old_hp)
            if self.expected_dmg > 0:
                expected_hp = old_hp - self.expected_dmg

                if self.use_defence:
                    diff = abs(expected_hp - new_hp)
                    if diff > 20 and expected_hp < new_hp:
                        self.defence += 1
                    elif diff > 20 and expected_hp > new_hp:
                        self.defence -= 1

                print(f'Real: {new_hp} VS Expected: {expected_hp} [{self.expected_dmg}] Def: {self.defence}')
            # print('Reset expected: {self.expected_dmg}')
            self.expected_dmg = 0

            possible_aoe = self.possible_aoe
            if possible_aoe != 0:
                print(f'Update HP: {new_hp} Possible aoe: {possible_aoe}')
            if new_hp < possible_aoe:
                print(f'Close because possible aoe can kill')
                self.close()

    def refresh_aoe(self):
        if self.aoe['dmg'] != 0 and time.time() - self.aoe['time'] < TOLERATE:
            self.aoe['time'] = time.time()

    @property
    def possible_aoe(self):
        if self.aoe['dmg'] != 0 and time.time() - self.aoe['time'] < TOLERATE:
            return self.aoe['dmg']
        elif time.time() - self.aoe['time'] < TOLERATE:
            self.aoe['dmg'] = 0
        return 0

    def dist(self, tx, ty):
        x, y = self.mypos
        return math.sqrt((tx - x) ** 2 + (ty - y) ** 2)

    def get_angle(self, tx, ty):
        x, y = self.mypos
        return math.atan2(ty - y, tx - x)

    def get_closest_enemy(self):
        out = list(self.enemies.values())
        if out:
            out.sort(key=lambda x: x['dist'])
            return out[0]

    async def clear_enemy(self, enemy_id):
        while True:
            await asyncio.sleep(1)
            if enemy_id in self.enemies and time.time() - self.enemies[enemy_id]['updated'] > 2:
                del self.enemies[enemy_id]
                return

    def add_enemy(self, enemy_id, pos_x, pos_y, bullets):
        # print(f'Add enemy: {enemy_id} {pos_x}/{pos_y}')
        if enemy_id not in self.enemies:
            if not self.is_test:
                asyncio.create_task(self.clear_enemy(enemy_id))
            self.enemies[enemy_id] = {}
        self.enemies[enemy_id].update({'pos_x': pos_x, 'pos_y': pos_y, 'updated': time.time(),
                                       'dist': self.dist(pos_x, pos_y), 'id': enemy_id})
        self.enemies[enemy_id].setdefault('bullets', {}).update(bullets)

    def aim_closest(self):
        e = self.get_closest_enemy()
        if not e:
            return
        angle = self.get_angle(e['pos_x'], e['pos_y'])
        return e['pos_x'], e['pos_y'], angle, e

    def set_mypos(self, pos_x, pos_y):
        self.mypos = [pos_x, pos_y]
        for k, v in self.enemies.items():
            dist = self.dist(v['pos_x'], v['pos_y'])
            v['dist'] = dist

    def count_packet(self, payload):
        _type = struct.unpack('!B', payload[:1])[0]
        self.stats[_type] += 1

    def close(self):
        print('State Run close')
        self.kill = True
        if not self.log.closed:
            self.log.write(json.dumps(self.stats, indent=4, sort_keys=True))
            self.log.close()

    def log_write(self, msg):
        if not self.log.closed:
            self.log.write(msg)

    @property
    def hp(self):
        if not self.me:
            return 1000
        return self.me.dct['hp']

    @property
    def hp_level(self):
        if not self.me:
            return 1
        return self.me.dct['hp'] / self.me.dct['max_hp']

    def hp_very_low_old(self):
        return not state.safe and (state.hp_level < 0.5 and state.hp < 600)

    smart_hp = True

    @property
    def hp_safe(self):
        if self.safe:
            return True

        if not self.smart_hp:
            return not self.hp_very_low_old()

        expected_hp = self.hp - self.expected_dmg
        if expected_hp <= self.reserve_hp:
            print(f'Not safe, expected hp: {expected_hp} [{self.hp} - {self.expected_dmg}]')
            return False
        return True


# use inplace get_state when need to get to prevent caching an old state object
__state = None


def get_state():
    return __state


def new_state(is_test=False):
    global state
    state = State(is_test=is_test)
    return state
