#!/usr/local/python3.6/bin/python3
# -*- coding: utf-8 -*-

# @File    :   dynamic_inventory.py
# @Version :   1.0
# @Author  :   yanghongjin
# @Email   :   xx
# @Time    :   2020/07/09 13:52:21
'''
  Dynamic inventory for ansible, query hosts and groups and vars from mysql.
  Using dynamic organization to manage servers.
'''
import argparse
import pymysql

from app.config import *

MYSQL = {
    'host': '', 
    'port': 3306,
    'user': '',
    'password': '',
    'db': ''
}


class DynamicInventory():
    def __init__(self):
        self.hosts = {
        '_meta': {'hostvars': {}},
        'all': {'hosts': []}
        }
        self.args = ""
        self.get_hosts()

    def query_servers(self):
        '''
        Query all servers and groups
        '''
        sql = '''select s.ip, g.group_name, h.ansible_python_interpreter 
            from t_server as s 
            left join t_server_group as sg on sg.server_id=s.server_id 
            left join t_group as g on sg.group_id=g.group_id 
            left join t_host_vars as h on s.os=h.os_version 
            where s.is_delete=0 and g.is_delete=0
            '''
        try:
            conn = pymysql.connect(host=MYSQL['host'], port=int(MYSQL['port']), \
                user=MYSQL['user'], passwd=MYSQL['password'], db=MYSQL['db'], \
                charset='utf8')
            cur = conn.cursor()
            cur.execute(sql)
            result = cur.fetchall()
            cur.close()
            conn.close()
            return result
        except Exception as e:
            print(repr(e))
            return

    def get_hosts(self):
        '''
        Create dict of servers
        '''
        servers = self.query_servers()
        if not servers:
            pass
        else:
            for item in servers:
                if item[1] not in self.hosts:
                    self.hosts.update({item[1]: {'hosts': [], 'vars': {}}})
                self.hosts[item[1]]['hosts'].append(item[0])
                if item[2]:
                    ansible_python_interpreter = item[2]
                else:
                    ansible_python_interpreter = '/usr/bin/python'
                self.hosts['_meta']['hostvars'].update({
                        item[0]: {
                            'ansible_python_interpreter': ansible_python_interpreter
                        }
                    })
                # self.hosts['all']['hosts'].append(item[0])

    def list_hosts(self):
        '''
        Print hosts
        '''
        return self.hosts

    def get_host_vars(self, host):
        '''
        Get vars of host
        '''
        for k, v in self.hosts.items():
            if host in v['hosts']:
                return v.get('vars', {})
            else:
                return {}
        else:
            return {}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ansible dynamic inventory")
    parser.add_argument('--list', help="Ansible inventory of all of the groups",
    action="store_true")
    parser.add_argument('--host', help="vars of a specified host", action="store", type=str)
    args = parser.parse_args()
    di = DynamicInventory()
    if args.list:
        print(di.list_hosts())
    elif args.host:
        print(di.get_host_vars(args.host))
    else:
        print('input -h to show usage.')
