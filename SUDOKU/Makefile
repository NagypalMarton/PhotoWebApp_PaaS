# 
# Example Makefile to compile and run
# should be modified according to the tools of the paralellization

# Source files 
SRCS = sudoku.cpp solver.cpp
# Generates the object file names from SRCS
OBJS = $(SRCS:.cpp=.o)

CXX = g++
CXXFLAGS = -g -std=c++11 -Wall -fopenmp
LDFLAGS = -fopenmp
LIBS = 

# compile
sudoku: $(OBJS)
	$(CXX) $(LDFLAGS) -o $@ $(OBJS) $(LIBS)

# extra dependency 
solver.o: solver.h

# pattern rules 
%.o:	%.cpp
	$(CXX) -c $(CXXFLAGS) $< -o $@


.PHONY:  easy5
easy5:	sudoku
	./sudoku `head -5 easy.sdk`

.PHONY: clean
clean:
	rm -rf sudoku *.o


