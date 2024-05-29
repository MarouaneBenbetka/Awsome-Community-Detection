#include <eigen3/Eigen/Dense>
#include <vector>
#include <iostream>
#include <numeric>
#include <utility>
#include <random> 
#include <algorithm>
#include <string>
#include <map>
#include <fstream>
#include <sstream>
#include <chrono>



#ifndef IG_HPP
#define IG_HPP








/**
 * Calculates the sum of the elements in the lower triangular part of a given matrix.
 *
 * @param matrix The input matrix.
 * @return The sum of the elements in the lower triangular part of the matrix.
 */
double sumLowerTriangular(const Eigen::MatrixXd& matrix);

/**
 * Calculates the modularity of a given network based on the adjacency matrix and communities.
 *
 * @param adjMatrix The adjacency matrix of the network.
 * @param communities The list of communities in the network.
 * @return The modularity value of the network.
 */
double modularity(const Eigen::MatrixXd& adjMatrix, const std::vector<std::vector<int>>& communities);


/**
 * Filters the adjacency matrix by keeping only the nodes specified in V.
 * 
 * @param adjMatrix The original adjacency matrix.
 * @param V The vector of nodes to keep.
 * @return The filtered adjacency matrix.
 */
Eigen::MatrixXd filterAdjMatrix(const Eigen::MatrixXd& adjMatrix, const std::vector<int>& V);


/**
 * @brief GCP is the first heuristic algorithm to enter the IG algorithm.
 * 
 * @param adjMatrix The adjacency matrix representing the graph.
 * @return A pair containing the solution as a vector of vectors of integers and the modularity as a double.
 */
std::pair<std::vector<std::vector<int>>, double> GCP(const Eigen::MatrixXd& adjMatrix);

/**
 * Destructs the graph by removing a specified percentage of nodes from the communities.
 *
 * @param communities The input communities.
 * @param beta The percentage of nodes to remove.
 * @return A pair containing the removed nodes as a vector and the updated communities as a vector of vectors.
 */
std::pair<std::vector<int>, std::vector<std::vector<int>>> destruct(const std::vector<std::vector<int>>& communities, float beta);

/**
 * Reconstructs the destructed graph by adding back the removed nodes to the communities,
 * according to the best modularity.
 *
 * @param adjMatrix The adjacency matrix representing the graph.
 * @param communities The communities of the original graph.
 * @param removedNodes The nodes that were removed from the communities.
 * @return A pair containing the reconstructed communities as a vector of vectors of integers
 *         and the modularity of the reconstructed graph as a double.
 */
std::pair<std::vector<std::vector<int>>, double> reconstruct(const Eigen::MatrixXd& adjMatrix,
                                                             std::vector<std::vector<int>> communities,
                                                             const std::vector<int>& removedNodes);


/**
 * Combines the GCP, reconstruct, and destruct functions to detect communities in a graph.
 *
 * @param adjMatrix The adjacency matrix representing the graph.
 * @param nb_iterations The number of iterations to perform. Default is 100.
 * @param beta The percentage of nodes to remove during the destruct phase. Default is 0.4.
 * @return The detected communities as a vector of vectors of integers.
 */
std::vector<std::vector<int>> IG(const Eigen::MatrixXd& adjMatrix, int nb_iterations = 100, float beta = 0.4);

/**
 * Reads a GML file and returns the adjacency matrix of the graph.
 *
 * @param filename The name of the GML file.
 * @return The adjacency matrix of the graph.
 */
Eigen::MatrixXd readGMLToAdjacencyMatrix(const std::string& filename) ;


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


/**
 * Converts a list of communities to a list of labels.
 *
 * @param communities The list of communities.
 * @return The list of labels.
 */
std::vector<int> communitiesToLabels(const std::vector<std::vector<int>>& communities) ;


/**
 * Reads a list of true labels from a file and returns it as a vector of integers.
 *
 * @param filename The name of the file containing the true labels.
 * @return The list of true labels as a vector of integers.
 */
std::vector<int> readTrueLabels(const std::string& filename) ;


/**
 * Reads a list of labels from a file and returns it as a vector of integers.
 *
 * @param filename The name of the file containing the labels.
 * @return The list of labels as a vector of integers.
 */
std::vector<int> readCommunityDatFileToListOfLabels(const std::string& filename) ;


/**
 * Reads a DAT file and returns the adjacency matrix of the graph.
 *
 * @param filename The name of the DAT file.
 * @return The adjacency matrix of the graph.
 */
Eigen::MatrixXd readDatFileToAdjacencyMatrix(const std::string& filename) ;


#endif 