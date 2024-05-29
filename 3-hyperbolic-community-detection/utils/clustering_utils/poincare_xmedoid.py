from sklearn.metrics import silhouette_score
import numpy as np
from utils.clustering_utils.poincare_kmedoid import RiemannianKMedoids
from geomstats.geometry.poincare_ball import PoincareBall


class XMedoid(object):
    def __init__(self, dim=2, min_clusters=2, max_clusters=None, verbose=False, random_seed=None):
        self._min_clusters = min_clusters
        self._max_clusters = max_clusters if max_clusters else float('inf')
        self._verbose = verbose
        self._random_seed = random_seed
        self._best_model = None
        self._best_num_clusters = None
        self._dim = dim

    def fit(self, X):
        best_score = float('-inf')
        best_num_clusters = self._min_clusters

        poincare_ball_space = PoincareBall(dim=self._dim)

        for num_clusters in range(self._min_clusters, self._max_clusters + 1):
            kmedoids = RiemannianKMedoids(
                space=poincare_ball_space, n_clusters=num_clusters)

            kmedoids.fit(X)

            # Store cluster labels obtained from k-medoids
            labels = kmedoids.labels_

            # Calculate silhouette score
            silhouette_avg = silhouette_score(X, labels)
            # print(silhouette_avg)
            if silhouette_avg > best_score:
                best_score = silhouette_avg
                best_num_clusters = num_clusters
                self._best_model = kmedoids

        self._best_num_clusters = best_num_clusters
        return self._best_model

    def predict(self, X):
        if self._best_model:
            return self._best_model.predict(X)
        else:
            raise RuntimeError(
                "Fit the model first before making predictions.")
