"""K-medoids clustering.

Lead author: Hadi Zaatiti.
"""
import numpy as np
import torch
from utils.functions_utils import pytorch_categorical
import logging

from sklearn.base import BaseEstimator, ClusterMixin

import geomstats.backend as gs
from geomstats.learning._template import TransformerMixin


class RiemannianKMedoids(TransformerMixin, ClusterMixin, BaseEstimator):
    """Class for K-medoids clustering on manifolds.

    K-medoids algorithm using Riemannian manifolds.

    Parameters
    ----------
    space : Manifold
        Equipped manifold.
    n_clusters : int
        Number of clusters (k value of k-medoids).
        Optional, default: 8.
    max_iter : int
        Maximum number of iterations.
        Optional, default: 100.
    init : str
        How to initialize centroids at the beginning of the algorithm. The
        choice 'random' will select training points as initial centroids
        uniformly at random.
        Optional, default: 'random'.
    n_jobs : int
        Number of jobs to run in parallel. `-1` means using all processors.
        Optional, default: 1.

    Notes
    -----
    * Required metric methods: `dist`, `dist_pairwise`.

    Example
    -------
    Available example on the Poincaré Ball and Hypersphere manifolds
    :mod:`examples.plot_kmedoids_manifolds`
    """

    def __init__(self, space, n_clusters=8, init="random", max_iter=100, n_jobs=1):
        self.space = space
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.init = init
        self.n_jobs = n_jobs

        self.centroids_ = None
        self.labels_ = None
        self.medoid_indices_ = None

    def _init_kmeansPP(self, X, distance):
        # initial distribution

        distribution_values = torch.ones(len(X))/len(X)
        distribution = pytorch_categorical.Categorical(distribution_values)

        # empty centroids
        centroids_index = []
        N, D = X.shape

        # fill centroids until reaching number of clusters

        while len(centroids_index) != self.n_clusters:

            # sample over the current distribution (can also
            # use argmax in a non stochastic process)
            sampled_point = distribution.sample(sample_shape=(1, 1)).item()

            # if the sampled point is not an already selected centroid
            if (sampled_point not in centroids_index):

                centroids_index.append(sampled_point)
                centroids_value = X[centroids_index]

                # compute the distance of each point to each centroids
                x = X.unsqueeze(1).expand(N, len(centroids_index), D)
                dst = distance(centroids_value, x)

                # selecting for each point only the closest centroids distance
                # and store the squared distance associated
                value, indexes = dst.min(-1)
                squared_distance = value**2

                # normalise the distance according to other distance
                # in order to get the distribution value
                distribution_value = squared_distance/(squared_distance.sum())

                # build the new distribution over examples
                distribution = pytorch_categorical.Categorical(
                    distribution_value)

        # transform data to pytorch tensor
        centroids_index = torch.tensor(centroids_index, device=X.device).long()
        centroids_value = X[centroids_index]

        # return centroids index and value
        return centroids_index, centroids_value

    def _initialize_medoids(self, distances):
        """Select initial medoids when beginning clustering."""
        n_samples = len(distances)

        # Choose the first medoid randomly
        medoids = [np.random.choice(n_samples)]

        # Select the rest of the medoids using k-means++ initialization
        for _ in range(1, self.n_clusters):
            # Compute the distance to the nearest medoid for each sample
            nearest_distances = np.array(
                [min(distances[i, j] for j in medoids) for i in range(n_samples)])

            # Compute the probability of each sample being selected as the next medoid
            probabilities = nearest_distances**2 / sum(nearest_distances**2)

            # Choose the next medoid with probability proportional to its squared distance
            next_medoid = np.random.choice(
                np.arange(n_samples), p=probabilities)
            medoids.append(next_medoid)

        return np.array(medoids)

    def fit(self, X):
        """Provide clusters centroids and data labels.

        Labels data by minimizing the distance between data points
        and cluster centroids chosen from the data points.
        Minimization is performed by swapping the centroids and data points.

        Parameters
        ----------
        X : array-like, shape=[n_samples, dim]
            Training data, where n_samples is the number of samples and
            dim is the number of dimensions.

        Returns
        -------
        self : object
            Returns self.
        """
        distances = self.space.metric.dist_pairwise(X, n_jobs=self.n_jobs)
        medoids_indices = self._init_kmeansPP(X, distances)

        for iteration in range(self.max_iter):
            old_medoids_indices = gs.copy(medoids_indices)
            labels = gs.argmin(distances[medoids_indices, :], axis=0)
            self._update_medoid_indexes(distances, labels, medoids_indices)

            if gs.all(old_medoids_indices == medoids_indices):
                break
            if iteration == self.max_iter - 1:
                logging.warning(
                    "Maximum number of iteration reached before "
                    "convergence. Consider increasing max_iter to "
                    "improve the fit."
                )

        self.centroids_ = X[medoids_indices]
        self.labels_ = labels
        self.medoid_indices_ = medoids_indices

        return self

    def _update_medoid_indexes(self, distances, labels, medoid_indices):
        for cluster in range(self.n_clusters):
            cluster_index = gs.where(labels == cluster)[0]
            if len(cluster_index) == 0:
                logging.warning("One cluster is empty.")
                continue

            in_cluster_distances = distances[
                cluster_index, gs.expand_dims(cluster_index, axis=-1)
            ]
            in_cluster_all_costs = gs.sum(in_cluster_distances, axis=1)
            min_cost_index = gs.argmin(in_cluster_all_costs)
            min_cost = in_cluster_all_costs[min_cost_index]
            current_cost = in_cluster_all_costs[
                gs.argmax(cluster_index == medoid_indices[cluster])
            ]

            if min_cost < current_cost:
                medoid_indices[cluster] = cluster_index[min_cost_index]

    def predict(self, X):
        """Predict the closest cluster for each sample in X.

        Parameters
        ----------
        X : array-like, shape=[n_samples, dim,]
            Training data, where n_samples is the number of samples and
            dim is the number of dimensions.

        Returns
        -------
        labels : array-like, shape=[n_samples,]
            Index of the cluster each sample belongs to.
        """
        labels = gs.zeros(len(X))

        for point_index, point_value in enumerate(X):
            distances = gs.zeros(len(self.centroids_))
            for cluster_index, cluster_value in enumerate(self.centroids_):
                distances[cluster_index] = self.space.metric.dist(
                    point_value, cluster_value
                )

            labels[point_index] = gs.argmin(distances)

        return labels