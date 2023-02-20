# -*- coding: utf-8 -*-
# created by fengweichao on 2023/2/20
import rpg_filter
import steam.game_servers as gs
import datetime
import json
import os


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


ret = rpg_filter.scan(
    rpg_filter.strKey2List(rpg_filter.DEFAULT_KEYS), 10000, gs.MSRegion.World
)
if ret:
    date = datetime.datetime.strftime(datetime.datetime.now(), '%Y_%m_%d')
    if not os.path.isdir('./IP_BLOCKER'):
        os.mkdir('./IP_BLOCKER')
    out_put = './IP_BLOCKER/L4D2_IP_BLOCKER_%s.json' % date
    ret = {'ver': '5.0', 'tag': 'ipblacklist', 'data': createIpBlackList(ret)}
    with open(out_put, 'w', encoding='utf-8') as f:
        f.write(json.dumps(ret, ensure_ascii=False, indent=2))
        f.close()
