#!/bin/bash
for url in "$@"; do
  echo "==== $url"
  curl -sS --max-time 30 "$url" | python3 -c 'import sys,json;d=json.load(sys.stdin);[print(x["type"][0],x["name"],x.get("size","")) for x in d]' 2>/dev/null || echo "(err)"
done
