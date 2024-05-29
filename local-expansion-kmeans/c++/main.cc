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
#include "include/network.hpp"
#include "include/kmeans.hpp"
#include "include/pca.hpp"
#include "include/utils.hpp"
#include "include/local_expansion.hpp"









int main() {
    std::string filename_reel = "../data/reel/karate/karate.gml";
    Eigen::MatrixXd adjMatrix = readGMLToAdjacencyMatrix(filename_reel);

    std::cout << "-------------------------------------" << std::endl;
    std::cout << "Reel :" << std::endl;
    std::cout << "Starting Kmeans with local Expansion Algorithm On Karate dataset :" << std::endl;
    // start time
    auto start_reel = std::chrono::high_resolution_clock::now();
    

    

    Eigen::MatrixXd  similarity = computeSimilarityMatrix(adjMatrix);
    Eigen::MatrixXd  distanceMatrix = computeDistanceMatrix(similarity);

    Eigen::MatrixXd  distance_reduced = PCA(distanceMatrix , .98);

    std::vector<std::vector<int>> bestCommunities;
    double bestModularity = -1.0;

    for (int k = 2; k <= 10; k++) {
        try {
            std::vector<int> initial_seeds = localExpansion(adjMatrix, distanceMatrix, k, 0.9, 1.1);
            Eigen::MatrixXd initial_seeds_vectors = extractRows(distance_reduced, initial_seeds);
            VectorXd labels = kMeans(distance_reduced, initial_seeds_vectors);
            auto communities = labelsToCommunities(labels);
            double qsim = modularity(adjMatrix, communities);

            if (qsim > bestModularity) {
                bestModularity = qsim;
                bestCommunities = communities;
            }
        } catch (...) {
            break;
        }
    }

    auto communities_reel = bestCommunities;

    auto end_reel = std::chrono::high_resolution_clock::now();

    // Calculating total time taken by the program.
    std::chrono::duration<double, std::milli> duration_reel = end_reel - start_reel;

    std::vector<int> labels_reel_predicted = communitiesToLabels(communities_reel);

    std::string trueLabelsFilename_reel = "../data/reel/karate/groundTruth.txt";
    std::vector<int> trueLabels = readTrueLabels(trueLabelsFilename_reel);

    double nmi_reel = calculateNMI(labels_reel_predicted, trueLabels);

    // Print NMI
    std::cout << "NMI: " << nmi_reel << std::endl;
    
    // Print the duration time
    std::cout << "Kmeans with local expansion Execution Time: " << duration_reel.count() << " ms" << std::endl;

    // Print the number of communities generated
    std::cout << "Number of Communities Generated: " << communities_reel.size() << std::endl;


  
    return 0;
}


