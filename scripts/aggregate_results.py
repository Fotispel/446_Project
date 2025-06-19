import pandas as pd
import os

def generate_final_report(gc_data_csv, dacapo_data_csv, final_output_csv):
    if not os.path.exists(gc_data_csv):
        print(f"Error: GC data CSV not found: {gc_data_csv}")
        return
    if not os.path.exists(dacapo_data_csv):
        print(f"Error: DaCapo data CSV not found: {dacapo_data_csv}")
        return

    try:
        gc_df = pd.read_csv(gc_data_csv)
        dacapo_df = pd.read_csv(dacapo_data_csv)
    except pd.errors.EmptyDataError as e:
        print(f"Error reading CSV (possibly empty): {e}")
        return


    if gc_df.empty:
        print(f"GC data CSV ({gc_data_csv}) is empty. Cannot proceed.")
        return
    if dacapo_df.empty:
        print(f"DaCapo data CSV ({dacapo_data_csv}) is empty. Cannot proceed.")
        return
    
    final_df = pd.merge(gc_df, dacapo_df, on=["gc_type", "heap_size", "benchmark"], how="left")
    final_df['total_gc_pause_time_ms'] = pd.to_numeric(final_df['total_gc_pause_time_ms'], errors='coerce').fillna(0)
    final_df['total_benchmark_time_ms'] = pd.to_numeric(final_df['total_benchmark_time_ms'], errors='coerce')
    valid_benchmark_time_mask = (final_df['total_benchmark_time_ms'].notna()) & (final_df['total_benchmark_time_ms'] > 0)

    final_df['application_time_ms'] = 0.0
    final_df['throughput_percentage'] = 0.0

    final_df.loc[valid_benchmark_time_mask, 'application_time_ms'] = \
        final_df.loc[valid_benchmark_time_mask, 'total_benchmark_time_ms'] - final_df.loc[valid_benchmark_time_mask, 'total_gc_pause_time_ms']

    final_df['application_time_ms'] = final_df['application_time_ms'].clip(lower=0)

    final_df.loc[valid_benchmark_time_mask, 'throughput_percentage'] = \
        (final_df.loc[valid_benchmark_time_mask, 'application_time_ms'] / final_df.loc[valid_benchmark_time_mask, 'total_benchmark_time_ms']) * 100

    final_df['stw_event_frequency_per_sec'] = 0.0
    final_df.loc[valid_benchmark_time_mask, 'stw_event_frequency_per_sec'] = \
        final_df.loc[valid_benchmark_time_mask, 'num_stw_pauses'] / (final_df.loc[valid_benchmark_time_mask, 'total_benchmark_time_ms'] / 1000.0)

    final_df.to_csv(final_output_csv, index=False, encoding='utf-8')
    print(f"Aggregated results saved to {final_output_csv}")
    print("\nSample of Final Aggregated Data:")
    print(final_df.head())

if __name__ == '__main__':
    input_gc_csv = "results/parsed_gc_data.csv"
    input_dacapo_csv = "results/parsed_dacapo_data.csv"
    final_results_csv = "results/final_project_results.csv"
    os.makedirs(os.path.dirname(final_results_csv), exist_ok=True)
    generate_final_report(input_gc_csv, input_dacapo_csv, final_results_csv)