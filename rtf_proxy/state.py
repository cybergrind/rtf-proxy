import asyncio
import time
import json
import io
import math
import struct
from collections import defaultdict


class State:
    def __init__(self, is_test=False):
        self.counter = 0
        self.stats = defaultdict(int)
        self.mypos = [0, 0]
        self.me = None
        self.safe = True
        self.kill = False
        self.enemies = {}
        self.is_test = is_test
        self.log = io.StringIO() if is_test else open('messages.log', 'w')

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

    def add_enemy(self, enemy_id, pos_x, pos_y):
        # print(f'Add enemy: {enemy_id} {pos_x}/{pos_y}')
        if enemy_id not in self.enemies:
            asyncio.create_task(self.clear_enemy(enemy_id))
        self.enemies[enemy_id] = {'pos_x': pos_x, 'pos_y': pos_y, 'updated': time.time(),
                                  'dist': self.dist(pos_x, pos_y), 'id': enemy_id}

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
        self.kill = True
        self.log.write(json.dumps(self.stats, indent=4, sort_keys=True))
        self.log.close()

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


# use inplace get_state when need to get to prevent caching an old state object
__state = None


def get_state():
    return __state


def new_state(is_test=False):
    global state
    state = State(is_test=is_test)
    return state
