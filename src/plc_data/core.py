#!/usr/bin/env python3
# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

import asyncio
import os
from time import sleep
from aion.microservice import main_decorator, Options
from . import send_command

SERVICE_NAME = "control-jtekt-plc-w"
ADDRESS = os.environ.get("PLC_ADDRESS", "192.168.1.2")
PORT = int(os.environ.get("PLC_PORT", 1025))


@main_decorator(SERVICE_NAME, async=True)
def main(opt: Options):
    conn = opt.get_conn()
    num = opt.get_number()
    loop = asyncio.get_event_loop()
    y = send_command.JtektPlcCommunicator(
        SERVICE_NAME, ADDRESS, PORT, loop
    )
    y.start_to_send(conn, num)
