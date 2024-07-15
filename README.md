# Community Detection

This repository contains implementations of three distinct community detection algorithms, executed in both C++ and Python. Each algorithm is based on innovative approaches described in recent research, and this project serves as a practical application of those concepts.

## Algorithms

### 1. Iterated Greedy Algorithm

The Iterated Greedy algorithm employs a decompose-and-fix strategy, where parts of the solution are iteratively modified to explore the solution space effectively.

-   **Reference Paper**: ["Iterated Greedy Algorithms for Community Detection"](https://doi.org/10.1016/j.future.2018.06.010)
-   **Paper PDF**: [Download PDF](./1-Iterative-Greedy/paper/)

#### Source Code

-   **C++**: [code](./1-Iterative-Greedy/c++/)
-   **Python**: [code](./1-Iterative-Greedy/python/)

### 2. Local Expansion and K-Means

This approach integrates local expansion techniques with K-means clustering to enhance the detection of community structures.

-   **Reference Paper**: ["Local Expansion and K-Means for Community Detection"](https://doi.org/10.14311/NNW.2016.26.034)
-   **Paper PDF**: [Download PDF](./2-local-expansion-kmeans/paper/)

#### Source Code

-   **C++**: [code](./2-local-expansion-kmeans/c++/)
-   **Python**: [code](./2-local-expansion-kmeans/python/)

### 3. Hyperbolic Community Detection

A novel method that uses the properties of hyperbolic space to identify communities. This approach leverages the natural clustering tendency of hyperbolic spaces to facilitate community detection.

-   **Paper PDF**: [Download PDF](./3-hyperbolic-community-detection/paper/)

#### Source Code

-   **Python**: [code](./3-hyperbolic-community-detection/)
