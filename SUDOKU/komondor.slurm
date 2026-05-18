#!/bin/bash
# Komondor OpenMP batch script.
#SBATCH --job-name=sudoku-omp
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=1G
#SBATCH --time=00:10:00
#SBATCH --account=p_parhpc

set -euo pipefail

mkdir -p logs

# Load the compiler toolchain used on Komondor.
# Adjust the module name if the cluster provides a different GCC module.
module purge || true
module load gcc || true

# Build the OpenMP version.
make clean
make sudoku

# Keep OpenMP threads aligned with the Slurm allocation.
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"

# Run a sample puzzle from the bundled dataset.
PUZZLE=$(head -n 1 easy.sdk)
echo "Using OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "Puzzle: ${PUZZLE}"

srun ./sudoku "${PUZZLE}"