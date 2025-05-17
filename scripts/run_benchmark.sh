#!/usr/bin/env bash
set -euxo pipefail

benchmark="$1"
gc_name="$2"
gc_flag="$3"
heap_size="$4"
runs="$5"
jar="../dacapo/dacapo-23.11-MR2-chopin.jar"

outdir="../data/raw_logs/${benchmark}/${gc_name}/${heap_size}"
mkdir -p "$outdir"

for i in $(seq 1 "$runs"); do
  logfile="$outdir/run_${i}.log"
  echo "Running ${benchmark} | ${gc_name} | ${heap_size} | run #${i}"
  
  set +e  # απενεργοποίηση 'exit on error' προσωρινά
  java -Xms${heap_size} -Xmx${heap_size} $gc_flag -jar "$jar" -s "$benchmark" > "$outdir/out_${i}.txt" 2>&1
  status=$?
  set -e  # ενεργοποίηση ξανά

  if [ $status -ne 0 ]; then
    echo "Run #${i} failed with status $status"
  fi
done
