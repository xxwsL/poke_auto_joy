import os,  sys  
import calendar
import asyncio
import time

from joycontrol.controller_state import ControllerState,  button_push
import real_key as rk

sys.setrecursionlimit(1000000)

task_file_name = ''
task_cycles = 0
stop_state = True
pause_state = False
shut_state = False

dHighSp = 0.05
dFastSp= 0.1

dHighDl = 0.08
dFastDl= 0.1

key_list = ['zl', 'zr', 'l', 'r', 'minus', 'plus',  'y', 'x', 'a', 'b', 'capture', 'home', 'up', 'left', 'right', 'down']

stick_l_list = [
                            'l1', 'l2', 'l3',
                             'l4', 'l5', 'l6',
                            'l7', 'l8', 'l9',
                            ]

stick_r_list = [
                            'r1', 'r2', 'r3',
                            'r4', 'r5', 'r6',
                            'r7', 'r8', 'r9',
                            ]

class switch_key_flag(int):
    Key = 0
    LStick = 1
    RStick = 2
    Loop = 3
    Delay = 4

class AutoJoy:

    def __init__(self, _dr,  _year, _month, _day):
        #switch控制设备
        self.dr_ = _dr
        self.ing_state = False

        #时间管理变量
        self.year_now_ = _year
        self.month_now_  = _month
        self.day_now = _day
        self.all_days = calendar.monthrange(_year, _month)[1]
        
        #获取所有配置文件名列表
        self.get_all_set_file('./set_files/')


    '''
    switch按健功能
    buttons_  : 'y', 'x', 'b', 'a', 'r', 'zr',
                            'minus', 'plus', 'r_stick', 'l_stick', 'home', 'capture',
                            'down', 'up', 'right', 'left', 'l', 'zl'
    release_sec_ : 延迟多长时间释放按键(单位:s)
    delay_sec_ : 本轮按键操作完毕延迟多长时间(单位:s)
    cycle_nums_ : 重复进行多少次当前按键操作
    '''
    async def press_key(self, buttons_, release_sec_ = 0.05, delay_sec_=0.0):
        # print(buttons_)
        #发送按键
        self.dr_.button_state.set_button(buttons_)
        await self.dr_.send()
        await asyncio.sleep(release_sec_)

        self.dr_.button_state.set_button(buttons_, pushed = False,)
        await self.dr_.send()
        await asyncio.sleep(delay_sec_)

    #左摇杆动作
    async def stick_l_action(self, direct_, release_sec_=0.05, delay_sec_=0.0):
        #左上
        if direct_ == 'l1':
            self.dr_.l_stick_state.set_left_up()
        #上
        elif direct_ == 'l2':
            self.dr_.l_stick_state.set_up()
        #右上
        elif direct_ ==  'l3':
            self.dr_.l_stick_state.set_right_up()
        #左
        elif direct_ == 'l4':
            self.dr_.l_stick_state.set_left()
        #中
        elif direct_ == 'l5':
            self.dr_.l_stick_state.set_center()
        #右
        elif direct_ == 'l6':
            self.dr_.l_stick_state.set_right()
        #左下
        elif direct_ == 'l7':
            self.dr_.l_stick_state.set_left_down()
        #下
        elif direct_ == 'l8':
            self.dr_.l_stick_state.set_down()
        #右下
        elif direct_ == 'l9':
            self.dr_.l_stick_state.set_right_down()

        #开始摇杆
        await self.dr_.send()
        await asyncio.sleep(release_sec_)
        #释放摇杆
        self.dr_.l_stick_state.set_center()
        await self.dr_.send()
        await asyncio.sleep(delay_sec_)
   
   #右摇杆动作
    async def stick_r_action(self, direct_, release_sec_=0.05, delay_sec_=0.0):
        #左上
        if direct_ == 'r1':
            self.dr_.r_stick_state.set_left_up()
        #上
        elif direct_ == 'r2':
            self.dr_r_stick_state.set_up()
        #右上
        elif direct_ ==  'r3':
            self.dr_.r_stick_state.set_right_up()
        #左
        elif direct_ == 'r4':
            self.dr_.r_stick_state.set_left()
        #中
        elif direct_ == 'r5':
            self.dr_.r_stick_state.set_center()
        #右
        elif direct_ == 'r6':
            self.dr_.r_stick_state.set_right()
        #左下
        elif direct_ == 'r7':
            self.dr_.r_stick_state.set_left_down()
        #下
        elif direct_ == 'r8':
            self.dr_.r_stick_state.set_down()
        #右下
        elif direct_ == 'r9':
            self.dr_.r_stick_state.set_right_down()

        #开始摇杆
        await self.dr_.send()
        await asyncio.sleep(release_sec_)
        #释放摇杆
        self.dr_.r_stick_state.set_center()
        await self.dr_.send()
        await asyncio.sleep(delay_sec_)
        
    #过帧时需要使用时间流来监控时间
    def time_flow_right(self): 
        res = 2
        if self.day_now == self.all_days:
            self.day_now = 1
            if self.month_now_ == 12:
                self.month_now_ = 1
                self.year_now_ += 1
                res =  0
            else:
                self.month_now_ += 1
                res = 1
            self.all_days = calendar.monthrange(self.year_now_, self.month_now_)[1] 
        else:
            self.day_now += 1
        return res

    #判断当前代码字符属于那个操作flag
    def parse_str_flag(self, str_):
        if str_ in key_list:
            return switch_key_flag.Key
        elif str_ in stick_l_list:
            return switch_key_flag.LStick
        elif str_ in stick_r_list:
            return switch_key_flag.RStick
        else:
            return -1

    #自动任务
    async def auto_task(self, task_name_, cycle_nums_=1):
        #解析配置文件数据
        vecTask_data_t = self.parse_set_file(task_name_)
        #无限循环任务
        if cycle_nums_ < 0:
            while 1:
                if stop_state:
                    break
                #执行任务
                await self.task_parse(vecTask_data_t)
        #按设定周期循环任务
        else:
            for i in range(cycle_nums_): 
                if stop_state:
                    break
                #执行任务
                await self.task_parse(vecTask_data_t)
                print('完成 %d 周期......' %(i))

    def cmd_len4(self, cmd_line_):
        cmd_flag = self.parse_str_flag(cmd_line_[0])
        if cmd_flag >= switch_key_flag.Key:
            return [cmd_flag, cmd_line_[0], float(cmd_line_[1]), float(cmd_line_[2]), int(cmd_line_[3])]
        else:
            return []

    #解析配置文件
    def parse_set_file(self, task_name_):
        #获取文本每一行
        with open(self.strSet_root + task_name_, 'r') as rf:
            self.line_datas = rf.readlines()
            self.line_datas_len = len(self.line_datas)
            self.task_str_index = 0
            self.def_diect = {}
            self.vecTask_data = self.parse_set_file_rec()
        # print(self.vecTask_data)
        return self.vecTask_data

    def parse_set_file_rec(self):
        vecTask_data_t = []
        cmd_period = []
        while self.task_str_index < self.line_datas_len:
            vecCmd_data = self.line_datas[self.task_str_index].split(', ')
            cmd_len = len(vecCmd_data)
            #判断是否是一个有效命令
            if cmd_len == 4:
                cmd_len4_res = self.cmd_len4(vecCmd_data)
                if cmd_len4_res != []:
                    cmd_period.append(cmd_len4_res)
                else:
                    raise PermissionError('switch指令错误0!!!')
            #判断是否是单命令
            elif cmd_len == 1:
                if (vecCmd_data[0] == 'end' or vecCmd_data[0] == 'end\n') and (cmd_period != []):
                    vecTask_data_t.append(cmd_period)
                    cmd_period = []
                if (vecCmd_data[0] == 'loop_end' or vecCmd_data[0] == 'loop_end\n'):
                    if cmd_period != []:
                        vecTask_data_t.append(cmd_period)
                    return vecTask_data_t
                else:
                    pass
                    # print('switch指令警告-1 = %s' %(vecCmd_data[0] ))
            #判断是否是双命令
            elif cmd_len == 2:
                if vecCmd_data[0] == 'loop':
                    loop_cycle = self.str_decode_num(vecCmd_data[1])
                    cmd_period_loop = [switch_key_flag.Loop, loop_cycle]
                    self.task_str_index += 1
                    cmd_period_loop.append(self.parse_set_file_rec())              
                    cmd_period.append(cmd_period_loop)
            elif cmd_len == 3:
                if vecCmd_data[0] == 'def':
                    self.def_diect[vecCmd_data[1] + '\n'] = int(vecCmd_data[2])
            #命令文本遍历加1
            self.task_str_index = self.task_str_index + 1
        #返回解析得到的列表
        return vecTask_data_t


    def str_decode_num(self, str_):
        if str_ in self.def_diect:
            return self.def_diect[str_]
        else:
            return int(str_)

    #任务解析
    async def task_parse(self, str_task_list_):
        for cmd_period in str_task_list_:
            if await self.task_parse_run(cmd_period) == False:
                break;
                
    
    async def task_parse_run(self,  cmd_period):
        for cmd in cmd_period:
            if stop_state:
                return False
            # print(cmd)
            #执行按键操作
            if cmd[0] == switch_key_flag.Key:
                for i in range(cmd[4]):
                    await self.press_key(cmd[1], cmd[2], cmd[3])
            #执行左摇杆操作
            elif cmd[0] == switch_key_flag.LStick:
                for i in range(cmd[4]):
                    await self.stick_l_action(cmd[1], cmd[2], cmd[3])
            #执行右摇杆操作
            elif cmd[0] == switch_key_flag.RStick:
                for i in range(cmd[4]):
                    await self.stick_r_action(cmd[1], cmd[2], cmd[3])
            #循环指令
            elif cmd[0]  == switch_key_flag.Loop:
                for i in range(cmd[1]):
                    await self.task_parse(cmd[2])
            elif cmd[0] == switch_key_flag.Delay:
                await asyncio.sleep(cmd[1])
            else:
                print(cmd[0])
        return True
    '''
    运行
    '''
    async def run_in_gui(self):
        await self.press_key('home', 0.1)
        asyncio.sleep(1)
        print('开始运行......')
        global stop_state
        while 1:
            if stop_state == False:
                print('运行  %d  周期  %s  任务......' %(task_cycles,  task_file_name))
                await self.auto_task(task_file_name, task_cycles)
                stop_state = True
                if shut_state:
                    os.system('sudo shutdown')
            await asyncio.sleep(0.1)

    #获取所有配置文件
    def get_all_set_file(self, path_str_ = './set_files/'):
        for root, dirs, files in os.walk(path_str_):
            self.strSet_root = root + '/'
            self.vecSet_files = files
            print(files)

    
