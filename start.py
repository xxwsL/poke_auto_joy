import argparse
import asyncio
import logging
import os
from contextlib import contextmanager
import calendar

from joycontrol import logging_default as log
from joycontrol.controller_state import ControllerState, button_push
from joycontrol.protocol import controller_protocol_factory, Controller
from joycontrol.server import create_hid_server

import real_key as rk
import auto_joy 

logger = logging.getLogger(__name__)


async def _main(controller, date_list, capture_file=None, spi_flash=None):
    factory = controller_protocol_factory(controller, spi_flash=spi_flash)
    transport, protocol = await create_hid_server(factory, 17, 19, capture_file=capture_file)
    
    dr = protocol.get_controller_state()
    while 1:
        if await dr.connect():
            print("蓝牙连接成功......")
            break
    
    mAutoJoy = auto_joy.AutoJoy (dr, date_list[0], date_list[1], date_list[2])
    await mAutoJoy.run()


    logger.info('Stopping communication...')
    await transport.close()


if __name__ == '__main__':
    # check if root
    if not os.geteuid() == 0:
        raise PermissionError('Script must be run as root!')

    # setup logging
    log.configure()

    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log')
    parser.add_argument('--spi_flash')
    parser.add_argument('-date')
    args = parser.parse_args()

    controller = Controller.PRO_CONTROLLER

    spi_flash = None
    if args.spi_flash:
    # if 1:
        # with open(args.spi_flash, 'rb') as spi_flash_file:
        with open('output', 'rb') as spi_flash_file:
            spi_flash = spi_flash_file.read()

    # creates file if arg is given
    @contextmanager
    def get_output(path=None):
        """
        Opens file if path is given
        """
        if path is not None:
            file = open(path, 'wb')
            yield file
            file.close()
        else:
            yield None

    date_list = args.date.split('-', 2)
    date_list_num = []
    date_list_num.extend([int(date_list[0]), int(date_list[1]), int(date_list[2])])
    print(date_list_num)
    with get_output(args.log) as capture_file:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_main(controller, date_list_num, capture_file=capture_file, spi_flash=spi_flash))
