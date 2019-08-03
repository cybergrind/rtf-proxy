import asyncio
import glob
import struct
from enum import Flag, auto
from itertools import chain

from rtf_proxy.packet_tools import save_packet
from rtf_proxy.state import new_state
from rtf_proxy.structs.rotf79 import Rotf79
from rtf_proxy.structs.rotf85 import Rotf85

unpackers = {79: Rotf79, 85: Rotf85}

look_name = 'cybergind'


class STATUS(Flag):
    B1 = auto()
    SILENT = auto()
    B3 = auto()
    SLOW = auto()
    B5 = auto()  # skull
    SLOW_ATTACK = auto()
    STAR = auto()  # NO ATTACK
    BLIND = auto()
    HALLUCINATING = auto()
    DRUNK = auto()
    CONFUSED = auto()
    B12 = auto()
    INVISIBLE = auto()
    PARALYZED = auto()
    SPEEDY = auto()
    BLEEDING = auto()
    B17 = auto()
    HEALING = auto()
    DAMAGING = auto()
    BERSERK = auto()
    DISABLED = auto()  # GRAY
    BLACK_WHITE = auto()
    B23 = auto()
    B24 = auto()
    INVULN = auto()
    BROWN_ARMOR = auto()
    CROSS = auto()
    IM_PET = auto()
    SPEEDY2 = auto()
    UNSTABLE = auto()
    DARKNESS = auto()
    B32 = auto()


MAPPING = {
    0x00: ('max_hp', 'value'),
    0x01: ('hp', 'value'),
    0x03: ('max_mp', 'value'),
    0x04: ('mp', 'value'),
    0x0c: ('slot_1', 'value'),
    0x0d: ('slot_2', 'value'),
    0x0e: ('slot_3', 'value'),
    0x0f: ('slot_4', 'value'),
    0x10: ('slot_5', 'value'),
    0x11: ('slot_6', 'value'),
    0x12: ('slot_7', 'value'),
    0x13: ('slot_8', 'value'),
    0x14: ('ATT', 'value'),
    0x15: ('DEF', 'value'),
    0x16: ('SPD', 'value'),
    0x1a: ('VIT', 'value'),
    0x1b: ('WIS', 'value'),
    0x1c: ('DEX', 'value'),
    0x1d: ('status', 'value'),
    0x1f: ('name', 'name'),
    0x26: ('0x26', 'name'),
    0x36: ('0x36', 'name'),
    0x3e: ('clan', 'name'),
    0x63: ('0x63', 'name'),
}


class GameObject:
    def __init__(self, state, entry, payload):
        self._position = None
        self.state = state
        self.entry = entry
        self.payload = payload
        self.dct = {}
        self.decode_object(entry.object)

    reset_flags = ~(
        STATUS.SILENT
        | STATUS.SLOW
        | STATUS.SLOW_ATTACK
        | STATUS.STAR
        | STATUS.BLIND
        | STATUS.HALLUCINATING
        | STATUS.DRUNK
        | STATUS.CONFUSED
        | STATUS.PARALYZED
        | STATUS.DISABLED
        | STATUS.IM_PET
        | STATUS.UNSTABLE
        | STATUS.DARKNESS
    )
    set_flags = STATUS.DAMAGING | STATUS.SPEEDY | STATUS.BERSERK | STATUS.SPEEDY2

    @property
    def position(self):
        if self._position:
            return self._position
        if not hasattr(self.entry, 'x_pos'):
            return
        b = struct.pack('!III', self.entry.id, self.entry.x_pos, self.entry.y_pos)
        self._position = self.payload.find(b)
        return self._position

    def fix_items(self):
        if not hasattr(self.entry, 'x_pos') or not self.dct['0x9']:
            return
        return
        spack = struct.pack('!BI', 0x9, self.dct['0x9'])
        location = self.payload.find(spack, self.position)
        assert self.payload[location : location + 5] == spack, spack
        new_item = 2730
        if self.dct['0x9'] != new_item:
            print(f'Replace skull: {self.dct["0x9"]} => {new_item}')
            self.payload[location : location + 5] = struct.pack('!BI', 0x9, new_item)

    def reset_effects(self):
        if not hasattr(self.entry, 'x_pos'):
            print(f'No pos effect: {STATUS(self.dct["status"])}')
            return
        print(f'{STATUS(self.dct["status"])}')
        spack = struct.pack('!BI', 0x1d, self.dct['status'])
        self.flags_position = self.payload.find(spack, self.position)
        status = STATUS(self.dct['status'])
        new_status = ((status & self.reset_flags) | self.set_flags).value
        self.state.good_status = new_status
        if self.dct['status'] != new_status:
            print(f'Replace status: {status} => {STATUS(new_status)}')
            self.payload[self.flags_position : self.flags_position + 5] = spack = struct.pack(
                '!BI', 0x1d, new_status
            )

    def decode_object(self, obj):
        if obj.num_fields == 0:
            return
        for kv in obj.dct:
            key = kv.key
            dct_key, dct_value = MAPPING.get(key, (hex(key), 'value'))
            self.dct[dct_key] = getattr(kv.value, dct_value)
        if self.entry.id in self.state.enemies and hasattr(self.entry, 'pos_x'):
            self.state.add_enemy(self.entry.id, self.entry.pos_x, self.entry.pos_y, {})
        if self.dct.get('name') == 'cybergrind':
            self.state.set_new_me(self)
            if hasattr(self.entry, 'x_pos'):
                self.state.set_mypos(self.entry.x_pos, self.entry.y_pos)

        if self.state.me and self.state.me.entry.id == self.entry.id:
            self.state.update_me_dct(self.dct)
            _type = struct.unpack('!B', self.payload[:1])[0]
            if len(self.dct) > 1:
                print(f'Ptype: {_type} => {self.dct}')
            if self.dct.get('status'):
                self.reset_effects()
                # import ipdb; ipdb.set_trace()
            if self.dct.get('0x9'):
                self.fix_items()
            # print(self.state.me.dct)


async def artificial_status(state, writer):
    while True:
        await asyncio.sleep(1)
        if writer.is_closing():
            return
        if state.safe:
            continue
        me = state.me.entry
        mask = '!BQHIIIHBI'
        pl = struct.pack(
            mask, 85, state.ts + 1, 1, me.id, me.x_pos, me.y_pos, 1, 0x1d, state.good_status
        )
        print(f'Write pl: {pl}')
        writer.write(pl)


def decode_object(obj):
    dct = {}
    if obj.num_fields == 0:
        return dct
    for kv in obj.dct:
        key = kv.key
        dct_key, dct_value = MAPPING.get(key, (hex(key), 'value'))
        dct[dct_key] = getattr(kv.value, dct_value)
        if dct[dct_key] == 0xffffffff:
            dct[dct_key] = 'empty'
    return dct


def handle_my_stats(payload, dct):
    print(dct)
    if 'SPD' not in dct:
        return payload
    search_for = struct.pack('!BIBI', 0x14, dct['ATT'], 0x15, dct['DEF'])
    struct_idx = payload.index(search_for)
    assert struct_idx > 0, 'Cannot find struct'

    def replace(_key, name, new_value):
        old = struct.pack('!BI', _key, dct[name])
        new = struct.pack('!BI', _key, new_value)
        idx = payload.find(old, struct_idx)
        payload[idx : idx + 5] = new

    count = 40
    replace(0x16, 'SPD', 75)
    for i in chain([0x1c]):
        count += 1
        name = MAPPING[i][0]
        replace(i, name, 180)
    return payload


def analyze_objects(state, payload):
    payload = bytearray(payload)
    _type = struct.unpack('!B', payload[:1])[0]
    if _type not in (79, 85):
        print(f'Wrong packet in analyze_objects: {_type}')
    obj = log_unpack(state, unpackers[_type], payload)
    if not obj:
        return bytes(payload)
    # print('ok packet')
    if hasattr(obj, 'ts'):
        state.ts = obj.ts
    if obj.num_entries > 0:
        for entry in obj.entries:
            GameObject(state, entry, payload)
    if hasattr(obj, 'end_entity'):
        other_dct = decode_object(obj.end_entity)
        if other_dct:
            payload = handle_my_stats(payload, other_dct)
    return bytes(payload)


def log_unpack(state, unpacker, payload, log_all=False):
    if log_all:
        save_packet(state, payload)
    try:
        return unpacker.from_bytes(payload)
    except Exception:
        # print('nok packet')
        if not log_all:
            save_packet(state, payload)


def main():
    state = new_state(is_test=True)
    for fname in glob.glob('packets/*.rotf85'):
        with open(fname, 'rb') as f:
            payload = f.read()
            analyze_objects(state, payload)


if __name__ == '__main__':
    main()
