import datetime
import csv
import re

def parse_ram_cpu_csv(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Παράλειψη του header
        
        for row in reader:
            if len(row) < 3:
                continue
            
            timestamp_str = row[0].strip().strip('"')
            ram_str = row[1].strip().strip('"')
            cpu_str = row[2].strip().strip('"')
            
            if not cpu_str or cpu_str == ' ':
                cpu_usage = 0.0
            else:
                try:
                    cpu_usage = float(cpu_str)
                except ValueError:
                    cpu_usage = 0.0
            
            try:
                ram_usage = float(ram_str) if ram_str else 0.0
            except ValueError:
                ram_usage = 0.0
            
            # Parse timestamp
            try:
                dt_object = datetime.datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S.%f')
            except ValueError:
                try:
                    dt_object = datetime.datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S')
                except ValueError:
                    continue
            
            data.append((dt_object, ram_usage, cpu_usage))
    
    return data

def parse_benchmark_summary(file_path):
    benchmarks = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Βρίσκουμε όλες τις εγγραφές "Running" και "Completed"
    running_pattern = r'Running GC: (\w+), Heap: (\w+), Benchmark: (\w+)'
    completed_pattern = r'Completed GC: \w+, Heap: \w+, Benchmark: \w+ at: (.+?)(?=\n|$)'
    
    running_matches = list(re.finditer(running_pattern, content))
    completed_matches = list(re.finditer(completed_pattern, content))
    
    previous_end_time = None
    
    for i, (running_match, completed_match) in enumerate(zip(running_matches, completed_matches)):
        gc = running_match.group(1)
        heap = running_match.group(2)
        benchmark = running_match.group(3)
        
        completed_time_str = completed_match.group(1).strip()
        completed_time_str = completed_time_str.replace('Δευ','Mon').replace('Τρι', 'Tue').replace('Τετ', 'Wed').replace('Πεμ', 'Thu').replace('Παρ', 'Fri').replace('Σαβ', 'Sat').replace('Κυρ', 'Sun')
        
        if ' 0:' in completed_time_str and '2025  0:' in completed_time_str:
            completed_time_str = completed_time_str.replace('2025  0:', '2025 0:')
            try:
                completion_time = datetime.datetime.strptime('Wed 18/06/2025 ' + completed_time_str.split(' ')[-1], '%a %d/%m/%Y %H:%M:%S')
            except ValueError:
                try:
                    completion_time = datetime.datetime.strptime('Wed 18/06/2025 ' + completed_time_str.split(' ')[-1], '%a %d/%m/%Y %H:%M:%S,%f')
                except ValueError:
                    continue
        else:
            try:
                completion_time = datetime.datetime.strptime(completed_time_str, '%a %d/%m/%Y %H:%M:%S,%f')
            except ValueError:
                try:
                    completion_time = datetime.datetime.strptime(completed_time_str, '%a %d/%m/%Y %H:%M:%S')
                except ValueError:
                    continue
        
        start_time = previous_end_time if previous_end_time else None
        
        benchmarks.append({
            'gc': gc,
            'heap': heap,
            'benchmark': benchmark,
            'start_time': start_time,
            'completion_time': completion_time
        })
        
        previous_end_time = completion_time
    
    return benchmarks

def infer_start_times(benchmarks, ram_cpu_data):
    if not benchmarks or not ram_cpu_data:
        return benchmarks
    
    if benchmarks[0]['start_time'] is None:
        benchmarks[0]['start_time'] = ram_cpu_data[0][0]
    
    for i in range(1, len(benchmarks)):
        if benchmarks[i]['start_time'] is None:
            benchmarks[i]['start_time'] = benchmarks[i-1]['completion_time']
    
    return benchmarks

def calculate_average_usage(ram_cpu_data, benchmark_data):
    results = []
    
    for bm in benchmark_data:
        if bm['start_time'] is None or bm['completion_time'] is None:
            continue
            
        bm_start = bm['start_time']
        bm_end = bm['completion_time']
        
        relevant_data = []
        for timestamp, ram, cpu in ram_cpu_data:
            if bm_start <= timestamp <= bm_end:
                relevant_data.append((ram, cpu))
        
        avg_ram = 0.0
        avg_cpu = 0.0
        
        if relevant_data:
            total_ram = sum([d[0] for d in relevant_data])
            total_cpu = sum([d[1] for d in relevant_data])
            avg_ram = total_ram / len(relevant_data)
            avg_cpu = total_cpu / len(relevant_data)
        
        results.append({
            'gc': bm['gc'],
            'heap': bm['heap'],
            'benchmark': bm['benchmark'],
            'start_time': bm_start,
            'completion_time': bm_end,
            'avg_ram': avg_ram,
            'avg_cpu': avg_cpu,
            'measurements_count': len(relevant_data)
        })
    
    return results

def write_csv_summary(results, output_csv):
    """
    Γράφει τα αποτελέσματα σε CSV αρχείο
    """
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['gc', 'heap', 'benchmark', 'start_time', 'end_time', 
                        'avg_ram_percent', 'avg_cpu_percent', 'measurements_count'])
        
        for result in results:
            writer.writerow([
                result['gc'],
                result['heap'], 
                result['benchmark'],
                result['start_time'].strftime('%Y-%m-%d %H:%M:%S'),
                result['completion_time'].strftime('%Y-%m-%d %H:%M:%S'),
                f"{result['avg_ram']:.2f}",
                f"{result['avg_cpu']:.2f}",
                result['measurements_count']
            ])

if __name__ == '__main__':
    print("Φόρτωση δεδομένων RAM/CPU...")
    ram_cpu_data = parse_ram_cpu_csv('ram_cpu.csv')
    print(f"Φορτώθηκαν {len(ram_cpu_data)} μετρήσεις RAM/CPU")
    
    print("Ανάλυση benchmark summary...")
    benchmark_summary_data = parse_benchmark_summary('benchmark_summary.txt')
    print(f"Βρέθηκαν {len(benchmark_summary_data)} benchmarks")
    
    benchmark_summary_data.sort(key=lambda x: x['completion_time'])
    
    benchmark_summary_data = infer_start_times(benchmark_summary_data, ram_cpu_data)
    
    print("Υπολογισμός μέσων όρων...")
    calculated_results = calculate_average_usage(ram_cpu_data, benchmark_summary_data)
    
    write_csv_summary(calculated_results, 'cpu_ram_usage_summary.csv')
    
    print("Η ανάλυση ολοκληρώθηκε.")
    print("Αποτελέσματα:")
    print("- cpu_ram_usage_summary.csv")
    
    print("\nΠερίληψη αποτελεσμάτων:")
    for result in calculated_results:
        print(f"{result['gc']}-{result['heap']}-{result['benchmark']}: "
              f"RAM={result['avg_ram']:.1f}%, CPU={result['avg_cpu']:.1f}%, "
              f"Μετρήσεις={result['measurements_count']}")