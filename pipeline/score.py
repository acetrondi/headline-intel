"""Score a headline with the fitted model (reference implementation).

    python3 src/score.py hackernews "How we cut p99 latency 40%"
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import features as F

M = json.load(open(os.path.join(ROOT, "data", "model.json"), encoding="utf-8"))


def pick_model(platform):
    """Per-platform model when it beat the mean on holdout, else the pooled one.

    Pooling hurts here: the platform rules invert, so a single pooled model
    averages them toward zero. See reports/07.
    """
    if M.get("recommended_model", {}).get(platform) == "platform":
        return M["platforms"][platform]["full"], "platform"
    return M["pooled"]["full"], "pooled"


def score(title, platform):
    f = F.title_features(title)
    m, which = pick_model(platform)
    s = m["intercept"]
    for k in m["features"]:
        v = (1.0 if k == "plat_" + platform else 0.0) if k.startswith("plat_") else float(f[k])
        s += ((v - m["mean"][k]) / m["std"][k]) * m["weights"][k]
    return {"raw": s, "pct": max(0.0, min(100.0, s * 100)), "features": f,
            "model": which}


if __name__ == "__main__":
    plat = sys.argv[1] if len(sys.argv) > 2 else "hackernews"
    title = sys.argv[-1]
    r = score(title, plat)
    print(f"{r['pct']:.2f}/100   [{plat} / {r['model']} model]  {title}")
    ax = M["axis_weights_by_platform"].get(plat, M["pooled"]["axes"]["weights"])
    for a in M["axes"]:
        print(f"  {M['axis_labels'][a]:20} value {r['features'][a]:.3f}  weight {ax.get(a,0):+.4f}")
