
#include <eigen3/Eigen/Dense>
#include <vector>
#include <iostream>
#include <unordered_set>
#include "../include/local_expansion.hpp"



using Eigen::MatrixXd;
using std::vector;
using std::unordered_set;


void BronKerbosch(vector<int>& R, vector<int> P, vector<int> X, const MatrixXd& adjMatrix, vector<vector<int>>& cliques) {
    if (P.empty() && X.empty()) {
        if (R.size() > 2) { // Only consider cliques with more than 2 nodes
            cliques.push_back(R);
        }
        return;
    }

    for (size_t i = 0; i < P.size(); ) {
        int v = P[i];
        vector<int> newR = R;
        newR.push_back(v);

        vector<int> newP, newX;
        for (int w : P) {
            if (adjMatrix(v, w) > 0) { // Check adjacency
                newP.push_back(w);
            }
        }
        for (int w : X) {
            if (adjMatrix(v, w) > 0) { // Check adjacency
                newX.push_back(w);
            }
        }

        BronKerbosch(newR, newP, newX, adjMatrix, cliques);

        P.erase(P.begin() + i); // Remove v from P
        X.push_back(v); // Add v to X
    }
}

vector<vector<int>> findAllCliques(const MatrixXd& adjMatrix) {
    vector<vector<int>> cliques;
    vector<int> R, P, X;

    for (int i = 0; i < adjMatrix.rows(); ++i) {
        P.push_back(i);
    }

    BronKerbosch(R, P, X, adjMatrix, cliques);

    return cliques;
}

double averageWeight(const MatrixXd& distMatrix, const vector<int>& nodes) {
    double sumDistances = 0.0;
    int nbEdges = nodes.size() * (nodes.size() - 1);

    for (int i = 0; i < nodes.size(); ++i) {
        for (int j = 0; j < nodes.size(); ++j) {
            if (i != j) { // Avoid counting self-loops in a complete graph
                sumDistances += distMatrix(nodes[i], nodes[j]);
            }
        }
    }

    return sumDistances / nbEdges;
}

struct CliqueWithWeight {
    vector<int> clique;
    double weight;
};

vector<vector<int>> findAndSortCliquesByAverageWeight(const MatrixXd& distMatrix , const MatrixXd& adjMatrix) {
    vector<vector<int>> cliques = findAllCliques(adjMatrix); // Assuming this function is defined
    vector<CliqueWithWeight> cliquesWithWeights;

    // Calculate average weight for each clique
    for (const auto& clique : cliques) {
        double avgWeight = averageWeight(distMatrix, clique);
        cliquesWithWeights.push_back({clique, avgWeight});
    }

    // Sort cliques by average weight
    std::sort(cliquesWithWeights.begin(), cliquesWithWeights.end(), [](const CliqueWithWeight& a, const CliqueWithWeight& b) {
        return a.weight >   b.weight;
    });

    // Extract sorted cliques
    vector<vector<int>> sortedCliques;
    for (const auto& cliqueWithWeight : cliquesWithWeights) {
        sortedCliques.push_back(cliqueWithWeight.clique);
    }

    return sortedCliques;
}

int findNodeWithHighestDegree(const MatrixXd& adjMatrix, const vector<int>& skipNodes) {
    int maxDegree = -1;
    int nodeWithMaxDegree = -1;
    unordered_set<int> skipSet(skipNodes.begin(), skipNodes.end());

    for (int i = 0; i < adjMatrix.rows(); ++i) {
        if (skipSet.find(i) != skipSet.end()) {
            // Skip this node
            continue;
        }

        int degree = 0;
        for (int j = 0; j < adjMatrix.cols(); ++j) {
            if (adjMatrix(i, j) > 0) {
                degree++;
            }
        }

        if (degree > maxDegree) {
            maxDegree = degree;
            nodeWithMaxDegree = i;
        }
    }

    return nodeWithMaxDegree;
}

int findSubgraphCentroid(const Eigen::MatrixXd& adjMatrix, const std::vector<int>& subgraphNodes) {
    Eigen::MatrixXd distanceMatrix = computeSubgraphDistanceMatrix(adjMatrix, subgraphNodes);
    int centroidNodeIndex = -1;
    double minDistanceSum = std::numeric_limits<double>::max();

    for (int i = 0; i < distanceMatrix.rows(); ++i) {
        double distanceSum = 0;
        for (int j = 0; j < distanceMatrix.cols(); ++j) {
            distanceSum += distanceMatrix(i, j);
        }

        if (distanceSum < minDistanceSum) {
            minDistanceSum = distanceSum;
            centroidNodeIndex = i;
        }
    }

    return subgraphNodes[centroidNodeIndex]; // Return the actual node ID, not the index within the subgraph
}


// Placeholder function for computing the distance matrix for the nodes in the subgraph
Eigen::MatrixXd computeSubgraphDistanceMatrix(const Eigen::MatrixXd& adjMatrix, const std::vector<int>& subgraphNodes) {
    size_t n = subgraphNodes.size();
    Eigen::MatrixXd distanceMatrix = Eigen::MatrixXd::Zero(n, n);

    // Assuming direct distances are stored in the adjacency matrix, 
    // replace this with your actual logic for computing distances
    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            distanceMatrix(i, j) = adjMatrix(subgraphNodes[i], subgraphNodes[j]);
        }
    }

    // If your graph is not fully connected or distances are not direct, 
    // you'll need to implement a pathfinding algorithm here (e.g., Floyd-Warshall for all pairs shortest paths)

    return distanceMatrix;
}




double fitnessFunction(const Eigen::MatrixXd& adjMatrix, const std::vector<int>& nodes, double alpha , double beta ) {
    // Create a subgraph matrix
    Eigen::MatrixXd subgraph(nodes.size(), nodes.size());

    // Fill the subgraph matrix
    for (size_t i = 0; i < nodes.size(); ++i) {
        for (size_t j = 0; j < nodes.size(); ++j) {
            subgraph(i, j) = adjMatrix(nodes[i], nodes[j]);
        }
    }

    // Count the number of edges inside the subgraph
    int numEdgesInside = (subgraph.array() > 0).count() - subgraph.diagonal().sum();

    // Find unused nodes
    std::vector<int> unusedNodes;
    for (int i = 0; i < adjMatrix.rows(); ++i) {
        if (std::find(nodes.begin(), nodes.end(), i) == nodes.end()) {
            unusedNodes.push_back(i);
        }
    }

    // Count the number of edges going outside the subgraph
    int numEdgesOutside = 0;
    for (int node : nodes) {
        for (int unusedNode : unusedNodes) {
            if (adjMatrix(node, unusedNode) > 0 || adjMatrix(unusedNode, node) > 0) {
                numEdgesOutside++;
            }
        }
    }

    // Compute the fitness
    double fitness = numEdgesInside / (pow(numEdgesInside, alpha) + pow(numEdgesOutside, beta));
    return fitness;
}


std::vector<int> localExpansion(const Eigen::MatrixXd& adjMatrix, const Eigen::MatrixXd& distanceMatrix, int k , double alpha , double beta) {
    auto cliques = findAndSortCliquesByAverageWeight(distanceMatrix, adjMatrix);
    std::vector<int> initialSeeds;
    std::unordered_set<int> unselectedNodes;
    for(int i = 0; i < adjMatrix.rows(); ++i) {
        unselectedNodes.insert(i);
    }
    std::vector<int> skipNodes;

    int M = 0;
    while (M < k && !cliques.empty()) {
        int maxDegreeNode = findNodeWithHighestDegree(adjMatrix, skipNodes);

\
        bool foundClique = false;
        std::vector<int> chosenClique;

        for (auto it = cliques.begin(); it != cliques.end() && !foundClique; ++it) {
            if (std::find(it->begin(), it->end(), maxDegreeNode) != it->end()) {
                chosenClique = *it;
                cliques.erase(it);
                foundClique = true;
                break;
            }
        }

        if (!foundClique) {
            skipNodes.push_back(maxDegreeNode);
            continue;
        }
        

        // Sort nodes in chosenClique by their distance in the distance matrix
        std::sort(chosenClique.begin(), chosenClique.end(), [&distanceMatrix, &chosenClique](int a, int b) {
            return distanceMatrix(a, chosenClique.front()) < distanceMatrix(b, chosenClique.front()); // Example sorting criterion
        });

        double fitnessValue = fitnessFunction(adjMatrix, chosenClique, alpha, beta);
        for (auto node : unselectedNodes) {
            if (std::find(chosenClique.begin(), chosenClique.end(), node) == chosenClique.end()) {
                auto tempClique = chosenClique;
                tempClique.push_back(node);
                double fitness = fitnessFunction(adjMatrix, tempClique, alpha, beta);
                if (fitness > fitnessValue) {
                    fitnessValue = fitness;
                    chosenClique.push_back(node);
                }
            }
        }

        // Assuming a function that computes closeness centrality for a subgraph represented by a vector of node indices
        int centroid = maxDegreeNode;
        initialSeeds.push_back(centroid);

        // Update unselectedNodes
        for (int node : chosenClique) {
            unselectedNodes.erase(node);
        }

        // Recompute weights and filter cliques
        std::vector<std::vector<int>> newCliques;
        for (auto& clique : cliques) {
            std::vector<int> updatedClique;
            std::copy_if(clique.begin(), clique.end(), std::back_inserter(updatedClique), [&unselectedNodes](int node) {
                return unselectedNodes.find(node) != unselectedNodes.end();
            });
            if (updatedClique.size() > 2) {
                newCliques.push_back(updatedClique);
            }
        }
        cliques = newCliques; // Update the cliques list

        M++;
    }

    // If we haven't reached k initial seeds, add based on maximum distance
    while (M < k) {
        if (unselectedNodes.empty()) {
            throw std::runtime_error("No more nodes to select, k is too large");
        }
        // Example approach to select max distance seed, actual implementation may vary
        int maxDistanceSeed = *std::max_element(unselectedNodes.begin(), unselectedNodes.end(), [&distanceMatrix, &initialSeeds](int a, int b) {
            double distA = 0, distB = 0;
            for (auto seed : initialSeeds) {
                distA += distanceMatrix(seed, a);
                distB += distanceMatrix(seed, b);
            }
            return distA < distB;
        });

        initialSeeds.push_back(maxDistanceSeed);
        unselectedNodes.erase(maxDistanceSeed);

        M++;
    }

    return initialSeeds;
}

