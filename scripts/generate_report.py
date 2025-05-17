#!/usr/bin/env python3
import pandas as pd

df = pd.read_csv('../data/parsed/metrics.csv')
# Ομαδοποίηση και pivot
pivot = df.pivot_table(
    index=['benchmark','gc','heap'],
    values=['max_pause_ms','avg_pause_ms','throughput_pct'],
    aggfunc='mean'
)

html = pivot.to_html()
with open('../data/reports/final_report.html','w') as f:
    f.write('<html><body>')
    f.write('<h1>GC Benchmark Report</h1>')
    f.write(html)
    f.write('</body></html>')
print('Report generated at data/reports/final_report.html')