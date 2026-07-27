"""Clean + normalize the raw corpus into an analysis-ready table.

The core problem: HN points, Medium claps, Dev.to reactions, Substack likes and
X likes are not comparable numbers. Everything is therefore converted to a
*within-platform percentile rank* (0-1), which is the only defensible common
currency. All modelling downstream uses that percentile, never raw counts.
"""
import json, os, re, sys, math, datetime
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import features as F

IN = os.path.join(ROOT, "data", "corpus.jsonl")
OUT_JSONL = os.path.join(ROOT, "data", "dataset.jsonl")
OUT_CSV = os.path.join(ROOT, "data", "dataset.csv")

# Minimum engagement to enter the corpus. Set deliberately: a corpus of
# mediocre posts teaches the model what makes mediocre slightly better, which is
# not the question. Keep the FULL range above each floor so the target still has
# variance to learn from - see reports/01.
FLOORS = {
    "hackernews": 300,   # points
    "reddit":     500,   # upvotes
    "x":          500,   # likes
    "devto":      100,   # reactions
    "substack":    50,   # likes
    "medium":     100,   # claps
}

# titles that are junk for headline analysis
JUNK_RE = re.compile(r"^(\[deleted\]|\[removed\]|)$", re.I)
URL_RE = re.compile(r"https?://\S+")


def load():
    rows = []
    with open(IN, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            rows.append(r)
    return rows


def clean_title(t, platform):
    t = URL_RE.sub("", t or "").strip()
    if platform == "x":
        t = re.sub(r"\s*#\w+", "", t)          # trailing hashtag spam
        t = re.sub(r"\s*@\w+", "", t)
        t = re.sub(r"\s+", " ", t).strip()
        # a tweet's "headline" is its first sentence/line
        first = re.split(r"(?<=[.!?])\s+|\n", t)[0].strip()
        if 15 <= len(first) <= 180:
            t = first
    return t.strip(" -–—:|")


def percentiles(values):
    """Fractional percentile rank with ties averaged."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg / max(1, len(values) - 1)
        i = j + 1
    return ranks


def main():
    rows = load()
    kept, seen = [], set()
    for r in rows:
        t = clean_title(r.get("title", ""), r["platform"])
        if len(t) < 12 or len(t) > 220:
            continue
        if JUNK_RE.match(t):
            continue
        if not re.search(r"[a-zA-Z]{3}", t):
            continue
        key = re.sub(r"[^a-z0-9]", "", t.lower())[:90]
        if key in seen:
            continue
        seen.add(key)
        r["title"] = t
        try:
            r["primary_metric"] = float(r.get("primary_metric") or 0)
        except Exception:
            continue
        if r["primary_metric"] < FLOORS.get(r["platform"], 1):
            continue
        kept.append(r)

    # within-platform percentile + log metric
    by_plat = defaultdict(list)
    for i, r in enumerate(kept):
        by_plat[r["platform"]].append(i)
    for plat, idxs in by_plat.items():
        vals = [kept[i]["primary_metric"] for i in idxs]
        pct = percentiles(vals)
        med = sorted(vals)[len(vals) // 2]
        for pos, i in enumerate(idxs):
            kept[i]["engagement_pct"] = round(pct[pos], 6)
            kept[i]["log_metric"] = round(math.log1p(kept[i]["primary_metric"]), 4)
            kept[i]["metric_vs_median"] = round(kept[i]["primary_metric"] / max(1e-9, med), 4)

    # features
    for r in kept:
        r["f"] = F.title_features(r["title"])
        r["fs"] = F.subtitle_features(r["title"], r.get("subtitle", ""))
        try:
            y = int(str(r.get("published", ""))[:4])
        except Exception:
            y = 0
        r["year"] = y if 2005 <= y <= 2027 else 0
        r["engagement_per_comment"] = round(
            r["primary_metric"] / max(1, float(r.get("comments") or 0) + 1), 3)

    with open(OUT_JSONL, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # flat CSV for humans / spreadsheets
    import csv
    fkeys = F.FEATURE_ORDER
    skeys = F.SUB_FEATURE_ORDER
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["platform", "title", "subtitle", "tags", "author", "published", "year",
                    "primary_metric", "primary_metric_name", "comments", "reading_time",
                    "engagement_pct", "log_metric", "metric_vs_median", "url"]
                   + fkeys + skeys)
        for r in kept:
            w.writerow([r["platform"], r["title"], r.get("subtitle", ""),
                        "|".join(r.get("tags") or []), r.get("author", ""),
                        r.get("published", ""), r["year"], r["primary_metric"],
                        r.get("primary_metric_name", ""), r.get("comments", ""),
                        r.get("reading_time", ""), r["engagement_pct"], r["log_metric"],
                        r["metric_vs_median"], r.get("url", "")]
                       + [r["f"][k] for k in fkeys] + [r["fs"][k] for k in skeys])

    counts = Counter(r["platform"] for r in kept)
    print("rows kept:", len(kept))
    for k, v in counts.most_common():
        sub = sum(1 for r in kept if r["platform"] == k and r.get("subtitle"))
        tg = sum(1 for r in kept if r["platform"] == k and r.get("tags"))
        print(f"  {k:11} {v:6}   subtitles {sub:5}   tagged {tg:5}")
    print("->", OUT_JSONL)
    print("->", OUT_CSV)


if __name__ == "__main__":
    main()
