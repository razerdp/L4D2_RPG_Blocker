# -*- coding: utf-8 -*-
# created by fengweichao on 2023/2/20
import steam.game_servers as gs
import datetime
import json
import os
import traceback
from fuzzywuzzy import fuzz

DEFAULT_KEYS = '弑神巅峰;RPG;杀戮世界;橡子杀戮;幻想杀戮;天域;午夜狂欢;猎人;帝王;风花雪月;暗黑之魂;无法逃脱;AK0048;梦幻天堂;腐尸之地;紫荆之巅;上帝之手;经典怀旧服;无人永生;星缘天空;破晓;混乱纪元;原生之初'
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
    print(server_addr)
    if not server_addr:
        return None
    ret = None
    server_info = None
    try:
        server_info = gs.a2s_info(server_addr)
        if server_info:
            name = server_info.get('name')
            if name:
                print(name)
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


def scan(
    checker_keys,
    count,
    region=gs.MSRegion.Asia,
):
    result = []
    checker_keys = list(checker_keys)
    print(checker_keys)
    cur_idx = 0
    try:
        for server_addr in gs.query_master(
            r'\appid\550', max_servers=count, region=region, timeout=1
        ):
            cur_idx += 1
            ret, server_info = serverInfo(checker_keys, server_addr)
            if ret:
                print(ret)
                result.append(ret)
    except:
        traceback.print_exc()
    return result


def createIpBlackList(scan_list):
    if not scan_list:
        return []
    ret = []
    ip_set = set()
    for idx, data in enumerate(scan_list):
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


ret = scan(strKey2List(DEFAULT_KEYS), 8000, gs.MSRegion.World)
if ret:
    date = datetime.datetime.strftime(datetime.datetime.now(), '%Y_%m_%d')
    if not os.path.isdir('./IP_BLOCKER'):
        os.mkdir('./IP_BLOCKER')
    out_put = './IP_BLOCKER/L4D2_IP_BLOCKER_%s.json' % date
    ret = {'ver': '5.0', 'tag': 'ipblacklist', 'data': createIpBlackList(ret)}
    with open(out_put, 'w', encoding='utf-8') as f:
        f.write(json.dumps(ret, ensure_ascii=False, indent=2))
        f.close()
else:
    print('no content')
