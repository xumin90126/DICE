#!/bin/bash
# usage: fetch.sh <owner> <repo> <branch> <relpath> <outdir>
owner=$1; repo=$2; branch=$3; rel=$4; out=$5
mkdir -p "$(dirname "$out")"
for i in 1 2 3; do
  if curl -sS --max-time 40 -o "$out" "https://raw.githubusercontent.com/$owner/$repo/$branch/$rel"; then
    if head -c 200 "$out" | grep -q '^<!DOCTYPE\|^<html\|404: Not Found'; then rm -f "$out"; echo "FAIL(marker) $rel"; exit 0; fi
    echo "OK $rel -> $out ($(wc -c < "$out")B)"; exit 0
  fi
  sleep 1
done
echo "FAIL $rel"; exit 0
