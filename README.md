# poke_auto_joy
简介  :  通过项目https://github.com/mart1nro/joycontrol ,使用蓝牙模拟switch手柄，用于宝可梦剑盾的自动化上.

运行平台  :  ubuntu16          蓝牙5.48

运行环境  :  python 3.6.9

1、快速开始

(1)打开switch的手柄界面,进入手柄搜索模式.

(2)打开终端,进入项目目录,运行命令:

    sudo python3 start.py -date [switch上设置的日期]    

    例:          sudo python3 start.py -date 2020-3-4

(3)通过在终端使用键盘按键w,s选择任务，选择任务后按键a开始任务

2、自定义任务

(1)修改根目录下的auto_joy.py文件的内容(下列所提及的文件均指auot_joy.py)

(2)使用文件第60行按键模块定义脚本任务:

    async def press_key(buttons_, release_sec_ = 0.05, delay_sec_ = 0.0, cycle_nums_ = 1)
    
    例:         await self.press_key('a', 0.05, 0.1, 1)

    switch执行按下a键在0.05s后释放a键，然后延时0.1s，只执行一次操作
    
(3)将自定义的脚本任务添入文件第52行的fun_list中(可选)

(4)在文件第17行添加要运行的任务，可通过键盘按键w,s选择任务

# 引用
[joycontrol](https://github.com/mart1nro/joycontrol)
