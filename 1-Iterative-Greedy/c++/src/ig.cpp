#include "../include/ig.hpp"
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

    double modularity = 0.0;
    // Directly sum over the lower triangular part, including diagonal
    for (int i = 0; i < C.rows(); ++i) {
        for (int j = 0; j <= i; ++j) {
            modularity += C(i, j) * modMatrix(i, j);
        }
    }

    return modularity;
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

std::pair<std::vector<std::vector<int>>, double> GCP(const Eigen::MatrixXd& adjMatrix) {
    int N = adjMatrix.rows();
    std::vector<int> V(N);
    std::iota(V.begin(), V.end(), 0); // Fill V with 0, 1, ..., N-1

    std::random_device rd;
    std::mt19937 g(rd());

    std::shuffle(V.begin(), V.end(), g); // Randomly shuffle V
    int v = V.back(); V.pop_back();

    std::vector<std::vector<int>> communities = {{v}};
    std::vector<int> nodes = {v};

    double Mdb = -1;

    while (!V.empty()) {
        std::shuffle(V.begin(), V.end(), g);
        v = V.back(); V.pop_back();
        nodes.push_back(v);

        Mdb = -1;
        std::vector<int> best_community;
        int best_community_index = -1;

        Eigen::MatrixXd newAdjMatrix = filterAdjMatrix(adjMatrix, nodes);

        for (size_t i = 0; i < communities.size(); ++i) {
            auto Ki = communities[i];
            Ki.push_back(v);

            auto newCommunities = communities;
            newCommunities[i] = Ki;

            double Md = modularity(newAdjMatrix, newCommunities);

            if (Md > Mdb) {
                Mdb = Md;
                best_community = Ki;
                best_community_index = i;
            }
        }

        if (nodes.size() > 1) {
            auto newCommunities = communities;
            newCommunities.push_back({v});
            double Mdphi = modularity(newAdjMatrix, newCommunities);

            if (Mdb > Mdphi) {
                communities[best_community_index] = best_community;
            } else {
                Mdb = Mdphi;
                communities.push_back({v});
            }
        } else {
            communities.push_back({v});
        }
    }

    return {communities, Mdb};
}

std::pair<std::vector<int>, std::vector<std::vector<int>>> destruct(const std::vector<std::vector<int>>& communities, float beta) {
    int n = 0; // Calculate the total number of nodes
    for (const auto& community : communities) {
        n += community.size();
    }
    
    std::vector<int> nodes(n);
    std::iota(nodes.begin(), nodes.end(), 0); // Fill nodes with 0, 1, ..., n-1

    int remove_count = static_cast<int>(beta * n);
    std::vector<int> removed_nodes(remove_count);

    std::random_device rd;
    std::mt19937 g(rd());
    std::shuffle(nodes.begin(), nodes.end(), g); // Shuffle nodes
    std::copy_n(nodes.begin(), remove_count, removed_nodes.begin()); // Select first `remove_count` as removed nodes

    std::vector<std::vector<int>> filtered_communities;

    for (const auto& community : communities) {
        std::vector<int> new_community;

        for (int node : community) {
            if (std::find(removed_nodes.begin(), removed_nodes.end(), node) == removed_nodes.end()) {
                new_community.push_back(node);
            }
        }

        if (!new_community.empty()) {
            filtered_communities.push_back(new_community);
        }
    }

    return {removed_nodes, filtered_communities};
}


std::pair<std::vector<std::vector<int>>, double> reconstruct(const Eigen::MatrixXd& adjMatrix, std::vector<std::vector<int>> communities, const std::vector<int>& removedNodes) {
    std::vector<int> nodes(adjMatrix.rows());
    std::iota(nodes.begin(), nodes.end(), 0); // Fill nodes with 0, 1, ..., N-1

    // Remove the removed nodes from the current list of nodes
    nodes.erase(std::remove_if(nodes.begin(), nodes.end(), [&removedNodes](int node) {
        return std::find(removedNodes.begin(), removedNodes.end(), node) != removedNodes.end();
    }), nodes.end());

    double Mdb = -1;

    for (int node : removedNodes) {
        Mdb = -1;
        std::vector<int> bestCommunity;
        int bestCommunityIndex = -1;

        nodes.push_back(node); // Temporarily add the node for modularity calculation
        Eigen::MatrixXd newAdjMatrix = filterAdjMatrix(adjMatrix, nodes);

        for (size_t i = 0; i < communities.size(); ++i) {
            auto Ki = communities[i];
            Ki.push_back(node); // Test adding node to this community

            auto newCommunities = communities;
            newCommunities[i] = Ki;

            double Md = modularity(newAdjMatrix, newCommunities);

            if (Md > Mdb) {
                Mdb = Md;
                bestCommunity = Ki;
                bestCommunityIndex = i;
            }
        }

        double Mdphi = modularity(newAdjMatrix, communities); // Modularity without adding the node to any community

        if (Mdb >= Mdphi && Mdb != -1) {
            communities[bestCommunityIndex] = bestCommunity;
        } else {
            communities.push_back({node}); // Create a new community with this node
            Mdb = Mdphi;
        }

        nodes.pop_back(); // Remove the node from the list after assignment
    }

    return {communities, Mdb};
}

std::vector<std::vector<int>> IG(const Eigen::MatrixXd& adjMatrix, int nb_iterations , float beta ) {

    auto [communities, mod] = GCP(adjMatrix);


    for (int i = 0; i < nb_iterations; ++i) {
        // Perform the destruction phase
        auto [removedNodes, filteredCommunities] = destruct(communities, beta);


        // Perform the reconstruction phase

        auto [newCommunities, newMod] = reconstruct(adjMatrix, filteredCommunities, removedNodes);

        // Accept the new solution if it provides better modularity
        if (modularity(adjMatrix, newCommunities) > modularity(adjMatrix, communities)) {
            communities = newCommunities;
            mod = newMod;
        }

    }

    return communities;
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
