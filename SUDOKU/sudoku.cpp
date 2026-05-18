// sudoku.cpp
//
//  vim :set expandtab ts=4 sw=4 ai

#include <chrono>
#include <iostream>
#include <vector>

#include "solver.h"

int main(int argc, const char* argv[]) {
    // other test puzzles can be found at 
    // https://github.com/grkuntzmd/sudoku/tree/master/test_puzzles
    const char *test = "000801000000000043500000000000070800020030000000000100600000075003400000000200600";
 
    for (int i = argc == 1 ? 0 : 1; i < argc; i++) {
        // use the test string if no command line arguments
        const char *t = i == 0 ? test : argv[i];
        Solver solver(t);
        std::cout << "Problem #" << i << ":\n";
        solver.print(std::cout);

        if (!solver.isValidBoard()) {
            std::cout << "Invalid problem #" << i << " (violates Sudoku rules)\n";
        } else {
            auto start = std::chrono::high_resolution_clock::now();
            std::vector<Solver> solutions = solver.solveAllParallel();
            auto end = std::chrono::high_resolution_clock::now();
            auto elapsed_ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

            if (solutions.empty()) {
                std::cout << "Cannot solve problem #" << i << "\n";
            } else {
                std::cout << "Found " << solutions.size() << " solution(s) for problem #" << i << "\n";
                for (std::size_t s = 0; s < solutions.size(); ++s) {
                    std::cout << "Solution #" << i << "." << (s + 1) << ":\n";
                    solutions[s].print(std::cout);
                }
            }
            std::cout << "Time: " << elapsed_ms << " ms\n";
        }

        if (i + 1 < argc) {
            std::cout << "-----------------\n";
        }
    }
    return 0;
}
