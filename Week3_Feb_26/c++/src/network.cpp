#include <iostream>
#include <vector>
#include "../include/network.hpp"

using namespace std;

// Function to check if a vertex 'v' is a neighbor of all vertices in 'clique'
bool isNeighborOfAll(int v, const vector<int>& clique, const vector<vector<int>>& graph) {
    for (int i : clique) {
        if (graph[v][i] == 0) { // No edge between v and vertex i
            return false;
        }
    }
    return true;
}

// Recursive function to find all cliques
void findCliquesRecursive(vector<int>& currentClique, vector<vector<int>>& allCliques,
                          vector<int>& potentialNodes, vector<int>& nonCandidates,
                          const vector<vector<int>>& graph) {
    if (potentialNodes.empty() && nonCandidates.empty()) {
        allCliques.push_back(currentClique); // Found a maximal clique
        return;
    }

    // Explore potential nodes for expanding the current clique
    for (int i = 0; i < potentialNodes.size(); ++i) {
        int v = potentialNodes[i];
        vector<int> newClique = currentClique;
        newClique.push_back(v);

        // Find neighbors of 'v' in potentialNodes to form the new potential nodes
        vector<int> newPotentialNodes;
        for (int w : potentialNodes) {
            if (graph[v][w] != 0) {
                newPotentialNodes.push_back(w);
            }
        }

        // Find neighbors of 'v' in nonCandidates to form the new non-candidates
        vector<int> newNonCandidates;
        for (int w : nonCandidates) {
            if (graph[v][w] != 0) {
                newNonCandidates.push_back(w);
            }
        }

        findCliquesRecursive(newClique, allCliques, newPotentialNodes, newNonCandidates, graph);

        // Move vertex from potentialNodes to nonCandidates
        potentialNodes.erase(potentialNodes.begin() + i);
        nonCandidates.push_back(v);
        --i; // Adjust index after erasure
    }
}

// Wrapper function to start the clique finding process
vector<vector<int>> findAllCliques(const vector<vector<int>>& graph) {
    vector<int> currentClique, potentialNodes, nonCandidates, allVertices;
    vector<vector<int>> allCliques;

    // Initially, all vertices are potential nodes
    for (int i = 0; i < graph.size(); ++i) {
        potentialNodes.push_back(i);
    }

    findCliquesRecursive(currentClique, allCliques, potentialNodes, nonCandidates, graph);
    return allCliques;
}