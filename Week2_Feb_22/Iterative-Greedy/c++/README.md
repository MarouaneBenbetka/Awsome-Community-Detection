
# IG project in C++


This C++ project features organized code with detailed function documentation in header files (include/).
Implementation resides in corresponding source files (src/). The main.cpp file serves as a test bed,
 including headers and testing functions for validation.


## 1. `Results`

-------------------------------------
Reel :
Starting IG Algorithm On Karate dataset :
NMI: 0.687263
IG Algorithm Execution Time: 280.926 ms
Number of Communities Generated: 4
-------------------------------------
Synth :
-------------------------------------
Starting IG Algorithm On LRF015 dataset :
NMI: 1
IG Algorithm Execution Time: 2980.23 ms
Number of Communities Generated: 4
_________________________________


## `2.Compiling Command`
```
g++ main.cc src/ig.cpp -o ig.out
```
3.Execution Command :
```
./ig.out
```

## `3.Note` 

Ensure Eigen3 library is correctly installed and linked during compilation.





