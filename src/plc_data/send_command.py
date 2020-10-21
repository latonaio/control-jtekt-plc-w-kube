#!/usr/bin/env python3
# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

import asyncio
import json
import os
import traceback
from datetime import datetime
from importlib import import_module
from aion.kanban import kanban
from aion.logger import lprint, lprint_exception
from .tcp_packet import SendPacket, RcvPacket
from .tcp_client import TCPClient
from .decoder import JtektPlcDataList
from google.protobuf.json_format import MessageToDict


BUF_SIZE = 4096
DEFAULT_TIMEOUT = 1


class JtektPlcCommunicator:
    def __init__(self, service_name, address, port, loop ):
        self.service_name = service_name
        self.send_queue = asyncio.Queue()
        self.rcv_queue = asyncio.Queue()
        self.address = address
        self.port = port
        self.loop = loop

        self.task_list = {}
        self.data_list = []
        self.timestamp = None

    def start_to_send(self, conn, num):
        asyncio.ensure_future(self.set_queue_by_kanban(conn, num))
        asyncio.ensure_future(self.send_request())
        self.loop.run_until_complete(self.output_status_json(conn))

    async def set_queue_by_kanban(self, conn, num):
        async for kanban in conn.get_kanban_itr(self.service_name, num):
            metadata = kanban.get_metadata()
            #metadata['data'] = MessageToDict(metadata['data'])
            lprint(metadata)

            command = metadata.get("command")
            expire_time = metadata.get("expire_time")

            if expire_time is None:
                lprint(f"there is no expire_time (command:{command})")
                continue
            dec_data_library = import_module(
                "src.plc_data.decoder.jtekt_decoder_0x" + command)
            decoder_class = dec_data_library.PlcData
            header_list = decoder_class.create_request(metadata, decoder_class)
            if header_list is None:
                lprint(f"cant get header data (command:{command})")
                continue
            await self.send_queue.put((command, header_list, decoder_class, expire_time))

    async def send_request(self):
        while True:
            command, header_list, decoder_class, expire_time = await self.send_queue.get()
            if not isinstance(header_list, dict):
                raise TypeError("header to list")
            lprint(f"[client] send to robot: {command}")

            resp_list = []

            async def get_response(wait_func):
                # return : request packet (SendPacket) , response packet (bytes)
                resp_list.append(await wait_func)

            # send all array no
            for array_no, header in header_list.items():
                on_response = self.loop.create_future()
                try:
                    transport, protocol = await self.loop.create_connection(
                        lambda: TCPClient(header, on_response), self.address, self.port)
                except OSError as e:
                    lprint(str(e))
                    continue
                try:
                    await asyncio.wait_for(get_response(on_response), DEFAULT_TIMEOUT)
                except asyncio.TimeoutError:
                    lprint(f"timeout to receive: {header.command.hex()}")
                    pass
                finally:
                    transport.close()
                # safety interval
                await asyncio.sleep(0.1)

            if len(resp_list) == 0:
                continue

            # set to data decoder class
            robot_data_list = decoder_class.create_datalist(resp_list, decoder_class)

            data_list = JtektPlcDataList(
                command, expire_time, robot_data_list)

            await self.rcv_queue.put((data_list, datetime.now().isoformat()))

    async def output_status_json(self, conn):
        while True:
            data_list, timestamp = await self.rcv_queue.get()
            robot_data = data_list.to_json()
            metadata_sets = {
                "RobotData": robot_data,
                "timestamp": timestamp
            }
            await conn.output_kanban(
                result=True,
                metadata=metadata_sets
            )
            lprint(f'[client] output kanban')


