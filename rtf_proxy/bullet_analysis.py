import asyncio
import struct
import random
from rtf_proxy.state import new_state
from rtf_proxy.packet_tools import payload_to_packet
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


MULTIPLY_COEFF = 8
SKIP_BASE = set()


async def delay_delete(ids):
    SKIP_BASE.update(ids)
    await asyncio.sleep(10)
    for i in ids:
        if i in SKIP_BASE:
            SKIP_BASE.remove(i)

def multiply_damage(state, payload):
    mask = '!BBHHIB'
    curr = struct.unpack(mask, payload)
    shot_id = curr[2]
    counter = curr[3]
    enemy_id = curr[4]
    if (enemy_id, counter) in SKIP_BASE:
        return payload

    ids = [(enemy_id, counter)]
    enemy_id = curr[4]
    for i in range(MULTIPLY_COEFF):
        new_counter = counter + 1 + i
        if (enemy_id, new_counter) in SKIP_BASE:
            continue
        ids.append((enemy_id, new_counter))
        payload += payload_to_packet(struct.pack(mask, 0x4c, 0, shot_id, new_counter, enemy_id, 0))
    asyncio.create_task(delay_delete(ids))
    return payload


def outcoming_shot(state, payload):
    return payload
    # modify outcoming shot aim
    # doesn't look like server use it, probably only 76 packets are used
    _type = struct.unpack('!B', payload[:1])[0]
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
        'owner_bullet': 0,
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
            # print(f'Btype: {btype}')
            pass

        dmg_idx = 3 + mapping['dmg'] * num_bullets + 2 * n
        dmg = struct.unpack('!H', payload[dmg_idx:dmg_idx + 2])[0]
        if dmg > 55550:
            print(f'Replace dmg: {dmg} => 50')
            payload[dmg_idx:dmg_idx + 2] = b'\x00\x10'  # 50

        count_idx = 3 + mapping['num_bullets'] * num_bullets + 1 * n
        bullets_in_shot = payload[count_idx]
        if payload[count_idx] > 0 and False:
            print(f'Num bullets: {payload[count_idx]}')
            payload[count_idx] = 0

        # disable small + regular bullets
        if dmg < 1 and btype == 0:
            payload[count_idx] = 0
        else:
            # keep one bullet for big one
            # payload[count_idx] = 1
            pass

        def replace(name, what):
            sz = len(what)
            idx = 3 + mapping[name] * num_bullets + sz * n
            payload[idx:idx + sz] = what

        def get(name, sz, mask):
            idx = 3 + mapping[name] * num_bullets + sz * n
            return struct.unpack(mask, payload[idx:idx + sz])[0]

        owner = get('owner', 4, '!I')
        owner_bullet = get('owner_bullet', 1, '!B')
        dmg = get('dmg', 2, '!H')
        # assert dmg < 300, payload
        bullets = {}
        for i in range(owner_bullet, owner_bullet + bullets_in_shot):
            # handle short
            if i > 255:
                i = i - 256
            bullets[i] = dmg
        state.add_bullets(owner, bullets)

    return bytes(payload)


def process_hit_ack(state, payload):
    """
    35
    """
    _type, bullet_id, owner_id = struct.unpack('!BBI', payload)
    if owner_id not in state.enemies:
        print(f'Cannot find owner: {owner_id}')
        # raise Exception(payload)
        return
    enemy = state.enemies[owner_id]
    if bullet_id not in enemy.bullets:
        if len(enemy.bullets) == 0:
            print(f'Cannot find any bullets. Skip: {payload} => {enemy.dct} {enemy} / {bullet_id}')
            # raise Exception
            # return
        print(f'Cannot find bullet: {bullet_id} in {enemy}. Use: {payload}')
        bullet_dmg = 300  # no bullet dmg
    else:
        bullet_dmg = enemy.bullets[bullet_id]
    state.add_expected_dmg(bullet_dmg)
    print(f'Expected dmg bullet: {bullet_dmg} => Total: {state.expected_dmg} hp: {state.hp}')


def process_aoe_dmg(state, payload):
    """
    98 - out notification
    36 - all in damage
    """
    _type = struct.unpack('!B', payload[:1])[0]
    if _type == 36:
        assert len(payload) == 15
        dmg = payload[7]
        _type, landed_on, flag, dmg, some_short, from_who, some_flag2 = struct.unpack('!BIHBHIB', payload)
        # print(f'ME: {state.me.entry.id} => TGT: {landed_on} F: {flag} DMG: {dmg} SS: {some_short} OWN: {from_who} F2: {some_flag2}')
        if landed_on != state.me.entry.id:
            return
        state.calc_burst(dmg)
        # state.add_expected_dmg(dmg)
        # state.aoe.update({'time': time.time(), 'dmg': dmg})
    elif _type == 98:
        if state.possible_aoe:
            dmg = state.possible_aoe
            state.add_expected_dmg(dmg)
        else:
            if state.hp_delta < 0:
                # print(f'Old AOE DMG: {payload} Use delta: {state.hp_delta}')
                state.add_expected_dmg(-state.hp_delta)
            else:
                # print(f'Old AOE DMG: {payload} Cannot use hp_delta: {state.hp_delta}')
                state.add_expected_dmg(state.prev_damage)
    elif _type == 8:
        # AOE ACK
        # print('type 8')
        dmg = struct.unpack('!H', payload[15:17])[0]
        # print(f'AOE Ack dmg with packet: {dmg}')
        state.add_expected_dmg(dmg)


def process_aoe_shot(state, payload):
    dmg = struct.unpack('!H', payload[13:15])[0]


def main():
    import sys
    state = new_state(is_test=True)
    with open(sys.argv[1], 'rb') as f:
        payload = f.read()
        process_bullet(state, payload)


if __name__ == '__main__':
    main()
