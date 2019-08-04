import asyncio
import time
import json
import io
import math
import struct
from collections import defaultdict
from packet_tools import payload_to_packet
from rtf_proxy.const import MAPPING, AUTOUSE, AUTOPICKUP, SLOTS, AUTOUSE_ON_FULL, ITEM


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
        self.packet_id = 0
        self.ts = 0
        self.ts_ensure_bigger = -1
        self.last_ts = 0
        self.to_interact = []
        self.to_send = []
        self.scheduled = {}
        self.prev_49 = None
        self.bags = {}

    async def burst(self, dmg):
        await asyncio.sleep(self.burst_time)
        self.burst_value = max(0, self.burst_value - dmg)


    bag_live = 60

    def remove_entities(self, ids):
        for _id in ids:
            if _id in self.enemies:
                # print(f'Remove Enemy: {self.enemies[_id]}')
                del self.enemies[_id]
            elif _id in self.bags:
                # print(f'Remove Bag: {self.bags[_id]}')
                del self.bags[_id]

    async def clear_bag(self, _id):
        await asyncio.sleep(self.bag_live)
        if _id in self.bags:
            del self.bags[_id]

    def after_bag_update(self, bag):
        print(f'AFTER BAG UPDATE: {bag.dct}')
        for i in range(0x8, 0x10):
            if i in MAPPING:
                name = MAPPING[i][0]
            else:
                name = hex(i)
            item = ITEM.get(bag.dct[name])
            if item == 'empty':
                continue
            print(f'ITEM: {item}')
            if item in AUTOUSE:
                self.use_bag_item(bag, i)
            elif item in AUTOPICKUP and self.get_free_slot():
                self.move_to_slot(bag.entry.id, item)
            elif item in AUTOUSE_ON_FULL:
                print(f'=======> Autouse because full: {self.me.dct}')
                self.use_bag_item(bag, i)

    def add_bag(self, bag):
        _id = bag.entry.id
        if _id not in self.bags:
            asyncio.create_task(self.clear_bag(_id))
            self.bags[_id] = bag
        else:
            # print(f'UPDATE BAG FROM: {self.bags[_id].dct} => {bag.dct}')
            self.bags[_id].dct.update(bag.dct)
        self.after_bag_update(self.bags[_id])


    reserve_hp = 50
    burst_time = 0.5
    burst_amount = 1
    use_defence = False

    switch = -1

    def schedule(self, what, shift=5):
        k = self.packet_id + shift
        if k not in self.scheduled:
            self.scheduled[k] = []
        self.scheduled[k].append(what)
        print(f'SCHEDULE in {self.scheduled}')

    def set_ts(self, packet_id, ts):
        if self.prev_49:
            print(f'After State TS: {ts} VS {self.prev_49} == {ts - self.prev_49}')
            self.prev_49 = None
        self.packet_id = packet_id
        if ts <= self.ts_ensure_bigger:
            print(f'Miss ts bigger: {self.ts} <= {self.ts_ensure_bigger}')
            ts = self.gen_ts()
            # self.close()
        # predicted = self.gen_ts()
        # if abs(ts - predicted) > 10:
        #     print(f'Miss prediction: {predicted} VS Real: {ts}')
        # else:
        #     # print(f'Pred: {predicted} VS Real: {ts}  [{ts - self.ts}]')
        #     pass
        self.ts = ts
        self.last_ts = int(time.time() * 1000)
        # self.switch = -self.switch
        # return self.gen_ts()
        # return ts + 10
        # return ts + self.switch

    def gen_ts(self):
        t = int(time.time() * 1000)
        ts = self.ts + t - self.last_ts
        if ts <= self.ts_ensure_bigger:
            ts += 10
        self.ts_ensure_bigger = ts
        return ts

    def calc_burst(self, dmg):
        self.prev_damage = dmg
        self.burst_value += dmg
        print(f'Received damage: {dmg} [Burst: {self.burst_value}]')
        if not self.is_test:
            asyncio.create_task(self.burst(dmg))
        if (self.hp - self.reserve_hp) < self.burst_value + dmg * self.burst_amount:
            print(f'Close due burst: {self.burst_value} + {dmg} VS {self.hp}')
            self.close()

    def on_teleport(self, payload):
        self.bags = {}
        self.enemies = {}

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

    def log_write(self, msg, stdout=False):
        if stdout:
            print(msg)
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

    def get_item_idx(self, inv_id, item_id):
        # print('Get item idx')
        bag = self.bags[inv_id]
        for i, v in self.bag_indexes.items():
            item = bag.dct.raw[i]
            if item == item_id:
                return v
        raise Exception(f'No {item_id} in {bag.dct.raw}')

    def get_free_slot(self):
        for s, idx in reversed(SLOTS):
            if s in self.me.dct.raw:
                item = self.me.dct.raw[s]
                if item == 0xffffffff:
                    return idx

    def move_to_slot(self, inv_id, item_id, to_slot=None, from_slot=None):
        print(f'MOVE TO SLOT: {item_id}')
        _type = 59
        ts = self.gen_ts()
        pos_x, pos_y = self.mypos
        inv_id = inv_id
        if not from_slot:
            from_slot = self.get_item_idx(inv_id, item_id)
        item_id = item_id
        who_pickup = self.me.entry.id
        if not to_slot:
            to_slot = self.get_free_slot()
        if not to_slot:
            print(f'CANNOT MOVE TO SLOT. NO SLOTS: {item_id}')
            return
        ffff = 0xffffffff
        payload = struct.pack('!BIIIIBIIBI', _type, ts, pos_x, pos_y, inv_id, from_slot,
                              item_id, who_pickup, to_slot, ffff)
        print(f'Move write: {payload}')
        self.remote_writer.write(payload_to_packet(payload))

    bag_indexes = {0x8: 0, 0x9: 1, 0xa: 2, 0xb: 3, 0xc: 4, 0xd: 5, 0xe: 6, 0xf: 7}

    def use_bag_item(self, bag, slot_id):
        item = bag.dct.raw[slot_id]
        idx = self.bag_indexes[slot_id]
        out_type = 49
        ts = self.gen_ts() + idx
        if ts == self.ts:
            ts += 1
        _id = bag.entry.id
        i1 = 0
        i2 = 0
        b1 = 1
        pl = struct.pack('!BIIBIIIB', out_type, ts, _id, idx, item, i1, i2, b1)
        what = payload_to_packet(pl)
        self.ts_ensure_bigger = ts
        assert len(what) == 23 + 4
        # self.state.to_interact.append([out_type, ts, _id, idx, item, i1, i2, b1])
        msg = f'!!Autoopen: {what}   TS: {self.ts} Gen: {ts} : {idx} && {slot_id}\n'
        print(msg)
        # self.state.log_write(msg)
        # self.state.to_send.append(what)
        self.remote_writer.write(what)


# use inplace get_state when need to get to prevent caching an old state object
__state = None


def get_state():
    return __state


def new_state(is_test=False):
    global state
    state = State(is_test=is_test)
    return state
