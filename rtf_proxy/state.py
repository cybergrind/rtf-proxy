import asyncio
import importlib
import io
import json
import math
import struct
import time
from collections import defaultdict

import rtf_proxy.const
from packet_tools import payload_to_packet
from rtf_proxy import const

TOLERATE = 20  # AOE memory


def without(dct, *keys):
    return {k: v for k, v in dct.items() if k not in keys}


class State:
    def __init__(self, is_test=False):
        self.counter = 0
        self.stats = defaultdict(int)
        self.mypos = [0, 0]
        self.me = None
        self.location = b'Nexus'
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
        self.to_send = []
        self.scheduled = {}
        self.prev_49 = None
        self.bags = {}
        self.loot = 0
        self.mode = None
        self.pending_switch = False
        self.shot_allowed = True

    def update_location(self, new_location):
        self.location = new_location
        if self.location in const.SAFE_LOCATIONS:
            self.safe = True
        else:
            self.safe = False
        print(f'Location to: {self.location} Is safe: "{self.safe}')
        # self.warn_message(f'Current mode: {self.mode}')
        self.clean_temporary()

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
        for i in range(0x8, 0x10):
            if i in const.MAPPING:
                name = const.MAPPING[i][0]
            else:
                name = hex(i)
            item = const.ITEM.get(bag.dct[name])
            if item in const.WARN and self.get_free_slot():
                self.warn_message(f'Cannot pickup item: {item} CHECK IT'.encode('utf8'))
        if self.location in const.NO_PICKUP:
            return
        # print(f'AFTER BAG UPDATE: {bag.dct}')
        for i in range(0x8, 0x10):
            if i in const.MAPPING:
                name = const.MAPPING[i][0]
            else:
                name = hex(i)
            item = const.ITEM.get(bag.dct[name])
            if item == 'empty':
                continue
            # print(f'ITEM: {item}')
            has_slot = self.get_free_slot()
            if self.loot > 0 and item in const.LOOT and has_slot:
                self.move_to_slot(bag.entry.id, item)
                self.loot -= 1
                self.warn_message(f'Loot {self.loot} more')
            elif item in const.AUTOUSE:
                self.use_bag_item(bag, i)
            elif item in const.AUTOPICKUP and has_slot:
                self.move_to_slot(bag.entry.id, item)
            elif item in const.AUTOUSE_ON_FULL:
                print(f'=======> Autouse because full: {self.me.dct}')
                self.use_bag_item(bag, i)
            elif item in const.IMPORTANT:
                self.warn_message(f'Got important item, PICKUP IT: {item}')
            elif not isinstance(item, const.ITEM):
                if self.get_free_slot():
                    self.move_to_slot(bag.entry.id, item)
                    self.warn_message(f'PICK new item: {item}')
                else:
                    self.warn_message(f'Get and process item: {item}')
            else:
                pass

    def handle_cmd(self, payload):
        skip = False
        _size = struct.unpack('!H', payload[1:3])[0]
        bin_send_msg = payload[3 : 3 + _size]
        command = bin_send_msg.decode('utf8')
        try:
            if command == '/cr' or command == 'creload':
                skip = True
                importlib.reload(rtf_proxy.const)
                self.warn_message('Reloaded...')
            elif command.startswith('/cl'):
                skip = True
                maybe_int = command.replace('/cl', '').strip()
                if maybe_int:
                    num = int(maybe_int)
                else:
                    num = 8
                self.loot = num
                self.warn_message(f'Set loot to: {num}')
            elif command.startswith('/necr'):
                skip = True
                self.necro_mode()
                self.warn_message(f'Enable Necro mode: skull {self.me.dct["item_2"]!r}')
            elif command == '/off':
                skip = True
                self.warn_message(f'From {self.mode} => None')
                self.mode = None
        except Exception as e:
            self.warn_message(f'Command exception: {e}')
        return skip

    def skull_shot(self, target=None):
        if self.location in const.NO_ACTION:
            return

        if not self.shot_allowed:
            return
        _type = 49
        ts = self.gen_ts()
        who = self.me.entry.id
        idx = 1
        item = self.me.dct['item_1']
        if not target:
            pos_x = self.mypos[0] + 1
            pos_y = self.mypos[1] + 1
        else:
            pos_x, pos_y = target
        end = 1
        pl = struct.pack('!BIIBIffB', _type, ts, who, idx, item, pos_x, pos_y, end)
        self.log_write(f'Write skull push: {pl}')
        self.remote_writer.write(payload_to_packet(pl))
        asyncio.create_task(self.after_shot())

    async def after_shot(self):
        self.shot_allowed = False
        await asyncio.sleep(0.3)
        self.shot_allowed = True

    def necro_mode(self):
        self.mode = 'necro'
        self.skulls = {'hp': None, 'dmg': None}
        self.all_skulls = {}
        self.curr_skulls = {'active': None, 'passive': None}
        self.skull_slot = -1
        for i in range(1, 9):
            slot_idx = i + 11
            key = f'slot_{i}'
            value = self.me.dct[key]
            if value in const.SKULLS:
                self.all_skulls[value] = slot_idx
        if self.me.dct['item_2'] in const.SKULLS:
            self.all_skulls[self.me.dct['item_2']] = -1

        for skull, idx in self.all_skulls.items():
            self.skulls[const.SKULLS[skull]['type']] = skull
            if idx > -1:
                self.skull_slot = idx
        print(f'SKULLS: {self.skulls}')
        self.handle_mode()

    def handle_mode(self):
        if self.mode == 'necro':
            # if self.is_safe:
            #     return
            active = self.me.dct['item_2']
            if self.pending_switch and active != self.curr_skulls['active']:
                self.pending_switch = False
            self.curr_skulls['active'] = active
            # print(f'DCT.RAW: {self.me.dct.raw}')
            self.curr_skulls['passive'] = self.me.dct.raw[self.skull_slot]
            if self.hp_level < 0.9 and self.skulls['hp']:
                self.switch_skull('hp')
            elif self.skulls['dmg']:
                self.switch_skull('dmg')

    def switch_skull(self, _type):
        if self.pending_switch:
            return
        if self.curr_skulls['active'] == self.skulls[_type]:
            return
        print(f'Switch skull to {_type} // {self.hp_level} {self.hp} vs {self.me.dct["max_hp"]}')
        # self.move_to_slot(0x1, self.skull_slot)
        self.pending_switch = True
        self.move_to_slot(
            self.me.entry.id,
            self.skulls[_type].value,
            to_slot=self.skull_slot - 8,
            from_slot=1,
            to_id=self.curr_skulls['passive'],
        )

    def handle_enemy(self, enemy):
        if self.mode == 'necro':
            # self.warn_message(f'Handle enemy: mp: {self.me.dct["mp"]} d: {enemy["dist"]}')
            print(
                f'Handle enemy: mp: {self.me.dct["mp"]} d: {without(enemy, "bullets")} {self.mypos}'
            )
            mp_level = 400
            if self.hp_level < 0.4:
                mp_level = 120

            if self.me.dct['mp'] > mp_level:
                if enemy['dist'] < 13:
                    print('Shot they')
                    self.skull_shot([enemy['pos_x'], enemy['pos_y']])
        self.handle_mode()

    def add_bag(self, bag):
        _id = bag.entry.id
        if _id not in self.bags:
            asyncio.create_task(self.clear_bag(_id))
            self.bags[_id] = bag
        else:
            # print(f'UPDATE BAG FROM: {self.bags[_id].dct} => {bag.dct}')
            self.bags[_id].dct.update(bag.dct)
        self.after_bag_update(self.bags[_id])

    reserve_hp = 75
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
        self.clean_temporary()

    def clean_temporary(self):
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
            self.me.dct.update(new_me.dct)
            new_me.dct = self.me.dct
        self.me = new_me

    def update_me_dct(self, new_dct):
        self.process_expected_dmg(self.me.dct, new_dct)
        self.hp_delta = new_dct.get('hp', self.hp) - self.hp
        self.me.dct.update(new_dct)
        self.handle_mode()

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

                print(
                    f'Real: {new_hp} VS Expected: {expected_hp} [{self.expected_dmg}] Def: {self.defence}'
                )
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
        obj = {
            'pos_x': pos_x,
            'pos_y': pos_y,
            'updated': time.time(),
            'dist': self.dist(pos_x, pos_y),
            'id': enemy_id,
        }
        self.enemies[enemy_id].update(obj)
        self.enemies[enemy_id].setdefault('bullets', {}).update(bullets)
        self.handle_enemy(self.enemies[enemy_id])

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
        return not self.safe and (self.hp_level < 0.5 and self.hp < 600)

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
        for s, idx in reversed(const.SLOTS):
            if s in self.me.dct.raw:
                item = self.me.dct.raw[s]
                if item == 0xffffffff:
                    return s, idx

    def move_to_slot(self, inv_id, item_id, to_slot=None, from_slot=None, to_id=0xffffffff):
        if self.location in const.NO_ACTION:
            return
        _type = 59
        ts = self.gen_ts()
        pos_x, pos_y = self.mypos
        inv_id = inv_id
        if not from_slot:
            from_slot = self.get_item_idx(inv_id, item_id)
        item_id = item_id
        who_pickup = self.me.entry.id
        if not to_slot:
            slot, to_slot = self.get_free_slot()
        print(f'MOVE {item_id} TO SLOT: {to_slot} From: {from_slot} [obj: {inv_id}]')
        if not to_slot:
            print(f'CANNOT MOVE TO SLOT. NO SLOTS: {item_id}')
            return
        payload = struct.pack(
            '!BIffIBIIBI',
            _type,
            ts,
            pos_x,
            pos_y,
            inv_id,
            from_slot,
            item_id,
            who_pickup,
            to_slot,
            to_id,
        )
        print(f'Move write: {payload}')
        # self.me.dct.raw[slot] = '<moving>'
        self.remote_writer.write(payload_to_packet(payload))

    bag_indexes = {0x8: 0, 0x9: 1, 0xa: 2, 0xb: 3, 0xc: 4, 0xd: 5, 0xe: 6, 0xf: 7}

    def use_bag_item(self, bag, slot_id):
        if self.location in const.NO_ACTION:
            raise Exception('use bag item')
            return
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
        print(out_type, ts, _id, idx, item, i1, i2, b1)
        pl = struct.pack('!BIIBIIIB', out_type, ts, _id, idx, item, i1, i2, b1)
        what = payload_to_packet(pl)
        self.ts_ensure_bigger = ts
        assert len(what) == 23 + 4
        msg = f'!!Autoopen: {what}   TS: {self.ts} Gen: {ts} : {idx} && {slot_id}\n'
        print(msg)
        # self.state.log_write(msg)
        # self.state.to_send.append(what)
        self.remote_writer.write(what)

    def warn_message(self, msg):
        # return
        _from = b'Toool'
        if isinstance(msg, str):
            msg = msg.encode('utf8')
        # r, g, b = 81, 245, 66 # green
        r, g, b = 255, 66, 245
        payload = struct.pack(
            f'!BH{len(_from)}sBBBBIIBHH{len(msg)}sH{len(msg)}s',
            23,
            len(_from),
            _from,
            0x00,
            r,
            g,
            b,
            self.me.entry.id,
            0xffffffff,  # 0x46,
            0x5,
            0,
            len(msg),
            msg,
            len(msg),
            msg,
        )
        self.local_writer.write(payload_to_packet(payload))


# use inplace get_state when need to get to prevent caching an old state object
__state = None


def get_state():
    return __state


def new_state(is_test=False):
    global state
    state = State(is_test=is_test)
    return state
