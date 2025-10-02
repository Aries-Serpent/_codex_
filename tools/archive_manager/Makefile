ROOT ?= .
JSONL ?= code_archive.jsonl
SQLITE ?= metadata.sqlite
PARQUET ?= code_blobs.parquet
DELTA_DIR ?= .
PY ?= python
TOMBS_CODE ?= tombstones_code.jsonl
TOMBS_LOGS ?= tombstones_logs.jsonl

.PHONY: build update compact query verify vacuum

build:
$(PY) archive_manager.py build --root $(ROOT) --jsonl $(JSONL) --sqlite $(SQLITE) --parquet $(PARQUET) --deltas-dir $(DELTA_DIR) --gzip-jsonl --workers auto -v

update:
$(PY) archive_manager.py update --root $(ROOT) --jsonl $(JSONL) --sqlite $(SQLITE) --parquet $(PARQUET) --deltas-dir $(DELTA_DIR) --tombstones-code $(TOMBS_CODE) --tombstones-logs $(TOMBS_LOGS) --gzip-tombstones --track-deletes --workers auto -v

compact:
$(PY) archive_manager.py compact --jsonl $(JSONL) --sqlite $(SQLITE) --parquet $(PARQUET) --deltas-dir $(DELTA_DIR) -v

query:
$(PY) archive_manager.py query --jsonl $(JSONL) --sqlite $(SQLITE) --parquet $(PARQUET) --deltas-dir $(DELTA_DIR) --sql "$(SQL)" -v

verify:
$(PY) archive_manager.py verify --jsonl $(JSONL) --sqlite $(SQLITE) --parquet $(PARQUET) --deltas-dir $(DELTA_DIR) -v

vacuum:
$(PY) archive_manager.py vacuum --tombstones-code $(TOMBS_CODE) --tombstones-logs $(TOMBS_LOGS) $(if $(BEFORE),--before $(BEFORE),) $(if $(SUMMARY),--summary,) $(if $(GZIP),--gzip-tombstones,) -v
