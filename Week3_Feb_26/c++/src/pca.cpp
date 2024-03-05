#include <eigen3/Eigen/Dense>
#include <eigen3/Eigen/Eigenvalues>
#include <iostream>
#include "../include/pca.hpp"


using namespace Eigen;
using namespace std;


// Function to perform PCA and keep components representing 95% of the variance
MatrixXd PCA(const MatrixXd& data , const int variance ) {
    // Step 1: Standardize the data (mean=0 and variance=1)
    MatrixXd centered = data.rowwise() - data.colwise().mean();
    MatrixXd stdData = centered.array().rowwise() / centered.array().square().colwise().sum().sqrt();

    // Step 2: Compute the covariance matrix
    MatrixXd covariance = (stdData.adjoint() * stdData) / double(stdData.rows() - 1);

    // Step 3: Compute eigenvalues and eigenvectors of the covariance matrix
    SelfAdjointEigenSolver<MatrixXd> eigenSolver(covariance);
    if (eigenSolver.info() != Success) abort();

    // Sort eigenvalues and corresponding eigenvectors in descending order
    VectorXd eigenValues = eigenSolver.eigenvalues().real();
    MatrixXd eigenVectors = eigenSolver.eigenvectors().real();
    VectorXd sortedEigenValues = eigenValues.reverse();
    MatrixXd sortedEigenVectors = eigenVectors.rowwise().reverse();

    // Step 4: Calculate the total variance
    double totalVariance = sortedEigenValues.sum();

    // Step 5: Calculate the cumulative variance
    VectorXd cumulativeVariance(sortedEigenValues.size());
    double sum = 0;
    for(int i = 0; i < sortedEigenValues.size(); ++i) {
        sum += sortedEigenValues[i];
        cumulativeVariance[i] = sum / totalVariance;
    }

    // Find the number of components required to reach 95% of the variance
    int components = 0;
    for(int i = 0; i < cumulativeVariance.size(); ++i) {
        if(cumulativeVariance(i) >=  variance) {
            components = i + 1;
            break;
        }
    }

    // Step 6: Projection of the data on the new basis (only the components representing 95% of variance)
    MatrixXd reducedEigenVectors = sortedEigenVectors.leftCols(components);
    MatrixXd transformed = stdData * reducedEigenVectors;

    return transformed;
}

