import struct


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

        # disable small bullets
        if dmg < 80:
            payload[count_idx] = 0
        else:
            # keep one bullet for big one
            payload[count_idx] = 1

        def replace(name, what):
            idx = 3 + mapping[name] * num_bullets + 4 * n
            sz = len(what)
            payload[idx:idx + sz] = what

        # replace('pos_x', b'\x00\x00\x00\x00')
        # replace('pos_y', b'\x00\x00\x00\x00')

        # pos_x = 3 + mapping['pos_x'] * num_bullets + 4 * n
        # pos_y = 3 + mapping['pos_y'] * num_bullets + 4 * n
        # payload[pos_x:pos_x + 4] = b'\x00\x00\x00\x00'
        # payload[pos_y:pos_y + 4] = b'\x00\x00\x00\x00'

        # magic = 3 + mapping['magic'] * num_bullets + 4 * n
        # payload[magic:magic + 4] = b'\x00\x00\x00\x00'

    return bytes(payload)
