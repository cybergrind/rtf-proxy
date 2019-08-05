meta:
  id: rotf59
  file-extension: rotf59
  endian: be
  encoding: ascii

seq:
  - id: p_type
    type: u1
  - id: ts
    type: u4
  - id: pos_x
    type: f4
  - id: pos_y
    type: f4
  - id: inv_id
    type: u4
  - id: idx
    type: u1
  - id: item
    type: u4
  - id: who_pickup
    type: u4
  - id: target_slot
    type: u1
  - id: magic_ffff
    type: u4
  - id: rest
    size-eos: true