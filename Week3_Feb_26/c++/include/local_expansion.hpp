#include <iostream>
#include <vector>
#include <eigen3/Eigen/Dense>
#include <numeric>
#include <cmath>
#include <map>
#include <unordered_set>




#ifndef EXPANSION_HPP
#define EXPANSION_HPP


using std::vector;
using std::unordered_set;
using namespace Eigen;
using namespace std;


void BronKerbosch(vector<int>& R, vector<int> P, vector<int> X, const MatrixXd& adjMatrix, vector<vector<int>>& cliques) ;


vector<vector<int>> findAllCliques(const MatrixXd& adjMatrix);


double averageWeight(const MatrixXd& distMatrix, const vector<int>& nodes) ;

vector<vector<int>> findAndSortCliquesByAverageWeight(const MatrixXd& distMatrix , const MatrixXd& adjMatrix) ;

int findNodeWithHighestDegree(const MatrixXd& adjMatrix, const vector<int>& skipNodes);


Eigen::MatrixXd computeSubgraphDistanceMatrix(const Eigen::MatrixXd& adjMatrix, const std::vector<int>& subgraphNodes) ;


int findSubgraphCentroid(const Eigen::MatrixXd& adjMatrix, const std::vector<int>& subgraphNodes) ;

double fitnessFunction(const Eigen::MatrixXd& adjMatrix, const std::vector<int>& nodes, double alpha = 0.9, double beta = 1.1) ;

std::vector<int> localExpansion(const Eigen::MatrixXd& adjMatrix, const Eigen::MatrixXd& distanceMatrix, int k = 2, double alpha = 0.9, double beta = 1.1) ;


#endif