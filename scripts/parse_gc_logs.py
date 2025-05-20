import re
import os
import csv

def parse_g1_pauses(content):
    pauses = []  # ms
    for line in content.splitlines():
        unified_match = re.search(r"\[info\s+\]\[gc\s+\].*?Pause(?:.*?)\s+(\d+\.\d+)ms", line)
        if unified_match:
            pauses.append(float(unified_match.group(1)))
            continue
    return pauses


def parse_parallel_pauses(content):
    pauses = []  # ms
    for line in content.splitlines():
        # Unified Logging Format (JDK 9+)
        unified_match = re.search(r"\[info\s+\]\[gc\s+\].*?Pause(?:.*?)\s+(\d+\.\d+)ms", line)
        if unified_match:
            pauses.append(float(unified_match.group(1)))
            continue
    return pauses


def parse_zgc_pauses(content):
    pauses = [] # ms
    for line in content.splitlines():
        summary_match = re.search(r"GC\(\d+\) Pauses: Mark (\d+\.\d+)ms, Relocate (\d+\.\d+)ms", line)
        if summary_match:
            pauses.append(float(summary_match.group(1))) # Mark Pause
            pauses.append(float(summary_match.group(2))) # Relocate Pause
            continue
        phase_match = re.search(r"\[gc,phases\s*\] GC\(\d+\) Pause (?:Mark Start|Mark End|Relocate Start)\s+(\d+\.\d+)ms", line)
        if phase_match: pauses.append(float(phase_match.group(1)))
    return pauses

def parse_shenandoah_pauses(content):
    pauses = [] # ms
    for line in content.splitlines():
        match = re.search(r"GC\(\d+\) Pause (?:Init Mark|Final Mark|Init Update Refs|Final Update Refs|Degenerated|Full)\s+.*?(\d+\.\d+)ms", line)
        if match: pauses.append(float(match.group(1)))
    return pauses

def process_gc_logs(gc_log_dir, output_csv_file):
    results = []
    for filename in os.listdir(gc_log_dir):
        if not (filename.startswith("gc_") and filename.endswith(".log")):
            continue
        filepath = os.path.join(gc_log_dir, filename)
        try:
            gc_type, heap_size, benchmark = filename.replace("gc_", "").replace(".log", "").split("_")
        except ValueError:
            print(f"Could not parse filename: {filename}")
            continue

        print(f"Parsing GC log: {filename}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        pauses_ms = []
        if gc_type.lower() == "g1": pauses_ms = parse_g1_pauses(content)
        elif gc_type.lower() == "parallel": pauses_ms = parse_parallel_pauses(content)
        elif gc_type.lower() == "zgc": pauses_ms = parse_zgc_pauses(content)
        elif gc_type.lower() == "shenandoah": pauses_ms = parse_shenandoah_pauses(content)
        else: print(f"Unknown GC type '{gc_type}' for {filename}")

        if pauses_ms:
            results.append({
                "gc_type": gc_type, "heap_size": heap_size, "benchmark": benchmark,
                "max_pause_ms": max(pauses_ms),
                "avg_pause_ms": sum(pauses_ms) / len(pauses_ms),
                "total_gc_pause_time_ms": sum(pauses_ms),
                "num_stw_pauses": len(pauses_ms) # Απλοϊκή μέτρηση, μπορεί να χρειαστεί βελτίωση
            })
        else:
             results.append({ # Προσθήκη γραμμής ακόμα και αν δεν βρέθηκαν παύσεις για πληρότητα
                "gc_type": gc_type, "heap_size": heap_size, "benchmark": benchmark,
                "max_pause_ms": 0, "avg_pause_ms": 0, "total_gc_pause_time_ms": 0, "num_stw_pauses": 0
            })


    if not results:
        print("No GC log data parsed.")
        return

    with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"GC log parsing complete. Results: {output_csv_file}")

if __name__ == '__main__':
    gc_log_directory = "gc_logs"
    parsed_gc_csv_path = "results/parsed_gc_data.csv"
    os.makedirs(os.path.dirname(parsed_gc_csv_path), exist_ok=True)
    process_gc_logs(gc_log_directory, parsed_gc_csv_path)