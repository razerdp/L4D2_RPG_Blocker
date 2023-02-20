# -*- coding: utf-8 -*-
# created by fengweichao on 2023/2/16
import asyncio
import functools
import os
import sys

import PySide2
import qasync
import qdarkstyle
from PySide2.QtWidgets import QApplication

import main_window

dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


async def main():
    def close_future(future, loop):
        loop.call_later(10, future.cancel)
        future.cancel()

    loop = asyncio.get_event_loop()
    future = asyncio.Future()

    app = QApplication.instance()
    if hasattr(app, "aboutToQuit"):
        getattr(app,
                "aboutToQuit").connect(functools.partial(close_future, future, loop))
    # app.setStyle(PySide2.QtWidgets.QStyleFactory.create('Fusion'))
    window = main_window.MainWindow()
    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    # or in new API
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside2'))
    window.show()
    await future
    return True


if __name__ == '__main__':
    try:
        qasync.run(main())
    except asyncio.CancelledError:
        sys.exit(0)
