#!/user/bin/env python
# -*- coding:utf-8 -*-
# Reference:**********************************************
# 作者：jc
# 创建：2019/12/9 16:27
# 用意：
# Reference:**********************************************


import os
import xml.sax

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QApplication, QLabel


def get_file_list(path):
    file_list = []
    for fl in os.walk(path):
        root = fl[0]
        for f in fl[2]:
            if os.path.splitext(f)[1] == ".tmx":
                file_path = os.path.join(root, f).replace('\\', '/')
                file_list.append(file_path)
                # print(file_path)
    return file_list


def insert_table(item: list, tableWidget: QTableWidget):
    # tableWidget.clearContents()
    row = tableWidget.rowCount()
    tableWidget.setRowCount(row+len(item))

    i = row
    for file in item:
        file_name = QTableWidgetItem(file.split('/')[-1])
        file_path = QTableWidgetItem(file)
        tableWidget.setItem(i, 0, file_name)
        tableWidget.setItem(i, 4, file_path)
        QApplication.processEvents()

        i += 1
    return i


class TmxParser(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentData = ""
        self.language = []
        self.count = 0

    # 元素开始事件处理
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "tuv" and attributes['xml:lang'] not in self.language:
            self.language.append(attributes['xml:lang'])
        if tag == "tu":
            self.count += 1

    # 元素结束事件处理
    def endElement(self, tag):
        self.CurrentData = ""


class ParserTmx(QThread):
    sinOut = pyqtSignal(str)

    def __init__(self, tableWidget: QTableWidget, lab_progress: QLabel, parent=None):
        super(ParserTmx, self).__init__(parent)
        self.working = True
        self.tableWidget = tableWidget
        self.lab_progress = lab_progress

    def __del__(self):
        self.working = False
        self.wait()

    def run(self):
        # 创建一个 XMLReader
        parser = xml.sax.make_parser()
        # turn off namespaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        # file_data = []
        file_count = self.tableWidget.rowCount()
        i = 0
        while i < file_count:
            file = self.tableWidget.item(i, 4).text()
            Handler = TmxParser()
            parser.setContentHandler(Handler)
            parser.parse(file)
            count = Handler.count
            language = Handler.language
            # print(count)
            # file_data.append([language, count])
            source = QTableWidgetItem(language[0])
            target = QTableWidgetItem(language[1])
            corpus_count = QTableWidgetItem(str(count))
            self.tableWidget.setItem(i, 1, source)
            self.tableWidget.setItem(i, 2, target)
            self.tableWidget.setItem(i, 3, corpus_count)
            i += 1

            process = round(i / file_count * 100, 2)
            self.lab_progress.setText(f"当前已完成{process}%")
        self.sinOut.emit(None)


class InsertData(QThread):
    sinOut = pyqtSignal(int)

    def __init__(self, folder_path, tableWidget, parent=None):
        super(InsertData, self).__init__(parent)
        self.working = True
        self.folder_path = folder_path
        self.tableWidget = tableWidget

    def __del__(self):
        self.working = False
        self.wait()

    def run(self):
        file_list = get_file_list(self.folder_path)
        file_count = insert_table(file_list, self.tableWidget)
        self.sinOut.emit(file_count)
