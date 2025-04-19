#!/bin/bash

# SNMP 配置
HOST="$1"  # 目标设备的IP地址

# SNMPv3 认证信息
USER="monitor_user"  # SNMP 用户名
AUTH_PROTO="SHA"  # 认证协议
AUTH_PASS="Aa123456!"  # 认证密码
PRIV_PROTO="AES"  # 加密协议
PRIV_PASS="Aa123456!!"  # 加密密码
BASE_OID="1.3.6.1.4.1.34774.4.1.23.5.3.1.2"    # 华为存储PSU信息私有OID
CACHE="/tmp/psu_oid_cache.txt"

# 获取 SNMP 数据
snmpwalk -v3 -u "$USER" -l authPriv -a "$AUTH" -A "$AUTH_PASS" -x "$PRIV" -X "$PRIV_PASS" "$HOST" "$BASE_OID" > "$CACHE" 2>/dev/null

# 初始化 JSON
json='{"data": ['

first=true
while IFS= read -r line; do
    psu_name=$(echo "$line" | awk -F ' = STRING: ' '{print $2}' | tr -d '"' | tr -d '\r')
    if [ -n "$psu_name" ]; then
        if $first; then
            first=false
        else
            json="${json}, "
        fi
        json="${json}{\"{#PSU_NAME}\": \"$psu_name\"}"
    fi
done < <(grep 'STRING:' "$CACHE")

json="${json}]}"

# 输出 JSON（确保无语法错误）
output=$(echo "$json" | python -m json.tool)
echo "echo '$output'"
