import logging
from joycontrol import logging_default as log

from PyQt5.QtCore import QThread

import start

logger = logging.getLogger(__name__)
log.configure()
    

class Thread(QThread):
    def __init__(self):
        super(Thread, self).__init__()
        self.bBlue_tooth_init = False
        self.vecDate = []
        self.mAuto_joy = None
        self.bExit = False
    
    def run(self):
        #是否初始化蓝牙
        while self.bBlue_tooth_init == False:
            if self.vecDate == []:
                print('vecDate is empty!!!')
                continue
            else:
                start.init(self.vecDate, self.mAuto_joy)
                if self.mAuto_joy != None:
                    self.bBlue_tooth_init = True
        #退出或者运行线程任务            
        while self.bExit == False:
            print('thread running!!!')
