# C++ Project: PCA and KMeans Implementations with Network Utilities to implement local Expansion Kmeans algorithm


## Features

- **PCA Implementation:** A robust Principal Component Analysis module for data dimensionality reduction and exploratory data analysis.
- **KMeans Implementation:** An efficient KMeans clustering algorithm for data partitioning into k distinct clusters.
- **Network Functions:**
  - **Modularity:** Function to calculate the modularity of a network, useful for assessing the quality of a division of a network into modules or communities.
  - **Similarity:** Functions to compute various similarity metrics between nodes in a network, aiding in network analysis tasks.
  - **NMI (Normalized Mutual Information):** An implementation for evaluating the quality of clusterings by comparing two sets of clusters.
- **Utilities:**
  - **I/O Functions:** A set of utilities for input/output operations, specifically tailored for reading GML data files and converting them into adjacency matrices for further processing.
-   **Local Expansion ** All we need to implement the local expansion algorithm
### Compilation

```bash
g++ main.cc src/* 
```


Resultat : 

KARATE  :
-------------------------------------
Starting Kmeans with local Expansion Algorithm On Karate dataset :
NMI: 1
Kmeans with local expansion Execution Time: 28.7289 ms
Number of Communities Generated: 2

Reel :
Starting Kmeans with local Expansion Algorithm On Dolphins dataset :
NMI: 0.814113
Kmeans with local expansion Execution Time: 396.425 ms
Number of Communities Generated: 2