# -*- coding: UTF-8 -*-
import calendar
import asyncio
from enum import Enum

from joycontrol.controller_state import ControllerState, button_push
import real_key as rk

dHighSp = 0.05
dFastSp = 0.1

dHighDl = 0.05
dFastDl = 0.1

# 任务列表
task_list = [
    ['poke_ID_LuckyDraw', 1000, None],
    ['poke_DigStone', -1, None],
    ['poke_BrushWatt', 640, None],
    ['poke_pass_frame_left', 1000, None],
    ['pass_shiny_frames', 1, 'home_to_set_time']
]


class JoyDirect(Enum):
    Center = 0
    Up = 1
    Down = 2
    Left = 3
    Right = 4
    UpLeft = 5
    UpRight = 6
    DownLeft = 7
    DownRight = 8


class AutoJoy:

    def __init__(self, _dr, _year, _month, _day):

        self.bPause = False
        self.bStop = True

        self.key_ = ''

        self.dr_ = _dr

        self.year_now_ = _year
        self.month_now_ = _month
        self.day_now = _day
        self.all_days = calendar.monthrange(_year, _month)[1]

        self.fun_list = {
            'poke_ID_LuckyDraw': self.poke_ID_LuckyDraw,
            'poke_DigStone': self.poke_DigStone,
            'poke_BrushWatt': self.poke_BrushWatt,
            'poke_pass_frame_left': self.poke_pass_frame_left,
            'pass_shiny_frames': self.pass_shiny_frames,
            'home_to_set_time': self.home_to_set_time
        }

    '''
    switch按健功能
    buttons_  : 'y', 'x', 'b', 'a', 'r', 'zr',
                            'minus', 'plus', 'r_stick', 'l_stick', 'home', 'capture',
                            'down', 'up', 'right', 'left', 'l', 'zl'
    release_sec_ : 延迟多长时间释放按键(单位:s)
    delay_sec_ : 本轮按键操作完毕延迟多长时间(单位:s)
    cycle_nums_ : 重复进行多少次当前按键操作
    '''

    async def press_key(self, buttons_, release_sec_=0.05, delay_sec_=0.0, cycle_nums_=1):
        print('>pass button: %s, cycle_nums:%d' %(buttons_,cycle_nums_))
        for i in range(cycle_nums_):
            while self.bPause:
                print('running pause.....')
            await button_push(self.dr_, buttons_, sec=release_sec_)
            await asyncio.sleep(0.06)
        await asyncio.sleep(delay_sec_)

    # 摇杆动作
    async def stick_l_action(self, direct_, release_sec_=0.05, delay_sec_=0.0):
        if direct_ == JoyDirect.Center:
            self.dr_.l_stick_state.set_center()
        elif direct_ == JoyDirect.Up:
            self.dr_.l_stick_state.set_up()
        elif direct_ == JoyDirect.Down:
            self.dr_.l_stick_state.set_down()
        elif direct_ == JoyDirect.Left:
            self.dr_.l_stick_state.set_left()
        elif direct_ == JoyDirect.Right:
            self.dr_.l_stick_state.set_right()
        elif direct_ == JoyDirect.UpRight:
            self.dr_.l_stick_state.set_up_right()

        await self.dr_.send()
        await asyncio.sleep(release_sec_)

    # 过帧时需要使用时间流来监控时间
    def time_flow_right(self):
        res = 2
        if self.day_now == self.all_days:
            self.day_now = 1
            if self.month_now_ == 12:
                self.month_now_ = 1
                self.year_now_ += 1
                res = 0
            else:
                self.month_now_ += 1
                res = 1
            self.all_days = calendar.monthrange(self.year_now_, self.month_now_)[1]
        else:
            self.day_now += 1
        return res

    # switch home界面到时间设置界面操作模块
    async def home_to_set_time(self):
        await self.press_key('down', dHighSp, dFastDl)
        await self.press_key('right', dHighSp, dFastDl, 4)
        await self.press_key('a', dHighSp, 0.2)
        await self.press_key('down', 1.8, dFastDl)
        await self.press_key('right', dHighSp, dFastDl)
        await self.press_key('down', dHighSp, dFastDl, 4)
        await self.press_key('a', dHighSp, dFastDl)
        await self.press_key('down', dHighSp, dFastDl, 2)
        await self.press_key('a', dHighSp, dFastDl)

    # 以向右的方式过帧
    async def pass_frame_right(self):
        time_index = self.time_flow_right()
        if time_index == 2:
            await self.press_key('right', dHighSp, dFastDl, 2)
            await self.press_key('up', dHighSp, dFastDl)
        elif time_index == 1:
            await self.press_key('right', dHighSp, dFastDl)
            await self.press_key('right', dHighSp, dFastDl)
            await self.press_key('up', dHighSp, dFastDl)
            await self.press_key('left', dHighSp, dFastDl)
            await self.press_key('up', dHighSp, dFastDl)
            await self.press_key('right', dHighSp, dFastDl)
        else:
            await self.press_key('up', dHighSp, dFastDl)
            await self.press_key('right', dHighSp, dFastDl)
            await self.press_key('up', dHighSp, dFastDl)
            await self.press_key('right', dHighSp, dFastDl)
            await self.press_key('up', dHighSp, dFastDl)
        await self.press_key('a', dHighSp, dFastDl, 4)

    # 自动任务
    async def auto_task(self, task_name_, cycle_nums_=1, before=None):
        if before is not None:
            print('--- run before: %s ---' %(before))
            await self.fun_list[before]()
        fun = self.fun_list[task_name_]
        print('--- run task: %s, times: %d---' % (task_name_,cycle_nums_))
        if cycle_nums_ < 0:
            while 1:
                mRk_val = rk.getKey()
                if (mRk_val == 'a'):
                    self.bStop == True
                    break
                await fun()
        else:
            for i in range(cycle_nums_):
                mRk_val = rk.getKey()
                if (mRk_val == 'a'):
                    self.bStop == True
                    break
                await fun()

    '''
    运行
    键盘按键w : 向上选择任务
    键盘按键s  : 向下选择任务
    键盘按键a : 开始或停止任务
    键盘按键e : 退出程序
    '''

    async def run(self):
        await self.press_key('home', 0.1, 1)
        print('start running......')

        task_index = 0
        while 1:
            mRk_val = rk.getKey()
            if mRk_val == 'w':
                if task_index == 0 and len(task_list) > 1:
                    task_index = len(task_list) - 1
                else:
                    task_index = task_index - 1
                print('selecting task: %s times: %d' % (task_list[task_index][0], task_list[task_index][1]))
            elif mRk_val == 's':
                task_index = task_index + 1
                if task_index == len(task_list):
                    task_index = 0
                print('selecting task: %s times: %d' % (task_list[task_index][0], task_list[task_index][1]))
            elif mRk_val == 'a':
                task_list[task_index][1] -= 1
                print('selecting task: %s times: %d' % (task_list[task_index][0], task_list[task_index][1]))
            elif mRk_val == 'd':
                task_list[task_index][1] += 1
                print('selecting task: %s times: %d' % (task_list[task_index][0], task_list[task_index][1]))
            elif mRk_val == 'c':
                task_list[task_index][1] += 100
                print('selecting task: %s times: %d' % (task_list[task_index][0], task_list[task_index][1]))
            elif mRk_val == 'z':
                task_list[task_index][1] -= 100
                print('selecting task: %s times: %d' % (task_list[task_index][0], task_list[task_index][1]))
            elif mRk_val == 'r':
                self.bStop = bool(1 - self.bStop)
            elif mRk_val == 'q':
                print('exiting......')
                break

            if self.bStop == False:
                # await self.stick_l_action(JoyDirect.Right, 5, 1)
                # await self.task_list[2]
                arr = task_list[task_index]
                await self.auto_task(arr[0], arr[1], arr[2])
                self.bStop = True

    # --------------------------------------------------------------------------------------------------#
    # 过闪帧
    async def pass_shiny_frames(self):
        await self.press_key('left', 1, dHighSp)
        await self.pass_frame_right()
        await self.press_key('a', dHighSp, 0.65)

    # ID抽奖
    async def poke_ID_LuckyDraw(self):
        # 移动到时间设置界面
        await self.home_to_set_time()
        # #过帧
        await  self.pass_frame_right()
        # 返回home界面，打开游戏
        await  self.press_key('home', dHighSp, 1.1)
        await  self.press_key('a', dHighSp, 0.65)
        # 返回人物界面
        await  self.press_key('b', dHighSp, 0.1, 8)
        # 打开宝可梦pc
        await  self.press_key('a', 0.15, 0.3, 2)
        # 选择ID抽奖
        await  self.press_key('down', 0.3, 0.25)
        # 无脑按a
        await  self.press_key('a', 0.2, 0.3)
        await  self.press_key('a', 0.1, 0.1, 15)
        await  self.press_key('b', 0.1, 0.1, 15)
        # 返回home界面
        await  self.press_key('home', dHighSp, 1.0)

    # 挖化石
    async def poke_DigStone(self):
        await  self.press_key('a', dHighSp, 0.05, 50)

    # 刷瓦特
    async def poke_BrushWatt(self):
        # 移动到时间设置界面
        await  self.home_to_set_time()
        # 过帧
        await  self.pass_frame_right()
        # 返回home界面，打开游戏
        # await press_key('home',  dHighSp,  1.1)
        # await press_key( 'a', dHighSp,  0.65,  1)
        # await press_key('b', dHighSp,  0.3 , 2)
        # await press_key('a', dHighSp,  0.5)
        # await press_key('b', dHighSp,  0.2, 12 )
        await  self.press_key('home', dHighSp, 0.8)

    # 向左过帧
    async def poke_pass_frame_left(self):
        await  self.press_key('a', dHighSp, dHighDl)
        await  self.press_key('left', dHighSp, dHighDl, 3)
        await  self.press_key('up', dHighSp, dHighDl)
        time_index = self.time_flow_right()
        if time_index == 1:
            await self.press_key('left', dHighSp, dHighDl)
            await self.press_key('up', dHighSp, dHighDl)
            await self.press_key('a', dHighSp, dHighDl)
        elif time_index == 0:
            await self.press_key('left', dHighSp, dHighDl)
            await self.press_key('up', dHighSp, dHighDl)
            await self.press_key('left', dHighSp, dHighDl)
            await self.press_key('up', dHighSp, dHighDl)
            await self.press_key('a', dHighSp, dHighDl, 2)
        await self.press_key('a', dHighSp, dHighDl, 4)

    async def poke_pass_frame_left_(self):
        await  self.press_key('a', dHighSp, dHighDl)
        await  self.press_key('left', dHighSp, dHighDl)
        await  self.press_key('left', dHighSp, dHighDl)
        await  self.press_key('left', dHighSp, dHighDl)
        await  self.press_key('up', dHighSp, dHighDl)
        time_index = self.time_flow_right()
        if time_index == 1:
            await self.press_key('left', dHighSp, dHighDl)
            await self.press_key('up', dHighSp, dHighDl)
            await self.press_key('a', dHighSp, dHighDl)
        elif time_index == 0:
            await self.press_key('left', dHighSp, dHighDl)
            await self.press_key('up', dHighSp, dHighDl)
            await self.press_key('left', dHighSp, dHighDl)
            await self.press_key('up', dHighSp, dHighDl)
            await self.press_key('a', dHighSp, dHighDl)
            await self.press_key('a', dHighSp, dHighDl)
        await self.press_key('a', dHighSp, dHighDl)
        await self.press_key('a', dHighSp, dHighDl)
        await self.press_key('a', dHighSp, dHighDl)
        await self.press_key('a', dHighSp, dHighDl)

# --------------------------------------------------------------------------------------------------#
