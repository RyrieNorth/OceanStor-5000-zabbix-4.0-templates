# -*- coding: utf-8 -*-
#!/usr/bin/env python2
import subprocess
import json
import argparse
import threading

def run_snmpwalk(host, oid):
    cmd = [
        'snmpwalk', '-v3', '-u', 'test_user', '-l', 'authPriv',
        '-a', 'SHA', '-A', 'Gzbbn@cloud', '-x', 'AES', '-X', 'Gzbbn@Cloud',
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

def collect_subsystem(label, oids, host, output_dict):
    datasets = {
        'names': (oids['name'], 'STRING'),
        'health': (oids['health'], 'GAUGE'),
        'status': (oids['status'], 'GAUGE')
    }

    results = {}
    for key in datasets:
        oid, vtype = datasets[key]
        results[key] = {}
        parse_snmp_output(run_snmpwalk(host, oid), oid, results[key], vtype)

    subsystem_data = {'health': {}, 'status': {}}
    for instance in results['names']:
        name = results['names'][instance]
        subsystem_data['health'][name] = results['health'].get(instance, 'N/A')
        subsystem_data['status'][name] = results['status'].get(instance, 'N/A')

    output_dict[label] = subsystem_data

def parse_args():
    parser = argparse.ArgumentParser(description='SNMP PSU、DISK、ETH、FC 信息采集器')
    parser.add_argument('host', metavar='<host>', help='目标设备IP地址')
    return parser.parse_args()

# 👇 OID组定义：两个子系统
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

    final_data = {}
    threads = []

    for label, oids in OID_GROUPS.items():
        t = threading.Thread(target=collect_subsystem, args=(label, oids, args.host, final_data))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print json.dumps(final_data, indent=2)

