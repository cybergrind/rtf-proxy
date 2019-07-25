meta:
  id: rotf79
  imports:
    - player
    - base
  file-extension: rotf79
  endian: be
  encoding: ascii

seq:
  - id: p_type
    type: u1
  - id: terrain_size
    type: u2
  - id: maybe_terrain_info
    type: unk
    repeat: expr
    repeat-expr: terrain_size
  - id: num_entries
    type: u2
  - id: entry
    type: entry
    repeat: expr
    repeat-expr: num_entries
  - id: unk_dies
    type: u2
  - id: unk_i4
    type: u4
    repeat: expr
    repeat-expr: unk_dies
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
  - id: value_04
    if: switch == 0x04
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
      - id: object
        type: base