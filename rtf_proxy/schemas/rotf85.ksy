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
      - id: obj_next
        type: u2
        enum: objs
      - id: nxtobj
        type:
          switch-on: obj_next
          cases:
            "objs::dummy": dummy
            "objs::type_26": player
            "objs::type_02": type_02
            "objs::type_01": type_01
            "objs::type_06": type_06
            "objs::type_04": type_04
  player:
    seq:
      - id: some_nu
        type: u1
      - id: name_len
        type: u2
      - id: name
        type: str
        size: name_len
      - id: s7
        size: 7
      - id: clan_len
        type: u1
      - id: clan_name
        type: str
        size: clan_len
      - id: i_3f
        type: u1
      - id: after_3f
        type: u4
      - id: some_short
        type: u2
      - id: num_size
        type: u1
      - id: size
        type: str
        size: num_size
      - id: magic_7c
        type: u1
      - id: after_7c
        type: u4
      - id: magic_07
        type: u1
      - id: after_07
        type: u4
      - id: magic_1e
        type: u4
      - id: unkown_s1
        type: u2
      - id: magic_0
        type: u4
      - id: magic_21
        type: u2
      - id: magic_50
        type: u4
      - id: unknown_i1
        type: u4
      - id: magic_27
        type: u2
      - id: unknown_i2
        type: u4
      - id: magic_0001
        type: u4
      - id: magic_68000000
        type: u4
      - id: magic_00040000
        type: u4
      - id: unk_byte
        type: u1
      - id: unk_s2
        type: u2
      - id: unknown_i3
        type: u4
      - id: magic_08
        type: u1
      - id: magic_s_00
        type: u2
      - id: unknown_s3
        type: u2
      - id: magic_09
        type: u1
      - id: unknown_i4
        type: u4
      - id: magic_0a
        type: u1
      - id: unknown_i5
        type: u4
      - id: magic_0b
        type: u1
      - id: unknown_i6
        type: u4
      - id: magic_00_2
        type: u1
      - id: unknown_s7
        type: u2
      - id: hp
        type: u2
      - id: magic_03
        type: u1
      - id: unknown_s8
        type: u2
      - id: mana
        type: u2
      - id: magic_2e000000
        type: u4
      - id: unknown_i9
        type: u4
      - id: unknown_i10
        type: u4
      - id: magic_60
        type: u4
      - id: magic_00000000_3
        type: u4
        # terminator: [0x60, 0, 0, 0, 0]
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
  type_06:
    seq:
      - id: name
        type: yyyy_ended
      - id: unk
        size: 16
  type_04:
    seq:
      - id: name
        type: yyyy_ended
      - id: magic_6401
        if: name.yyyy_switch == yyyy::yyyy
        type: u2
      - id: magic_00
        if: name.yyyy_switch == yyyy::yyyy
        type: u4
  yyyy_ended:
    seq:
      - id: yyyy_switch
        type: u1
        enum: yyyy
      - id: yyyy_data
        type:
          switch-on: yyyy_switch
          cases:
            'yyyy::yyyy': yyyy_name
            'yyyy::dummy': dummy_yyyy
  dummy_yyyy:
    seq:
      - id: unk
        size: 19
  yyyy_name:
    seq:
      - id: name_size
        type: u2
      - id: name
        type: str
        size: name_size
      - id: magic_3d
        type: u1
      - id: magic_ffff
        type: u4
      - id: magic_02
        type: u4
  dummy: {}
enums:
  yyyy:
    0x1f: yyyy
    1: dummy
  objs:
    0: dummy
    0x1a: type_26
    0x18: type_26
    1: type_01
    2: type_02
    6: type_06
    4: type_04
    
