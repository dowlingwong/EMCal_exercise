# gmm_test.py
# Standalone unit tests for the energy-weighted GaussianMixtureEM class of Exercise 03, Problem 4.2.
# Run from the notebook with   %run -i ../../tests/exercise03/gmm_test.py
# (the class must already be defined in the notebook namespace), or standalone with
#   python3 tests/exercise03/gmm_test.py   if a module gmm.py providing GaussianMixtureEM is importable.

import numpy as np

try:
    GaussianMixtureEM  # type: ignore  # noqa: B018
except NameError:
    try:
        from gmm import GaussianMixtureEM  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise ImportError("GaussianMixtureEM is not defined. Execute the cell with your class first.") from exc


def _toy_data(seed=0):
    rng = np.random.default_rng(seed)
    a = rng.normal([0.0, 0.0], 2.0, size=(40, 2))
    b = rng.normal([12.0, 5.0], 3.0, size=(30, 2))
    X = np.vstack([a, b])
    w = rng.uniform(0.1, 5.0, size=len(X))
    w = w * len(X) / w.sum()
    return X, w


def _prepared_model(X, covariance="full"):
    g = GaussianMixtureEM(2, covariance=covariance, sigma=2.5)
    g.means_ = np.array([[1.0, -1.0], [10.0, 4.0]])
    g.covariances_ = np.array([np.eye(2) * 4.0, np.array([[9.0, 1.0], [1.0, 6.0]])])
    g.weights_ = np.array([0.6, 0.4])
    return g


def _brute_force_responsibilities(g, X):
    dens = np.zeros((len(X), g.K))
    for k in range(g.K):
        S = g.covariances_[k]
        diff = X - g.means_[k]
        maha = np.einsum("ni,ij,nj->n", diff, np.linalg.inv(S), diff)
        tower = np.exp(-0.5 * g.reg * np.trace(np.linalg.inv(S)))  # tower-averaged density
        dens[:, k] = g.weights_[k] * np.exp(-0.5 * maha) / (2 * np.pi * np.sqrt(np.linalg.det(S))) * tower
    return dens / dens.sum(axis=1, keepdims=True), dens


def test_e_step():
    X, _ = _toy_data()
    g = _prepared_model(X)
    r = np.asarray(g.e_step(X))
    assert r.shape == (len(X), 2), f"e_step must return shape (N, K) = {(len(X), 2)}, got {r.shape}"
    assert np.all(r >= 0) and np.all(r <= 1), "responsibilities must lie in [0, 1]"
    assert np.allclose(r.sum(axis=1), 1.0), "responsibilities of every point must sum to 1"
    r_ref, _ = _brute_force_responsibilities(g, X)
    assert np.allclose(r, r_ref, atol=1e-8), "e_step disagrees with the brute-force posterior"
    # far away points must not produce NaN (log-space normalisation)
    r_far = np.asarray(g.e_step(np.array([[1e4, 1e4]])))
    assert np.all(np.isfinite(r_far)), "e_step returns NaN/inf for a distant point: normalise in log space"
    print("  e_step ............ OK")


def test_m_step():
    X, w = _toy_data()
    g = _prepared_model(X)
    rng = np.random.default_rng(1)
    r = rng.dirichlet([1.0, 1.0], size=len(X))
    g.m_step(X, w, r)
    wr = w[:, None] * r
    Nk = wr.sum(axis=0)
    assert np.allclose(g.weights_, Nk / Nk.sum()), "mixing weights pi_k are wrong"
    mu_ref = np.array([np.average(X, axis=0, weights=wr[:, k]) for k in range(2)])
    assert np.allclose(g.means_, mu_ref), "means mu_k are wrong (energy-weighted responsibilities!)"
    for k in range(2):
        diff = X - mu_ref[k]
        S_ref = (wr[:, k, None] * diff).T @ diff / Nk[k] + g.reg * np.eye(2)
        assert np.allclose(g.covariances_[k], S_ref), f"covariance of component {k} is wrong (did you add reg * I?)"
    g_fixed = _prepared_model(X, covariance="fixed")
    g_fixed.m_step(X, w, r)
    assert np.allclose(g_fixed.covariances_, 2.5 ** 2 * np.eye(2)), "fixed covariance must stay sigma^2 * I"
    print("  m_step ............ OK")


def test_elbo():
    X, w = _toy_data()
    g = _prepared_model(X)
    r_ref, dens = _brute_force_responsibilities(g, X)
    loglik = np.sum(w * np.log(dens.sum(axis=1)))
    elbo_post = g.elbo(X, w, r_ref)
    assert np.isclose(elbo_post, loglik, rtol=1e-8), "with q = posterior the ELBO must equal the log-likelihood"
    r_other = np.random.default_rng(2).dirichlet([1.0, 1.0], size=len(X))
    assert g.elbo(X, w, r_other) < loglik, "the ELBO must be a lower bound of the log-likelihood"
    r_hard = np.eye(2)[np.argmax(r_ref, axis=1)]
    assert np.isfinite(g.elbo(X, w, r_hard)), "ELBO must handle r = 0 (use 0 * log 0 = 0)"
    print("  elbo .............. OK")


def test_fit_monotonic():
    X, w = _toy_data()
    for cov in ["full", "fixed"]:
        g = GaussianMixtureEM(2, covariance=cov, sigma=2.5).fit(X, sample_weight=w, init_means=[[0.0, 0.0], [5.0, 5.0]])
        elbos = np.array([h[2] for h in g.history_])
        assert np.all(np.diff(elbos) >= -1e-8 * np.abs(elbos[:-1])), f"ELBO decreased during EM ({cov} covariance)"
        found = sorted(map(tuple, np.round(g.means_)))
        assert np.allclose(found[0], [0, 0], atol=1.5) and np.allclose(found[1], [12, 5], atol=1.5), \
            f"EM ({cov}) did not find the two clusters: {g.means_}"
    print("  fit / monotonic ... OK")


def test_kmeans_limit():
    X, w = _toy_data()
    g = GaussianMixtureEM(2, covariance="fixed", sigma=0.05).fit(X, sample_weight=w, init_means=[[0.0, 0.0], [12.0, 5.0]])
    r = g.responsibilities_
    assert np.all((r < 1e-6) | (r > 1 - 1e-6)), "for sigma -> 0 the responsibilities must become one-hot (K-means)"
    print("  sigma -> 0 limit .. OK")


if __name__ == "__main__" or True:
    print("Running GaussianMixtureEM tests ...")
    test_e_step()
    test_m_step()
    test_elbo()
    test_fit_monotonic()
    test_kmeans_limit()
    print("All GaussianMixtureEM tests passed!")
