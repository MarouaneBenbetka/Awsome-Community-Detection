#include <iostream>
#include <vector>
#include "include/network.hpp"
#include "include/pca.hpp"
#include "include/utils.h"


int main() {
    // Example graph represented as an adjacency matrix
    vector<vector<int>> graph = {
            {0, 2, 1, 1, 1, 1}, // Adjacency matrix representation
            {2, 0, 1, 1, 1, 0}, // 1 represents an edge between vertices
            {1, 1, 0, 1, 0, 0}, // 0 represents no edge
            {1, 1, 1, 0, 1, 0},
            {1, 1, 0, 1, 0, 0},
            {1, 0, 0, 0, 0, 0}
    };



    // cout << computeSimilarityMatrix(graph) << endl;
    MatrixXd graphMatrix = convertToEigenMatrix(graph);
    vector<vector<int>> allCliques = findAllCliques(graph);

    cout << "All maximal cliques in the graph:" << endl;
    for (const auto &clique: allCliques) {
        for (int vertex: clique) {
            cout << vertex << " ";
        }
        cout << endl;
    }

    // in the first place, we have the ADJACENCY MATRIX
    // we compute the S matrix by S = M * tr(M)
    MatrixXd similarityMatrix = computeSimilarityMatrix(graphMatrix);

    // M is the adjacency matrix

    // Based on S, we can get the matrix D
    MatrixXd distanceMatrix = computeDistanceMatrix(similarityMatrix);

    // We apply a PCA On the D matrix to get the matrix of representation of nodes
    // in a space of p dimensions (p < N)
    MatrixXd transformed = PCA(distanceMatrix);

    // select the centroids as an initialization for the kmeans algorithm
    // 1st: get all the cliques in the graph


    // there is some serious work to be done here

    // apply the K-means algorithm as it is




    return 0;
}
