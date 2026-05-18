#!/usr/bin/env python3
"""
Benchmark analysis script for Sudoku OpenMP solver.
Extracts timing results from benchmark output files and computes speed-up and efficiency.
"""

import os
import re
import sys
from pathlib import Path

def extract_times_from_file(filepath):
    """
    Extract all timing measurements (in ms) from a benchmark result file.
    Looks for lines matching 'Time: XXX ms'.
    Returns a list of times in milliseconds.
    """
    times = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                match = re.search(r'Time:\s*(\d+)\s*ms', line)
                if match:
                    times.append(int(match.group(1)))
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}", file=sys.stderr)
        return []
    
    return times

def analyze_benchmark_results(results_dir='results'):
    """
    Analyze benchmark results from the results directory.
    Computes total time, speed-up, and efficiency for each thread count.
    """
    thread_counts = [1, 2, 4, 8]
    results = {}
    
    for threads in thread_counts:
        filepath = Path(results_dir) / f"benchmark-threads-{threads}.txt"
        times = extract_times_from_file(str(filepath))
        
        if not times:
            print(f"Warning: No timing data found for {threads} threads", file=sys.stderr)
            results[threads] = {
                'count': 0,
                'total_ms': 0,
                'avg_ms': 0
            }
        else:
            total_ms = sum(times)
            avg_ms = total_ms / len(times)
            results[threads] = {
                'count': len(times),
                'total_ms': total_ms,
                'avg_ms': avg_ms
            }
    
    return results

def compute_speedup(results):
    """
    Compute speed-up and efficiency metrics.
    Speed-up = T(1) / T(p)
    Efficiency = Speed-up / p
    """
    if 1 not in results or results[1]['total_ms'] == 0:
        print("Error: Could not find results for 1 thread or total time is 0", file=sys.stderr)
        return None
    
    baseline_time = results[1]['total_ms']
    speedup_data = {}
    
    for threads in [1, 2, 4, 8]:
        if threads in results:
            current_time = results[threads]['total_ms']
            speedup = baseline_time / current_time if current_time > 0 else 0
            efficiency = speedup / threads if threads > 0 else 0
            speedup_data[threads] = {
                'speedup': speedup,
                'efficiency': efficiency
            }
    
    return speedup_data

def print_results_table(results, speedup_data):
    """
    Print a formatted table with benchmark results.
    """
    print("\n" + "=" * 80)
    print("Sudoku OpenMP Benchmark Results")
    print("=" * 80)
    
    print(f"\n{'Threads':<10} {'Total Time (ms)':<20} {'Avg Time (ms)':<20} {'Speed-up':<15} {'Efficiency':<15}")
    print("-" * 80)
    
    for threads in [1, 2, 4, 8]:
        if threads in results:
            total_ms = results[threads]['total_ms']
            avg_ms = results[threads]['avg_ms']
            speedup = speedup_data[threads]['speedup'] if speedup_data else 0
            efficiency = speedup_data[threads]['efficiency'] if speedup_data else 0
            
            print(f"{threads:<10} {total_ms:<20.2f} {avg_ms:<20.2f} {speedup:<15.2f} {efficiency:<15.2%}")
    
    print("=" * 80)
    print("\nNote: Speed-up and Efficiency are relative to single-thread execution.")
    print("Ideal speed-up for p threads = p (i.e., linear scaling).")
    print("Ideal efficiency = 1.0 (100%).")

def main():
    results_dir = 'results'
    
    if not os.path.isdir(results_dir):
        print(f"Error: Results directory '{results_dir}' not found.", file=sys.stderr)
        print("Please run the benchmark.slurm script first.", file=sys.stderr)
        sys.exit(1)
    
    print("Analyzing benchmark results...")
    results = analyze_benchmark_results(results_dir)
    
    # Check if we have any data
    has_data = any(results[t]['count'] > 0 for t in [1, 2, 4, 8])
    if not has_data:
        print("Error: No timing data found in any benchmark result file.", file=sys.stderr)
        sys.exit(1)
    
    speedup_data = compute_speedup(results)
    
    if speedup_data:
        print_results_table(results, speedup_data)
    else:
        print("Error: Could not compute speed-up metrics.", file=sys.stderr)
        sys.exit(1)
    
    # Optionally save results to a CSV for further analysis
    csv_file = 'benchmark_results.csv'
    print(f"\nSaving detailed results to {csv_file}...")
    try:
        with open(csv_file, 'w') as f:
            f.write("Threads,Total_Time_ms,Avg_Time_ms,Speed_up,Efficiency\n")
            for threads in [1, 2, 4, 8]:
                if threads in results and speedup_data:
                    total_ms = results[threads]['total_ms']
                    avg_ms = results[threads]['avg_ms']
                    speedup = speedup_data[threads]['speedup']
                    efficiency = speedup_data[threads]['efficiency']
                    f.write(f"{threads},{total_ms:.2f},{avg_ms:.2f},{speedup:.2f},{efficiency:.4f}\n")
        print(f"Results saved to {csv_file}")
    except IOError as e:
        print(f"Warning: Could not save CSV: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
