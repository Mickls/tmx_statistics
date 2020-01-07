#!/user/bin/env python
# -*- coding:utf-8 -*-
# Reference:**********************************************
# 作者：jc
# 创建：2019/12/9 16:27
# 用意：
# Reference:**********************************************


import os
import xml.sax
import chardet

from xml.sax.handler import ErrorHandler
from xml.sax._exceptions import SAXParseException
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
    tableWidget.setRowCount(row + len(item))

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
        if tag == "tuv":
            if 'xml:lang' in attributes:
                if attributes['xml:lang'] not in self.language:
                    self.language.append(attributes['xml:lang'])
            elif 'lang' in attributes:
                if attributes['lang'] not in self.language:
                    self.language.append(attributes['lang'])
        if tag == "tu":
            self.count += 1

    # 元素结束事件处理
    def endElement(self, tag):
        self.CurrentData = ""


class ExceptHandler(ErrorHandler):
    def fatalError(self, exceptions):
        print(exceptions)


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
        create_file_list = []
        # 创建一个 XMLReader
        parser = xml.sax.make_parser()
        # turn off namespaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        # file_data = []
        file_count = self.tableWidget.rowCount()
        i = 0

        while i < file_count:
            file = self.tableWidget.item(i, 4).text()
            dir_name = file.rsplit('/', 1)[0]
            handler = TmxParser()
            parser.setContentHandler(handler)
            # parser.setErrorHandler(ExceptHandler())
            while True:
                try:
                    parser.parse(file)
                    parser.setErrorHandler(ErrorHandler())
                    count = handler.count
                    language = handler.language
                    # print(count)
                    # file_data.append([language, count])
                    source = QTableWidgetItem(language[0])
                    target = QTableWidgetItem(language[1])
                    corpus_count = QTableWidgetItem(str(count))
                    break
                except ValueError as ex:
                    self.value_except(ex, dir_name, create_file_list)
                except SAXParseException as ex:
                    error = str(ex).rsplit(":", 1)[-1].strip()
                    print(error)
                    if error == "not well-formed (invalid token)":
                        parser.setErrorHandler(ExceptHandler())
                    elif error == "encoding specified in XML declaration is incorrect":
                        with open(file, 'rb') as f:
                            t = f.readline()
                        if chardet.detect(t)['encoding'] != 'UTF-16':
                            source = QTableWidgetItem("tmx文件解析错误")
                            target = QTableWidgetItem("tmx文件解析错误")
                            corpus_count = QTableWidgetItem(str(0))
                            break
                        self.convert2utf8(file)
                except Exception:
                    source = QTableWidgetItem("tmx文件解析错误")
                    target = QTableWidgetItem("tmx文件解析错误")
                    corpus_count = QTableWidgetItem(str(0))
                    break
            self.tableWidget.setItem(i, 1, source)
            self.tableWidget.setItem(i, 2, target)
            self.tableWidget.setItem(i, 3, corpus_count)
            i += 1

            process = round(i / file_count * 100, 2)
            self.lab_progress.setText(f"当前已完成{process}%")
        for f in create_file_list:
            os.remove(f)
        self.sinOut.emit(None)

    @staticmethod
    def value_except(exception, dir_name, file_list):
        filename = eval(str(exception).split(' ')[-1])
        create_file = f"{dir_name}/{filename}"
        with open(create_file, 'w') as f:
            pass
        if create_file not in file_list:
            file_list.append(create_file)

    @staticmethod
    def convert2utf8(file):
        file_bak = f"{file}.bak"
        with open(file, 'r', encoding='utf16') as f:
            with open(file_bak, 'w', encoding='utf8') as fl:
                while True:
                    t = f.readline()
                    if not t:
                        break
                    fl.write(t)
        os.remove(file)
        os.rename(file_bak, file)


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
