#include "../include/utils.hpp"
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






double sumLowerTriangular(const Eigen::MatrixXd& matrix) {
    double sum = 0.0;
    for (int i = 0; i < matrix.rows(); ++i) {
        for (int j = 0; j <= i; ++j) {
            sum += matrix(i, j);
        }
    }
    return sum;
}



Eigen::MatrixXd filterAdjMatrix(const Eigen::MatrixXd& adjMatrix, const std::vector<int>& V) {
    Eigen::MatrixXd newAdjMatrix = adjMatrix;
    int dim = adjMatrix.rows(); // Assuming square matrix

    // Instead of creating a boolean vector, directly work on the matrix
    for (int i = 0; i < dim; ++i) {
        if (std::find(V.begin(), V.end(), i) == V.end()) {
            // If i is not in V, zero out the row and column
            newAdjMatrix.row(i).setZero();
            newAdjMatrix.col(i).setZero();
        }
    }

    return newAdjMatrix;
}




Eigen::MatrixXd readGMLToAdjacencyMatrix(const std::string& filename) {
    std::ifstream file(filename);
    std::string line, token;
    std::map<int, int> nodeIdToIndex;
    int nodeCount = 0;
    bool inNode = false, inEdge = false;
    int source = -1, target = -1;

    if (!file.is_open()) {
        std::cerr << "Could not open file: " << filename << std::endl;
        return Eigen::MatrixXd(0, 0); // Return an empty matrix in case of error
    }

    // First pass: count nodes to allocate matrix of the right size
    while (getline(file, line)) {
        std::istringstream iss(line);
        while (iss >> token) {
            if (token == "node") {
                inNode = true;
            } else if (token == "edge") {
                inEdge = true;
            } else if (token == "id" && inNode) {
                int id;
                if (iss >> id) {
                    nodeIdToIndex[id] = nodeCount++;
                }
            } else if (token == "]") {
                if (inNode) {
                    inNode = false;
                } else if (inEdge) {
                    inEdge = false;
                }
            }
        }
    }

    // Initialize Eigen matrix
    Eigen::MatrixXd adjMatrix = Eigen::MatrixXd::Zero(nodeCount, nodeCount);

    // Reset to start of file for second pass
    file.clear();
    file.seekg(0, std::ios::beg);

    // Second pass: fill in the adjacency matrix
    while (getline(file, line)) {
        std::istringstream iss(line);
        while (iss >> token) {
            if (token == "edge") {
                inEdge = true;
            } else if (token == "source" && inEdge) {
                iss >> source;
            } else if (token == "target" && inEdge) {
                iss >> target;
            } else if (token == "]") {
                if (inEdge) {
                    if (source != -1 && target != -1 && nodeIdToIndex.count(source) && nodeIdToIndex.count(target)) {
                        adjMatrix(nodeIdToIndex[source], nodeIdToIndex[target]) = 1; // Directed edge
                        adjMatrix(nodeIdToIndex[target], nodeIdToIndex[source]) = 1; // Assuming undirected graph for simplicity
                    }
                    inEdge = false;
                    source = target = -1; // Reset for next edge
                }
            }
        }
    }

    return adjMatrix;
}





std::vector<int> communitiesToLabels(const std::vector<std::vector<int>>& communities) {
    std::vector<int> labels;
    // First, find the maximum node index to initialize the labels vector with the correct size.
    int maxIndex = -1;
    for (const auto& community : communities) {
        for (int node : community) {
            maxIndex = std::max(maxIndex, node);
        }
    }
    
    labels.resize(maxIndex + 1, -1); // Initialize with -1 to indicate that a node hasn't been assigned yet.
    
    // Assign each node to its community label.
    for (int i = 0; i < communities.size(); ++i) {
        for (int node : communities[i]) {
            labels[node] = i; // Assign the community index as the label.
        }
    }
    
    return labels;
}


std::vector<int> readTrueLabels(const std::string& filename) {
    std::vector<int> labels;
    std::ifstream file(filename);
    std::string line;

    if (!file.is_open()) {
        std::cerr << "Could not open file: " << filename << std::endl;
        return labels; // Return an empty vector in case of error
    }

    while (getline(file, line)) {
        // Convert line to integer and add to labels vector
        try {
            int label = std::stoi(line);
            labels.push_back(label);
        } catch (const std::exception& e) {
            std::cerr << "Error parsing line '" << line << "': " << e.what() << std::endl;
            // Optionally handle the error, e.g., by continuing to the next line
        }
    }

    file.close();
    return labels;
}


std::vector<int> readCommunityDatFileToListOfLabels(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Could not open file: " << filename << std::endl;
        return std::vector<int>(); // Return an empty vector in case of error
    }

    int node, community;
    // Create a temporary container to hold the highest node index found.
    int maxNodeIndex = 0;
    std::vector<std::pair<int, int>> tempCommunityAssignments;

    while (file >> node >> community) {
        maxNodeIndex = std::max(maxNodeIndex, node);
        tempCommunityAssignments.emplace_back(node, community);
    }

    file.close();

    // Initialize the labels vector with size equal to the max node index.
    // Fill with an initial value indicating no assignment.
    std::vector<int> labels(maxNodeIndex, -1); 

    // Assign nodes to their communities based on the temporary container.
    for (const auto& assignment : tempCommunityAssignments) {
        // Assuming node indices start from 1, adjust index when accessing the vector.
        labels[assignment.first - 1] = assignment.second;
    }

    return labels;
}



// Function to read .dat file and return an Eigen::MatrixXd as the adjacency matrix
Eigen::MatrixXd readDatFileToAdjacencyMatrix(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Could not open file: " << filename << std::endl;
        return Eigen::MatrixXd(0, 0); // Return an empty matrix in case of error
    }

    int maxNodeIndex = 0;
    int u, v;
    while (file >> u >> v) {
        maxNodeIndex = std::max(maxNodeIndex, std::max(u, v));
    }

    // Initialize the adjacency matrix with zeros
    Eigen::MatrixXd adjMatrix = Eigen::MatrixXd::Zero(maxNodeIndex, maxNodeIndex);

    // Reset file to beginning to read again
    file.clear();
    file.seekg(0, std::ios::beg);

    // Fill the adjacency matrix
    while (file >> u >> v) {
        // Adjust for 1-based indexing if necessary
        adjMatrix(u - 1, v - 1) = 1;
        adjMatrix(v - 1, u - 1) = 1; // Uncomment this line for undirected graphs
    }

    file.close();
    return adjMatrix;
}


std::vector<std::vector<int>> labelsToCommunities(const Eigen::VectorXd& labels) {
    std::unordered_map<int, std::vector<int>> communities;

    // Group elements by label
    for (int i = 0; i < labels.size(); ++i) {
        communities[labels[i]].push_back(i);
    }

    // Convert the unordered_map to a vector of vectors
    std::vector<std::vector<int>> result;
    for (const auto& entry : communities) {
        result.push_back(entry.second);
    }

    return result;
}

Eigen::MatrixXd extractRows(const Eigen::MatrixXd& inputMatrix, const std::vector<int>& rowIndices) {
    Eigen::MatrixXd result(rowIndices.size(), inputMatrix.cols());

    // Extract specified rows
    for (size_t i = 0; i < rowIndices.size(); ++i) {
        result.row(i) = inputMatrix.row(rowIndices[i]);
    }

    return result;
}
