//
// Created by ramzi on 02/03/24.
//

#ifndef C___UTILS_H
#define C___UTILS_H

#include <vector>

#include "eigen3/Eigen/Dense"

using namespace std;
using namespace Eigen;

MatrixXd convertToEigenMatrix(const vector<vector<int>> &graph);

MatrixXd computeDistanceMatrix(const MatrixXd &s);

//
double averageWeight(const MatrixXd &distanceMatrix, const vector<int> &clique);

double fitnessFunction(const vector<vector<int>> &adjMatrix, const vector<int> &nodes, double alpha = 0.9,
                       double beta = 1.1);

double sumDistanceNodeNodes(MatrixXd D, const int node, vector<int>& nodes);

vector<int> localExpansion(vector<vector<int>> &cliques,
                           const MatrixXd &distanceMatrix,
                           const vector<vector<int>> &adjMatrix,
                           int k);

#endif //C___UTILS_H
