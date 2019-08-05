meta:
  id: rotf49
  file-extension: rotf49
  endian: be
  encoding: ascii

seq:
  - id: p_type
    type: u1
  - id: ts
    type: u4
  - id: storage_id
    type: u4
  - id: idx
    type: u1
  - id: itm
    type: u4
  - id: pos_x
    type: f4
  - id: pos_y
    type: f4
  - id: byte
    type: u1
  - id: rest
    size-eos: true
