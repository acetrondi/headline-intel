"""Product-level validation: does the score actually pick the better headline?

R2 and Spearman answer "does the model fit". Neither answers the question a
customer cares about, which is "if I give it two drafts, does it pick the one
that will do better?" That is a *pairwise ranking* question, and it has a
natural baseline: 50%.

Three tests here, in increasing order of how hard they are to pass:

  1. PAIRWISE      — random pairs within a platform. Confounded by topic, author
                     and era, so this is the optimistic number.
  2. SAME-AUTHOR   — pairs by the same author on the same platform. Holds
                     audience size and reputation constant, which are the two
                     biggest confounds. This is the number that most closely
                     mirrors real use: one writer choosing between their own drafts.
  3. OUT-OF-TIME   — train on older posts, test on newer ones. Catches a model
                     that has memorised a period instead of learning something
                     durable. A random holdout cannot catch this.
"""
import json, os, sys, math, random
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import features as F
from model import fit, FULL_FEATS
import score as SC

IN = os.path.join(ROOT, "data", "dataset.jsonl")
OUT = os.path.join(ROOT, "data", "validation.json")

PLAT_NAME = {"hackernews": "Hacker News", "reddit": "Reddit", "devto": "Dev.to",
             "medium": "Medium", "substack": "Substack", "x": "X / Twitter"}


def wilson(k, n, z=1.96):
    """95% CI for a proportion. Small-sample honest, unlike normal approx."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d, (c + m) / d)


def pairwise(rows, pairs, label):
    """Accuracy at picking the higher-engagement post of a pair."""
    ok = tie = 0
    for a, b in pairs:
        ya, yb = a["engagement_pct"], b["engagement_pct"]
        if ya == yb:
            tie += 1
            continue
        sa = SC.score(a["title"], a["platform"])["pct"]
        sb = SC.score(b["title"], b["platform"])["pct"]
        if sa == sb:
            tie += 1
            continue
        if (sa > sb) == (ya > yb):
            ok += 1
    n = len(pairs) - tie
    lo, hi = wilson(ok, n)
    return {"label": label, "n_pairs": n, "ties_skipped": tie,
            "accuracy": round(ok / n, 4) if n else 0.0,
            "ci95": [round(lo, 4), round(hi, 4)],
            "beats_coinflip": bool(lo > 0.5)}


def main():
    rows = [json.loads(l) for l in open(IN, encoding="utf-8")]
    rnd = random.Random(11)
    by_plat = defaultdict(list)
    for r in rows:
        by_plat[r["platform"]].append(r)

    out = {"n": len(rows), "tests": {}}

    # ---- 1 + 2: pairwise, random and same-author -----------------------
    print("\n[1] RANDOM PAIRS within platform  (optimistic: topic/author/era uncontrolled)")
    rand_res = {}
    for p, rs in sorted(by_plat.items()):
        pairs = []
        for _ in range(6000):
            a, b = rnd.sample(rs, 2)
            pairs.append((a, b))
        d = pairwise(rs, pairs, p)
        rand_res[p] = d
        flag = "yes" if d["beats_coinflip"] else "NO"
        print(f"  {PLAT_NAME[p]:14} {d['accuracy']:.3f}  "
              f"CI [{d['ci95'][0]:.3f}, {d['ci95'][1]:.3f}]  n={d['n_pairs']:5}  beats 50%: {flag}")
    out["tests"]["random_pairs"] = rand_res

    print("\n[2] SAME-AUTHOR PAIRS  (audience + reputation held constant — the real use case)")
    sa_res = {}
    for p, rs in sorted(by_plat.items()):
        by_auth = defaultdict(list)
        for r in rs:
            a = (r.get("author") or "").strip().lower()
            if a and a not in ("[deleted]", "unknown", ""):
                by_auth[a].append(r)
        pairs = []
        for a, group in by_auth.items():
            if len(group) < 2:
                continue
            for _ in range(min(40, len(group) * (len(group) - 1) // 2)):
                x, y = rnd.sample(group, 2)
                pairs.append((x, y))
        if len(pairs) < 60:
            print(f"  {PLAT_NAME[p]:14} skipped — only {len(pairs)} same-author pairs available")
            sa_res[p] = {"skipped": True, "n_pairs": len(pairs)}
            continue
        d = pairwise(rs, pairs, p)
        d["n_authors"] = sum(1 for g in by_auth.values() if len(g) >= 2)
        sa_res[p] = d
        flag = "yes" if d["beats_coinflip"] else "NO"
        print(f"  {PLAT_NAME[p]:14} {d['accuracy']:.3f}  "
              f"CI [{d['ci95'][0]:.3f}, {d['ci95'][1]:.3f}]  n={d['n_pairs']:5}  "
              f"authors={d['n_authors']:4}  beats 50%: {flag}")
    out["tests"]["same_author_pairs"] = sa_res

    # ---- 3: out-of-time generalisation ---------------------------------
    print("\n[3] OUT-OF-TIME  (train on <=2023, test on >=2024 — catches period memorisation)")
    oot = {}
    for p, rs in sorted(by_plat.items()):
        old = [r for r in rs if r.get("year") and r["year"] <= 2023]
        new = [r for r in rs if r.get("year") and r["year"] >= 2024]
        if len(old) < 250 or len(new) < 120:
            print(f"  {PLAT_NAME[p]:14} skipped — old={len(old)} new={len(new)} (need 250/120)")
            oot[p] = {"skipped": True, "n_old": len(old), "n_new": len(new)}
            continue
        # fit on the old period only, using the same machinery as model.py
        m = fit(old, FULL_FEATS)
        X = np.array([[float(r["f"][k]) for k in FULL_FEATS] for r in new], dtype=float)
        mu = np.array([m["mean"][k] for k in FULL_FEATS])
        sd = np.array([m["std"][k] for k in FULL_FEATS])
        w = np.array([m["weights"][k] for k in FULL_FEATS])
        pred = ((X - mu) / sd) @ w + m["intercept"]
        y = np.array([r["engagement_pct"] for r in new])
        from analyze import spearman
        rho = spearman(list(pred), list(y))
        r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
        # pairwise on the future period, using the past-only model
        ok = n = 0
        for _ in range(4000):
            i, j = rnd.sample(range(len(new)), 2)
            if y[i] == y[j] or pred[i] == pred[j]:
                continue
            n += 1
            ok += int((pred[i] > pred[j]) == (y[i] > y[j]))
        lo, hi = wilson(ok, n)
        oot[p] = {"n_train_old": len(old), "n_test_new": len(new),
                  "spearman_future": round(float(rho), 4),
                  "r2_future": round(float(r2), 4),
                  "pairwise_future": round(ok / n, 4) if n else 0.0,
                  "ci95": [round(lo, 4), round(hi, 4)],
                  "holds_up": bool(lo > 0.5)}
        flag = "yes" if oot[p]["holds_up"] else "NO"
        print(f"  {PLAT_NAME[p]:14} rho={rho:+.3f}  pairwise={ok/n:.3f} "
              f"CI [{lo:.3f}, {hi:.3f}]  train={len(old)} test={len(new)}  holds: {flag}")
    out["tests"]["out_of_time"] = oot

    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nwrote", OUT)

    # ---- headline summary ---------------------------------------------
    good = [p for p, d in sa_res.items() if not d.get("skipped") and d["beats_coinflip"]]
    print(f"\nSame-author test passed on {len(good)}/{sum(1 for d in sa_res.values() if not d.get('skipped'))} "
          f"platforms with enough data: {', '.join(PLAT_NAME[p] for p in good) or 'none'}")


if __name__ == "__main__":
    main()
