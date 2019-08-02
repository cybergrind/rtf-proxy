import struct
import random


counter = 0
skip = []


def bullet_double(payload):
    # cannot manipulate with landed values
    global skip
    unpack_mask = '!BBHHIB'
    mask = '!IBBHHIB'
    repeat = 2
    _4c, _0, shot_id, counter, enemy_id, _ = struct.unpack(unpack_mask, payload)
    if counter in skip:
        return
    skip = skip[-20:]
    for i in range(repeat):
        counter += 1
        if counter in skip:
            continue
        skip.append(counter)
        payload += struct.pack(mask, 11, 0x4c, 0, shot_id, counter, enemy_id, 0)
    return payload


def gen_76(shot_id, enemy_id):
    global counter
    mask = '!IBBHHIB'
    repeat = 4
    out = []
    counter = random.randint(10000, 63000)
    for i in range(repeat):
        counter += 1
        out.append(struct.pack(mask, 11, 0x4c, 0, shot_id, counter, enemy_id, 0))
    return out


def outcoming_shot(state, payload):
    return payload
    # modify outcoming shot aim
    # doesn't look like server use it, probably only 76 packets are used
    if len(payload) != 24:
        return payload
    payload = bytearray(payload)
    _type, _, shot_id, _, pos_x, pos_y, angle, _ = struct.unpack('!BBHIIIfI', payload)
    aim = state.aim_closest()
    if aim:
        new_x, new_y, angle, enemy = aim
        payload[8:8 + 4*3] = struct.pack('!IIf', new_x, new_y, angle)
        print(f'{pos_x} x {pos_y} VS {state.mypos} {struct.unpack("!IIf", payload[8:8+4*3])}')
        # confirmations = gen_76(shot_id, enemy['id'])
        # for c in confirmations:
        #     payload += c
    return payload


def process_bullet(state, payload):
    num_bullets = struct.unpack('!H', payload[1:3])[0]
    # non multiplied
    # type + num = 3 bytes
    # multiplied
    # owner bullet + 1, owner + 4, eff + 1, shot_id + 4, damage + 2, num bullets inside shot ? + 1
    # magic + 4, coords + 8
    # num_bullets start pos: 11
    payload = bytearray(payload)

    mapping = {
        'owner': 1,
        'zero_idx': 5,
        'shot_id': 6,
        'dmg': 10,
        'num_bullets': 12,
        'magic': 13,
        'pos_x': 17,
        'pos_y': 21,
    }
    for n in range(num_bullets):
        zero_idx = 3 + mapping['zero_idx'] * num_bullets + 1 * n
        # btype: 0 - regular
        btype = payload[zero_idx]
        if btype not in (0, 1):
            # payload[zero_idx] = 1
            print(f'Btype: {btype}')
            pass

        dmg_idx = 3 + mapping['dmg'] * num_bullets + 2 * n
        dmg = struct.unpack('!H', payload[dmg_idx:dmg_idx + 2])[0]
        if dmg > 55550:
            print(f'Replace dmg: {dmg} => 50')
            payload[dmg_idx:dmg_idx + 2] = b'\x00\x10'  # 50

        count_idx = 3 + mapping['num_bullets'] * num_bullets + 1 * n
        if payload[count_idx] > 0 and False:
            print(f'Num bullets: {payload[count_idx]}')
            payload[count_idx] = 0

        # disable small + regular bullets
        if dmg < 10 and btype == 0:
            payload[count_idx] = 0
        else:
            # keep one bullet for big one
            # payload[count_idx] = 1
            pass

        def replace(name, what):
            idx = 3 + mapping[name] * num_bullets + 4 * n
            sz = len(what)
            payload[idx:idx + sz] = what

        def get(name, sz, mask):
            idx = 3 + mapping[name] * num_bullets + 4 * n
            return struct.unpack(mask, payload[idx:idx + sz])[0]

        # replace('pos_x', b'\x00\x00\x00\x00')
        # replace('pos_y', b'\x00\x00\x00\x00')
        owner = get('owner', 4, '!I')
        pos_x = get('pos_x', 4, '!I')
        pos_y = get('pos_y', 4, '!I')
        state.add_enemy(owner, pos_x, pos_y)
        # payload[pos_x:pos_x + 4] = b'\x00\x00\x00\x00'
        # payload[pos_y:pos_y + 4] = b'\x00\x00\x00\x00'

        # magic = 3 + mapping['magic'] * num_bullets + 4 * n
        # payload[magic:magic + 4] = b'\x00\x00\x00\x00'

    return bytes(payload)
