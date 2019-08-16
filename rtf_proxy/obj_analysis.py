import asyncio
import glob
import struct
import time
from copy import copy

from rtf_proxy import const
from rtf_proxy.const import STATUS
from rtf_proxy.packet_tools import save_packet
from rtf_proxy.state import new_state
from rtf_proxy.structs.rotf79 import Rotf79
from rtf_proxy.structs.rotf85 import Rotf85

unpackers = {79: Rotf79, 85: Rotf85}

look_name = 'cybergind'


class GameObject:
    def __init__(self, state, entry, payload):
        self._position = None
        self.state = state
        self.entry = entry
        self.payload = payload
        self.dct = {}
        self.dist = 1000
        self.updated = time.time()
        self.bullets = {}
        self._obj_type = None
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
    # set_flags = STATUS.DAMAGING | STATUS.SPEEDY | STATUS.BERSERK | STATUS.SPEEDY2
    set_flags = STATUS.DAMAGING | STATUS.BERSERK | STATUS.SPEEDY

    @property
    def msg_type(self):
        if hasattr(self.entry, 'obj_type'):
            return 79
        return 85

    @property
    def obj_type(self):
        if self._obj_type:
            return self._obj_type
        if hasattr(self.entry, 'obj_type'):
            self._obj_type = self.entry.obj_type
            return self.entry.obj_type

    @property
    def type_str(self):
        obj_type = self.obj_type
        if obj_type:
            return str(obj_type)

    @property
    def name(self):
        return self.dct.get('name')

    @property
    def id(self):
        return self.entry.id

    @property
    def pos(self):
        return self.entry.pos_x, self.entry.pos_y

    def __str__(self):
        td = time.time() - self.updated
        return f'<GO {hex(hash(self))}:{self.id} / up: {td:.3f} / d: {self.state.dist(*self.pos)} {self.pos}>'

    @property
    def position(self):
        if self._position:
            return self._position
        if not hasattr(self.entry, 'pos_x'):
            return
        b = struct.pack('!Iff', self.entry.id, self.entry.pos_x, self.entry.pos_y)
        pos = self.payload.find(b)
        if pos == -1:
            self.state.log_write(f'Cannot find position: {b}')
            self.state.log_write(f'Payload for position: {self.payload}')
            return
        self._position = pos
        return self._position

    @property
    def status(self):
        return STATUS(self.dct.get('status', 0))

    def fix_items(self):
        if not hasattr(self.entry, 'pos_x') or not self.dct['0x9']:
            return
        return
        spack = struct.pack('!BI', 0x9, self.dct['0x9'])
        location = self.payload.find(spack, self.position)
        assert self.payload[location : location + 5] == spack, spack
        new_item = 2730
        if self.dct['0x9'] != new_item:
            self.state.log_write(f'Replace skull: {self.dct["0x9"]} => {new_item}')
            self.payload[location : location + 5] = struct.pack('!BI', 0x9, new_item)

    def reset_effects(self):
        if not hasattr(self.entry, 'pos_x'):
            # print(f'No pos effect: {STATUS(self.dct["status"])}')
            return
        # print(f'{STATUS(self.dct["status"])}')
        if not self.position:
            return

        spack = struct.pack('!BI', 0x1d, self.dct['status'])
        self.flags_position = self.payload.find(spack, self.position)
        if self.flags_position == -1:
            self.state.log_write(
                f'Flags position = -1: {spack} / {self.position} / {self.id}\n {self.payload}'
            )
            raise NotImplementedError
        status = STATUS(self.dct['status'])
        new_status = ((status & self.reset_flags) | self.set_flags).value
        self.state.good_status = new_status
        if self.dct['status'] != new_status:
            # print(f'Replace status: {status} => {STATUS(new_status)}')
            self.state.log_write(f'Update status: {self.flags_position}')
            self.payload[self.flags_position : self.flags_position + 5] = spack = struct.pack(
                '!BI', 0x1d, new_status
            )

    def decode_object(self, obj):
        self.dct = decode_object(obj)
        self.real_dct = self.dct.copy()

        self.state.add_object(self)

        if self.id in self.state.enemies:
            self.state.add_enemy(self)

        if self.msg_type == 79:
            if self.state.is_enemy(self):
                self.state.add_enemy(self)

        if obj.num_fields == 0:
            return

        name = self.dct.get('name')
        add_bag = True
        if name and name.endswith('/8'):
            if hasattr(self.entry, 'obj_type'):
                self.move_object()
                self.state.add_bag(self)
                add_bag = False
                # print(f'Got bag entry: {self.dct} => Type: {hex(self.entry.obj_type)} {bin(self.entry.obj_type)} EID: {self.entry.id}')

        if name == 'cybergrind':
            self.state.set_new_me(self)
            if hasattr(self.entry, 'pos_x'):
                self.state.set_mypos(self.entry.pos_x, self.entry.pos_y)

        if self.entry.id in self.state.bags and add_bag:
            self.move_object()
            self.state.add_bag(self)

        if self.state.me and self.state.me.entry.id == self.entry.id:
            self.state.update_me_dct(self.dct)
            # _type = struct.unpack('!B', self.payload[:1])[0]
            # if len(self.dct) > 2:
            #     print(f'Ptype: {_type} => {self.dct}')
            if self.real_dct.get('status'):
                self.reset_effects()
                # import ipdb; ipdb.set_trace()
            if self.real_dct.get('0x9'):
                self.fix_items()
            # print(self.state.me.dct)

        raw = self.dct.raw
        if (
            0x1f in raw
            and 0x3d in raw
            and 0x2 in raw
            and raw[0x3d] == 0xffffffff
            and raw[0x2] == 0x64
        ):
            self.process_location(obj)

    def move_object(self, delta=1.5):
        _id = self.entry.id
        pos_x = self.entry.pos_x
        pos_y = self.entry.pos_y
        to_replace = struct.pack('!Iff', _id, pos_x, pos_y)
        new_location = struct.pack('!Iff', _id, pos_x + delta, pos_y + delta)
        self.payload = self.payload.replace(to_replace, new_location)
        self.state.log_write('Move object')

    def process_location(self, obj):
        # print(f'GOT LOCATION => {self.dct["name"]} => {self.dct} [{self.entry.pos_x} / {self.entry.pos_y}]')
        return

    def update_from_old(self, old_obj):
        if not self.obj_type and old_obj.obj_type:
            self._obj_type = old_obj.obj_type

        dct = old_obj.dct
        dct.update(self.dct)
        self.dct.update(dct)
        if old_obj.name:
            assert self.name
        # if self.id in self.state.enemies and self.dist < 20:
        #     print(f'Update from old: {self} <= {old_obj} : {self.dct}')
        assert len(self.dct) >= len(old_obj.dct), f'{self.dct} vs {old_obj.dct}'


async def artificial_status(state, writer):
    while True:
        await asyncio.sleep(1)
        if writer.is_closing():
            return
        if state.safe:
            continue
        me = state.me.entry
        mask = '!BQHIffHBI'
        pl = struct.pack(
            mask, 85, state.ts + 1, 1, me.id, me.pos_x, me.pos_y, 1, 0x1d, state.good_status
        )
        print(f'Write pl: {pl}')
        writer.write(pl)


class MyDict(dict):
    def update(self, what):
        super().update(what)
        self.raw.update(what.raw)

    def copy(self):
        ret = MyDict(copy(self))
        ret.raw = copy(self.raw)
        return ret


def decode_object(obj):
    dct = MyDict()
    dct.raw = {}
    if obj.num_fields == 0:
        return dct
    for kv in obj.dct:
        key = kv.key
        dct_key, dct_value = const.MAPPING.get(key, (hex(key), 'value'))
        if hasattr(kv.value, dct_value):
            value = raw_value = getattr(kv.value, dct_value)
        else:
            value = raw_value = None
        if dct_key == 'max_hp':
            if value > 19293798:
                dct[dct_key] = raw_value
                dct.raw[key] = raw_value
                continue
        if 'bag_' in dct_key or 'slot_' in dct_key or 'item_' in dct_key:
            value = const.ITEM.get(raw_value)
        dct[dct_key] = value
        if dct[dct_key] == 0xffffffff:
            dct[dct_key] = 'empty'
        dct.raw[key] = raw_value
    return dct


def find_last(payload, what):
    idx = -10
    while True:
        found = payload.find(what, idx + 10)
        # print(f'Found {found}')
        if found == -1:
            break
        idx = found
    return idx


def handle_my_stats(state, payload, dct):
    # print(dct)
    if 'SPD' not in dct:
        return payload
    search_for = struct.pack('!BIBI', 0x14, dct['ATT'], 0x15, dct['DEF'])
    struct_idx = find_last(payload, search_for)
    if struct_idx == -1:
        return payload
    assert struct_idx > 0, 'Cannot find struct'

    def replace(_key, name, new_value):
        old = struct.pack('!BI', _key, dct[name])
        new = struct.pack('!BI', _key, new_value)
        idx = payload.find(old, struct_idx)
        payload[idx : idx + 5] = new

    state.log_write('Update stats')
    replace(0x16, 'SPD', 96)
    replace(0x1c, 'DEX', min(dct['DEX'] + 25, 240))
    # replace(0x1b, 'WIS', min(dct['WIS'] + 300, 840))
    return payload


def handle_my_inventory(payload, dct):
    if 'slot_1' not in dct:
        return payload
    return payload


def analyze_objects(state, payload):
    payload = bytearray(payload)
    _type = struct.unpack('!B', payload[:1])[0]
    if _type not in (79, 85):
        print(f'Wrong packet in analyze_objects: {_type}')
        raise NotImplementedError
    obj = log_unpack(state, unpackers[_type], payload)
    if not obj:
        raise NotImplementedError
        return bytes(payload)
    # print('ok packet')
    if hasattr(obj, 'ts'):
        state.__ts = obj.ts
    if obj.num_entries > 0:
        for entry in obj.entries:
            o = GameObject(state, entry, payload)
            payload = o.payload
    if hasattr(obj, 'end_entity'):
        other_dct = decode_object(obj.end_entity)
        if other_dct:
            state.log_write(f'New end_entity: {other_dct}')
            dct_w = {}
            for k, v in other_dct.items():
                if 'bag_' in k or 'slot_' in k or 'item_' in k:
                    if not isinstance(v, const.ITEM) and v != 'empty':
                        dct_w[k] = v
            if dct_w:
                state.log_write('unk_dct:')
                for k, v in dct_w.items():
                    state.log_write(f'    {k} = {v}')
            state.update_me_dct(other_dct)
            payload = handle_my_stats(state, payload, other_dct)
            payload = handle_my_inventory(payload, other_dct)
    if _type == 79:
        # 0503 => violet bag
        # 0504 => small chest in vault
        # 0505 => purchase chest
        # 0506 => pink bag
        # 0507 => violet bag
        # 0508 => basket
        # 0509 => potion bag (light blue)
        # 050b => blue bag
        # 050e => yellow bag
        # 0523 => regular bag
        # 06db => blue big
        if obj.gone_object_ids:
            state.remove_entities(obj.gone_object_ids)
        if b'0/8' in payload:
            print(f'Replace => 0/8 => 8/8: ME: {state.me.entry.id}')
            # payload = payload.replace(b'\x05\x03', b'\x78\x08')
    return bytes(payload)


def log_unpack(state, unpacker, payload, log_all=False):
    if log_all:
        save_packet(state, payload)
    try:
        return unpacker.from_bytes(payload)
    except Exception:
        print('nok packet')
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
