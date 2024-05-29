#include <iostream>
#include <vector>
#include <eigen3/Eigen/Dense>
#include <numeric>
#include <cmath>




#ifndef NETWORK_HPP
#define NETWORK_HPP


using namespace std;
using namespace Eigen;





MatrixXd computeSimilarityMatrix(const MatrixXd& A) ;

MatrixXd computeDistanceMatrix(const MatrixXd& S) ;

/**
 * Calculates the entropy of a given list of labels.
 *
 * @param labels The list of labels.
 * @return The entropy value of the list of labels.
 */
double calculateEntropy(const std::vector<int>& labels) ;



/**
 * Calculates the mutual information of two given lists of labels.
 *
 * @param labels1 The first list of labels.
 * @param labels2 The second list of labels.
 * @return The mutual information value of the two lists of labels.
 */
double calculateMutualInformation(const std::vector<int>& labels1, const std::vector<int>& labels2) ;


/**
 * Calculates the normalized mutual information of two given lists of labels.
 *
 * @param labels1 The first list of labels.
 * @param labels2 The second list of labels.
 * @return The normalized mutual information value of the two lists of labels.
 */
double calculateNMI(const std::vector<int>& labels1, const std::vector<int>& labels2) ;


double modularity(const Eigen::MatrixXd& adjMatrix, const std::vector<std::vector<int>>& communities) ;

#endif