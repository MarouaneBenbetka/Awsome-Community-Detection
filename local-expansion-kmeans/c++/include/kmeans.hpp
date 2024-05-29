#include <eigen3/Eigen/Dense>
#include <iostream>
#include <vector>



#ifndef KMEANS_HPP
#define KMEANS_HPP


using namespace Eigen;
using namespace std;

double calculateDistance(const VectorXd& point, const VectorXd& centroid);

VectorXd assignPointsToCentroids(const MatrixXd& data, const MatrixXd& centroids);

MatrixXd recalculateCentroids(const MatrixXd& data, const VectorXd& labels, int k) ;

VectorXd kMeans(const MatrixXd& data, MatrixXd& initialCentroids, int maxIterations = 100) ;

#endif