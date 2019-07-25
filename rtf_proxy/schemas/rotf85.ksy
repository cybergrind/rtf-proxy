meta:
  id: rotf85
  file-extension: rotf85
  endian: be
  encoding: ascii

seq:
  - id: p_type
    type: u1
  - id: ts
    type: u8
  - id: num_objs
    type: u2
  - id: objects
    type: obj_info
    repeat: expr
    repeat-expr: num_objs
  - id: rest
    size-eos: true
    
types:
  obj_info:
    meta:
      title: TTTT
    seq:
      - id: id
        type: u4
      - id: x_pos
        type: u4
      - id: y_pos
        type: u4
      - id: obj_type
        type: u2
      - id: object
        type:
          switch-on: obj_type
          cases:
            0: dummy
            0x1a: player
            0x18: player
            2: type_02
            1: type_01
            6: type_06
            4: type_04
            3: type_03
            8: type_08
            9: type_09
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
  type_01:
    seq:
      - id: some_id
        type: u1
      
      - id: unkn
        type:
          switch-on: some_id
          cases:
            4: t_01_04
            1: t_01_01
  type_02:
    seq:
      - id: unk
        size: 10
  t_01_04:
    seq:
      - id: unk
        size: 4
  t_01_01:
    seq:
      - id: unk
        size: 4
  type_03:
    seq:
      - id: unk
        size: 15
        
  type_08:
    seq:
      - id: unk
        size: 40
        
  type_09:
    seq:
      - id: unk
        size: 45
  type_06:
    seq:
      - id: name_indicator_1f
        contents: [0x1f]
      - id: name
        type: sized_name
      - id: indicator_3d
        type: u1
      - id: value_3d
        type: u4
      - id: indicator_02
        type: u1
      - id: value_02
        type: u4
      - id: indicator_01
        type: u1
      - id: value_01
        type: u4
      - id: indicator_1d
        type: u1
      - id: value_1d
        type: u4
      - id: indicator_60
        type: u1
      - id: value_60
        type: u4
  sized_name:
    seq:
      - id: size
        type: u2
      - id: name
        type: str
        size: size
  type_04:
    seq:
      - id: switch
        type: u1
      - id: content
        type:
          switch-on: switch
          cases:
            0x1f: type_04_named
            1: type_04_dummy
  type_04_dummy:
    seq:
      - id: dummy
        size: 19
  type_04_named:
    seq:
      - id: name
        type: sized_name
      - id: indicator_3d
        type: u1
      - id: value_3d
        type: u4
      - id: indicator_02
        type: u1
      - id: value_02
        type: u4
      - id: indicator_01
        type: u1
      - id: value_01
        type: u4
  dummy: {}
    
