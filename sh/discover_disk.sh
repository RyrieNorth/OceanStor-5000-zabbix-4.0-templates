#!/bin/bash

USER="minitor_user"    # SNMP (USM) 用户名称
AUTH="SHA"            # SNMP (USM) 鉴权加密方式
AUTH_PASS="Aa123456!"    #SNMP (USM) 鉴权密码
PRIV="AES"        # SNMP (USM) 数据加密方式
PRIV_PASS="Aa123456!"    # SNMP (USM) 加密密码
HOST="$1"
BASE_OID="1.3.6.1.4.1.34774.4.1.23.5.1.1.4"  # 华为存储磁盘信息私有OID
CACHE="/tmp/disk_oid_cache.txt"

# 获取 SNMP 数据
snmpwalk -v3 -u "$USER" -l authPriv -a "$AUTH" -A "$AUTH_PASS" -x "$PRIV" -X "$PRIV_PASS" "$HOST" "$BASE_OID" > "$CACHE" 2>/dev/null

# 初始化 JSON
json='{"data": ['

first=true
while IFS= read -r line; do
    disk_name=$(echo "$line" | awk -F ' = STRING: ' '{print $2}' | tr -d '"' | tr -d '\r')
    if [ -n "$disk_name" ]; then
        if $first; then
            first=false
        else
            json="${json}, "
        fi
        json="${json}{\"{#DISK_NAME}\": \"$disk_name\"}"
    fi
done < <(grep 'STRING:' "$CACHE")

json="${json}]}"

# 输出 JSON
output=$(echo "$json" | python -m json.tool)
echo "echo '$output'"
