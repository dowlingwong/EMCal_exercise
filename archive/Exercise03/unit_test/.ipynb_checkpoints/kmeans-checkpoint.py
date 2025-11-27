
import numpy as np

def _euclidean_squared(a, b):
    # a: (n_samples, n_features), b: (n_clusters, n_features)
    # returns (n_samples, n_clusters)
    a2 = np.sum(a*a, axis=1, keepdims=True)
    b2 = np.sum(b*b, axis=1)
    ab = a @ b.T
    d2 = a2 - 2*ab + b2
    return d2

def _kmeanspp_init(X, k, rng):
    n_samples = X.shape[0]
    centroids = np.empty((k, X.shape[1]), dtype=X.dtype)
    # choose first centroid uniformly
    idx0 = rng.integers(0, n_samples)
    centroids[0] = X[idx0]
    # choose remaining with prob proportional to D^2
    closest_dist_sq = _euclidean_squared(X, centroids[0:1]).ravel()
    for i in range(1, k):
        probs = closest_dist_sq / closest_dist_sq.sum()
        idx = rng.choice(n_samples, p=probs)
        centroids[i] = X[idx]
        d2 = _euclidean_squared(X, centroids[i:i+1]).ravel()
        closest_dist_sq = np.minimum(closest_dist_sq, d2)
    return centroids

def kmeans(X, k, max_iter=300, tol=1e-4, init="k-means++", random_state=None):
    X = np.asarray(X, dtype=float)
    rng = np.random.default_rng(random_state)
    if init == "k-means++":
        centroids = _kmeanspp_init(X, k, rng)
    elif init == "random":
        indices = rng.choice(X.shape[0], size=k, replace=False)
        centroids = X[indices].copy()
    else:
        raise ValueError("init must be 'k-means++' or 'random'")
    
    labels = None
    for it in range(1, max_iter+1):
        # assignment step
        d2 = _euclidean_squared(X, centroids)  # (n_samples, k)
        new_labels = np.argmin(d2, axis=1)
        # update step
        new_centroids = centroids.copy()
        for j in range(k):
            mask = new_labels == j
            if np.any(mask):
                new_centroids[j] = X[mask].mean(axis=0)
            else:
                # reinitialize empty cluster to a random point
                new_centroids[j] = X[rng.integers(0, X.shape[0])]
        # check convergence
        shift = np.sqrt(np.sum((new_centroids - centroids)**2))
        centroids = new_centroids
        if labels is not None and np.all(new_labels == labels):
            break
        if shift < tol:
            labels = new_labels
            break
        labels = new_labels
    
    inertia = float(np.sum((X - centroids[labels])**2))
    return labels, centroids, inertia, it
