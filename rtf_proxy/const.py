from enum import Flag, IntEnum, auto
from itertools import chain


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

# SLOTS + BAG
SLOTS = list(
    zip(
        chain(range(0xc, 0x14), range(0x47, 0x50)),
        range(4, 20)
    ),
)
# SLOTS = list(range(0xc, 0x14))


class ITEM(IntEnum):
    ATT = 0xa1f
    DEF = 0xa20
    SPD = 0xa21
    VIT = 0xa34
    WIS = 0xa35
    DEX = 0xa4c
    HP = 0xae9
    MANA = 0xaea
    SKULL_TORMENT = 0x911
    SKULL_CHOCO = 0x568a
    POTION_CRATE = 0x533f
    ITEM_CRATE = 0x533e

    @staticmethod
    def get(value):
        try:
            return ITEM(value)
        except Exception:
            return value

I = ITEM
SKILL = [I.SKULL_CHOCO, I.SKULL_TORMENT]
AUTOUSE = [I.POTION_CRATE, I.ITEM_CRATE, I.VIT, I.WIS, I.DEF]
AUTOPICKUP = [I.SPD, I.ATT, I.MANA, I.HP, I.DEX]
AUTOUSE_ON_FULL = [I.SPD, I.ATT, I.MANA, I.HP, I.DEX]
