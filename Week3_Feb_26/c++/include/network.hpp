

#include <iostream>
#include <vector>




#ifndef NETWORK_HPP
#define NETWORK_HPP


using namespace std;




bool isNeighborOfAll(int v, const vector<int>& clique, const vector<vector<int>>& graph);


void findCliquesRecursive(vector<int>& currentClique, vector<vector<int>>& allCliques,
                          vector<int>& potentialNodes, vector<int>& nonCandidates,
                          const vector<vector<int>>& graph); 


vector<vector<int>> findAllCliques(const vector<vector<int>>& graph);



#endif