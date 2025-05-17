#!/usr/bin/env bash
set -euo pipefail

# Συγκεντρώνει raw logs σε μονάδα
root="../data/raw_logs"
for bm in "$root"/*; do
  # παραδείγματα: data/raw_logs/avrora/Shenandoah/4G/run_1.log
  echo "Found benchmark logs under $bm"
done
# (εδώ μπορεί να γίνει απλά mkdir -p & mv αν χρειάζεται grouping)