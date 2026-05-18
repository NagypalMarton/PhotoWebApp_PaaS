// solver.h

#pragma once

#include <cstddef>
#include <iosfwd>
#include <vector>

class Solver {
public:
    Solver();
    explicit Solver(const char* init);

    void print(std::ostream &s) const;
    bool isSolved() const;
    bool isAllowed(char val, int x, int y) const;
    bool isValidBoard() const;
    bool solveBackTrack();
    std::vector<Solver> solveAllParallel() const;
    void set(char val, int x, int y);

private:
    bool findFirstEmpty(int &x, int &y) const;
    void collectSolutionsSequential(std::vector<Solver> &solutions, std::size_t limit = 0) const;

    char data[9][9];
};

