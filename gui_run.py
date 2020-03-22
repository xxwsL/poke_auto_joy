import os, sys, asyncio
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QTextEdit
from PyQt5.QtWidgets import QPushButton, QGridLayout, QLabel, QInputDialog
from PyQt5.QtWidgets import QFileDialog, QComboBox
from PyQt5.QtGui import QIcon, QFont

from quamash import QEventLoop

from joycontrol.server import create_hid_server
from joycontrol.protocol import controller_protocol_factory, Controller
import auto_joy

save_path = './set_files/'

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.key_list = [
                                ['', 'zl', '', '', '', '', '', '','', 'zr', ''],
                                ['', 'l', '', '', '', '', '', '','', 'r', ''],
                                ['', '', '', '', 'minus', '', 'plus', '','', '', ''],
                                ['l1', 'l2', 'l3', '', '', '', '','', '', 'x', ''],
                                ['l4', 'l5', 'l6', '', '', '', '','', 'y', '', 'a'],
                                ['l7', 'l8', 'l9', '', '', '', '','', '', 'b', ''],
                                ['', '', '', '', 'capture', '', 'home', '','', '', ''],
                                ['', 'up', '', '', '', '', '','', 'r1', 'r2', 'r3',],
                                ['left', '', 'right', '', '', '', '','', 'r4', 'r5', 'r6'],
                                ['', 'down', '', '', '', '', '','', 'r7', 'r8', 'r9'],
                                ]

        self.key_icon = [
                                        'l1', 'l2', 'l3',   'r1', 'r2', 'r3',
                                        'l4', 'l5', 'l6',   'r4', 'r5', 'r6',
                                        'l7', 'l8', 'l9',   'r7', 'r8', 'r9'
                                        ]

        #初始化
        self.window = QWidget()

        self.mMain_layout = QGridLayout()
        self.mSet_gui_layout = QGridLayout()

        #初始化按钮gui
        self.init_button_gui()
        #初始化set_gui
        self.init_button_set_gui()
        #显示文本初始化
        self.init_display_set()
        #初始化蓝牙gui
        self.init_BlueTooth_gui()
        
        #设置主界面参数
        self.setLayout(self.mMain_layout)
        self.setFixedSize(1250, 550)
        self.move(150, 300)
        self.setWindowTitle('poke_auto任务生成器')

        self.loading_name = ''

    #初始化按钮gui
    def init_button_gui(self):
        for i in range(len(self.key_list)):
            for j in range(len(self.key_list[i])):
                if self.key_list[i][j] == '':
                    self.mMain_layout.addWidget(QLabel(''), i, j)
                else:
                    #创建switch按钮
                    mButton = QPushButton()
                    mButton.setObjectName(self.key_list[i][j])
                    mButton.setFixedSize(80, 40)
                    if self.key_list[i][j] in self.key_icon:
                        icom_path = './image/button/' + self.key_list[i][j] + '.png'
                        mButton.setIcon(QIcon(icom_path))
                    else:
                        mButton.setText(self.key_list[i][j])
                    mButton.clicked.connect(lambda checked: self.joy_button_clicked())
                    self.mMain_layout.addWidget(mButton, i, j)

    #初初始化按钮设置gui
    def init_button_set_gui(self):
        self.mSet_gui = QWidget()
        mLabel_release_time = QLabel('按键按住时间')
        self.mText_release_time = QLineEdit()
        #限制只能输入double类型数据
        self.mText_release_time.setValidator(QtGui.QDoubleValidator())
        self.mSet_gui_layout.addWidget(mLabel_release_time, 0, 0)
        self.mSet_gui_layout.addWidget(self.mText_release_time, 0, 1)

        mLabel_delay_time = QLabel('按键延时时间')
        self.mText_delay_time = QLineEdit()
        #限制只能输入double类型数据
        self.mText_delay_time.setValidator(QtGui.QDoubleValidator())
        self.mSet_gui_layout.addWidget(mLabel_delay_time, 1, 0)
        self.mSet_gui_layout.addWidget(self.mText_delay_time, 1, 1)

        mLabel_cycle_num = QLabel('执行次数')
        self.mText_cycle_num = QLineEdit()
        #限制只能输入int类型数据
        self.mText_cycle_num.setValidator(QtGui.QIntValidator())
        self.mSet_gui_layout.addWidget(mLabel_cycle_num, 2, 0)
        self.mSet_gui_layout.addWidget(self.mText_cycle_num, 2, 1)


        self.mButton_sure = QPushButton('确定')
        self.mButton_sure.clicked.connect(lambda :self.button_set_sure_clicked())
        self.mButton_sure.setFixedSize(60, 20)
        self.mSet_gui_layout.addWidget(self.mButton_sure, 3, 1)

        self.mSet_gui_layout.setAlignment(QtCore.Qt.AlignRight)
        self.mSet_gui.setLayout(self.mSet_gui_layout)

    #按钮按下回调函数
    def joy_button_clicked(self):
        button = self.sender()
        mPos = self.pos()
        mSize = self.size()
        self.mSet_gui.move(mPos.x() + mSize.width() / 4, mPos.y() + mSize.height() / 2)
        #窗口置于最顶层显示
        self.mSet_gui.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.mSet_gui.show() 
        self.strbutton_value = button.objectName()
        # print('button = %s' %(self.strbutton_value))

    #显示文本初始化
    def init_display_set(self):
        #设置显示文本标题
        mDisplay_set_label = QLabel('任务执行步骤')
        self.mMain_layout.addWidget(mDisplay_set_label, 0, 11)

        #初始化clear按钮
        mButton_clear = QPushButton('Clear')
        mButton_clear.setFixedSize(48, 35)
        mButton_clear.clicked.connect(lambda : self.button_clear_clicked())
        self.mMain_layout.addWidget(mButton_clear, 0, 12)

        #初始化clear按钮
        mButton_module = QPushButton('Module')
        mButton_module.setFixedSize(48, 35)
        mButton_module.clicked.connect(lambda : self.button_clear_clicked())
        self.mMain_layout.addWidget(mButton_module, 0, 13)

        #初始化module按钮
        mButton_load = QPushButton('Load')
        mButton_load.setFixedSize(48, 35)
        mButton_load.clicked.connect(lambda: self.button_load_clicked())
        self.mMain_layout.addWidget(mButton_load, 0, 14)

        #初始化save按钮
        mButton_save = QPushButton('Save')
        mButton_save.setFixedSize(48, 35)
        mButton_save.clicked.connect(lambda : self.button_save_clicked())
        self.mMain_layout.addWidget(mButton_save, 0, 15)

        #设置显示文本
        self.mDisplay_set = QTextEdit()
        self.mDisplay_set.setFont(QFont('微软雅黑', 12))
        # mDisplay_set.setReadOnly(True)
        self.mDisplay_set.setFixedSize(460, 432)
        self.mMain_layout.addWidget(self.mDisplay_set, 1, 11)

    #设置按钮参数gui确定按钮回调函数
    def button_set_sure_clicked(self):
        iRelease_time = self.mText_release_time.text()
        iDelay_time = self.mText_delay_time.text()
        iCycle_num = self.mText_cycle_num.text()
        if iRelease_time != '' and iDelay_time != '' and iCycle_num != '':
            cmd_str = self.strbutton_value + ', ' + iRelease_time + ', ' + iDelay_time + ', ' + iCycle_num
            self.mDisplay_set.append(cmd_str)
            # print('release_time = %s\ndelay_time = %s\ncycle_num = %s' % (iRelease_time, iDelay_time, iCycle_num))
        #隐藏窗口
        self.mSet_gui.hide()

    #save按钮回调函数
    def button_save_clicked(self):
        self.mDisplay_set.toPlainText()
        mInputDialog = QInputDialog()
        strNane, get_ok = mInputDialog.getText(self, '保存', '文件命名')
        if get_ok:
            # text_line_list = str(self.mDisplay_set.toPlainText()).split('\n')
            if strNane ==  '':
                with open(self.loading_name, 'w') as wf:
                    wf.write(self.mDisplay_set.toPlainText() + '\nend')
            else:
                with open(save_path + strNane, 'w') as wf:
                    wf.write(self.mDisplay_set.toPlainText() + '\nend')
                self.loading_name = save_path +  strNane
                self.combox_set_refresh()
        
    #clear按钮回调函数
    def button_clear_clicked(self):
        self.mDisplay_set.clear()

    #load按钮回调函数
    def button_load_clicked(self):
        page = QFileDialog.getOpenFileName(self, 'Open file', save_path)
        if page[0]:
            self.loading_name = page[0]
            print(page[0])
            rf = open(page[0], 'r')
            with rf:
                data = rf.read()
                self.mDisplay_set.setText(data)

    #lmodule按钮回调函数
    def button_module_clicked(self):
        pass

    #初始化运行蓝牙操作界面
    def init_BlueTooth_gui(self):
        self.mBlueTooth_gui = QWidget()
        # self.mBlueTooth_gui.setFixedSize(300, 50)
        self.mMain_layout.addWidget(self.mBlueTooth_gui, 10, 11)

        self.mBlueTooth_layout = QGridLayout()
        self.mBlueTooth_gui.setLayout(self.mBlueTooth_layout)

        #初始化运行任务按钮
        self.mButton_run  = QPushButton('运行任务')
        self.mButton_run.setFixedSize(58, 35)
        self.mButton_run.clicked.connect(lambda : self.buuton_run_clicked())
        self.mBlueTooth_layout.addWidget(self.mButton_run, 0, 1)

        #初始化运行完成任务按钮
        self.mButton_TaskComplete  = QPushButton('自动关机')
        self.mButton_TaskComplete.setFixedSize(58, 35)
        self.mButton_TaskComplete.clicked.connect(lambda : self.buuton_TaskComplete_clicked())
        self.mBlueTooth_layout.addWidget(self.mButton_TaskComplete, 0, 0)

        #初始化任务周期设置栏
        self.mText_task_cycles  = QLineEdit()
        self.mText_task_cycles.setText('1')
        self.mText_task_cycles.setValidator(QtGui.QIntValidator())
        self.mText_task_cycles.returnPressed.connect(lambda :self.set_task_cycles_cb())
        self.mText_task_cycles.setFixedSize(60, 35)
        self.mBlueTooth_layout.addWidget(self.mText_task_cycles, 0, 2)

        #初始化任务配置选择栏
        self.mCombox_set  = QComboBox()
        self.mCombox_set.setFixedSize(120, 35)
        self.mCombox_set.currentIndexChanged.connect(lambda :self.combox_set_choose())
        self.get_all_set_file()
        self.mMain_layout.addWidget(self.mCombox_set,  10, 13)

    #运行按钮回调函数
    def buuton_run_clicked(self):
        if self.mButton_run.text() == '运行任务':
            auto_joy.task_cycles = int(self.mText_task_cycles.text())
            auto_joy.stop_state = False
            self.mButton_run.setText('停止任务')   
        else:
            self.mButton_run.setText('运行任务')
            auto_joy.stop_state = True
        
     #获取所有配置文件
    
    #获取所有配置文件
    def get_all_set_file(self, path_str_ = './set_files/'):
        for root, dirs, files in os.walk(path_str_):
            self.strSet_root = root + '/'
            self.vecSet_files = files
        for i in self.vecSet_files:
            self.mCombox_set.addItem(i)
    
    #刷新配置选择项
    def combox_set_refresh(self):
        self.mCombox_set.clear()
        self.get_all_set_file()

    #选中配置回调函数
    def combox_set_choose(self):
        auto_joy.task_file_name =  self.mCombox_set.currentText()
        # print(auto_joy.task_file_name)

    #设置任务周期回调函数
    def set_task_cycles_cb(self):
        auto_joy.task_cycles = int(self.mText_task_cycles.text())

    def buuton_TaskComplete_clicked(self):
        if auto_joy.sleep_state == False:
            self.mButton_TaskComplete.setStyleSheet("background-color: rgb(255,0,0)");
            auto_joy.shut_state = True
        else:
            self.mButton_TaskComplete.setStyleSheet("background-color: rgb(255,255,255)");
            auto_joy.shut_state = False

        
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
    await mAutoJoy.run_in_gui()
    logger.info('Stopping communication...')
    await transport.close()

if __name__ == '__main__':
    # check if root
    if not os.geteuid() == 0:
        raise PermissionError('Script must be run as root!')

    app = QApplication(sys.argv)
    
    mMainWindow = MainWindow()
    mMainWindow.show()

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop) 

    date_list_num = [2020, 3, 10]
    with loop: 
        loop.run_until_complete(_main(date_list_num))

    # start.
    
