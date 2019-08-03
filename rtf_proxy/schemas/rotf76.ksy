meta:
  id: rotf76
  file-extension: rotf76
  endian: be
  encoding: ascii

seq:
  - id: p_type
    type: u1
  - id: unk
    type: u1
  - id: shot_id
    type: u2
  - id: counter
    type: u2
  - id: enemy_id
    type: u4
  - id: rest
    size-eos: true
