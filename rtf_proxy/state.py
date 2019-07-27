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

    def count_packet(self, payload):
        _type = struct.unpack('!B', payload[:1])[0]
        self.stats[_type] += 1

    def close(self):
        self.kill = True
        self.log.write(json.dumps(self.stats, indent=4, sort_keys=True))
        self.log.close()

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
