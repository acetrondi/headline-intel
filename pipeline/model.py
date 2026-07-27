"""Fit the attention-scoring model from the data.

Two models are fitted and compared:

  FULL  - ridge regression on ~45 raw title features (best predictive accuracy)
  AXES  - ridge regression on the 9 human-readable axes the brief asks for
          (curiosity, novelty, specificity, emotional impact, readability,
           authority, clarity, promise of value, information density)

Target is the within-platform engagement percentile, so the model learns
"which headline out-performs its platform's baseline", not "which platform is
bigger". Weights are exported to data/model.json for the web app and the skill.

Honesty note: headline text is a weak signal. Expect small R2. The value is in
the *direction and relative size* of the weights, not in point prediction.
"""
import json, os, sys, math, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import features as F
from analyze import spearman

IN = os.path.join(ROOT, "data", "dataset.jsonl")
OUT = os.path.join(ROOT, "data", "model.json")

AXES = ["curiosity_gap", "novelty", "specificity", "emotional_intensity",
        "readability_norm", "authority", "clarity", "promise_of_value", "info_density"]

AXIS_LABEL = {
    "curiosity_gap": "Curiosity",
    "novelty": "Novelty",
    "specificity": "Specificity",
    "emotional_intensity": "Emotional impact",
    "readability_norm": "Readability",
    "authority": "Authority",
    "clarity": "Clarity",
    "promise_of_value": "Promise of value",
    "info_density": "Information density",
}

# raw features excluded from FULL because they are the composites themselves
EXCLUDE = set(AXES) | {"sentiment"}
FULL_FEATS = [k for k in F.FEATURE_ORDER if k not in EXCLUDE]


def ridge(X, y, lam):
    n, p = X.shape
    A = X.T @ X + lam * np.eye(p)
    return np.linalg.solve(A, X.T @ y)


def fit(rows, feats, platform_dummies=False, lam_grid=(0.1, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000), seed=7):
    """Standardize -> ridge with lambda picked on a validation split -> holdout eval."""
    X = np.array([[float(r["f"][k]) for k in feats] for r in rows], dtype=float)
    y = np.array([r["engagement_pct"] for r in rows], dtype=float)
    dummy_names = []
    if platform_dummies:
        plats = sorted({r["platform"] for r in rows})[1:]   # drop first as base
        dummy_names = ["plat_" + p for p in plats]
        D = np.array([[1.0 if r["platform"] == p else 0.0 for p in plats] for r in rows])
        X = np.hstack([X, D])
    feats = list(feats) + dummy_names
    idx = list(range(len(rows)))
    random.Random(seed).shuffle(idx)
    ntr = int(len(idx) * 0.70)
    nva = int(len(idx) * 0.85)
    tr, va, te = idx[:ntr], idx[ntr:nva], idx[nva:]

    mu, sd = X[tr].mean(0), X[tr].std(0)
    sd[sd == 0] = 1.0
    Z = (X - mu) / sd
    Z = np.hstack([Z, np.ones((len(Z), 1))])

    best, best_lam = None, None
    for lam in lam_grid:
        w = ridge(Z[tr], y[tr], lam)
        pred = Z[va] @ w
        r2 = 1 - ((y[va] - pred) ** 2).sum() / ((y[va] - y[va].mean()) ** 2).sum()
        if best is None or r2 > best:
            best, best_lam = r2, lam
    w = ridge(Z[np.array(tr + va)], y[np.array(tr + va)], best_lam)

    pred_te = Z[te] @ w
    r2_te = 1 - ((y[te] - pred_te) ** 2).sum() / ((y[te] - y[te].mean()) ** 2).sum()
    rho_te = spearman(list(pred_te), list(y[te]))
    pred_tr = Z[np.array(tr + va)] @ w
    r2_tr = 1 - ((y[np.array(tr+va)] - pred_tr) ** 2).sum() / (
        (y[np.array(tr+va)] - y[np.array(tr+va)].mean()) ** 2).sum()

    # decile check: does a higher score actually mean higher engagement?
    order = np.argsort(pred_te)
    deciles = []
    k = max(1, len(order) // 10)
    for d in range(10):
        seg = order[d * k:(d + 1) * k] if d < 9 else order[9 * k:]
        if len(seg):
            deciles.append(round(float(y[te][seg].mean()), 4))

    return {
        "features": feats,
        "weights": {k: round(float(v), 5) for k, v in zip(feats, w[:-1])},
        "intercept": round(float(w[-1]), 5),
        "mean": {k: round(float(v), 6) for k, v in zip(feats, mu)},
        "std": {k: round(float(v), 6) for k, v in zip(feats, sd)},
        "lambda": best_lam,
        "n_train": len(tr) + len(va), "n_holdout": len(te),
        "r2_train": round(float(r2_tr), 4),
        "r2_holdout": round(float(r2_te), 4),
        "spearman_holdout": round(float(rho_te), 4),
        "holdout_decile_mean_engagement": deciles,
    }


def main():
    rows = [json.loads(l) for l in open(IN, encoding="utf-8")]
    platforms = sorted({r["platform"] for r in rows})

    model = {"target": "within-platform engagement percentile (0-1)",
             "n_total": len(rows), "axes": AXES, "axis_labels": AXIS_LABEL,
             "platforms": {}, "pooled": {}}

    model["pooled"]["full"] = fit(rows, FULL_FEATS, platform_dummies=True)
    model["pooled"]["axes"] = fit(rows, AXES, platform_dummies=True)
    model["pooled"]["full_no_dummies"] = fit(rows, FULL_FEATS)

    for p in platforms:
        sub = [r for r in rows if r["platform"] == p]
        if len(sub) < 200:
            model["platforms"][p] = {"n": len(sub), "skipped": "n<200"}
            continue
        model["platforms"][p] = {"n": len(sub),
                                 "full": fit(sub, FULL_FEATS),
                                 "axes": fit(sub, AXES)}

    # which model to serve per platform: the per-platform fit when it actually
    # generalised (positive holdout R2), otherwise the pooled fallback.
    # This MUST be computed here, not patched in afterwards, or a refit silently
    # reverts every platform to pooled.
    model["recommended_model"] = {
        p: ("platform" if ("full" in d and d["full"]["r2_holdout"] > 0) else "pooled")
        for p, d in model["platforms"].items()}

    # normalized, human-facing axis weights: share of absolute weight, signed
    aw = {k: v for k, v in model["pooled"]["axes"]["weights"].items() if not k.startswith("plat_")}
    tot = sum(abs(v) for v in aw.values()) or 1
    model["axis_weights_normalized"] = {
        k: {"weight": round(v, 5), "share": round(abs(v) / tot, 4),
            "direction": "positive" if v >= 0 else "negative",
            "label": AXIS_LABEL[k]}
        for k, v in sorted(aw.items(), key=lambda kv: -abs(kv[1]))}

    # per-platform axis weights, for the app's platform selector
    model["axis_weights_by_platform"] = {}
    for p, d in model["platforms"].items():
        if "axes" in d:
            model["axis_weights_by_platform"][p] = d["axes"]["weights"]

    json.dump(model, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("wrote", OUT)
    print(f"\n{'model':22} {'n_train':>8} {'R2 train':>9} {'R2 hold':>9} {'rho hold':>9}")
    for name, d in [("pooled/full", model["pooled"]["full"]),
                    ("pooled/axes", model["pooled"]["axes"])]:
        print(f"{name:22} {d['n_train']:8} {d['r2_train']:9.4f} {d['r2_holdout']:9.4f} "
              f"{d['spearman_holdout']:9.4f}")
    for p, d in model["platforms"].items():
        if "full" in d:
            for tag in ("full", "axes"):
                print(f"{p+'/'+tag:22} {d[tag]['n_train']:8} {d[tag]['r2_train']:9.4f} "
                      f"{d[tag]['r2_holdout']:9.4f} {d[tag]['spearman_holdout']:9.4f}")
    print("\npooled axis weights (standardized):")
    for k, v in model["axis_weights_normalized"].items():
        print(f"  {v['label']:20} {v['weight']:+.4f}   share {v['share']:.3f}")
    print("\nmodel served per platform:", model["recommended_model"])
    print("\npooled/full holdout deciles:", model["pooled"]["full"]["holdout_decile_mean_engagement"])


if __name__ == "__main__":
    main()
