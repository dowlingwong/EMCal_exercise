# kmeans_test.py (improved / Python 3)
# Steve Marschner (srm2), Walker M. White (wmw2)
# Updated by ChatGPT — September 13, 2025
"""Unit tests for k-means clustering (Dataset, Cluster, Clustering)."""

import random

import cornelltest  # Make sure you have NEW version
import ref.kmeans as kmeans


# ----------------------------
# Small helpers for this file
# ----------------------------
def expect_raises(exc_type, func, *args, **kwargs):
    """Assert that calling func(*args, **kwargs) raises exc_type."""
    try:
        func(*args, **kwargs)
    except Exception as e:  # noqa: BLE001 (test-only convenience)
        cornelltest.assert_true(
            isinstance(e, exc_type),
            'Expected {} but got {}'.format(exc_type.__name__, type(e).__name__),
        )
        return
    raise AssertionError('Expected {} to be raised, but no exception occurred.'.format(exc_type.__name__))


def seed_rng():
    """Make tests that depend on randomness deterministic."""
    random.seed(123456)


# ----------------------------
# Tests
# ----------------------------
def test_dataset():
    """Test the Dataset class."""

    # TEST CASE 1
    # Create and test an empty dataset
    dset = kmeans.Dataset(3)
    cornelltest.assert_equals(3, dset.dimension)

    # We use this assert function to compare lists
    cornelltest.assert_float_lists_equal([], dset.data)

    # Add something to the dataset (and check it was added)
    dset.add_point([0.0, 0.5, 4.2])
    # Dataset is a list of lists of numbers.
    cornelltest.assert_float_lists_equal([[0.0, 0.5, 4.2]], dset.data)

    print('    Default initialization looks okay')

    # TEST CASE 2
    # Create and test a non-empty dataset
    items = [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 1.0]]
    dset = kmeans.Dataset(3, items)
    cornelltest.assert_equals(3, dset.dimension)

    # Check that contents are initialized correctly
    # Make sure items is COPIED
    cornelltest.assert_float_lists_equal(items, dset.data)
    cornelltest.assert_false(dset.data is items)
    cornelltest.assert_false(dset.data[0] is items[0])

    # Add something to the dataset (and check it was added)
    extra = [0.0, 0.5, 4.2]
    dset.add_point(extra)
    items.append(extra)
    cornelltest.assert_float_lists_equal(items, dset.data)
    # Check the point was COPIED (id not the same object in stored list)
    cornelltest.assert_false(id(extra) in map(id, dset.data))

    # NEW: wrong-dimension add should raise
    expect_raises(ValueError, dset.add_point, [1.0, 2.0])  # length 2 instead of 3

    print('    User-given contents looks okay')
    print('  class Dataset appears correct')


def test_cluster():
    """Test the Cluster class."""

    # TEST CASE 1
    # Create and test a cluster (always empty)
    dset = kmeans.Dataset(3)
    point = [0.0, 1.0, 0.0]
    cluster1 = kmeans.Cluster(dset, point)

    # Compare centroid and contents
    cornelltest.assert_float_lists_equal(point, cluster1.centroid)
    cornelltest.assert_equals([], cluster1._inds)
    # Make sure centroid COPIED
    cornelltest.assert_not_equals(id(point), id(cluster1.centroid))

    # Add something to cluster (and check it was added)
    extra = [0.0, 0.5, 4.2]
    dset.add_point(extra)
    cluster1.add_point(0)
    cornelltest.assert_equals([0], cluster1._inds)

    # And clear it
    cluster1.clear()
    cornelltest.assert_equals([], cluster1._inds)
    print('    Basic cluster methods look okay')

    # A dataset with four points
    items = [[1.0, 0.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 0.0],
             [0.0, 0.0, 1.0]]
    dset = kmeans.Dataset(3, items)

    # Create two clusters
    cluster2 = kmeans.Cluster(dset, [0.5, 0.5, 0.0])
    cluster3 = kmeans.Cluster(dset, [0.0, 0.0, 0.5])

    # TEST CASES (distance)
    dist = cluster2.distance([1.0, 0.0, -1.0])
    cornelltest.assert_floats_equal(1.22474487139, dist)

    dist = cluster2.distance([0.5, 0.5, 0.0])
    cornelltest.assert_floats_equal(0.0, dist)

    dist = cluster3.distance([0.5, 0.0, 0.5])
    cornelltest.assert_floats_equal(0.5, dist)
    print('    Method Cluster.distance() looks okay')

    # TEST CASES (update_centroid)
    cluster2.add_point(0)
    cluster2.add_point(1)
    stable = cluster2.update_centroid()
    cornelltest.assert_float_lists_equal([0.5, 0.5, 0.0], cluster2.centroid)
    cornelltest.assert_true(stable)

    cluster2.add_point(2)
    cluster2.add_point(3)
    stable = cluster2.update_centroid()
    cornelltest.assert_float_lists_equal([0.25, 0.25, 0.25], cluster2.centroid)
    cornelltest.assert_false(stable)
    # updating again without changing points: centroid stable
    stable = cluster2.update_centroid()
    cornelltest.assert_float_lists_equal([0.25, 0.25, 0.25], cluster2.centroid)
    cornelltest.assert_true(stable)

    # NEW: empty-cluster update policy: clearing and updating should keep centroid unchanged and be stable
    cluster3.clear()
    old = list(cluster3.centroid)
    stable_empty = cluster3.update_centroid()
    cornelltest.assert_float_lists_equal(old, cluster3.centroid)
    cornelltest.assert_true(stable_empty)

    print('    Method Cluster.update_centroid() looks okay')
    print('  class Cluster appears correct')


def test_clustering():
    """Test the Clustering class (including private helpers for coverage)."""

    # A dataset with four points almost in a square
    items = [[0.0, 0.0], [10.0, 1.0], [10.0, 10.0], [0.0, 9.0]]
    dset = kmeans.Dataset(2, items)

    # Test creating a clustering with random seeds (deterministic via seeding)
    seed_rng()
    c = kmeans.Clustering(dset, 3)
    # Should have 3 clusters
    cornelltest.assert_equals(len(c.clusters), 3)
    seen = []
    for clust in c.clusters:
        # cluster centroids should have been chosen from items
        cornelltest.assert_true(clust.centroid in items)
        # cluster centroids should be distinct (since items are)
        for clust2 in c.clusters:
            if clust2 is not clust:
                cornelltest.assert_float_lists_not_equal(clust.centroid, clust2.centroid)
        seen.append(tuple(clust.centroid))

    # Clusterings of that dataset, with two and three deterministic clusters
    c2 = kmeans.Clustering(dset, 2, [0, 2])
    cornelltest.assert_equals(items[0], c2.clusters[0].centroid)
    cornelltest.assert_equals(items[2], c2.clusters[1].centroid)
    c3 = kmeans.Clustering(dset, 3, [0, 2, 3])
    cornelltest.assert_equals(items[0], c3.clusters[0].centroid)
    cornelltest.assert_equals(items[2], c3.clusters[1].centroid)
    cornelltest.assert_equals(items[3], c3.clusters[2].centroid)

    nearest = c2._nearest_cluster([1.0, 1.0])
    cornelltest.assert_true(nearest is c2.clusters[0])

    nearest = c2._nearest_cluster([1.0, 10.0])
    cornelltest.assert_true(nearest is c2.clusters[1])

    nearest = c3._nearest_cluster([1.0, 1.0])
    cornelltest.assert_true(nearest is c3.clusters[0])

    nearest = c3._nearest_cluster([1.0, 10.0])
    cornelltest.assert_true(nearest is c3.clusters[2])
    print('    Method Clustering._nearest_cluster() looks okay')

    # Testing _partition()
    # For this example points 0 and 3 are closer, as are 1 and 2
    c2._partition()
    for _ in range(2):
        cornelltest.assert_equals(set([0, 3]), set(c2.clusters[0]._inds))
        cornelltest.assert_equals(set([1, 2]), set(c2.clusters[1]._inds))
        # partition and repeat -- should not change clusters (idempotent)
        c2._partition()

    print('    Method Clustering._partition() looks okay')

    # Test _update()
    stable = c2._update()
    cornelltest.assert_float_lists_equal([0, 4.5], c2.clusters[0].centroid)
    cornelltest.assert_float_lists_equal([10.0, 5.5], c2.clusters[1].centroid)
    cornelltest.assert_false(stable)
    # updating again should not change anything, but should return stable
    stable = c2._update()
    cornelltest.assert_float_lists_equal([0, 4.5], c2.clusters[0].centroid)
    cornelltest.assert_float_lists_equal([10.0, 5.5], c2.clusters[1].centroid)
    cornelltest.assert_true(stable)

    print('    Method Clustering._update() looks okay')

    # Now test the k-means process itself.

    # FOR ALL TEST CASES
    # Create and initialize a non-empty dataset
    items = [[0.5, 0.5, 0.5],
             [0.5, 0.6, 0.6],
             [0.6, 0.5, 0.6],
             [0.5, 0.6, 0.5],
             [0.5, 0.4, 0.5],
             [0.5, 0.4, 0.4]]
    dset = kmeans.Dataset(3, items)

    # Create a clustering, providing non-random seed indices so the test is deterministic
    c = kmeans.Clustering(dset, 2, [1, 3])

    # PRE-TEST: Check first cluster (should be okay if passed part D)
    cluster1 = c.clusters[0]
    cornelltest.assert_float_lists_equal([0.5, 0.6, 0.6], cluster1.centroid)
    cornelltest.assert_equals(set([]), set(cluster1._inds))

    # PRE-TEST: Check second cluster (should be okay if passed part D)
    cluster2 = c.clusters[1]
    cornelltest.assert_float_lists_equal([0.5, 0.6, 0.5], cluster2.centroid)
    cornelltest.assert_equals(set([]), set(cluster2._inds))

    # Make a fake cluster to test update_centroid() method
    clustertest = kmeans.Cluster(dset, [0.5, 0.6, 0.6])
    for ind in [1, 2]:
        clustertest.add_point(ind)

    # TEST CASE 1 (update)
    stable = clustertest.update_centroid()
    cornelltest.assert_float_lists_equal([0.55, 0.55, 0.6], clustertest.centroid)
    cornelltest.assert_false(stable)  # Not yet stable

    # TEST CASE 2 (update)
    stable = clustertest.update_centroid()
    cornelltest.assert_float_lists_equal([0.55, 0.55, 0.6], clustertest.centroid)
    cornelltest.assert_true(stable)  # Now it is stable
    print('    Method update_centroid() looks okay')

    # TEST CASE 3 (k_means_step)
    c.k_means_step()

    # Check first cluster (CHANGED)
    cluster1 = c.clusters[0]
    cornelltest.assert_float_lists_equal([0.55, 0.55, 0.6], cluster1.centroid)
    cornelltest.assert_equals(set([1, 2]), set(cluster1._inds))

    # Check second cluster (CHANGED)
    cluster2 = c.clusters[1]
    cornelltest.assert_float_lists_equal([0.5, 0.475, 0.475], cluster2.centroid)
    cornelltest.assert_equals(set([0, 3, 4, 5]), set(cluster2._inds))

    # TEST CASE 4 (k_means_step again)
    c.k_means_step()

    # Check first cluster (CHANGED)
    cluster1 = c.clusters[0]
    cornelltest.assert_float_lists_equal([8.0 / 15, 17.0 / 30, 17.0 / 30], cluster1.centroid)
    cornelltest.assert_equals(set([1, 2, 3]), set(cluster1._inds))

    # Check second cluster (CHANGED)
    cluster2 = c.clusters[1]
    cornelltest.assert_float_lists_equal([0.5, 13.0 / 30, 14.0 / 30], cluster2.centroid)
    cornelltest.assert_equals(set([0, 4, 5]), set(cluster2._inds))
    print('    Method k_means_step() looks okay')

    # Try the same test case straight from the top using perform_k_means
    c_new = kmeans.Clustering(dset, 2, [1, 3])
    c_new.perform_k_means(10)

    # Check first cluster
    cluster1 = c_new.clusters[0]
    cornelltest.assert_float_lists_equal([8.0 / 15, 17.0 / 30, 17.0 / 30], cluster1.centroid)
    cornelltest.assert_equals(set([1, 2, 3]), set(cluster1._inds))

    # Check second cluster
    cluster2 = c_new.clusters[1]
    cornelltest.assert_float_lists_equal([0.5, 13.0 / 30, 14.0 / 30], cluster2.centroid)
    cornelltest.assert_equals(set([0, 4, 5]), set(cluster2._inds))
    print('    Method perform_k_means() looks okay')

    # NEW: perform_k_means with 0 iterations should be a no-op
    c_zero = kmeans.Clustering(dset, 2, [1, 3])
    before = ([list(c_zero.clusters[0].centroid), list(c_zero.clusters[1].centroid)],
              [list(c_zero.clusters[0]._inds), list(c_zero.clusters[1]._inds)])
    c_zero.perform_k_means(0)
    after = ([list(c_zero.clusters[0].centroid), list(c_zero.clusters[1].centroid)],
             [list(c_zero.clusters[0]._inds), list(c_zero.clusters[1]._inds)])
    cornelltest.assert_equals(before, after)

    print('  class Clustering appears correct')


def test_invalid_k_vs_points():
    """NEW: k greater than number of points should raise (define behavior)."""
    items = [[0.0, 0.0], [1.0, 1.0]]
    dset = kmeans.Dataset(2, items)
    expect_raises(ValueError, kmeans.Clustering, dset, 3)


if __name__ == '__main__':
    print('Starting unit test')
    test_dataset()
    test_cluster()
    test_clustering()
    test_invalid_k_vs_points()
    print('All test cases passed!')

