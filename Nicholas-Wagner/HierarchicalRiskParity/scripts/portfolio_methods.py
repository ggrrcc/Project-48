import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as sch
import scipy.optimize as sco

# ----------------------------------------------------------------------
#  A.  INVERSE-VARIANCE PORTFOLIO  (single-line implementation)
# ----------------------------------------------------------------------
def inverse_variance(cov: pd.DataFrame | np.ndarray) -> np.ndarray:
    """IVP weights  w_i ∝ 1 / σ_i²  (sum to 1)"""
    cov = np.asarray(cov)
    ivp = 1.0 / np.diag(cov)
    return ivp / ivp.sum()          # :contentReference[oaicite:0]{index=0}


# ----------------------------------------------------------------------
#  B.  MARKOWITZ MINIMUM-VARIANCE PORTFOLIO
# ----------------------------------------------------------------------
def min_variance_portfolio(cov: pd.DataFrame | np.ndarray,
                           allow_short: bool = False) -> np.ndarray:
    """
    Numerical solver for the global-minimum-variance (GMV) portfolio
    subject to Σ w = 1 and (optionally) 0 ≤ w ≤ 1.
    """

    cov = np.asarray(cov)
    n    = cov.shape[0]
    x0   = np.repeat(1.0 / n, n)        # equal-weight initial guess
    bounds = None if allow_short else [(0.0, 1.0)] * n
    cons   = ({"type": "eq", "fun": lambda w: w.sum() - 1.0},)

    def port_variance(w):
        return w @ cov @ w

    res = sco.minimize(port_variance, x0,
                       method="SLSQP",
                       bounds=bounds,
                       constraints=cons)

    if not res.success:
        raise ValueError(res.message)
    return res.x
#  (The paper refers to Markowitz’s “Critical Line Algorithm”; the
#   objective is identical – deliver the GMV weights)  :contentReference[oaicite:1]{index=1}


# ----------------------------------------------------------------------
#  C.  HIERARCHICAL RISK PARITY (HRP)
# ----------------------------------------------------------------------

# --- helper #1: convert correlation → distance ------------------------
def correl_dist(corr: pd.DataFrame | np.ndarray) -> np.ndarray:
    """Distance metric d_ij = sqrt((1 – ρ_ij)/2)  (0 ≤ d ≤ 1)."""
    return np.sqrt((1.0 - np.asarray(corr)) / 2.0)    # :contentReference[oaicite:2]{index=2}


# --- helper #2: quasi-diagonalisation --------------------------------
def quasi_diag(link: np.ndarray) -> list[int]:
    """Return indices that reorder the covariance matrix into block form."""
    link  = link.astype(int)
    sort  = pd.Series([link[-1, 0], link[-1, 1]])
    m     = link[-1, 3]                              # number of original items
    while sort.max() >= m:
        sort.index = range(0, sort.shape[0] * 2, 2)  # make space
        d = sort[sort >= m]
        j = d.index; k = d.values - m
        sort[j] = link[k, 0]
        d = pd.Series(link[k, 1], index=j + 1)
        sort = sort.append(d).sort_index()
        sort.index = range(sort.shape[0])
    return sort.tolist()                             # :contentReference[oaicite:3]{index=3}


# --- helper #3: inverse-variance weights within a cluster -------------
def _cluster_var(cov: pd.DataFrame, items: list[int]) -> float:
    cov_ = cov.loc[items, items]
    w    = inverse_variance(cov_)[:, None]
    return float(w.T @ cov_ @ w)                      # :contentReference[oaicite:4]{index=4}


# --- helper #4: recursive bisection allocation ------------------------
def _rec_bipart(cov: pd.DataFrame, sorted_index: list[int]) -> pd.Series:
    w = pd.Series(1.0, index=sorted_index)            # start with equal 1s
    clusters = [sorted_index]
    while clusters:
        # split every cluster exactly in half
        clusters = [c[j:k] for c in clusters
                    for j, k in ((0, len(c) // 2), (len(c) // 2, len(c)))
                    if len(c) > 1]
        for i in range(0, len(clusters), 2):
            c0, c1 = clusters[i], clusters[i + 1]
            var0   = _cluster_var(cov, c0)
            var1   = _cluster_var(cov, c1)
            alpha  = 1.0 - var0 / (var0 + var1)       # split factor
            w[c0] *= alpha
            w[c1] *= 1.0 - alpha
    return w                                          # :contentReference[oaicite:5]{index=5}


def hrp_allocation(cov: pd.DataFrame | np.ndarray,
                   corr: pd.DataFrame | np.ndarray) -> np.ndarray:
    """
    Full HRP pipeline – returns a NumPy weight vector that sums to 1.
    """
    cov  = pd.DataFrame(cov)
    corr = pd.DataFrame(corr)

    # Stage 1 – hierarchical clustering (single linkage on distance)
    dist    = correl_dist(corr)
    linkage = sch.linkage(dist, method="single")

    # Stage 2 – quasi-diagonalise
    sort_ix = quasi_diag(linkage)
    sort_ix = corr.index[sort_ix].tolist()            # recover label order

    # Stage 3 – recursive bisection
    w = _rec_bipart(cov, sort_ix).sort_index()
    return w.values


# ----------------------------------------------------------------------
#  D.  CONVENIENCE WRAPPER
# ----------------------------------------------------------------------
def all_methods(returns: pd.DataFrame,
                allow_short: bool = False) -> pd.DataFrame:
    """
    Given a (T × N) returns DataFrame, compute weights for IVP,
    Markowitz GMV, and HRP.  Columns are assets; rows are methods.
    """
    cov  = returns.cov()
    corr = returns.corr()

    weights = {
        "IVP":  inverse_variance(cov),
        "GMV":  min_variance_portfolio(cov, allow_short=allow_short),
        "HRP":  hrp_allocation(cov, corr),
    }
    return pd.DataFrame(weights, index=returns.columns).T

