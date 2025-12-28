# test_kmeans_standalone_for_user_class.py
# Standalone unit tests (no cornelltest) for a NumPy-only KMeans class.
# Assumes a class named `KMeans` is importable from the current environment
# (e.g., defined above in the same notebook/script, or from a module import).

import math
import numpy as np

# ---------------- Helper assertion functions ----------------

def assert_equals(expected, actual, msg=None):
    assert expected == actual, msg or f"Expected {expected!r}, got {actual!r}"

def assert_not_equals(a, b, msg=None):
    assert a != b, msg or f"Did not expect {a!r} == {b!r}"

def assert_true(expr, msg=None):
    assert bool(expr), msg or f"Expression is not true: {expr!r}"

def assert_false(expr, msg=None):
    assert not bool(expr), msg or f"Expression is not false: {expr!r}"

def assert_floats_equal(expected, actual, tol=1e-6, msg=None):
    if (isinstance(expected, float) and math.isnan(expected)) and (isinstance(actual, float) and math.isnan(actual)):
        return
    assert abs(expected-actual) <= tol, msg or f"Expected {expected}, got {actual} (tol={tol})"

def assert_float_lists_equal(expected, actual, tol=1e-6, msg=None):
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    assert expected.shape == actual.shape, msg or f"Shape mismatch: {expected.shape} vs {actual.shape}"
    diff = np.abs(expected - actual)
    assert np.all(diff <= tol), msg or f"Max diff {diff.max()} exceeds tol {tol}"

def rows_equal_any_permutation(A, B, tol=1e-8):
    """Return True if A and B contain the same rows up to permutation (within tol)."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    if A.shape != B.shape:
        return False
    used = np.zeros(B.shape[0], dtype=bool)
    for i in range(A.shape[0]):
        found = False
        for j in range(B.shape[0]):
            if not used[j] and np.allclose(A[i], B[j], atol=tol, rtol=0):
                used[j] = True
                found = True
                break
        if not found:
            return False
    return True

# ---------------- Tests for user's KMeans class ----------------

try:
    KMeans  # type: ignore
except NameError:
    try:
        from kmeans import KMeans  # try local module named kmeans.py
    except Exception as e:
        raise ImportError(
            "Could not find KMeans in the current environment. " "Define your KMeans class above or ensure 'from kmeans import KMeans' works."
        ) from e


def test_basic_shapes_and_types():
    rng = np.random.default_rng(0)
    X = np.vstack([
        rng.normal([0,0], 0.2, size=(30,2)),
        rng.normal([5,5], 0.2, size=(30,2)),
        rng.normal([10,0], 0.2, size=(30,2)),
    ])
    km = KMeans(n_clusters=3, init="random", random_state=123)
    labels = km.fit_predict(X)

    assert_equals(X.shape[0], labels.shape[0])
    assert_equals((3, X.shape[1]), km.cluster_centers_.shape)
    assert_true(km.inertia_ >= 0.0)
    assert_true(isinstance(km.n_iter_, int) and km.n_iter_ >= 1)


def test_determinism_with_seed():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(100, 2))

    km1 = KMeans(n_clusters=3, init="random", random_state=7)
    km2 = KMeans(n_clusters=3, init="random", random_state=7)

    labels1 = km1.fit_predict(X)
    labels2 = km2.fit_predict(X)

    assert_float_lists_equal(labels1, labels2, tol=0.0)
    assert_true(rows_equal_any_permutation(km1.cluster_centers_, km2.cluster_centers_))


def test_predict_matches_training_assignment():
    rng = np.random.default_rng(2)
    X = np.vstack([rng.normal([0,0], 0.3, size=(50,2)),
                   rng.normal([4,4], 0.3, size=(50,2))])
    km = KMeans(n_clusters=2, init="random", random_state=9).fit(X)

    d2 = ((X[:, None, :] - km.cluster_centers_[None, :, :])**2).sum(axis=2)
    nearest = np.argmin(d2, axis=1)
    assert_float_lists_equal(nearest, km.labels_, tol=0.0)

    new_pts = np.array([[0.05, -0.02], [4.1, 3.9]])
    preds = km.predict(new_pts)
    d2_new = ((new_pts[:, None, :] - km.cluster_centers_[None, :, :])**2).sum(axis=2)
    nearest_new = np.argmin(d2_new, axis=1)
    assert_float_lists_equal(preds, nearest_new, tol=0.0)


def test_inertia_definition():
    rng = np.random.default_rng(3)
    X = rng.normal(size=(80, 3))
    km = KMeans(n_clusters=4, init="random", random_state=11).fit(X)

    d2 = ((X[:, None, :] - km.cluster_centers_[None, :, :])**2).sum(axis=2)
    manual_inertia = float(np.sum(d2[np.arange(X.shape[0]), km.labels_]))
    assert_floats_equal(km.inertia_, manual_inertia, tol=1e-8)


def run_all_tests():
    print("Running KMeans standalone tests...")
    test_basic_shapes_and_types()
    print("  \u2713 test_basic_shapes_and_types")
    test_determinism_with_seed()
    print("  \u2713 test_determinism_with_seed")
    test_predict_matches_training_assignment()
    print("  \u2713 test_predict_matches_training_assignment")
    test_inertia_definition()
    print("  \u2713 test_inertia_definition")
    print("All tests passed!")

if __name__ == '__main__':
    run_all_tests()