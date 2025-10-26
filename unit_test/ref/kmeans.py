# kmeans.py
# Steve Marschner, Walker White, Lillian Lee, Travis Westura
# Cornell CS1110, Spring 2014

import math
import random
import numpy

class Dataset(object):
    """Instance is a dataset for k-means clustering.

    The data is stored as a list of list of numbers
    (ints or floats).  Each component list is a data point.

    Instance Attributes:
        dimension: the point dimension for this dataset
                    [int > 0. Value never changes after initialization]
        data:  the dataset contents
                    [a list of lists of numbers (float or int), possibly empty.
    Invariant:
        The number of columns in data is equal to dimension.  That is,
        for every item data[i] in the list data, len(data[i]) == dimension.
    """

    def __init__(self, dim, contents=None):
        """Initializer: a dataset of dimensionality dim, containing
        a *copy* of <contents>, with the lists in data being distinct
        objects from the lists in <contents>.

        If contents is None, this dataset's data attribute will be an empty
        list.

        Pre: dim is an int > 0. contents is either None or
        a list of lists of numbers (int or float). If contents is not None,
        then each list in contents has length equal to dim.
        """
        pass

    def add_point(self, point):
        """Add a copy of the single point <point> to the dataset.

        Pre: <point> is a list of numbers, and len(point) == dimension
        """
        pass


class Cluster(object):
    """An instance is a cluster, a subset of the points in a dataset.

    A cluster is represented as a list of integers that give the indices
    in the dataset of the points contained in the cluster.  For instance,
    a cluster consisting of the points with indices 0, 4, and 5 in the
    dataset's data array would be represented by the index list [0,4,5].

    A cluster instance also contains a centroid that is used as part of
    the k-means algorithm.  This centroid is an n-D point (where n is
    the dimension of the dataset), represented as a list of n numbers,
    not as an index into the dataset.  (This is because the centroid
    is generally not a point in the dataset, but rather is usually in between
    the data points.)

    Instance attributes:
        _ds [Dataset]: the dataset this cluster is a subset of
        _inds [list of int]: the indices of this cluster's points in the
                            dataset
        centroid [list of numbers]: the centroid of this cluster
    Invariants:
        len(centroid) == _ds.dimension
        0 <= _inds[i] < len(_ds.data), for all 0 <= i < len(_inds)
    """

    def __init__(self, ds, centroid):
        """A new empty cluster whose centroid is a copy of <centroid> for the
        given dataset ds.

        Pre: ds is a Dataset instance.
             centroid is a list of ds.dimension numbers.
        """
        pass

    def __str__(self):
        """Returns: String representation of the centroid of this cluster."""
        return str(self.centroid)

    def __repr__(self):
        """Returns: Unambiguous representation of this cluster."""
        return str(self.__class__) + str(self)

    def clear(self):
        """Remove all points from this cluster, but leave the centroid
        unchanged."""
        pass

    def add_point(self, ind):
        """Add the point at index ind in the dataset to this cluster.
        Pre: ind is a valid index into this cluster's dataset.
        """
        pass

    def get_contents(self):
        """Return: a new list containing copies of the points in this cluster,
        that is, a list of lists of numbers.
        """
        pass

    def distance(self, point):
        """Return: The euclidean distance from point to this cluster's centroid.

        Pre: point is a list of numbers (int or float)
             len(point) = _ds.dimension
        """
        pass

    def update_centroid(self):
        """Recompute the centroid of this cluster from the current contents,
        and return True if the update did NOT change the centroid, False otherwise.

        Whether the centroid "remained the same" after recomputation is
        determined by numpy.allclose.  The return value should be interpreted
        as an indication of whether the starting centroid was a "stable"
        position or not.

        If there are no points in the cluster, do not change the centroid.
        """
        pass


class Clustering(object):
    """An instance is a clustering of the points in a dataset.

    Instance attributes:
        _ds [Dataset]: the dataset which this is a clustering of
        clusters [list of Cluster]: the clusters in this clustering (not empty)
    """

    def __init__(self, ds, k, seed_inds=None):
        """A clustering of the dataset ds into k clusters.

        The clusters are initialized by randomly selecting k different points
        from the database to be the centroids of the clusters.  If seed_inds
        is supplied, it is a list of indices into the dataset that specifies
        which points should be the initial cluster centroids.

        Pre: k > 0 and k <= number of distinct points in dataset ds.
             seed_inds is None, or a list of k valid indices into the dataset.
        """
        pass

    def _nearest_cluster(self, point):
        """Returns: Cluster nearest to point

        This method uses the distance method of each Cluster to compute
        the distance between point and the cluster centroid. It returns
        the Cluster that is the closest.

        Ties are broken in favor of clusters occurring earlier in the
        list of self.clusters.

        Pre: point is a list of numbers (int or float),
             len(point) = self._ds.dimension.
        """
        pass

    def _partition(self):
        """Repartition the dataset so each point is in exactly one Cluster.
        """
        # First, clear each cluster of its points.  Then, for each point in the
        # dataset, find the nearest cluster and add the point to that cluster.

        pass

    def _update(self):
        """Update all clusters' centroids, and returns True if all centroids
        remain unchanged, False otherwise.
        """
        pass

    def k_means_step(self):
        """Perform one cycle of the k-means algorithm, and return True if the
        algorithm has converged, False otherwise.
        """
        # In a cycle, we partition the points and then update the means.
        pass

    def perform_k_means(self, maxstep):
        """Refine the clustering to convergence or until maxstep steps
        using the k-means algorithm.
        """
        # Call k_means_step repeatedly, up to maxstep times, until the algorithm
        # converges.  Stop after maxstep iterations even if the algorithm has not
        # converged.

        pass




