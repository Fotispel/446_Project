#!/usr/bin/env bash
#set -euo pipefail
set -x

benchmarks=(avrora jython lusearch lusearch-lr sunflow tomcat tradebeans tradesoap)
gcs_name=(Shenandoah G1 ZGC PS)
gcs_flag=(-XX:+UseShenandoahGC -XX:+UseG1GC -XX:+UseZGC -XX:+UseParallelGC)
heap_sizes=(4G 8G 12G)
runs_per_config=3

project_root="$(cd "$(dirname "$0")/.." && pwd)"

for bm in "${benchmarks[@]}"; do
  for i in "${!gcs_name[@]}"; do
    gc_name="${gcs_name[$i]}"
    gc_flag="${gcs_flag[$i]}"
    for heap in "${heap_sizes[@]}"; do
      echo "→ Benchmark: $bm | GC: $gc_name | Heap: $heap"
      bash "$project_root/scripts/run_benchmark.sh" \
        "$bm" "$gc_name" "$gc_flag" "$heap" "$runs_per_config"
    done
  done
done
