meta:
  id: rotf79
  file-extension: rotf79
  endian: be
  encoding: ascii

seq:
  - id: p_type
    type: u1
  - id: maybe_size
    type: u2
  - id: maybe_terrain_info
    type: unk
    repeat: expr
    repeat-expr: maybe_size
  - id: num_entries
    type: u2
  - id: entry
    type: entry
    repeat: expr
    repeat-expr: num_entries
  - id: unk_s00
    type: u2
  - id: switch
    type: u2
  - id: some_int_when_03
    if: switch == 0x3
    type: u4
  - id: indicator_06
    if: switch == 0x02
    type: u1
  - id: value_06
    if: switch == 0x02
    type: u4
  - id: magic_6300
    type: u2
  - id: indicator_04
    type: u1
  - id: magic_31293139
    type: u4
    
types:
  unk:
    seq:
      - id: unk_s
        type: u2
      - id: unk_s2
        type: u2
      - id: unk_s3
        type: u2
  entry:
    seq:
      - id: some_short
        type: u2
      - id: id
        type: u4
      - id: pos_x
        type: u4
      - id: pos_y
        type: u4
      - id: obj_type
        type: u2
      - id: dungeon
        if: obj_type == 0x05
        type: dungeon_info
      - id: enemy
        if: obj_type == 0x07
        type: enemy_info
      - id: player
        if: obj_type == 0x1a
        type: player
      - id: player_18
        if: obj_type == 0x18
        type: player
      - id: terrain
        if: obj_type == 0x04
        type: terrain
  terrain:
    seq:
      - id: name_indicator_1f
        type: u1
      - id: name
        type: sized_str
      - id: indicator_02
        type: u1
      - id: value_02
        type: u4
      - id: some_indicator_01
        type: u1
      - id: somve_value_01
        type: u4
      
  dungeon_info:
    seq:
      - id: name_indicator_1f
        type: u1
      - id: dung_name
        type: sized_str
      - id: indicator_02
        type: u1
      - id: value_02
        type: u4
      - id: indicator_01
        type: u1
      - id: value_01
        type: u4
      - id: indicator_00
        type: u1
      - id: value_00
        type: u4
  enemy_info:
    seq:
      - id: name_indicator_1f
        type: u1
      - id: enemy_name
        type: sized_str
      - id: indicator_02
        type: u1
      - id: value_02
        type: u4
      - id: indicator_01
        type: u1
      - id: value_01
        type: u4
      - id: indicator_15
        type: u1
      - id: value_15
        type: u4
      - id: indicator_76
        type: u1
      - id: value_76
        type: u4
      - id: indicator_00
        type: u1
      - id: value_00
        type: u4
  sized_str:
    seq:
      - id: size
        type: u2
      - id: name
        type: str
        size: size
      - id: sometimes_yyyy
        size: 5
  player:
    seq:
      - id: name_indicator_1f
        type: u1
      - id: name_len
        type: u2
      - id: name
        type: str
        size: name_len
      - id: indicator_01
        type: u1
      - id: value_01
        type: u4
      - id: clan_indicator_3e
        type: u1
      - id: clan_len
        type: u2
      - id: clan_name
        type: str
        size: clan_len
      - id: indicator_3f
        type: u1
      - id: value_3f
        type: u4
      - id: some_short
        type: u2
      - id: num_size
        type: u1
      - id: size
        type: str
        size: num_size
      - id: indicator_7c
        type: u1
      - id: value_7c
        type: u4
      - id: indicator_07
        type: u1
      - id: value_07
        type: u4
      - id: indicator_1e
        type: u1
      - id: value_1e
        type: u4
      - id: indicator_20
        type: u1
      - id: value_20
        type: u4
      - id: indicator_21
        type: u1
      - id: value_21
        type: u4
      - id: indicator_50
        type: u1
      - id: value_50
        type: u4
      - id: indicator_27
        type: u1
      - id: value_27
        type: u4
      - id: indicator_38
        type: u1
      - id: value_38
        type: u4
      - id: indicator_68
        type: u1
      - id: value_68
        type: u4
      - id: indicator_04
        type: u1
      - id: value_04
        type: u4
      - id: indicator_62
        type: u1
      - id: avlue_62
        type: u4
      - id: indicator_08
        type: u1
      - id: value_08
        type: u4
      - id: indicator_09
        type: u1
      - id: value_09
        type: u4
      - id: indicator_0a
        type: u1
      - id: value_02
        type: u4
      - id: indicator_0b
        type: u1
      - id: value_0b
        type: u4
      - id: hp_indicator_00
        type: u1
      - id: hp
        type: u4
      - id: mp_indicator_03
        type: u1
      - id: mana
        type: u4
      - id: some_indicator_2e
        type: u1
      - id: some_value_2e
        type: u4
      - id: some_indicator_2f
        type: u1
      - id: some_value_2f
        type: u4
      - id: additional
        if: _parent.obj_type == 0x1a
        type: player_additional
  player_additional:
    seq:
      - id: some_indicator_01
        type: u1
      - id: somve_value_01
        type: u4
      - id: indicator_60
        type: u1
      - id: value_60
        type: u4