#!/bin/bash

# SNMP 配置
HOST="$1"  # 目标设备的IP地址

# SNMPv3 认证信息
USER="test_user"  # SNMP 用户名
AUTH_PROTO="SHA"  # 认证协议
AUTH_PASS="Gzbbn@cloud"  # 认证密码
PRIV_PROTO="AES"  # 加密协议
PRIV_PASS="Gzbbn@Cloud"  # 加密密码

# OID 定义：CPU使用率
CPU_USEAGE_1="1.3.6.1.4.1.34774.4.1.23.5.2.1.8.2.48.65"  # CPU 1 使用率 OID
CPU_USEAGE_2="1.3.6.1.4.1.34774.4.1.23.5.2.1.8.2.48.66"  # CPU 2 使用率 OID

# SNMP 获取 CPU 使用率（SNMPv3）
cpu_usage_1=$(snmpget -v 3 -l authPriv -u $USER -a $AUTH_PROTO -A $AUTH_PASS -x $PRIV_PROTO -X $PRIV_PASS $HOST $CPU_USEAGE_1 | awk -F ': ' '{print $2}' | sed 's/[^0-9]*//g')
cpu_usage_2=$(snmpget -v 3 -l authPriv -u $USER -a $AUTH_PROTO -A $AUTH_PASS -x $PRIV_PROTO -X $PRIV_PASS $HOST $CPU_USEAGE_2 | awk -F ': ' '{print $2}' | sed 's/[^0-9]*//g')

# 检查数据是否有效
if [ -z "$cpu_usage_1" ] || [ -z "$cpu_usage_2" ]; then
  echo "无法获取 CPU 使用率数据"
  exit 1
fi

# 计算平均 CPU 使用率（这里可以根据实际情况修改计算方式）
average_cpu_usage=$(echo "($cpu_usage_1 + $cpu_usage_2) / 2" | bc)

echo $average_cpu_usage
