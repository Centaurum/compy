# compy
Python-based heuristic C compiling tool

Compy tries to compile given main C-file. If you have a heap of sources and you want to compile certain main c-file, this tool will try to find minimal set of sources for successful compilation of given main c-file.

TODO:
1. Extend standard C libraries support (not only math).
2. Extend compilation errors to be detected (not only 'undefined reference')
3. In case of new project directory creating, implement headers copying instead of cpp-preprocessing.
4. Implement other languages support, at least c++ (now, only c is supported normally).

Note: cscope is used to solve undefined references compilation errors. So, you need to install cscope.
