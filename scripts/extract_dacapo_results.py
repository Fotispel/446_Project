import re
import os
import csv

def parse_dacapo_output(content):
    # Παράδειγμα: ===== DaCapo 9.12 avrora PASSED in 12345 ms =====
    match = re.search(r"PASSED in (\d+) ms", content)
    if match:
        return int(match.group(1))
    # Προσπαθήστε να βρείτε χρόνους μεμονωμένων επαναλήψεων αν το "PASSED in" δεν είναι αρκετό
    # Iteration 1 (123 ms) κλπ. - αυτό απαιτεί πιο σύνθετη λογική.
    # Για τώρα, βασιζόμαστε στο "PASSED in X ms" που είναι ο συνολικός χρόνος.
    print("Warning: 'PASSED in X ms' not found in DaCapo output.")
    return None

def process_dacapo_logs(dacapo_out_dir, output_csv_file):
    results = []
    for filename in os.listdir(dacapo_out_dir):
        if not (filename.startswith("dacapo_") and filename.endswith(".log")):
            continue
        filepath = os.path.join(dacapo_out_dir, filename)
        try:
            gc_type, heap_size, benchmark = filename.replace("dacapo_", "").replace(".log", "").split("_")
        except ValueError:
            print(f"Could not parse filename: {filename}")
            continue

        print(f"Parsing DaCapo output: {filename}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        total_time_ms = parse_dacapo_output(content)
        results.append({
            "gc_type": gc_type, "heap_size": heap_size, "benchmark": benchmark,
            "total_benchmark_time_ms": total_time_ms if total_time_ms is not None else -1 # -1 για ένδειξη προβλήματος
        })

    if not results:
        print("No DaCapo output data parsed.")
        return

    with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"DaCapo output parsing complete. Results: {output_csv_file}")

if __name__ == '__main__':
    dacapo_output_directory = "dacapo_outputs"
    parsed_dacapo_csv_path = "results/parsed_dacapo_data.csv"
    os.makedirs(os.path.dirname(parsed_dacapo_csv_path), exist_ok=True)
    process_dacapo_logs(dacapo_output_directory, parsed_dacapo_csv_path)