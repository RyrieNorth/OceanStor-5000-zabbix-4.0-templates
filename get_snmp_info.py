# -*- coding: utf-8 -*-
#!/usr/bin/env python2
import subprocess
import json
import argparse
import threading
import time

def run_snmpwalk(host, oid, snmp_config):
    cmd = [
        'snmpwalk', '-v3',
        '-u', snmp_config['user'],
        '-l', snmp_config['level'],
        '-a', snmp_config['auth_protocol'], '-A', snmp_config['auth_pass'],
        '-x', snmp_config['priv_protocol'], '-X', snmp_config['priv_pass'],
        host, oid
    ]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
        return output.splitlines()
    except subprocess.CalledProcessError as e:
        print "SNMP Error:\n{}".format(e.output)
        return []

def parse_snmp_output(output_lines, parent_oid, result_dict, value_type='STRING'):
    parent_oid_list = parent_oid.split('.')
    for line in output_lines:
        if ' = ' not in line:
            continue
        oid_part, value_part = line.split(' = ', 1)
        oid = oid_part.replace('SNMPv2-SMI::enterprises.', '1.3.6.1.4.1.')
        oid_parts = oid.split('.')
        if oid_parts[:len(parent_oid_list)] != parent_oid_list:
            continue
        instance = '.'.join(oid_parts[len(parent_oid_list):])
        try:
            if value_type == 'STRING':
                value = value_part.split('"')[1]
            else:
                value = value_part.split(': ')[1].strip()
            result_dict[instance] = value
        except IndexError:
            print "解析失败: {}".format(line)
            continue

def collect_subsystem(label, oids, host, output_dict, snmp_config):
    datasets = {
        'names': (oids['name'], 'STRING'),
        'health': (oids['health'], 'GAUGE'),
        'status': (oids['status'], 'GAUGE')
    }

    results = {}
    for key in datasets:
        oid, vtype = datasets[key]
        results[key] = {}
        parse_snmp_output(run_snmpwalk(host, oid, snmp_config), oid, results[key], vtype)

    subsystem_data = {'health': {}, 'status': {}}
    for instance in results['names']:
        name = results['names'][instance]
        subsystem_data['health'][name] = results['health'].get(instance, 'N/A')
        subsystem_data['status'][name] = results['status'].get(instance, 'N/A')

    output_dict[label] = subsystem_data

def parse_args():
    parser = argparse.ArgumentParser(description='SNMP PSU、DISK、ETH、FC 信息采集器')

    # SNMP 认证参数，附带默认值
    parser.add_argument('-u', '--user', default='test_user', help='SNMP v3 用户名')
    parser.add_argument('-l', '--level', default='authPriv', help='认证级别：noAuthNoPriv、authNoPriv、authPriv')
    parser.add_argument('-a', '--auth_protocol', default='SHA', help='认证协议：MD5 或 SHA')
    parser.add_argument('-A', '--auth_pass', default='Aa123456!', help='认证密码')
    parser.add_argument('-x', '--priv_protocol', default='AES', help='加密协议：DES 或 AES')
    parser.add_argument('-X', '--priv_pass', default='Aa123456!', help='加密密码')

    parser.add_argument('--delay', type=float, default=1.0, help='线程启动间隔时间（秒）')

    parser.add_argument('host', metavar='<host>', help='目标设备IP地址')

    return parser.parse_args()

OID_GROUPS = {
    'PSU': {
        'name': '1.3.6.1.4.1.34774.4.1.23.5.3.1.2',
        'health': '1.3.6.1.4.1.34774.4.1.23.5.3.1.3',
        'status': '1.3.6.1.4.1.34774.4.1.23.5.3.1.4'
    },
    'DISK': {
        'name': '1.3.6.1.4.1.34774.4.1.23.5.1.1.4',
        'health': '1.3.6.1.4.1.34774.4.1.23.5.1.1.2',
        'status': '1.3.6.1.4.1.34774.4.1.23.5.1.1.3'
    },
    'ETH': {
        'name': '1.3.6.1.4.1.34774.4.1.23.5.8.1.2',
        'health': '1.3.6.1.4.1.34774.4.1.23.5.8.1.3',
        'status': '1.3.6.1.4.1.34774.4.1.23.5.8.1.4',
    },
    'FC': {
        'name': '1.3.6.1.4.1.34774.4.1.23.5.9.1.2',
        'health': '1.3.6.1.4.1.34774.4.1.23.5.9.1.3',
        'status': '1.3.6.1.4.1.34774.4.1.23.5.9.1.4',
    },
}

if __name__ == "__main__":
    args = parse_args()

    snmp_config = {
        'user': args.user,
        'level': args.level,
        'auth_protocol': args.auth_protocol,
        'auth_pass': args.auth_pass,
        'priv_protocol': args.priv_protocol,
        'priv_pass': args.priv_pass
    }

    final_data = {}
    threads = []

    for label, oids in OID_GROUPS.items():
        t = threading.Thread(target=collect_subsystem, args=(label, oids, args.host, final_data, snmp_config))
        threads.append(t)
        t.start()
        time.sleep(args.delay)  # 加延迟防止瞬间并发太多请求

    for t in threads:
        t.join()

    print json.dumps(final_data, indent=2)
