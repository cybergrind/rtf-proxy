import asyncio
import glob
import struct
from enum import Flag, auto

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


class GameObject:
    mapping = {
        0x1f: ('name', 'name'),
        0x3e: ('clan', 'name'),
        0x26: ('0x26', 'name'),
        0x00: ('max_hp', 'value'),
        0x01: ('hp', 'value'),
        0x03: ('max_mp', 'value'),
        0x04: ('mp', 'value'),
        0x1d: ('status', 'value'),
    }

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
        print(
            f'{self.position} : {self.flags_position} => {self.payload[self.position:self.flags_position + 20]}'
        )
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
            dct_key, dct_value = self.mapping.get(key, (hex(key), 'value'))
            self.dct[dct_key] = getattr(kv.value, dct_value)
        if self.entry.id in self.state.enemies and hasattr(self.entry, 'pos_x'):
            self.state.add_enemy(self.entry.id, self.entry.pos_x, self.entry.pos_y, {})
        if self.dct.get('name') == 'cybergrind':
            self.state.set_new_me(self)
            if hasattr(self.entry, 'x_pos'):
                self.state.set_mypos(self.entry.x_pos, self.entry.y_pos)

        """
        status:
        invuln: 16777216
        blind: {'status': 8388608, '0x60': 65536} {'hp': 857, 'status': 128, '0x60': 0}
        silent: 'status': 2,
        slow: status: 8
        0x9 => totem: 22880, medusa: 22351
        Medusa: Ptype: 85 => {'0x8': 2320, '0x9': 22880, '0xa': 2512, '0xb': 2985, 'max_hp': 863, 'max_mp': 490, '0x2e': 240, '0x2f': 105, 'mp': 490}
        Ptype: 85 => {'0x8': 2320, '0x9': 22880, '0xa': 2512, '0xb': 2985, 'max_hp': 863, 'max_mp': 490, '0x2e': 240, '0x2f': 105, 'mp': 490}
Ptype: 85 => {'0x8': 2320, '0x9': 22351, '0xa': 2512, '0xb': 2985, 'max_hp': 863, 'max_mp': 610, '0x2e': 240, '0x2f': 225, 'mp': 492}

        """
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
        pl = struct.pack(mask, 85, state.ts + 1,
                         1, me.id, me.x_pos, me.y_pos, 1, 0x1d,
                         state.good_status)
        print(f'Write pl: {pl}')
        writer.write(pl)


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
    return bytes(payload)


def log_unpack(state, unpacker, payload, log_all=False):
    if log_all:
        save_packet(state, payload)
    try:
        return unpacker.from_bytes(payload)
    except Exception:
        # print('nok packet')
        if False and not log_all:
            save_packet(state, payload)


async def delete_enemy(_id):
    await asyncio.sleep(60)
    del enemies[_id]


def unp75(packet):
    _type, _num = struct.unpack('!BH', packet[:3])
    for i in range(_num):
        # size: 25
        start = 3 + i * 25
        end = 3 + i * 25 + 25
        print_unpack('!BIIIIII', packet[start:end])
        _i, _id, _a, _b, _c, _x, _y = struct.unpack('!BIIIIII', packet[start:end])
        if _id not in enemies:
            enemies[_id] = {'tx': _x, 'ty': _y}
            asyncio.create_task(delete_enemy(_id))
        enemies[_id]['dist'] = dist(_x, _y)


def unp85(packet):
    # 14 each
    # b'U\x00\x00\x02\x9e\x00\x00\x00d\x00\x04\x00\x00\x07\xafBK\xdc5B\xed\x00\x00\x00\x00\x00\x00\x040BM]jB\xe3\xe9\x18\x00\x00\x00\x00\x03\xd2BG\xb0\xf0B\xdfT\x97\x00\x00\x00\x00\x03fBC\xe9\xc3B\xe1\xfa\xaf\x00\x00'
    global pos
    _type, _id, _num = struct.unpack('!BQH', packet[:11])
    # print(f'Num: {_num}')
    start = 11
    for i in range(_num):
        # start = 11 + 14 * i
        end = start + 14
        sub = packet[start:end]
        print(f'Len: {len(sub)} {start}/{end} => {sub}')
        sub = struct.unpack('!IIIH', sub)
        start = end
        print(f'Sub[{i}] => {sub}')
        if sub[3] > 0:
            end = start + sub[3]
            buff = packet[start:end]
            print(f'Buff: {buff} / {start}:{end} = {len(buff)}')
            start = end
        # 292 - ufo
        # 624 -?
        # if 300 < sub[1] < 38:
        #    pos = [sub[2], sub[3]]
    print(f'End: {end} VS {len(packet)}')


def main():
    state = new_state(is_test=True)
    for fname in glob.glob('packets/*.rotf85'):
        with open(fname, 'rb') as f:
            payload = f.read()
            analyze_objects(state, payload)


if __name__ == '__main__':
    main()
