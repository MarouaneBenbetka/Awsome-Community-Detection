#include <iostream>
#include <vector>
#include <eigen3/Eigen/Dense>
#include <numeric>
#include <cmath>
#include "../include/network.hpp"


using namespace Eigen;
using namespace std;

// Function to check if a vertex 'v' is a neighbor of all vertices in 'clique'
bool isNeighborOfAll(int v, const vector<int>& clique, const vector<vector<int>>& graph) {
    for (int i : clique) {
        if (graph[v][i] == 0) { // No edge between v and vertex i
            return false;
        }
    }
    return true;
}

// Recursive function to find all cliques
void findCliquesRecursive(vector<int>& currentClique, vector<vector<int>>& allCliques,
                          vector<int>& potentialNodes, vector<int>& nonCandidates,
                          const vector<vector<int>>& graph) {
    if (potentialNodes.empty() && nonCandidates.empty()) {
        allCliques.push_back(currentClique); // Found a maximal clique
        return;
    }

    // Explore potential nodes for expanding the current clique
    for (int i = 0; i < potentialNodes.size(); ++i) {
        int v = potentialNodes[i];
        vector<int> newClique = currentClique;
        newClique.push_back(v);

        // Find neighbors of 'v' in potentialNodes to form the new potential nodes
        vector<int> newPotentialNodes;
        for (int w : potentialNodes) {
            if (graph[v][w] != 0) {
                newPotentialNodes.push_back(w);
            }
        }

        // Find neighbors of 'v' in nonCandidates to form the new non-candidates
        vector<int> newNonCandidates;
        for (int w : nonCandidates) {
            if (graph[v][w] != 0) {
                newNonCandidates.push_back(w);
            }
        }

        findCliquesRecursive(newClique, allCliques, newPotentialNodes, newNonCandidates, graph);

        // Move vertex from potentialNodes to nonCandidates
        potentialNodes.erase(potentialNodes.begin() + i);
        nonCandidates.push_back(v);
        --i; // Adjust index after erasure
    }
}

// Wrapper function to start the clique finding process
vector<vector<int>> findAllCliques(const vector<vector<int>>& graph) {
    vector<int> currentClique, potentialNodes, nonCandidates, allVertices;
    vector<vector<int>> allCliques;

    // Initially, all vertices are potential nodes
    for (int i = 0; i < graph.size(); ++i) {
        potentialNodes.push_back(i);
    }

    findCliquesRecursive(currentClique, allCliques, potentialNodes, nonCandidates, graph);
    return allCliques;
}


MatrixXd computeSimilarityMatrix(const MatrixXd& A) {
    // Calculate A * A.transpose()
    MatrixXd similarityMatrix = A * A.transpose();
    return similarityMatrix;
}

// MatrixXd computeDistanceMatrix(const MatrixXd& S) {
//     // Extract the diagonal of S
//     VectorXd diag = S.diagonal();
    
//     // Create a matrix where each column is the diagonal of S
//     MatrixXd diagMat = diag.replicate(1, S.cols());
    
//     // Compute D = sqrt((diag(S) + diag(S)^T - 2*S))
//     MatrixXd D = ((diagMat.transpose() + diagMat) - 2 * S).array().sqrt();
    
//     return D;
// }


// double averageWeight(const MatrixXd& distMatrix, const std::vector<int>& nodes) {
//     // Calculate the size of the submatrix
//     size_t numNodes = nodes.size();

//     // Filter the distance matrix based on the given nodes
//     MatrixXd filteredDistMatrix(numNodes, numNodes);
//     for (size_t i = 0; i < numNodes; ++i) {
//         for (size_t j = 0; j < numNodes; ++j) {
//             filteredDistMatrix(i, j) = distMatrix(nodes[i], nodes[j]);
//         }
//     }

//     // Sum of distances in the filtered matrix
//     double sumDistances = filteredDistMatrix.sum();

//     // Number of edges in a complete graph
//     int nbEdges = numNodes * (numNodes - 1);

//     // Calculate the average weight
//     double averageWeight = sumDistances / nbEdges;

//     return averageWeight;
// }



// double fitnessFunction(const vector<vector<double>>& adjMatrix, const vector<int>& nodes, double alpha = 0.9, double beta = 1.1) {
//     // Calculate the number of edges inside the subgraph
//     int numEdgesInside = 0;
//     for (size_t i = 0; i < nodes.size(); ++i) {
//         for (size_t j = i + 1; j < nodes.size(); ++j) {
//             if (adjMatrix[nodes[i]][nodes[j]] > 0) {
//                 ++numEdgesInside;
//             }
//         }
//     }

//     // Calculate the number of edges going outside the subgraph
//     int numEdgesOutside = 0;
//     vector<bool> isInSubgraph(adjMatrix.size(), false);
//     for (int node : nodes) {
//         isInSubgraph[node] = true;
//     }

//     for (int node : nodes) {
//         for (size_t i = 0; i < adjMatrix.size(); ++i) {
//             if (!isInSubgraph[i] && adjMatrix[node][i] > 0) {
//                 ++numEdgesOutside;
//             }
//         }
//     }

//     // Calculate the fitness
//     double fitness = static_cast<double>(numEdgesInside) / (std::pow(numEdgesInside, alpha) + std::pow(numEdgesOutside, beta));
//     return fitness;
// }