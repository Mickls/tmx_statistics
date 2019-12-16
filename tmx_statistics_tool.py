#!/user/bin/env python
# -*- coding:utf-8 -*-
# Reference:**********************************************
# 作者：jc
# 创建：2019/12/9 14:39
# 用意：
# Reference:**********************************************


import sys, os
import xlwt
from server import ParserTmx, InsertData
from tmx_statistics import TmxStatisticsUi

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent


class TmxStatisticsMainWindow(QWidget, TmxStatisticsUi):

    def __init__(self, parent=None):
        super(TmxStatisticsMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setAcceptDrops(True)

        # region 设置tableWidget
        # 设置不可编辑
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置列宽占满
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置手动调整列宽
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        # endregion

        self.lab_data.setStyleSheet("color:red")
        self.lab_progress.setStyleSheet("color:red")

        self.let_path.setFocusPolicy(Qt.NoFocus)

        self.process = False
        self.file_list = []

        self.btn_statistics.clicked.connect(self.total_quantity)
        self.btn_export.clicked.connect(self.export_excel)
        self.btn_path.clicked.connect(self.get_folder)
        self.btn_reset.clicked.connect(self.reset)

    def dragEnterEvent(self, QDragEnterEvent: QDragEnterEvent):
        # path = QDragEnterEvent.mimeData().text().split("file:///")
        # del path[0]
        QDragEnterEvent.accept()

    def dropEvent(self, QDropEvent: QDropEvent):
        """
        拖拽文件
        :param QDropEvent:
        :return:
        """
        path = QDropEvent.mimeData().text().replace("\n", "").split("file:///")
        del path[0]
        if os.path.isdir(path[0]):
            self.btn_export.setEnabled(False)
            self.let_path.setText(path[0])

            self.thread = InsertData(path[0], self.tableWidget)
            self.thread.sinOut.connect(self.insert_data)
            self.thread.start()
        else:
            for p in path:
                if os.path.splitext(p)[1] == ".tmx":
                    # self.file_list.append(self.path)
                    file_name = QTableWidgetItem(p.split('/')[-1])
                    row = self.tableWidget.rowCount()
                    self.tableWidget.insertRow(row)
                    self.tableWidget.setItem(row, 0, file_name)
                    self.tableWidget.setItem(row, 4, QTableWidgetItem(p))
        if self.process:
            self.process = False
            self.lab_progress.setText("")
            self.lab_data.setText("")
            self.tableWidget.clearContents()
            self.btn_export.setEnabled(False)

    def reset(self):
        """
        重置
        :return:
        """
        self.tableWidget.clearContents()
        self.btn_export.setEnabled(False)
        self.btn_statistics.setEnabled(True)
        self.btn_path.setEnabled(True)

        self.lab_data.setText("")
        self.lab_progress.setText("")

    def get_folder(self):
        """
        打开文件夹按钮
        :return:
        """
        self.path = QFileDialog.getExistingDirectory(self, "选择需要统计的目录", '')
        if self.path != "":
            self.btn_export.setEnabled(False)
            self.let_path.setText(self.path)

            self.thread = InsertData(self.path, self.tableWidget)
            self.thread.sinOut.connect(self.insert_data)
            self.thread.start()

    def insert_data(self, file_count):
        self.lab_data.setText(f"共导入{file_count}个文件")
        self.lab_progress.setText("")

    def total_quantity(self):
        """
        统计句对数
        :return:
        """
        self.process = True
        self.setAcceptDrops(False)
        self.btn_statistics.setEnabled(False)
        self.btn_path.setEnabled(False)
        self.btn_reset.setEnabled(False)

        self.thread = ParserTmx(self.tableWidget, self.lab_progress)
        self.thread.sinOut.connect(self.active_btn)
        self.thread.start()

    def active_btn(self, e):
        """
        激活按钮
        :param e:
        :return:
        """
        self.setAcceptDrops(True)
        self.btn_path.setEnabled(True)
        self.btn_statistics.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.btn_reset.setEnabled(True)

    def export_excel(self):
        """
        导出为excel
        过程简短，后台运行还得做进度，直接单线程
        :return:
        """
        self.btn_export.setText("导出中")
        self.btn_export.setEnabled(False)
        file_path, click = QFileDialog.getSaveFileName(self, "选择文件导出路径",
                                                       os.path.join(os.path.expanduser("~"), 'Desktop'),
                                                       "Excel Files (*.xls)")
        if click:
            try:
                workbook = xlwt.Workbook()
                sheet = workbook.add_sheet("sheet1")
                row_count = self.tableWidget.rowCount()
                column_count = self.tableWidget.columnCount()
                sheet.write(0, 0, "文件名")
                sheet.write(0, 1, "源语言")
                sheet.write(0, 2, "译后语言")
                sheet.write(0, 3, "句对数")
                sheet.write(0, 4, "文件路径")
                all_count = 0
                r = 1
                while r <= row_count:
                    c = 0
                    while c < column_count:
                        sheet.write(r, c, self.tableWidget.item(r-1, c).text())
                        if c == 3:
                            all_count += int(self.tableWidget.item(r-1, c).text())
                        c += 1
                    r += 1
                sheet.write(r, 0, "总文件")
                sheet.write(r, 1, "总句对")
                sheet.write(r+1, 0, row_count)
                sheet.write(r+1, 1, all_count)
                workbook.save(file_path)
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.NoIcon)
                msg_box.setText("文件已导出")
                msg_box.setWindowTitle("操作信息")
                msg_box.setStandardButtons(QMessageBox.Ok)
                # msg_box.setStandardButtons(QMessageBox.No)
                msg_box.exec_()
            except Exception as e:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setText(f"导出错误\r\n{e}")
                msg_box.setWindowTitle("操作信息")
                msg_box.setStandardButtons(QMessageBox.Ok)
                # msg_box.setStandardButtons(QMessageBox.No)
                msg_box.exec_()
        self.btn_export.setText("导出excel")
        self.btn_export.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app_win = TmxStatisticsMainWindow()
    app_win.show()
    sys.exit(app.exec_())
