#include <eigen3/Eigen/Dense>
#include <iostream>
#include <vector>
#include "../include/kmeans.hpp"
#include "../include/network.hpp"
#include "../include/utils.h"
#include "pca.hpp"


using namespace Eigen;
using namespace std;

// Function to calculate the Euclidean distance between a point and a centroid
double calculateDistance(const VectorXd& point, const VectorXd& centroid) {
    return (point - centroid).norm();
}

// Function to assign each point to the closest centroid
VectorXd assignPointsToCentroids(const MatrixXd& data, const MatrixXd& centroids) {
    VectorXd labels(data.rows());
    for (int i = 0; i < data.rows(); ++i) {
        double minDistance = numeric_limits<double>::max();
        int closestCentroid = 0;
        for (int j = 0; j < centroids.rows(); ++j) {
            double distance = calculateDistance(data.row(i), centroids.row(j));
            if (distance < minDistance) {
                minDistance = distance;
                closestCentroid = j;
            }
        }
        labels(i) = closestCentroid;
    }
    return labels;
}

// Function to recalculate centroids based on the current assignment of points
MatrixXd recalculateCentroids(const MatrixXd& data, const VectorXd& labels, int k) {
    MatrixXd newCentroids = MatrixXd::Zero(k, data.cols());
    VectorXd counts = VectorXd::Zero(k);

    for (int i = 0; i < data.rows(); ++i) {
        int centroidIndex = static_cast<int>(labels(i));
        newCentroids.row(centroidIndex) += data.row(i);
        counts(centroidIndex) += 1;
    }

    for (int i = 0; i < k; ++i) {
        if (counts(i) > 0) {
            newCentroids.row(i) /= counts(i);
        }
    }

    return newCentroids;
}

// K-means algorithm function
VectorXd  kMeans(const MatrixXd& data, MatrixXd& initialCentroids, int maxIterations ) {
    int k = initialCentroids.rows();
    MatrixXd centroids = initialCentroids;
    VectorXd labels;

    for (int iteration = 0; iteration < maxIterations; ++iteration) {
        VectorXd newLabels = assignPointsToCentroids(data, centroids);
        if (labels.size() > 0 && (newLabels - labels).norm() == 0) {
            break; // Convergence achieved
        }
        labels = newLabels;
        centroids = recalculateCentroids(data, labels, k);
    }

    return labels;
}



// TODO: there is still some work to be done on this function
auto localExpansionKMeans(MatrixXd& matrix, vector<vector<int>>& A, vector<vector<int>>& cliques,
                          int kMin, int kMax, const int metric) {
    // compute the similarity matrix
    MatrixXd similarityMatrix = computeSimilarityMatrix(matrix);
    MatrixXd distanceMatrix = computeDistanceMatrix(similarityMatrix);
    MatrixXd mTransformed = PCA(distanceMatrix);

    vector<vector<int>> Cmax;
    double Qmax = -1;
    int kBest = kMin;

    for (int k = kMin; k < kMax + 1; k++) {
        vector<int> initialSeeds = localExpansion(cliques, matrix, A, k);

        // still do not understand how these become represented with MatrixXd
        MatrixXd seeds;
        int iterations = 199;
        // cluster the nodes
        // recover the vector of labels
        MatrixXd labels = kMeans(matrix, seeds, iterations);

        // extract the communities and the labels
        vector<vector<int>> communities;

        // the quality measure
        double Qs = 0;

        if (metric == MOD) {
            Qs = 0; // computeModularity(G, communities)
        } else if (metric == QS) {
            Qs = 0; // compute Q SIM(A, communities)
        }

        if (Qs > Qmax) {
            Qmax = Qs;
            Cmax = communities;
        }

        // there is still something to fix here

        return make_tuple()

    }

}
