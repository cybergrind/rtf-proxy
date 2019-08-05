meta:
  id: rotf82
  file-extension: rotf82
  endian: be
  encoding: ascii

seq:
  - id: p_type
    type: u1
  - id: unk_b
    type: u1
  - id: shot_id
    type: u2
  - id: unk
    size: 4
  - id: pos_x
    type: f4
  - id: pos_y
    type: f4
  - id: angle
    type: f4
  - id: rest
    size-eos: true
