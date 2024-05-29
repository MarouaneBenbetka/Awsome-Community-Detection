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
 * Reads a GML file and returns the adjacency matrix of the graph.
 *
 * @param filename The name of the GML file.
 * @return The adjacency matrix of the graph.
 */
Eigen::MatrixXd readGMLToAdjacencyMatrix(const std::string& filename) ;




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


/**
 * Converts labels to communities.
 *
 * This function takes a vector of labels and converts them into communities represented as a vector of vectors.
 *
 * @param labels The vector of labels to be converted.
 * @return A vector of vectors representing the communities.
 */
std::vector<std::vector<int>> labelsToCommunities(const Eigen::VectorXd& labels) ;


/**
 * @brief Extracts specific rows from an input matrix based on the given row indices.
 * 
 * @param inputMatrix The input matrix from which rows are to be extracted.
 * @param rowIndices The indices of the rows to be extracted.
 * @return The matrix containing the extracted rows.
 */
Eigen::MatrixXd extractRows(const Eigen::MatrixXd& inputMatrix, const std::vector<int>& rowIndices);


#endif 