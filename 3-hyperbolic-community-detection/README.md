# Hyperbolic Community Detection

This project implements a novel community detection method using hyperbolic space, specifically within the framework of the Poincaré ball model. The repository is structured to facilitate testing, development, and application of hyperbolic community detection algorithms.

## Project Structure

### `/data`

Contains the datasets used by the algorithms. These datasets are prepared and formatted to be compatible with hyperbolic space representations.

### `/utils`

This directory contains various utility modules that support the main algorithms. Each utility serves a specific role described below:

-   **`clustering_utils`**: Functions related to clustering operations within the Poincaré ball model.
-   **`data_utils`**: Utilities for data manipulation and preparation specific to hyperbolic geometry.
-   **`embedding_utils`**: Tools for embedding data points into the hyperbolic space.
-   **`evaluation_utils`**: Scripts for evaluating the performance of the community detection algorithms.
-   **`functions_utils`**: General utility functions that are used across various parts of the project.
-   **`manifold`**: Contains functions and classes that handle operations directly on the Poincaré ball manifold.
-   **`optim_tools`**: Optimization tools specifically tuned for hyperbolic space.
-   **`visualisation_tools`**: Tools to visualize data and results in hyperbolic space, illustrating the clustering and community detection outcomes.

### `/test.ipynb`

A Jupyter notebook designed for testing and demonstrating the functionality of the hyperbolic community detection algorithms. Includes examples of how to use the utilities and visualize the results in the Poincaré ball.

## Implementation Details

All implementations are based in the Poincaré ball model of hyperbolic space, which allows us to exploit the natural hierarchical properties of hyperbolic geometry for community detection. This model is particularly well-suited for data with inherent hierarchical structures, such as social networks or biological data.
