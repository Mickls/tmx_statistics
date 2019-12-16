#!/user/bin/env python
# -*- coding:utf-8 -*-
#Reference:**********************************************
# 作者：jc
# 创建：2019/12/9 15:18
# 用意：
#Reference:**********************************************
import sys
from PyQt5.QtWidgets import *

class Fennbk_com(QWidget):
    def __init__(self):
        super(Fennbk_com, self).__init__()
        self.resize(500, 400)
        self.QLabl = QLabel('我是李明                    ',self)
        self.QLabl.setGeometry(0, 100, 400, 38)
        self.setAcceptDrops(True)  #接收拖拽事件

    # 鼠标拖入事件
    def dragEnterEvent(self, evn):
        self.setWindowTitle('鼠标拖入窗口了')
        self.QLabl.setText('文件路径：\n' + evn.mimeData().text())
        # 鼠标放开函数事件
        evn.accept()

    # 鼠标放开执行
    def dropEvent(self, evn):
        self.setWindowTitle('鼠标放开了')

    def dragMoveEvent(self, evn):
        print('鼠标移入')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fennbk = Fennbk_com()
    fennbk.show()
    sys.exit(app.exec_())
