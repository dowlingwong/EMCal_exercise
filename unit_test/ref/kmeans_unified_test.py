
# kmeans_unified_test.py
# Integrated unit test for k-means (Dataset, Cluster, Clustering)
# Merges: cornell_kmean_test.py + improved_test_untested.py
# Python 3 compatible; no external deps required (shim provided if cornelltest missing).

import random

# Try to import cornelltest; fall back to a minimal shim.
try:
    import cornelltest  # type: ignore
except Exception:  # pragma: no cover
    class cornelltest:  # type: ignore
        @staticmethod
        def assert_equals(a, b, msg=None):
            assert a == b, msg or f"{a} != {b}"

        @staticmethod
        def assert_true(x, msg=None):
            assert bool(x), msg or "expected True"

        @staticmethod
        def assert_false(x, msg=None):
            assert not bool(x), msg or "expected False"

        @staticmethod
        def assert_not_equals(a, b, msg=None):
            assert a != b, msg or f"{a} == {b}"

        @staticmethod
        def assert_floats_equal(a, b, tol=1e-9, msg=None):
            assert abs(float(a) - float(b)) <= tol, msg or f"{a} != {b}"

        @staticmethod
        def assert_float_lists_equal(a, b, tol=1e-9, msg=None):
            assert len(a) == len(b), msg or f"len {len(a)} != {len(b)}"
            for i, (x, y) in enumerate(zip(a, b)):
                if isinstance(x, list) and isinstance(y, list):
                    cornelltest.assert_float_lists_equal(x, y, tol, f"index {i} differs")
                else:
                    assert abs(float(x) - float(y)) <= tol, msg or f"idx {i}: {x} != {y}"

        @staticmethod
        def assert_float_lists_not_equal(a, b, tol=1e-12, msg=None):
            try:
                cornelltest.assert_float_lists_equal(a, b, tol)
            except AssertionError:
                return
            raise AssertionError(msg or "lists unexpectedly equal")

def expect_raises(exc_type, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        cornelltest.assert_true(isinstance(e, exc_type), f"Expected {exc_type.__name__}, got {type(e).__name__}")
        return
    raise AssertionError(f"Expected {exc_type.__name__} to be raised, but no exception occurred.")

def seed_rng():
    random.seed(123456)

import ref.kmeans as kmeans  # The implementation under test

def test_dataset():
    # Empty dataset
    dset = kmeans.Dataset(3)
    cornelltest.assert_equals(3, dset.dimension)
    cornelltest.assert_float_lists_equal([], dset.data)
    dset.add_point([0.0, 0.5, 4.2])
    cornelltest.assert_float_lists_equal([[0.0, 0.5, 4.2]], dset.data)
    print("    Default initialization looks okay")

    # Non-empty init and copy semantics
    items = [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 1.0]]
    dset = kmeans.Dataset(3, items)
    cornelltest.assert_equals(3, dset.dimension)
    cornelltest.assert_float_lists_equal(items, dset.data)
    cornelltest.assert_false(dset.data is items)
    cornelltest.assert_false(dset.data[0] is items[0])

    extra = [0.0, 0.5, 4.2]
    dset.add_point(extra)
    items.append(extra)
    cornelltest.assert_float_lists_equal(items, dset.data)
    cornelltest.assert_false(id(extra) in map(id, dset.data))

    # Wrong dimensionality should raise
    expect_raises(ValueError, dset.add_point, [1.0, 2.0])
    print("    User-given contents looks okay")
    print("  class Dataset appears correct")

def test_cluster():
    # Basic cluster
    dset = kmeans.Dataset(3)
    point = [0.0, 1.0, 0.0]
    cluster1 = kmeans.Cluster(dset, point)
    cornelltest.assert_float_lists_equal(point, cluster1.centroid)
    cornelltest.assert_equals([], cluster1._inds)
    cornelltest.assert_not_equals(id(point), id(cluster1.centroid))

    extra = [0.0, 0.5, 4.2]
    dset.add_point(extra)
    cluster1.add_point(0)
    cornelltest.assert_equals([0], cluster1._inds)
    cluster1.clear()
    cornelltest.assert_equals([], cluster1._inds)
    print("    Basic cluster methods look okay")

    # Distances
    items = [[1.0, 0.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 0.0],
             [0.0, 0.0, 1.0]]
    dset = kmeans.Dataset(3, items)
    cluster2 = kmeans.Cluster(dset, [0.5, 0.5, 0.0])
    cluster3 = kmeans.Cluster(dset, [0.0, 0.0, 0.5])

    dist = cluster2.distance([1.0, 0.0, -1.0])
    cornelltest.assert_floats_equal(1.22474487139, dist)
    dist = cluster2.distance([0.5, 0.5, 0.0])
    cornelltest.assert_floats_equal(0.0, dist)
    dist = cluster3.distance([0.5, 0.0, 0.5])
    cornelltest.assert_floats_equal(0.5, dist)
    print("    Method Cluster.distance() looks okay")

    # update_centroid behavior
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

    stable = cluster2.update_centroid()
    cornelltest.assert_float_lists_equal([0.25, 0.25, 0.25], cluster2.centroid)
    cornelltest.assert_true(stable)

    # Empty-cluster update should be stable and keep centroid
    cluster3.clear()
    old = list(cluster3.centroid)
    stable_empty = cluster3.update_centroid()
    cornelltest.assert_float_lists_equal(old, cluster3.centroid)
    cornelltest.assert_true(stable_empty)

    print("    Method Cluster.update_centroid() looks okay")
    print("  class Cluster appears correct")

def test_clustering():
    # Square-ish 2D dataset
    items = [[0.0, 0.0], [10.0, 1.0], [10.0, 10.0], [0.0, 9.0]]
    dset = kmeans.Dataset(2, items)

    # Random seeds (deterministic under seed)
    seed_rng()
    c = kmeans.Clustering(dset, 3)
    cornelltest.assert_equals(len(c.clusters), 3)
    for clust in c.clusters:
        cornelltest.assert_true(clust.centroid in items)
        for clust2 in c.clusters:
            if clust2 is not clust:
                cornelltest.assert_float_lists_not_equal(clust.centroid, clust2.centroid)

    # Deterministic seed indices
    c2 = kmeans.Clustering(dset, 2, [0, 2])
    cornelltest.assert_equals(items[0], c2.clusters[0].centroid)
    cornelltest.assert_equals(items[2], c2.clusters[1].centroid)
    c3 = kmeans.Clustering(dset, 3, [0, 2, 3])
    cornelltest.assert_equals(items[0], c3.clusters[0].centroid)
    cornelltest.assert_equals(items[2], c3.clusters[1].centroid)
    cornelltest.assert_equals(items[3], c3.clusters[2].centroid)

    # _nearest_cluster
    nearest = c2._nearest_cluster([1.0, 1.0]); cornelltest.assert_true(nearest is c2.clusters[0])
    nearest = c2._nearest_cluster([1.0, 10.0]); cornelltest.assert_true(nearest is c2.clusters[1])
    nearest = c3._nearest_cluster([1.0, 1.0]); cornelltest.assert_true(nearest is c3.clusters[0])
    nearest = c3._nearest_cluster([1.0, 10.0]); cornelltest.assert_true(nearest is c3.clusters[2])
    print("    Method Clustering._nearest_cluster() looks okay")

    # _partition idempotence
    c2._partition()
    for _ in range(2):
        cornelltest.assert_equals(set([0, 3]), set(c2.clusters[0]._inds))
        cornelltest.assert_equals(set([1, 2]), set(c2.clusters[1]._inds))
        c2._partition()
    print("    Method Clustering._partition() looks okay")

    # _update stability
    stable = c2._update()
    cornelltest.assert_float_lists_equal([0, 4.5], c2.clusters[0].centroid)
    cornelltest.assert_float_lists_equal([10.0, 5.5], c2.clusters[1].centroid)
    cornelltest.assert_false(stable)
    stable = c2._update()
    cornelltest.assert_float_lists_equal([0, 4.5], c2.clusters[0].centroid)
    cornelltest.assert_float_lists_equal([10.0, 5.5], c2.clusters[1].centroid)
    cornelltest.assert_true(stable)
    print("    Method Clustering._update() looks okay")

    # 3D deterministic example
    items3 = [[0.5, 0.5, 0.5],
              [0.5, 0.6, 0.6],
              [0.6, 0.5, 0.6],
              [0.5, 0.6, 0.5],
              [0.5, 0.4, 0.5],
              [0.5, 0.4, 0.4]]
    dset3 = kmeans.Dataset(3, items3)
    cdet = kmeans.Clustering(dset3, 2, [1, 3])

    # One step
    cdet.k_means_step()
    cornelltest.assert_float_lists_equal([0.55, 0.55, 0.6], cdet.clusters[0].centroid)
    cornelltest.assert_equals(set([1, 2]), set(cdet.clusters[0]._inds))
    cornelltest.assert_float_lists_equal([0.5, 0.475, 0.475], cdet.clusters[1].centroid)
    cornelltest.assert_equals(set([0, 3, 4, 5]), set(cdet.clusters[1]._inds))

    # Second step
    cdet.k_means_step()
    cornelltest.assert_float_lists_equal([8.0/15, 17.0/30, 17.0/30], cdet.clusters[0].centroid)
    cornelltest.assert_equals(set([1, 2, 3]), set(cdet.clusters[0]._inds))
    cornelltest.assert_float_lists_equal([0.5, 13.0/30, 14.0/30], cdet.clusters[1].centroid)
    cornelltest.assert_equals(set([0, 4, 5]), set(cdet.clusters[1]._inds))
    print("    Method k_means_step() looks okay")

    # Full run
    cnew = kmeans.Clustering(dset3, 2, [1, 3])
    cnew.perform_k_means(10)
    cornelltest.assert_float_lists_equal([8.0/15, 17.0/30, 17.0/30], cnew.clusters[0].centroid)
    cornelltest.assert_equals(set([1, 2, 3]), set(cnew.clusters[0]._inds))
    cornelltest.assert_float_lists_equal([0.5, 13.0/30, 14.0/30], cnew.clusters[1].centroid)
    cornelltest.assert_equals(set([0, 4, 5]), set(cnew.clusters[1]._inds))
    print("    Method perform_k_means() looks okay")
    print("  class Clustering appears correct")

def test_invalid_k_vs_points():
    items = [[0.0, 0.0], [1.0, 1.0]]
    dset = kmeans.Dataset(2, items)
    expect_raises(ValueError, kmeans.Clustering, dset, 3)

if __name__ == "__main__":
    print("Starting unit test")
    test_dataset()
    test_cluster()
    test_clustering()
    test_invalid_k_vs_points()
    print("All test cases passed!")
