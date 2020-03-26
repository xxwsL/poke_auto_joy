# poke_auto_joy
简介  :  通过项目https://github.com/mart1nro/joycontrol ,使用蓝牙模拟switch手柄，用于宝可梦剑盾的自动化上.

运行平台  :  ubuntu16          蓝牙5.48

运行环境  :  python 3.6.9    pyqt5

1、快速开始

(1)打开switch的手柄界面,进入手柄搜索模式.

(2)打开终端,进入项目目录,运行命令:

    sudo python3 gui_run.py

(3)通过界面或者手动编写配置文件

2、自定义任务

例如：
   a, 0.1, 0.1, 1
   end
   
   按下按键0.1s释放，延时0.1s，执行此次操作1次

# 引用
[joycontrol](https://github.com/mart1nro/joycontrol)
