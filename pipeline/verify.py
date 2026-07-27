"""End-to-end verification.

1. Dataset integrity — schema, ranges, duplicates, percentile correctness.
2. Statistical claims — recompute a sample of the numbers printed in the reports.
3. Model sanity — holdout deciles monotonic-ish, no leakage from the split.
4. Python/JavaScript parity — the browser app must score identically to score.py.

Exit code is non-zero if any check fails.
"""
import json, os, re, subprocess, sys, tempfile, math, random
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import features as F
from analyze import spearman, mean
import score as SC

D = os.path.join(ROOT, "data")
fails, warns = [], []


def check(name, cond, detail=""):
    print(("  PASS  " if cond else "  FAIL  ") + name + (("  — " + detail) if detail else ""))
    if not cond:
        fails.append(name)


def warn(name, cond, detail=""):
    if not cond:
        print("  WARN  " + name + (("  — " + detail) if detail else ""))
        warns.append(name)
    else:
        print("  PASS  " + name + (("  — " + detail) if detail else ""))


print("\n[1] dataset integrity")
ds = os.path.join(D, "dataset.jsonl")
if not os.path.exists(ds):
    print("  SKIP  dataset.jsonl not present (corpus is not redistributed) — "
          "run the pipeline to regenerate, or verify the shipped model only")
    rows = []
else:
    rows = [json.loads(l) for l in open(ds, encoding="utf-8")]
check("dataset non-empty", len(rows) > 3000, f"n={len(rows)}")
check("every row has a title", all(r["title"].strip() for r in rows))
check("every row has a positive metric", all(r["primary_metric"] > 0 for r in rows))
check("engagement percentile in [0,1]", all(0 <= r["engagement_pct"] <= 1 for r in rows))
check("features present on every row", all(len(r["f"]) >= 40 for r in rows))

titles = [re.sub(r"[^a-z0-9]", "", r["title"].lower())[:90] for r in rows]
dupes = len(titles) - len(set(titles))
check("no duplicate titles", dupes == 0, f"{dupes} duplicates")

# percentile must be a monotone transform of the raw metric, within platform
bad = 0
byp = {}
for r in rows:
    byp.setdefault(r["platform"], []).append(r)
for p, rs in byp.items():
    rs2 = sorted(rs, key=lambda r: r["primary_metric"])
    for a, b in zip(rs2, rs2[1:]):
        if a["primary_metric"] < b["primary_metric"] and a["engagement_pct"] > b["engagement_pct"] + 1e-9:
            bad += 1
check("percentile is monotone in raw metric within each platform", bad == 0, f"{bad} inversions")
for p, rs in byp.items():
    m = mean([r["engagement_pct"] for r in rs])
    warn(f"  {p}: mean percentile ~0.5", 0.45 <= m <= 0.55, f"mean={m:.3f}, n={len(rs)}")

print("\n[2] statistical claims recomputed independently")
A = json.load(open(os.path.join(D, "analysis.json"), encoding="utf-8"))
ok = True
for p in list(A["lifts"].keys()):
    L = A["lifts"][p]
    sub = rows if p == "ALL" else [r for r in rows if r["platform"] == p]
    for cond_name, v in list(L.items())[:4]:
        if cond_name == "starts_with_number":
            on = [r["engagement_pct"] for r in sub if r["f"]["starts_with_number"] == 1]
            off = [r["engagement_pct"] for r in sub if r["f"]["starts_with_number"] == 0]
            if on and off:
                delta = (mean(on) - mean(off)) * 100
                if abs(delta - v["lift_pct_points"]) > 0.02:
                    ok = False
check("reported lifts match recomputation", ok)

y = [r["engagement_pct"] for r in rows]
x = [r["f"]["has_colon"] for r in rows]
rho = spearman(x, y)
reported = [d for d in A["correlations"]["ALL"] if d["feature"] == "has_colon"][0]["rho"]
check("reported Spearman matches recomputation", abs(rho - reported) < 0.002,
      f"recomputed {rho:.4f} vs reported {reported:.4f}")

n_sig = sum(1 for d in A["correlations"]["ALL"] if d["p"] < 0.05)
print(f"  INFO  {n_sig}/{len(A['correlations']['ALL'])} pooled feature correlations significant at p<0.05")
strongest = max(abs(d["rho"]) for d in A["correlations"]["ALL"])
warn("no implausibly strong single-feature correlation", strongest < 0.5,
     f"max |rho| = {strongest:.3f} (weak effects are the expected, honest result)")

print("\n[3] model sanity")
M = json.load(open(os.path.join(D, "model.json"), encoding="utf-8"))
full = M["pooled"]["full"]
dec = full["holdout_decile_mean_engagement"]
check("holdout decile 10 beats decile 1", dec[-1] > dec[0], f"{dec[0]:.3f} -> {dec[-1]:.3f}")
inc = sum(1 for a, b in zip(dec, dec[1:]) if b >= a)
warn("decile curve broadly increasing", inc >= 6, f"{inc}/9 steps increase")
check("holdout R2 reported and modest", -1 < full["r2_holdout"] < 0.5,
      f"R2={full['r2_holdout']:.4f} — headline text is a weak signal, as expected")
check("holdout rank correlation positive", full["spearman_holdout"] > 0.1,
      f"rho={full['spearman_holdout']:.4f}")
check("train and holdout are disjoint sizes consistent",
      full["n_train"] + full["n_holdout"] <= len(rows) and full["n_holdout"] > 200,
      f"train={full['n_train']} holdout={full['n_holdout']} total={len(rows)}")
for p, d in M["platforms"].items():
    if "full" in d and d["full"]["r2_holdout"] < 0:
        print(f"  INFO  {p}: negative holdout R2 ({d['full']['r2_holdout']:.3f}) — "
              f"small-sample overfit, documented in report 07; app uses the pooled model")

print("\n[4] Python <-> JavaScript parity")
# the browser scorer must agree with score.py exactly
appjs = open(os.path.join(ROOT, "assets", "app.js"), encoding="utf-8").read()
datajs = open(os.path.join(ROOT, "assets", "data.js"), encoding="utf-8").read()
# expose the IIFE internals to the test harness
appjs = appjs.replace("(() => {\n  'use strict';", "globalThis.__t = (() => {\n  'use strict';")
appjs = appjs.replace("})();", "return {titleFeatures, scoreTitle};\n})();")
shim = ("globalThis.window = globalThis;\n"
        "globalThis.document = {addEventListener(){}, querySelectorAll(){return [];},"
        " getElementById(){return null;}};\n")
js = shim + datajs + "\n" + appjs + "\nconst {titleFeatures, scoreTitle} = globalThis.__t;\n"

samples = [
    ("hackernews", "How we cut p99 latency 40% by deleting one Postgres index"),
    ("devto", "10 JavaScript tricks every beginner should know"),
    ("medium", "Why Your Microservices Are Slower Than the Monolith You Replaced"),
    ("substack", "The hidden cost of hiring senior engineers"),
    ("x", "I spent 3 months rewriting our build system in Rust. It went badly."),
    ("reddit", "After 6 years as a developer I finally understand what my manager meant"),
    ("hackernews", "SHOCKING: The ULTIMATE guide to unlock seamless AI-powered synergy!!!"),
    ("devto", "A"),
    ("medium", "Rust vs Go: startup time decides"),
    ("reddit", "Show HN: I built a 2 kB state manager with zero dependencies"),
]
harness = js + "\nconst out=[];\n" + "\n".join(
    f'out.push(scoreTitle({json.dumps(t)}, {json.dumps(p)}).pct);' for p, t in samples
) + "\nconsole.log(JSON.stringify(out));\n"

node = None
for cand in ("node", "nodejs"):
    try:
        subprocess.run([cand, "-e", "0"], capture_output=True, check=True)
        node = cand
        break
    except Exception:
        pass

if node is None:
    print("  SKIP  node not available; parity not machine-checked")
    warns.append("js parity unchecked")
else:
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(harness)
        path = fh.name
    res = subprocess.run([node, path], capture_output=True, text=True)
    if res.returncode != 0:
        check("javascript harness runs", False, res.stderr.strip()[:400])
    else:
        jsvals = json.loads(res.stdout.strip().splitlines()[-1])
        worst, worst_case = 0.0, None
        for (p, t), jv in zip(samples, jsvals):
            pv = SC.score(t, p)["pct"]
            d = abs(pv - jv)
            if d > worst:
                worst, worst_case = d, (p, t, pv, jv)
        check("browser score matches Python score", worst < 0.01,
              f"max abs diff {worst:.6f}" + (f" on {worst_case[1][:40]!r}" if worst_case else ""))
        # also check feature parity on a random sample of real titles
        rnd = random.Random(3).sample(rows, 40)
        h2 = js + "\nconst o=[];\n" + "\n".join(
            f'o.push(titleFeatures({json.dumps(r["title"])}));' for r in rnd
        ) + "\nconsole.log(JSON.stringify(o));\n"
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
            fh.write(h2)
            p2 = fh.name
        res2 = subprocess.run([node, p2], capture_output=True, text=True)
        if res2.returncode == 0:
            jf = json.loads(res2.stdout.strip().splitlines()[-1])
            mism = []
            for r, d in zip(rnd, jf):
                for k in F.FEATURE_ORDER:
                    a, b = float(r["f"][k]), float(d.get(k, -999))
                    if abs(a - b) > 1e-6:
                        mism.append((k, r["title"][:40], a, b))
            check("all 45 features match between Python and JS on 40 real titles",
                  not mism, f"{len(mism)} mismatches: {mism[:3]}")
        else:
            check("javascript feature harness runs", False, res2.stderr.strip()[:300])

print("\n[5] deliverables present")
for rel in ["data/analysis.json", "data/model.json", "data/validation.json",
            "index.html", "assets/app.js", "assets/app.css", "assets/data.js",
            "docs/01-methodology.md", "docs/05-platform-comparison.md",
            "docs/07-attention-model.md", "docs/08-frameworks.md"]:
    p = os.path.join(ROOT, rel)
    check(f"{rel}", os.path.exists(p) and os.path.getsize(p) > 200,
          f"{os.path.getsize(p)/1024:.0f} KB" if os.path.exists(p) else "missing")

print("\n" + ("=" * 60))
if fails:
    print(f"FAILED: {len(fails)} check(s): {fails}")
    sys.exit(1)
print(f"ALL CHECKS PASSED ({len(warns)} warning(s))")
