meta:
  id: rotf85
  imports:
    - player
    - base
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
      - id: object
        type: base
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
    
