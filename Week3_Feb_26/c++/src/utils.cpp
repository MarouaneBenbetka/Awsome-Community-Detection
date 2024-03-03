#include <vector>
#include "set"
#include "eigen3/Eigen/Dense"
#include "network.hpp"

using namespace std;
using namespace Eigen;

MatrixXd convertToEigenMatrix(const vector<vector<int>> &graph) {
    int n = graph.size(); // Number of rows
    MatrixXd adjacencyMatrix(n, n);

    // Copy data from graph vector<vector<int>> to Eigen MatrixXd
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            adjacencyMatrix(i, j) = graph[i][j];
        }
    }

    return adjacencyMatrix;
}


MatrixXd computeDistanceMatrix(const MatrixXd &s) {

    // compute each element of the D matrix like the following
    long rows = s.rows();
    long cols = s.cols();
    MatrixXd D(rows, cols);

    // D(i,j) = (S(i, i) + S(j, j) - 2*S(i, j))^(1/2)
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {

            D(i, j) = s(i, i) + s(j, j) - 2 * s(i, j);
        }
    }
    D = D.array().sqrt();
    return D;
}

double sumDistanceNodeNodes(MatrixXd D, const int node, const vector<int> &nodes) {
    // compute the sumDistance of distances between node and nodes
    double sumDistance = 0;
    for (int n: nodes) {
        sumDistance += D(node, n);
    }


    return sumDistance;

}

double averageWeight(const MatrixXd &distanceMatrix, const vector<int> &clique) {
    double sum = 0;
    long rows = distanceMatrix.rows();
    long cols = distanceMatrix.cols();
    long size = clique.size();

    // compute the sum of distance concerning the nodes in the clique
    for (int i: clique) {
        for (int j: clique) {
            sum += distanceMatrix(i, j);
        }
    }

    // the number of edges in the clique
    long edge_count = size * (size - 1);
    return sum / (double) edge_count;

}

double fitnessFunction(const vector<vector<int>> &adjMatrix, const vector<int> &nodes, double alpha,
                       double beta) {     // Calculate the number of edges inside the subgraph
    int numEdgesInside = 0;
    for (size_t i = 0; i < nodes.size(); ++i) {
        for (size_t j = i + 1; j < nodes.size(); ++j) {
            if (adjMatrix[nodes[i]][nodes[j]] > 0) {
                ++numEdgesInside;
            }
        }
    }

    // Calculate the number of edges going outside the subgraph
    int numEdgesOutside = 0;
    vector<bool> isInSubgraph(adjMatrix.size(), false);
    for (int node: nodes)
        isInSubgraph[node] = true;

    for (int node: nodes) {
        for (size_t i = 0; i < adjMatrix.size(); ++i) {
            if (!isInSubgraph[i] && adjMatrix[node][i] > 0) {
                ++numEdgesOutside;
            }
        }
    }
    // Calculate the fitness
    double fitness =
            static_cast<double>(numEdgesInside) / (std::pow(numEdgesInside, alpha) + std::pow(numEdgesOutside, beta));
    return fitness;
}


int nodeDegree(vector<vector<int>> matrix, int node) {
    // count the number of non-null elements in the node-th element of the vector
    int sum = 0;
    for (int i: matrix[node]) {
        sum += i;
    }
    return sum;
}

vector<int> localExpansion(vector<vector<int>> &cliques,
                           const MatrixXd &distanceMatrix,
                           const vector<vector<int>> &adjMatrix,
                           int k) {
    // return the initial centroids to take into consideration
    vector<int> initialSeeds;

    // find all the cliques in the graph
    // the cliques are already there
    // sort the cliques
    sort(cliques.begin(), cliques.end(),
         [distanceMatrix](const vector<int> &left, const vector<int> &right) {
             return averageWeight(distanceMatrix, left) < averageWeight(distanceMatrix, right);
         });

    set<int> unselectedNodes;
    // the set initially comprises all the nodes in the graph
    // --

    set<int> skipNodes; // the nodes that satisfy the degree rquirement
    // but not the clique requirement
    // initially empty

    int M = 0;

    while (M < k && !cliques.empty()) {
        // find the degree with max degree that does not belong to skipNodes

        auto maxDegreeNodeIterator = max_element(
                unselectedNodes.begin(), unselectedNodes.end(),
                [adjMatrix, skipNodes](const int &a, const int &b) {
                    double aKey = 0;
                    double bKey = 0;

                    if (!skipNodes.count(a)) {
                        // consider the degree of the node in the matrix
                        aKey = nodeDegree(adjMatrix, a);
                    }

                    if (!skipNodes.count(b)) {
                        // consider the degree of the node in the matrix
                        bKey = nodeDegree(adjMatrix, b);
                    }

                    return aKey < bKey;
                });
        // the node with max degree not belonging to the skipNodes set

        int maxDegreeNode = *maxDegreeNodeIterator;

        // Choose a clique among the previous

        int chosenCliqueIndex = -1;
        vector<int> chosenClique;

        // check if the chosen max-degree node is in a certain clique
        // among  the cliques we have
        size_t cliqueCount = cliques.size();

        for (int i = 0; i < cliqueCount; i++) {
            vector<int> currentClique = cliques[i];
            size_t cliqueSize = currentClique.size();

            for (int j = 0; j < cliqueSize; j++) {
                // check if the current element is the max degree node
                int currentNode = currentClique[j];
                if (currentNode == maxDegreeNode) {
                    chosenCliqueIndex = i;
                    chosenClique = currentClique;
                    break;
                }
            }
        }

        // if there is no chosen clique
        if (chosenCliqueIndex == -1) {
            // add the max degree node to the skip nodes
            skipNodes.insert(maxDegreeNode);
            continue;
        }

        // if we achive this poing
        // this means that the selected max degree node belongs to
        // a clique

        // remove the chosen clique from the cliques to consider in the future
        // Erase the vector at index chosenCliqueIndex
        cliques.erase(cliques.begin() + chosenCliqueIndex);


        // we consider computing the  and the fitness score
        // current value of the fitness function
        double initialFitness = fitnessFunction(adjMatrix, chosenClique, 0.9, 1.1);

        // consider each unselect
        for (int node: unselectedNodes) {
            bool nodeInChosenClique = false;
            for (int i: chosenClique) {
                if (node == i) {
                    nodeInChosenClique = true;
                    break;
                }
            }
            if (!nodeInChosenClique) {
                vector<int> toConsider = chosenClique;
                toConsider.push_back(node);
                double newFitness = fitnessFunction(adjMatrix, toConsider, 0.9, 1.1);

                if (newFitness >= initialFitness) { // if node makes fitness better
                    initialFitness = newFitness;
                    chosenClique.push_back(node);
                }
            }
        }

        // from the newly constructed list of nodes
        // we need to find node to consider as centroid
        // choose the node that maximizes with maximum centrality
        // or another measure that I forgot about
        auto centroidIterator = max_element(chosenClique.begin(), chosenClique.end(),
                                            [](const int a, const int b) {
                                                double keyA = 0; // compute the measure of a
                                                // (centrality or somethingg like that)
                                                double keyB = 0; // compute the measure of b
                                                // (centrality or something like that )
                                                return keyA < keyB;
                                            });

        int centroid = *centroidIterator;\

        // adding the centroid to the set of initial centroids
        initialSeeds.push_back(centroid);

        // remove the elements of the selected clique from the unselected nodes
        for (int i: chosenClique) {
            unselectedNodes.erase(i);
        }

        // construct the new list of cliques
        // only keep the nodes that are still
        // in the set of unselected nodes
        vector<vector<int>> newCliques;
        for (const vector<int> &clique: cliques) {
            vector<int> newClique;
            for (int node: clique) {
                if (unselectedNodes.count(node)) {
                    newClique.push_back(node);
                }
            }
            // the siz eof newClqieu should be >= 3;
            if (newClique.size() > 2) {
                newCliques.push_back(newClique);
            }
        }

        // sort the new cliques again
        sort(newCliques.begin(), newCliques.end(),
             [distanceMatrix](const vector<int> &a, const vector<int> &b) {
                 // order according to the average weight
                 double keyA = averageWeight(distanceMatrix, a);
                 double keyB = averageWeight(distanceMatrix, b);

                 return keyA < keyB;

             }
        );
        // update the cliques to newCliques
        cliques = newCliques;

        // GO handle the next centroid
        M++;
    }

    // if quit due to the second condition:
    // there are no more clusters to process
    if (M < k) {
        for (int i = 0; i < k - M; i++) {

            if (unselectedNodes.empty()) { // If there are no more nodes to process
                cerr << "There are no more nodes to select, k is too large" << endl;
            }

            auto maxDistanceSeedIterator = max_element(
                    unselectedNodes.begin(), unselectedNodes.end(),
                    [distanceMatrix, initialSeeds](const int &a, const int &b) {
                        // choose the one maximizing the distance to the
                        // other previously selected centroids
                        double distanceA =
                                sumDistanceNodeNodes(distanceMatrix, a, initialSeeds);
                        double distanceB =
                                sumDistanceNodeNodes(distanceMatrix, b, initialSeeds);
                        return distanceA < distanceB;
                    }
            );

            // adding the node with max distance to the set of initial seeds
            int maxDistanceSeed = *maxDistanceSeedIterator;
            initialSeeds.push_back(maxDistanceSeed);

            // removing the node from the list of unselected nodes
            unselectedNodes.erase(maxDistanceSeed);

            // go to the next iteration
            M++;
        }
    }


    return initialSeeds;
}