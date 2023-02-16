# -*- coding: utf-8 -*-
# created by Vinc on 2023/2/16
# https://github.com/ValvePython/steam
import asyncio
import sys
import threading

import qasync
import steam.game_servers as gs
from fuzzywuzzy import fuzz

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

DEFAULT_KEYS = 'RPG;杀戮世界;橡子杀戮;幻想杀戮;天域;午夜狂欢;猎人;帝王;风花雪月;暗黑之魂;无法逃脱;AK0048;梦幻天堂;腐尸之地;紫荆之巅;上帝之手;经典怀旧服;无人永生;星缘天空;破晓;混乱纪元;原生之初'
DEFAULT_RATIO = 25


def strKey2List(str_keys):
    str_keys = str_keys.replace('；', ';')
    str_keys = str_keys.replace('：', ':')
    ret = []
    for k in str_keys.split(';'):
        ratio = DEFAULT_RATIO
        if ':' in k:
            name, t_r = k.split(':')
            try:
                ratio = int(t_r)
            except:
                ratio = DEFAULT_RATIO
        else:
            name = k
        if name:
            ret.append((name, int(max(0, min(ratio, 100)))))
    return ret


def serverInfo(checker_keys, server_addr):
    if not server_addr:
        return None
    ret = None
    server_info = None
    try:
        server_info = gs.a2s_info(server_addr)
        if server_info:
            name = server_info.get('name')
            if name:
                for check_name, check_ratio in checker_keys:
                    score = fuzz.ratio(name, check_name)
                    if score >= check_ratio:
                        ret = {
                            'ip': server_addr[0],
                            'port': server_addr[1],
                            'score': score,
                            'name': name
                        }
                        break
    except:
        pass
    return ret, server_info


def scan(checker_keys, count, progress_cb=None, ret_cb=None, **kwargs):
    result = []
    checker_keys = list(checker_keys)
    cur_idx = 0
    stop_event = kwargs.get('stop_event')
    try:
        for server_addr in gs.query_master(
            r'\appid\550', max_servers=count, region=gs.MSRegion.Asia, timeout=1
        ):
            if stop_event and stop_event.isSet():
                progress_cb and progress_cb(None, None, None, 100)
                return
            cur_idx += 1
            ret, server_info = serverInfo(checker_keys, server_addr)
            ret_cb and ret_cb(ret)
            if ret:
                result.append(ret)
            progress_cb and progress_cb(
                ret, server_info, server_addr, int(100.0 * cur_idx / count)
            )
    except:
        progress_cb and progress_cb(None, None, None, 100)


def backGroundScan(checker_keys, count, progress_signal, ret_signal):
    stop_event = threading.Event()

    def _pcb(filter_ret, server_info, server_addr, progress):
        progress_signal.emit(filter_ret, server_info, server_addr, progress)

    def _rcb(ret):
        ret_signal.emit(ret)

    thread = threading.Thread(
        target=scan,
        args=(checker_keys, count, _pcb, _rcb),
        kwargs={'stop_event': stop_event}
    )
    thread.start()
    return stop_event
