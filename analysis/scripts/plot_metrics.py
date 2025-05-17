#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('../data/parsed/metrics.csv')

# Παράδειγμα: μέση max παύση ανά GC
grouped = df.groupby('gc')['max_pause_ms'].mean().reset_index()

plt.figure()
plt.bar(grouped['gc'], grouped['max_pause_ms'])
plt.ylabel('Avg Max Pause (ms)')
plt.title('Mean Max Pause per GC')
plt.savefig('../data/reports/max_pause_comparison.png')