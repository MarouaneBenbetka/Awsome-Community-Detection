#include <eigen3/Eigen/Dense>
#include <iostream>
#include <vector>
#include "../include/kmeans.hpp"

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
