# Sudoku solver (Problem #4)
## Goal
To create an efficient parallel Sudoku solver

## Tools
Any parallelization method can be used. The solution must also run on the **Para** cluster.

## Help
**solver.cpp** implements a recursive algorithm with sequential execution.
**sudoku.cpp** is the main program uses the above algorithm.
**Makefile** provides help for compiling and running the serial version.
**easy.sdk** contains 50 easy to solve minimal Sudoku.

## Minimum requirements:
- Solving a 9x9 board.
- If there is no solution, the algorithm should indicate this.
- If there is more than one solution, the algorithm should give the other solutions.

## Optional tasks:
- The algorithm should be able to solve larger tables.
- The algorithm should also be able to generate Sudoku puzzles.

## To be submitted
Source files of the solution and a documentation/presentation describing the solution and measurement method, including the measurement results and their interpretation.
