meta:
  id: rotf82
  file-extension: rotf82
  endian: be
  encoding: ascii

seq:
  - id: p_type
    type: u1
  - id: unk
    size: 7
  - id: pos_x
    type: u4
  - id: pos_y
    type: u4
  - id: angle
    type: f4
  - id: rest
    size-eos: true
