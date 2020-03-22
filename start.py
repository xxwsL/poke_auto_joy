import argparse, os
import asyncio
import logging
from contextlib import contextmanager
import calendar

from joycontrol import logging_default as log
from joycontrol.controller_state import ControllerState, button_push
from joycontrol.protocol import controller_protocol_factory, Controller
from joycontrol.server import create_hid_server

import real_key as rk
import auto_joy

async def _main(date_list_):
    controller_ = Controller.PRO_CONTROLLER
    factory = controller_protocol_factory(controller_)
    transport, protocol = await create_hid_server(factory, 17, 19)
    
    dr = protocol.get_controller_state()
    while 1:
        if await dr.connect():
            print("蓝牙连接成功......")
            break
    
    mAutoJoy = auto_joy.AutoJoy (dr, date_list_[0], date_list_[1], date_list_[2])
    await mAutoJoy.run()
    logger.info('Stopping communication...')
    await transport.close()

