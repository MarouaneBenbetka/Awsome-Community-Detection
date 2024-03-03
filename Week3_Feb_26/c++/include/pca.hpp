
#include <eigen3/Eigen/Eigenvalues>
#include <eigen3/Eigen/Dense>
#include <iostream>


#ifndef PCA_HPP
#define PCA_HPP


using namespace Eigen;
using namespace std;


/**
 * @brief Performs Principal Component Analysis (PCA) on the given data matrix.
 *
 * @param data The input data matrix.
 * @param variance The desired variance to be explained by the principal components (default is 0.98).
 * @return The transformed data matrix after applying PCA.
 */
MatrixXd PCA(const MatrixXd& data , const int variance = .98);



#endif 