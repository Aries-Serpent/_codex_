#!/usr/bin/env bash
# imds_aggregate_json.sh
# Aggregate multiple diagnostic_results.json files into a single summary table.
# ENERGY 5/5

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "jq required" >&2
  exit 1
fi

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <json_file1> [json_file2 ...]" >&2
  exit 1
fi

TMP=$(mktemp)
echo "host,status,apply,dry_run,recommendation_count,error_count" > "$TMP"

for f in "$@"; do
  if [ ! -f "$f" ]; then
    echo "Skipping missing file: $f" >&2
    continue
  fi
  host=$(jq -r '.script' "$f")
  status=$(jq -r '.status' "$f")
  apply=$(jq -r '.apply' "$f")
  dry=$(jq -r '.dry_run' "$f")
  rec_count=$(jq '.recommendations | length' "$f")
  err_count=$(jq '.error_reasons | length' "$f")
  echo "${host},${status},${apply},${dry},${rec_count},${err_count}" >> "$TMP"
done

echo "Aggregate CSV:"
cat "$TMP"

# Optional JSON matrix
jq -n --slurpfile rows <(tail -n +2 "$TMP" | jq -R 'split(",") | {
    script: .[0],
    status: .[1],
    apply: (.[2]=="true"),
    dry_run: (.[3]=="true"),
    recommendation_count: (.[4]|tonumber),
    error_count: (.[5]|tonumber)
  }') '{aggregate: $rows}' > aggregate_imds_matrix.json

echo "JSON matrix written: aggregate_imds_matrix.json"
