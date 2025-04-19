# OceanStor-5000-zabbix-4.0-templates

## 采集基本信息

```bash
# 发现磁盘
bash discover_disk.sh 172.16.100.100 > disk_name.sh && chmod +x disk_name.sh

# 发现以太网光口
bash discover_eth.sh 172.16.100.100 > eth_name.sh && chmod +x eth_name.sh

# 发现PSU
bash discover_psu.sh 172.16.100.100 > psu_name.sh && chmod +x psu_name.sh
```

## 采集 snmp 信息

```bash
# 信息采集脚本（centos默认python环境为python2.7）
python2 get_snmp_info.py 172.16.100.100 > snmp_info_all.json

# 查看帮助
[root@localhost ~]# python get_snmp_info.py -h
usage: get_snmp_info.py [-h] <host>

SNMP PSU、DISK、ETH、FC 信息采集器

positional arguments:
  <host>      目标设备IP地址

optional arguments:
  -h, --help  show this help message and exit

```

## 导入 zabbix UserParameters

```bash
mv os5000.conf /etc/zabbix/zabbix_agentd.d/
systemctl restart zabbix_agentd
```

## zabbix 自动发现示例：

```bash
# 自动发现磁盘
zabbix_get -s 127.0.0.1 -k 'os5000.disk.172.16.100.100.discovery'
{
    "data": [
        {
            "{#DISK_NAME}": "CTE0.0"
        },
        {
            "{#DISK_NAME}": "CTE0.1"
        },
        ...
    ]
}

```

## zabbix 信息采集示例：

```bash
zabbix_get -s 127.0.0.1 -k 'os5000.disk.info[172.16.100.100,health,"CTE0.0"]'
1

zabbix_get -s 127.0.0.1 -k 'os5000.disk.info[172.16.100.100,status,"CTE0.0"]'
27
```
