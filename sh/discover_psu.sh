#!/bin/bash

USER="test_user"
AUTH="SHA"
AUTH_PASS="Gzbbn@cloud"
PRIV="AES"
PRIV_PASS="Gzbbn@Cloud"
HOST="$1"
BASE_OID="1.3.6.1.4.1.34774.4.1.23.5.3.1.2"
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
echo "$json" | python -m json.tool
