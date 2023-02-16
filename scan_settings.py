# -*- coding: utf-8 -*-
# created by fengweichao on 2023/2/16
import qasync
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import settings
import rpg_filter
import functools


class Panel(QWidget):
    def __init__(self, main_window):
        super(Panel, self).__init__(main_window)
        self.main_window = main_window
        str_keys = settings.GetSettings('key_words', rpg_filter.DEFAULT_KEYS)
        self.keys = rpg_filter.strKey2List(str_keys)
        self.installEventFilter(self)
        self.initPanel()

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
                return True
        return super().eventFilter(obj, event)

    def initPanel(self):
        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.setLayout(layout)
        self.initProgramDetailList(layout)
        self.initActions(layout)

    def initProgramDetailList(self, layout):
        self.table_list = QTableWidget(self.main_window)
        self.table_list.setColumnCount(3)
        self.table_list.setHorizontalHeaderLabels(['服务器关键字', '精准度(0~100)', '操作'])
        self.table_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_list.setSelectionMode(QTableWidget.NoSelection)
        header = self.table_list.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.table_list, 1)
        self.RefreshProgramDetailList()

    def RefreshProgramDetailList(self, add=False):
        if not self.table_list:
            return
        self.table_list.clearContents()
        if add:
            self.keys.append(('', -1))
        self.table_list.setRowCount(len(self.keys))
        for idx, (name, ratio) in enumerate(self.keys):
            self.table_list.setRowHeight(idx, 65)

            edit_name = QLineEdit(self.main_window)
            hint = '请输入扫描关键字,支持模糊匹配'
            edit_name.setPlaceholderText(hint)
            edit_name.setDragEnabled(False)
            edit_name.setFixedWidth(380)
            if name:
                edit_name.setText(name)
            edit_name.setStyleSheet('QLineEdit{margin:5px;}')
            self.table_list.setCellWidget(idx, 0, edit_name)

            edit_ratio = QLineEdit(self.main_window)
            hint = '请输入精准度(0~100),不填默认%s' % rpg_filter.DEFAULT_RATIO
            edit_ratio.setPlaceholderText(hint)
            edit_ratio.setDragEnabled(False)
            edit_ratio.setFixedWidth(380)
            if ratio >= 0:
                edit_ratio.setText(str(ratio))
            edit_ratio.setStyleSheet('QLineEdit{margin:5px;}')
            self.table_list.setCellWidget(idx, 1, edit_ratio)

            del_btn = QPushButton(self.main_window)
            del_btn.setText('删除')
            del_btn.setFont(QFont('Microsoft YaHei', 10, 75))
            del_btn.setStyleSheet('QPushButton{margin:5px;}')
            del_btn.setFixedHeight(45)
            del_btn.setFixedWidth(380)
            del_btn.clicked.connect(functools.partial(self.DelRow, idx))
            self.table_list.setCellWidget(idx, 2, del_btn)

        self.table_list.resizeRowsToContents()
        self.table_list.resizeColumnsToContents()

    def DelRow(self, idx):
        self.keys.pop(idx)
        self.RefreshProgramDetailList()

    def initActions(self, layout):
        add_btn = QPushButton(self.main_window)
        add_btn.setText('增加一行')
        add_btn.setFont(QFont('Microsoft YaHei', 10, 75))
        add_btn.setStyleSheet('QPushButton{margin-top:10px;}')
        add_btn.setFixedHeight(45)
        add_btn.clicked.connect(self.AddRow)

        save_btn = QPushButton(self.main_window)
        save_btn.setText('保存')
        save_btn.setFont(QFont('Microsoft YaHei', 10, 75))
        save_btn.setStyleSheet('QPushButton{margin-top:10px;}')
        save_btn.setFixedHeight(45)
        save_btn.clicked.connect(functools.partial(self.SaveTable))

        layout.addWidget(add_btn, 1)
        layout.addWidget(save_btn, 1)

    def AddRow(self):
        self.SaveTable(False)
        self.RefreshProgramDetailList(True)

    def SaveTable(self, show_box=True):
        save_list = []
        for row in range(self.table_list.rowCount()):
            name = self.table_list.cellWidget(row, 0).text()
            if not name:
                continue
            ratio = self.table_list.cellWidget(row, 1).text()
            if not ratio:
                ratio = rpg_filter.DEFAULT_RATIO
            else:
                try:
                    ratio = int(ratio)
                except:
                    ratio = rpg_filter.DEFAULT_RATIO
            ratio = max(0, min(ratio, 100))
            save_list.append('%s:%s' % (name, ratio))
        save_str = ';'.join(save_list)
        settings.SaveSettings('key_words', save_str)
        if save_list:
            self.keys = rpg_filter.strKey2List(save_str)
        show_box and QMessageBox.about(self.main_window, '保存成功', '您现在可以去扫描了')
