# Project Folder Structure Overview

This project is structured into several directories and files, each serving a distinct purpose in the analysis of community detection within networks using different algorithms. Below is a description of each primary component within the project directory:

## Data

The `data` folder contains various datasets that are used throughout the project to test and validate the community detection algorithms.

## Output

The `output` folder holds saved files, which typically include outputs of the algorithms such as images or result summaries.

## Utils

This directory includes a collection of Python scripts that provide utility functions for the project:

-   `communities_network.py`: Contains general functions related to network graph manipulation and analysis.
-   `iterated_greedy.py`: Houses the necessary functions for the Iterated Greedy (IG) algorithm.
-   `kmeans.py`: Implements the main functions for the Local Expansion KMeans algorithm for community detection.
-   `utils.py`: Provides essential functions for file handling and data preprocessing.

## Notebooks

Jupyter notebooks are used for interactive data analysis and algorithm testing:

-   `main_notebook.ipynb`: Demonstrates the testing of the Local Expansion algorithm on different datasets, including visualizations and performance scoring.
-   `kmeans_parallel.ipynb`: Enhances the Local Expansion KMeans algorithm by adding parallelism to efficiently determine the optimal number of clusters `K` using the `concurrent.futures` module.
-   `different_algorithms_comparaison.ipynb`: Presents a comparative analysis of various community detection algorithms such as KMeans with random initialization, Local Expansion KMeans, Louvain, and the Iterated Greedy (IG) algorithm.

Please refer to individual files for detailed documentation and usage instructions.
