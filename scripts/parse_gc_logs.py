#!/usr/bin/env python3
import os
import re
import csv

root = '../data/raw_logs'
out_csv = '../data/parsed/metrics.csv'

with open(out_csv, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        'benchmark','gc','heap','run',
        'max_pause_ms','avg_pause_ms','throughput_pct','gc_count'
    ])
    writer.writeheader()
    for bm in os.listdir(root):
        for gc in os.listdir(os.path.join(root, bm)):
            for heap in os.listdir(os.path.join(root, bm, gc)):
                path = os.path.join(root, bm, gc, heap)
                for f in os.listdir(path):
                    if f.endswith('.log'):
                        run = f.split('_')[1].split('.')[0]
                        text = open(os.path.join(path, f)).read()
                        pauses = [float(m) for m in re.findall(r'Pause \d+: (\d+\.\d+) ms', text)]
                        # пример parsing
                        maxp = max(pauses)
                        avgp = sum(pauses)/len(pauses)
                        th = float(re.search(r'Throughput: (\d+\.\d+)%', text).group(1))
                        gc_cnt = len(pauses)
                        writer.writerow({
                            'benchmark': bm,
                            'gc': gc,
                            'heap': heap,
                            'run': run,
                            'max_pause_ms': maxp,
                            'avg_pause_ms': avgp,
                            'throughput_pct': th,
                            'gc_count': gc_cnt,
                        })