#!/bin/bash
# Komondor OpenMP benchmark script for Sudoku solver.
# Measures runtime with varying thread counts (1, 2, 4, 8).
# Runs multiple puzzles from easy.sdk to accumulate measurable runtime.

#SBATCH --job-name=sudoku-benchmark
#SBATCH --output=logs/benchmark-%j.out
#SBATCH --error=logs/benchmark-%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=2G
#SBATCH --time=00:30:00
#SBATCH --account=p_parhpc

set -euo pipefail

mkdir -p logs results

# Load the compiler toolchain used on Komondor.
module purge || true
module load gcc || true

# Build the OpenMP version once.
make clean
make sudoku

# Prepare test data: first 10 puzzles from easy.sdk.
PUZZLE_DATA=$(head -10 easy.sdk)

# Array of thread counts to test.
THREAD_COUNTS=(1 2 4 8)

# Run benchmark for each thread count.
for THREADS in "${THREAD_COUNTS[@]}"; do
  echo "============================================"
  echo "Running benchmark with OMP_NUM_THREADS=${THREADS}"
  echo "============================================"
  
  export OMP_NUM_THREADS=${THREADS}
  
  # Store results in a timestamped file for later analysis.
  RESULT_FILE="results/benchmark-threads-${THREADS}.txt"
  {
    echo "Thread count: ${THREADS}"
    echo "Timestamp: $(date)"
    echo "---"
    # Run with multiple puzzles to accumulate meaningful runtime.
    srun ./sudoku ${PUZZLE_DATA}
  } | tee "${RESULT_FILE}"
  
  echo ""
done

echo "Benchmark complete. Results saved in results/ directory."