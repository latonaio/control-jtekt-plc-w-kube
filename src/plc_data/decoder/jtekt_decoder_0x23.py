#!/usr/bin/env python3
# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

from .jtekt_decoder import JtektPlcDataMulti 

ADDR_SIZE = 2
DATA_SIZE = 2

class PlcData(JtektPlcDataMulti):

    def __init__(self, req, res):
        super().__init__(req, res)

    def to_array(self):
        addr_num = int(len(self.head_binary)/ADDR_SIZE)
        array_list = []

        for i in range(addr_num):
            bit_value = self.binary[i*DATA_SIZE:(i+1)*DATA_SIZE][::-1]
            array_list.append({
                "Word": int(bit_value.hex(), 16),
            })
        return array_list

    @staticmethod
    def generate_binary(data):
        body_bytes = b''
        for row in data:
            array_no = row.get("ArrayNo")
            word = None
            if row.get("Word"):
                word = int(row.get("Word"), 2)
            elif row.get("Value"):
                word = int(row.get("Value"))

            if array_no is not None and word is not None:
                body_bytes += bytes.fromhex(array_no)[::-1]
                body_bytes += word.to_bytes(2, 'little')
        return body_bytes

