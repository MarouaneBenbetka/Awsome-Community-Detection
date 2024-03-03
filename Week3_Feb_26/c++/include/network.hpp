    #include <iostream>
#include <vector>
#include <eigen3/Eigen/Dense>
#include <numeric>
#include <cmath>




#ifndef NETWORK_HPP
#define NETWORK_HPP


using namespace std;
using namespace Eigen;




/**
 * Checks if a vertex is a neighbor of all vertices in a given clique.
 *
 * @param v The vertex to check.
 * @param clique The clique to check against.
 * @param graph The graph representing the connections between vertices.
 * @return True if the vertex is a neighbor of all vertices in the clique, false otherwise.
 */

bool isNeighborOfAll(int v, const vector<int>& clique, const vector<vector<int>>& graph);


void findCliquesRecursive(vector<int>& currentClique, vector<vector<int>>& allCliques,
                          vector<int>& potentialNodes, vector<int>& nonCandidates,
                          const vector<vector<int>>& graph); 


vector<vector<int>> findAllCliques(const vector<vector<int>>& graph);

MatrixXd computeSimilarityMatrix(const MatrixXd& A) ;

// MatrixXd computeDistanceMatrix(const MatrixXd& S) ;

// double averageWeight(const MatrixXd& distMatrix, const vector<int>& nodes) ;

// double fitnessFunction(const vector<vector<double>>& adjMatrix, const vector<int>& nodes, double alpha = 0.9, double beta = 1.1)


#endif