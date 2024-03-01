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
#include "include/ig.hpp"


int main() {
    std::string filename_reel = "../data/reel/karate/karate.gml";
    Eigen::MatrixXd adjMatrix = readGMLToAdjacencyMatrix(filename_reel);

    std::cout << "-------------------------------------" << std::endl;
    std::cout << "Reel :" << std::endl;
    std::cout << "Starting IG Algorithm On Karate dataset :" << std::endl;
    // start time
    auto start_reel = std::chrono::high_resolution_clock::now();
    auto communities_reel = IG(adjMatrix, 20, 0.4);
    // end time
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
    std::cout << "IG Algorithm Execution Time: " << duration_reel.count() << " ms" << std::endl;

    // Print the number of communities generated
    std::cout << "Number of Communities Generated: " << communities_reel.size() << std::endl;


    std::cout << "-------------------------------------" << std::endl;
    std::cout << "Synth :" << std::endl;
    std::cout << "-------------------------------------" << std::endl;

    std::cout << "Starting IG Algorithm On LRF015 dataset :" << std::endl;

    std::string filename_synth = "../data/synth/LFR/0.15/network.dat";
    Eigen::MatrixXd adjMatrix_synth = readDatFileToAdjacencyMatrix(filename_synth);

       // start time
    auto start = std::chrono::high_resolution_clock::now();
    auto communities = IG(adjMatrix_synth, 6, 0.4);
    // end time
    auto end = std::chrono::high_resolution_clock::now();

    // Calculating total time taken by the program.
    std::chrono::duration<double, std::milli> duration = end - start;

    std::vector<int> labels = communitiesToLabels(communities);

    std::string synthLabelsFileName = "../data/synth/LFR/0.15/community.dat";
    std::vector<int> synthTrueLabels = readCommunityDatFileToListOfLabels(synthLabelsFileName);

    double nmi = calculateNMI(labels, synthTrueLabels);
    
        // Print NMI
    std::cout << "NMI: " << nmi << std::endl;
    // Print the number of communities generated
    std::cout << "Number of Communities Generated: " << communities.size() << std::endl;

    std::cout << "============================" << std::endl;

    return 0;
}


