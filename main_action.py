# -*- coding: utf-8 -*-
# created by fengweichao on 2023/2/16
import asyncio
import os.path
import qasync
import rpg_filter
import functools
import datetime
import json
import os
import settings
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import steam.game_servers as gs

STATE_IDLE = 0
STATE_SCANING = 1
STATE_DONE = 2

KEYS = ('亚洲', '南美洲', '美洲东部', '美洲西部', '欧洲', '澳大利亚', '中东', '非洲', '全球')

REGIONS = {
    '全球': gs.MSRegion.World,
    '南美洲': gs.MSRegion.South_America,
    '美洲东部': gs.MSRegion.US_East,
    '美洲西部': gs.MSRegion.US_West,
    '欧洲': gs.MSRegion.Europe,
    '亚洲': gs.MSRegion.Asia,
    '澳大利亚': gs.MSRegion.Australia,
    '中东': gs.MSRegion.Middle_East,
    '非洲': gs.MSRegion.Africa
}

DEFAULT_REGIONS = '亚洲'


class UiSignals(QObject):
    progress_signal = Signal(dict, dict, tuple, int)
    ret_signal = Signal(dict)


class Panel(QWidget):
    def __init__(self, main_window):
        super(Panel, self).__init__(main_window)
        self.main_window = main_window
        self.scan_list = []
        self.thread_stop = None
        self.ui_signal = UiSignals(main_window)
        self.ui_signal.progress_signal.connect(self.onScanProgressCb)
        self.ui_signal.ret_signal.connect(self.onScanCb)
        self.initPanel()
        self.installEventFilter(self)
        self.setState(STATE_IDLE)

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
                return True
        return super().eventFilter(obj, event)

    def initPanel(self):
        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.setLayout(layout)
        self.initTitle(layout)
        self.initButton(layout)
        self.initDetail(layout)

    def initTitle(self, layout):
        self.tableWidget = QTableWidget(self.main_window)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['服务器名字', 'IP', '匹配度', '操作'])
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.NoSelection)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.tableWidget, 0)

    def initButton(self, root_layout):
        layout = QHBoxLayout()
        self.region_list = QComboBox(self.main_window)
        for item in KEYS:
            self.region_list.addItem(item)
        self.region_list.setCurrentIndex(0)
        layout.addWidget(self.region_list)
        self.scan_button = self.createButton('扫描')
        self.scan_button.clicked.connect(self.onScanClick)
        layout.addWidget(self.scan_button, 1)
        self.export_button = self.createButton('导出火绒json')
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.onExportClick)
        layout.addWidget(self.export_button, 1)
        widget = QWidget(self)
        widget.setLayout(layout)
        root_layout.addWidget(widget, 0)

    def initDetail(self, root_layout):
        layout = QHBoxLayout()
        self.message = QLabel(self.main_window)
        layout.addWidget(self.message, 1)
        self.progress = QProgressBar(self.main_window)
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setOrientation(Qt.Horizontal)
        layout.addWidget(self.progress, 1)
        widget = QWidget(self)
        widget.setStyleSheet('border-width: 0px;}')
        widget.setLayout(layout)
        root_layout.addWidget(widget, 0)

    def createButton(self, txt):
        btn = QPushButton(self)
        btn.setText(txt)
        btn.setStyleSheet('QPushButton{margin:5px;}')
        btn.setFixedHeight(45)
        return btn

    def onScanClick(self):
        if self.state != STATE_SCANING:
            count, reply = QInputDialog.getText(
                self.main_window, '扫描服务器数量', '请输入数量(默认300)', QLineEdit.Normal, '300'
            )
            if reply:
                try:
                    count = int(count)
                except:
                    count = 300
                del self.scan_list[:]
                while self.tableWidget.rowCount() > 0:
                    self.tableWidget.removeRow(0)
                self.setState(STATE_SCANING)
                self.thread_stop = rpg_filter.backGroundScan(
                    self.main_window.panel_setting.keys, count,
                    REGIONS.get(self.region_list.currentText(), gs.MSRegion.Asia),
                    self.ui_signal.progress_signal, self.ui_signal.ret_signal
                )
        else:
            reply = QMessageBox.information(
                self.main_window, '停止扫描确认', '是否要确认停止', QMessageBox.Ok,
                QMessageBox.Cancel
            )
            if reply == QMessageBox.Ok:
                self.setState(STATE_DONE)
                self.thread_stop and self.thread_stop.set()

    def onScanProgressCb(self, filter_ret, server_info, server_addr, progress):
        if server_info and server_addr:
            self.message.setText(
                '正在扫描服务器：%s(%s:%s)' %
                (server_info.get('name'), server_addr[0], server_addr[1])
            )
        self.progress.setValue(progress)
        if progress >= 100:
            self.setState(STATE_DONE)

    def onScanCb(self, ret):
        if not ret:
            return
        self.scan_list.append(ret)
        row_count = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_count)
        name_item = QTableWidgetItem(ret['name'])
        name_item._data = ret
        self.tableWidget.setItem(row_count, 0, name_item)
        self.tableWidget.setItem(
            row_count, 1, QTableWidgetItem('%s:%s' % (ret['ip'], ret['port']))
        )
        self.tableWidget.setItem(row_count, 2, QTableWidgetItem(str(ret['score'])))

        del_btn = QPushButton(self.main_window)
        del_btn.setText('删除')
        del_btn.setFont(QFont('Microsoft YaHei', 10, 75))
        del_btn.setStyleSheet('QPushButton{margin:3px;}')
        del_btn.clicked.connect(functools.partial(self.DelRow, name_item))
        self.tableWidget.setCellWidget(row_count, 3, del_btn)

    def DelRow(self, name_item):
        model_item = self.tableWidget.indexFromItem(name_item)
        if model_item:
            row = model_item.row()
            self.tableWidget.removeRow(row)
        self.scan_list.remove(name_item._data)

    def onExportClick(self):
        date = datetime.datetime.strftime(datetime.datetime.now(), '%Y_%m_%d')
        out_put = './L4D2_IP拦截规则_%s.json' % date
        ret = {'ver': '5.0', 'tag': 'ipblacklist', 'data': self.createIpBlackList()}
        with open(out_put, 'w', encoding=settings.ENCODE) as f:
            f.write(json.dumps(ret, ensure_ascii=False, indent=2))
            f.close()
        abs_path = os.path.abspath(out_put)
        reply = QMessageBox.information(
            self.main_window, '导出成功', '文件路径:%s\n是否打开文件所在文件夹?' % abs_path,
            QMessageBox.Ok, QMessageBox.Cancel
        )
        if reply == QMessageBox.Ok:
            os.startfile(os.path.abspath(os.path.dirname(abs_path)))

    def createIpBlackList(self):
        if not self.scan_list:
            return []
        ret = []
        ip_set = set()
        for idx, data in enumerate(self.scan_list):
            ip = data['ip']
            if ip in ip_set:
                continue
            ip_set.add(ip)
            ret.append(
                {
                    'id': idx,
                    'raddr': ip,
                    'tmp_field_sel': True,
                    'memo': data['name']
                }
            )
        return ret

    def setState(self, state):
        self.state = state
        self.refreshButton()

    def refreshButton(self):
        if self.state == STATE_IDLE:
            self.message.setText('当前状态：空闲')
            self.export_button.setEnabled(False)
        elif self.state == STATE_SCANING:
            self.progress.reset()
            self.message.setText('当前状态：运行中')
            self.scan_button.setText('停止')
            self.export_button.setEnabled(False)
        elif self.state == STATE_DONE:
            self.message.setText('当前状态：完成')
            self.scan_button.setText('重新扫描')
            self.export_button.setEnabled(True)
            self.tableWidget.sortItems(2, Qt.SortOrder.DescendingOrder)
