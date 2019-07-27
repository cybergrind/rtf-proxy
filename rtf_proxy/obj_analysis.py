import glob
import asyncio
import struct
from rtf_proxy.structs.rotf85 import Rotf85
from rtf_proxy.structs.rotf79 import Rotf79
from rtf_proxy.packet_tools import save_packet
from rtf_proxy.state import new_state


unpackers = {
    79: Rotf79,
    85: Rotf85
}

look_name = 'cybergind'


class GameObject:
    mapping = {
        0x1f: ('name', 'name'),
        0x3e: ('clan', 'name'),
        0x26: ('0x26', 'name'),
        0x00: ('max_hp', 'value'),
        0x01: ('hp', 'value'),
        0x03: ('max_mp', 'value'),
        0x04: ('mp', 'value'),
    }

    def __init__(self, state, entry):
        self.state = state
        self.entry = entry
        self.dct = {}
        self.decode_object(entry.object)

    def decode_object(self, obj):
        if obj.num_fields == 0:
            return
        for kv in obj.dct:
            key = kv.key
            dct_key, dct_value = self.mapping.get(key, (hex(key), 'value'))
            self.dct[dct_key] = getattr(kv.value, dct_value)
        if self.dct.get('name') == 'cybergrind':
            self.state.me = self

        if self.state.me and self.state.me.entry.id == self.entry.id:
            self.state.me.dct.update(self.dct)
            print(self.dct)
            # print(self.state.me.dct)


def analyze_objects(state, payload):
    _type = struct.unpack('!B', payload[:1])[0]
    if _type not in (79, 85):
        print(f'Wrong packet in analyze_objects: {_type}')
    obj = log_unpack(state, unpackers[_type], payload)
    if not obj:
        return
    # print('ok packet')
    if obj.num_entries > 0:
        for entry in obj.entries:
            GameObject(state, entry)


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
    for fname in glob.glob('packets/*.bin'):
        with open(fname, 'rb') as f:
            payload = f.read()
            analyze_objects(state, payload)


if __name__ == '__main__':
    main()
