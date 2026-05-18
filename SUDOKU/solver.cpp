// solver.cpp

#include <cstring>
#include <iostream>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

#include "solver.h"

Solver::Solver() {
    for (int y = 0; y < 9; ++y) {
        for (int x = 0; x < 9; ++x) {
            data[y][x] = 0;
        }
    }
}

// Impements the Gordon Royle's input format and
// "SDK" format from G.Ralph Kuntz https://github.com/grkuntzmd/go-sudoku
Solver::Solver(const char* init) {
    const std::size_t inputLength = init == nullptr ? 0U : std::strlen(init);

    for (int i = 0; i < 81; ++i) {
        const int x = i % 9;
        const int y = i / 9;
        const char cell = static_cast<std::size_t>(i) < inputLength ? init[i] : '0';

        if (cell < '0' || cell > '9') {
            data[y][x] = 0;
        } else {
            data[y][x] = cell - '0';
        }
    }
}

void Solver::print(std::ostream &s) const {
    for (int y = 0; y < 9; ++y) {
        for (int x = 0; x < 9; ++x) {
            s << (char)(data[y][x] + '0') << " ";
        }
        s << std::endl;
    }
}

bool Solver::isSolved() const {
    // Check whether every cell is filled in the table?
    for (int y = 0; y < 9; ++y) {
        for (int x = 0; x < 9; ++x) {
            if (data[y][x] == 0) return false;
        }
    }
    return isValidBoard();
}

bool Solver::isAllowed(char val, int x, int y) const {
    if (val < 1 || val > 9) {
        return false;
    }

    // Only one 'val' is allowed in same row and column
    for (int i = 0; i < 9; ++i) {
        if (data[y][i] == val) return false;
        if (data[i][x] == val) return false;
    }

    // Only one 'val' is allowed in a 3x3 cell
    const int cellBaseX = 3 * (x / 3);
    const int cellBaseY = 3 * (y / 3);
    for (int yy = cellBaseY; yy < cellBaseY + 3; ++yy) {
        for (int xx = cellBaseX; xx < cellBaseX + 3; ++xx) {
            if (data[yy][xx] == val) return false;
        }
    }
    return true;
}

bool Solver::isValidBoard() const {
    for (int y = 0; y < 9; ++y) {
        bool used[10] = { false };
        for (int x = 0; x < 9; ++x) {
            const int v = data[y][x];
            if (v < 0 || v > 9) return false;
            if (v == 0) continue;
            if (used[v]) return false;
            used[v] = true;
        }
    }

    for (int x = 0; x < 9; ++x) {
        bool used[10] = { false };
        for (int y = 0; y < 9; ++y) {
            const int v = data[y][x];
            if (v == 0) continue;
            if (used[v]) return false;
            used[v] = true;
        }
    }

    for (int boxY = 0; boxY < 9; boxY += 3) {
        for (int boxX = 0; boxX < 9; boxX += 3) {
            bool used[10] = { false };
            for (int y = boxY; y < boxY + 3; ++y) {
                for (int x = boxX; x < boxX + 3; ++x) {
                    const int v = data[y][x];
                    if (v == 0) continue;
                    if (used[v]) return false;
                    used[v] = true;
                }
            }
        }
    }

    return true;
}

bool Solver::solveBackTrack() {
    std::vector<Solver> firstSolution;
    collectSolutionsSequential(firstSolution, 1);
    if (firstSolution.empty()) {
        return false;
    }

    *this = firstSolution[0];
    return true;
}

void Solver::set(char val, int x, int y) {
    data[y][x] = val;
}

bool Solver::findFirstEmpty(int &x, int &y) const {
    for (y = 0; y < 9; ++y) {
        for (x = 0; x < 9; ++x) {
            if (data[y][x] == 0) {
                return true;
            }
        }
    }

    return false;
}

void Solver::collectSolutionsSequential(std::vector<Solver> &solutions, std::size_t limit) const {
    if (!isValidBoard()) {
        return;
    }

    int x = 0;
    int y = 0;
    if (!findFirstEmpty(x, y)) {
        solutions.push_back(*this);
        return;
    }

    for (char n = 1; n <= 9; ++n) {
        if (!isAllowed(n, x, y)) {
            continue;
        }

        Solver next(*this);
        next.set(n, x, y);
        next.collectSolutionsSequential(solutions, limit);

        if (limit != 0 && solutions.size() >= limit) {
            return;
        }
    }
}

std::vector<Solver> Solver::solveAllParallel() const {
    std::vector<Solver> solutions;
    if (!isValidBoard()) {
        return solutions;
    }

    int x = 0;
    int y = 0;
    if (!findFirstEmpty(x, y)) {
        solutions.push_back(*this);
        return solutions;
    }

#pragma omp parallel
    {
        std::vector<Solver> localSolutions;

#pragma omp for schedule(dynamic)
        for (int n = 1; n <= 9; ++n) {
            if (!isAllowed(static_cast<char>(n), x, y)) {
                continue;
            }

            Solver next(*this);
            next.set(static_cast<char>(n), x, y);
            next.collectSolutionsSequential(localSolutions);
        }

#pragma omp critical
        {
            solutions.insert(solutions.end(), localSolutions.begin(), localSolutions.end());
        }
    }

    return solutions;
}
