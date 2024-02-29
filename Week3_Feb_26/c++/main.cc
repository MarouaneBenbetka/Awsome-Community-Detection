#include <iostream>
#include <vector>
#include "include/network.hpp"



int main() {
    // Example graph represented as an adjacency matrix
    vector<vector<int>> graph = {
        {0, 2, 1, 1, 1, 1}, // Adjacency matrix representation
        {2, 0, 1, 1, 1, 0}, // 1 represents an edge between vertices
        {1, 1, 0, 1, 0, 0}, // 0 represents no edge
        {1, 1, 1, 0, 1, 0},
        {1, 1, 0, 1, 0, 0},
        {1, 0, 0, 0, 0, 0}
    };


    // cout << computeSimilarityMatrix(graph) << endl;

    vector<vector<int>> allCliques = findAllCliques(graph);

    cout << "All maximal cliques in the graph:" << endl;
    for (const auto& clique : allCliques) {
        for (int vertex : clique) {
            cout << vertex << " ";
        }
        cout << endl;
    }


    


    return 0;
}
