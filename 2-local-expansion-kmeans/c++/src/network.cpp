#include <iostream>
#include <vector>
#include <eigen3/Eigen/Dense>
#include <numeric>
#include <cmath>
#include <map>
#include "../include/network.hpp"


using namespace Eigen;
using namespace std;



MatrixXd computeSimilarityMatrix(const MatrixXd& A) {
    // Calculate A * A.transpose()
    MatrixXd similarityMatrix = A * A.transpose();
    return similarityMatrix;
}

MatrixXd computeDistanceMatrix(const MatrixXd& S) {
      // Normalize the input matrix
    MatrixXd normalizedS = S.normalized();

    // Compute the distance matrix: D = 1 - normalized(S)
    MatrixXd D = MatrixXd::Constant(S.rows(), S.cols(), 1.0) - normalizedS;

    return D;
    }


double calculateEntropy(const std::vector<int>& labels) {
    std::map<int, int> labelCounts;
    for (int label : labels) {
        labelCounts[label]++;
    }
    
    double entropy = 0.0;
    for (const auto& pair : labelCounts) {
        double p = static_cast<double>(pair.second) / labels.size();
        entropy -= p * log(p);
    }
    return entropy;
}

double calculateMutualInformation(const std::vector<int>& labels1, const std::vector<int>& labels2) {
    std::map<int, int> counts1, counts2;
    std::map<std::pair<int, int>, int> jointCounts;
    int n = labels1.size();
    
    for (int i = 0; i < n; ++i) {
        counts1[labels1[i]]++;
        counts2[labels2[i]]++;
        jointCounts[std::make_pair(labels1[i], labels2[i])]++;
    }
    
    double mutualInformation = 0.0;
    for (const auto& joint : jointCounts) {
        double pxy = static_cast<double>(joint.second) / n;
        double px = static_cast<double>(counts1[joint.first.first]) / n;
        double py = static_cast<double>(counts2[joint.first.second]) / n;
        mutualInformation += pxy * log(pxy / (px * py));
    }
    
    return mutualInformation;
}

double calculateNMI(const std::vector<int>& labels1, const std::vector<int>& labels2) {
    double mutualInformation = calculateMutualInformation(labels1, labels2);
    double entropy1 = calculateEntropy(labels1);
    double entropy2 = calculateEntropy(labels2);
    double nmi = 2.0 * mutualInformation / (entropy1 + entropy2);
    return nmi;
}

double modularity(const Eigen::MatrixXd& adjMatrix, const std::vector<std::vector<int>>& communities) {
      Eigen::VectorXd k_i = adjMatrix.rowwise().sum();
    double weights_sum = k_i.sum();

    // Early exit if the network is not connected
    if (weights_sum == 0) return -1;

    double norm = 1 / weights_sum;
    Eigen::MatrixXd K = norm * (k_i * k_i.transpose());
    Eigen::MatrixXd modMatrix = norm * (adjMatrix - K);

    // Initialize a zero matrix for community connections
    Eigen::MatrixXd C = Eigen::MatrixXd::Zero(modMatrix.rows(), modMatrix.cols());

    // Efficiently fill matrix C based on community memberships
    for (const auto& community : communities) {
        for (auto node : community) {
            for (auto inner_node : community) {
                if (node != inner_node) {
                    C(node, inner_node) = 1.0;
                }
            }
        }
    }

    double Q = 0.0;
    // Directly sum over the lower triangular part, including diagonal
    for (int i = 0; i < C.rows(); ++i) {
        for (int j = 0; j <= i; ++j) {
            Q += C(i, j) * modMatrix(i, j);
        }
    }

    return Q;
}


