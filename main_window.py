# -*- coding: utf-8 -*-
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import settings
import rpg_filter
import main_action
import scan_settings
import functools
import requests
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        if not self.objectName():
            self.setObjectName('main_window')
        self.setWindowTitle('L4D2火绒屏蔽IP扫描生成器')
        self.resize(1280, 720)
        self.initToolBar()
        # 主界面
        main_widget = QWidget(self)
        self.root = QStackedLayout()
        self.panel_action = main_action.Panel(self)
        self.root.addWidget(self.panel_action)
        self.panel_setting = scan_settings.Panel(self)
        self.root.addWidget(self.panel_setting)
        main_widget.setLayout(self.root)
        self.setCentralWidget(main_widget)
        self.root.setCurrentIndex(0)
        self.checkUpdate()

    def initToolBar(self):
        btn_scan = self.createButton('扫描')
        btn_setting = self.createButton('设置')
        btn_scan.clicked.connect(functools.partial(self.showPanel, 0))
        btn_setting.clicked.connect(functools.partial(self.showPanel, 1))

        tooBar = QToolBar(self)
        tooBar.addWidget(btn_scan)
        tooBar.addWidget(btn_setting)
        self.addToolBar(Qt.LeftToolBarArea, tooBar)

    def createButton(self, txt):
        icon = QApplication.style().standardIcon(QStyle.SP_DesktopIcon)
        btn = QToolButton(self)
        btn.setText(txt)
        btn.setIcon(icon)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        return btn

    def showPanel(self, *args):
        idx = args[0]
        if 0 <= idx < self.root.count():
            self.root.setCurrentIndex(idx)

    def checkUpdate(self):
        ver = settings.GetSettings('version', '1.0')
        response = requests.get(
            'https://api.github.com/repos/razerdp/L4D2_RPG_Blocker/releases/latest'
        )
        data = json.loads(response.text)
