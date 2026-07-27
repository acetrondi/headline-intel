"""Statistical + NLP + sentiment + tag + pattern analysis over the normalized dataset.

Writes machine-readable results to data/analysis.json so the reports and the web
app both read from one source of truth.
"""
import json, os, re, sys, math
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import features as F

IN = os.path.join(ROOT, "data", "dataset.jsonl")
OUT = os.path.join(ROOT, "data", "analysis.json")

STOP = F.STOPWORDS | {"using", "make", "made", "new", "one", "get", "like", "just", "now",
                      "into", "about", "after", "than", "then", "some", "more", "most",
                      "over", "out", "up", "if", "so", "all", "no", "s", "t", "re", "ve"}


# ---------------------------------------------------------------- statistics

def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else 0.0


def median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return 0.0
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def stdev(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(a, b):
    """Rank correlation, no scipy needed."""
    if len(a) < 8:
        return 0.0
    ra, rb = rank(a), rank(b)
    ma, mb = mean(ra), mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else 0.0


def spearman_p(r, n):
    """Two-sided p-value via the t approximation. Good enough at n>30."""
    if n < 10 or abs(r) >= 1:
        return 1.0
    t = abs(r) * math.sqrt((n - 2) / max(1e-12, 1 - r * r))
    df = n - 2
    # Student-t survival via continued-fraction-free approximation (Hill's)
    x = df / (df + t * t)
    # regularized incomplete beta I_x(df/2, 1/2) via series
    a, b = df / 2.0, 0.5
    lbeta = (math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b))
    if x <= 0:
        ib = 0.0
    else:
        # continued fraction (Lentz) for I_x(a,b)
        def betacf(a, b, x, it=200):
            qab, qap, qam = a + b, a + 1.0, a - 1.0
            c, d = 1.0, 1.0 - qab * x / qap
            if abs(d) < 1e-30:
                d = 1e-30
            d = 1.0 / d
            h = d
            for m in range(1, it):
                m2 = 2 * m
                aa = m * (b - m) * x / ((qam + m2) * (a + m2))
                d = 1.0 + aa * d
                c = 1.0 + aa / c
                if abs(d) < 1e-30: d = 1e-30
                if abs(c) < 1e-30: c = 1e-30
                d = 1.0 / d
                h *= d * c
                aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
                d = 1.0 + aa * d
                c = 1.0 + aa / c
                if abs(d) < 1e-30: d = 1e-30
                if abs(c) < 1e-30: c = 1e-30
                d = 1.0 / d
                de = d * c
                h *= de
                if abs(de - 1.0) < 1e-10:
                    break
            return h
        if x < (a + 1) / (a + b + 2):
            ib = math.exp(a * math.log(x) + b * math.log(1 - x) - lbeta) * betacf(a, b, x) / a
        else:
            ib = 1 - math.exp(b * math.log(1 - x) + a * math.log(x) - lbeta) * betacf(b, a, 1 - x) / b
    return max(0.0, min(1.0, ib))


def lift(rows, pred, key="engagement_pct"):
    """Mean engagement percentile when a binary condition holds vs when it doesn't."""
    on = [r[key] for r in rows if pred(r)]
    off = [r[key] for r in rows if not pred(r)]
    if len(on) < 15 or len(off) < 15:
        return None
    return {"n_with": len(on), "n_without": len(off),
            "mean_with": round(mean(on), 4), "mean_without": round(mean(off), 4),
            "lift_pct_points": round((mean(on) - mean(off)) * 100, 2),
            "share": round(len(on) / (len(on) + len(off)), 4)}


# ---------------------------------------------------------------- main

def main():
    rows = [json.loads(l) for l in open(IN, encoding="utf-8")]
    platforms = sorted({r["platform"] for r in rows})
    out = {"n": len(rows), "platforms": {}, "generated": "content-intel"}

    fkeys = [k for k in F.FEATURE_ORDER]

    # ---- per-platform descriptive stats
    for p in platforms + ["ALL"]:
        sub = rows if p == "ALL" else [r for r in rows if r["platform"] == p]
        if not sub:
            continue
        titles = [r["title"] for r in sub]
        out["platforms"][p] = {
            "n": len(sub),
            "metric": sub[0].get("primary_metric_name", "") if p != "ALL" else "mixed",
            "metric_median": round(median([r["primary_metric"] for r in sub]), 1),
            "metric_p90": round(sorted(r["primary_metric"] for r in sub)[int(len(sub) * .9)], 1),
            "metric_max": round(max(r["primary_metric"] for r in sub), 1),
            "title_chars_mean": round(mean([len(t) for t in titles]), 1),
            "title_chars_median": round(median([len(t) for t in titles]), 1),
            "title_words_mean": round(mean([r["f"]["word_count"] for r in sub]), 2),
            "title_words_median": round(median([r["f"]["word_count"] for r in sub]), 1),
            "readability_mean": round(mean([r["f"]["readability"] for r in sub]), 1),
            "pct_with_number": round(100 * mean([r["f"]["has_number"] for r in sub]), 1),
            "pct_listicle": round(100 * mean([r["f"]["is_listicle"] for r in sub]), 1),
            "pct_question": round(100 * mean([r["f"]["has_question"] for r in sub]), 1),
            "pct_howto": round(100 * mean([r["f"]["is_howto"] for r in sub]), 1),
            "pct_colon": round(100 * mean([r["f"]["has_colon"] for r in sub]), 1),
            "pct_second_person": round(100 * mean([r["f"]["second_person"] for r in sub]), 1),
            "pct_first_person": round(100 * mean([r["f"]["first_person"] for r in sub]), 1),
            "pct_superlative": round(100 * mean([r["f"]["has_superlative"] for r in sub]), 1),
            "pct_negative_framing": round(100 * mean([1 if r["f"]["negative_words"] else 0 for r in sub]), 1),
            "mean_power_words": round(mean([r["f"]["power_words"] for r in sub]), 2),
            "mean_sentiment": round(mean([r["f"]["sentiment"] for r in sub]), 4),
            "mean_curiosity": round(mean([r["f"]["curiosity_gap"] for r in sub]), 3),
            "mean_authority": round(mean([r["f"]["authority"] for r in sub]), 3),
            "mean_emotional_intensity": round(mean([r["f"]["emotional_intensity"] for r in sub]), 3),
            "mean_ai_tells": round(mean([r["f"]["ai_tells"] for r in sub]), 3),
            "pct_with_subtitle": round(100 * mean([1 if r.get("subtitle") else 0 for r in sub]), 1),
        }

    # ---- feature <-> engagement correlations
    corr = {}
    for scope in ["ALL"] + platforms:
        sub = rows if scope == "ALL" else [r for r in rows if r["platform"] == scope]
        if len(sub) < 60:
            continue
        y = [r["engagement_pct"] for r in sub]
        res = []
        for k in fkeys:
            x = [r["f"][k] for r in sub]
            if len(set(x)) < 2:
                continue
            rho = spearman(x, y)
            res.append({"feature": k, "rho": round(rho, 4),
                        "p": round(spearman_p(rho, len(sub)), 6), "n": len(sub)})
        res.sort(key=lambda d: -abs(d["rho"]))
        corr[scope] = res
    out["correlations"] = corr

    # ---- binary lifts (interpretable "does X help?")
    conds = {
        "starts_with_number": lambda r: r["f"]["starts_with_number"] == 1,
        "contains_any_number": lambda r: r["f"]["has_number"] == 1,
        "has_colon": lambda r: r["f"]["has_colon"] == 1,
        "is_question": lambda r: r["f"]["has_question"] == 1,
        "starts_with_how": lambda r: r["f"]["is_howto"] == 1,
        "starts_with_why": lambda r: r["f"]["is_why"] == 1,
        "imperative_open": lambda r: r["f"]["is_imperative"] == 1,
        "addresses_you": lambda r: r["f"]["second_person"] == 1,
        "first_person_story": lambda r: r["f"]["first_person"] == 1,
        "superlative": lambda r: r["f"]["has_superlative"] == 1,
        "comparison_vs": lambda r: r["f"]["has_comparison"] == 1,
        "negative_framing": lambda r: r["f"]["negative_words"] >= 1,
        "strong_negative_framing": lambda r: r["f"]["negative_words"] >= 2,
        "positive_framing": lambda r: r["f"]["positive_words"] >= 1,
        "power_word_present": lambda r: r["f"]["power_words"] >= 1,
        "two_plus_power_words": lambda r: r["f"]["power_words"] >= 2,
        "curiosity_marker": lambda r: r["f"]["curiosity_markers"] >= 1,
        "authority_marker": lambda r: r["f"]["authority_markers"] >= 1,
        "urgency_marker": lambda r: r["f"]["urgency_markers"] >= 1,
        "fear_word": lambda r: r["f"]["fear_words"] >= 1,
        "surprise_word": lambda r: r["f"]["surprise_words"] >= 1,
        "beginner_framing": lambda r: r["f"]["beginner_markers"] >= 1,
        "deep_technical": lambda r: r["f"]["tech_depth_markers"] >= 1,
        "big_number_specific": lambda r: r["f"]["has_big_number"] == 1,
        "mentions_year": lambda r: r["f"]["has_year"] == 1,
        "money_figure": lambda r: r["f"]["has_money"] == 1,
        "parenthetical": lambda r: r["f"]["has_parens"] == 1,
        "ai_tell_phrasing": lambda r: r["f"]["ai_tells"] >= 1,
        "short_title_<=7w": lambda r: r["f"]["word_count"] <= 7,
        "medium_title_8_12w": lambda r: 8 <= r["f"]["word_count"] <= 12,
        "long_title_>=13w": lambda r: r["f"]["word_count"] >= 13,
        "has_subtitle": lambda r: bool(r.get("subtitle")),
    }
    lifts = {}
    for scope in ["ALL"] + platforms:
        sub = rows if scope == "ALL" else [r for r in rows if r["platform"] == scope]
        if len(sub) < 120:
            continue
        d = {}
        for name, fn in conds.items():
            v = lift(sub, fn)
            if v:
                d[name] = v
        lifts[scope] = dict(sorted(d.items(), key=lambda kv: -kv[1]["lift_pct_points"]))
    out["lifts"] = lifts

    # ---- title length curve
    curves = {}
    for scope in ["ALL"] + platforms:
        sub = rows if scope == "ALL" else [r for r in rows if r["platform"] == scope]
        if len(sub) < 120:
            continue
        buckets = defaultdict(list)
        for r in sub:
            buckets[min(20, max(3, r["f"]["word_count"]))].append(r["engagement_pct"])
        curves[scope] = {str(k): {"n": len(v), "mean_pct": round(mean(v), 4)}
                         for k, v in sorted(buckets.items()) if len(v) >= 15}
    out["length_curve"] = curves

    # ---- sentiment buckets
    sent = {}
    for scope in ["ALL"] + platforms:
        sub = rows if scope == "ALL" else [r for r in rows if r["platform"] == scope]
        if len(sub) < 120:
            continue
        b = defaultdict(list)
        for r in sub:
            s = r["f"]["sentiment"]
            lab = "negative" if s < -0.02 else ("positive" if s > 0.02 else "neutral")
            b[lab].append(r["engagement_pct"])
        sent[scope] = {k: {"n": len(v), "share": round(len(v) / len(sub), 4),
                           "mean_pct": round(mean(v), 4)} for k, v in b.items()}
        emo = {}
        for axis in ["fear_words", "surprise_words", "excitement_words", "trust_words",
                     "curiosity_markers", "power_words"]:
            on = [r["engagement_pct"] for r in sub if r["f"][axis] >= 1]
            off = [r["engagement_pct"] for r in sub if r["f"][axis] == 0]
            if len(on) >= 15 and len(off) >= 15:
                emo[axis] = {"n": len(on), "mean_with": round(mean(on), 4),
                             "mean_without": round(mean(off), 4),
                             "delta_pct_points": round((mean(on) - mean(off)) * 100, 2)}
        sent[scope]["emotions"] = emo
    out["sentiment"] = sent

    # ---- tags
    tagged = [r for r in rows if r.get("tags")]
    tag_stats, pair_stats = {}, {}
    tcount = Counter()
    for r in tagged:
        for t in r["tags"]:
            if t:
                tcount[t.lower()] += 1
    for t, c in tcount.most_common(120):
        vals = [r["engagement_pct"] for r in tagged if t in [x.lower() for x in r["tags"]]]
        if len(vals) >= 8:
            tag_stats[t] = {"n": c, "mean_pct": round(mean(vals), 4),
                            "median_metric": round(median(
                                [r["primary_metric"] for r in tagged
                                 if t in [x.lower() for x in r["tags"]]]), 1)}
    pcount = Counter()
    for r in tagged:
        ts = sorted({x.lower() for x in r["tags"] if x})
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                pcount[(ts[i], ts[j])] += 1
    for (a, b), c in pcount.most_common(60):
        if c < 6:
            continue
        vals = [r["engagement_pct"] for r in tagged
                if a in [x.lower() for x in r["tags"]] and b in [x.lower() for x in r["tags"]]]
        pair_stats[f"{a} + {b}"] = {"n": c, "mean_pct": round(mean(vals), 4)}
    out["tags"] = {
        "n_tagged_posts": len(tagged),
        "per_tag": dict(sorted(tag_stats.items(), key=lambda kv: -kv[1]["mean_pct"])),
        "pairs": dict(sorted(pair_stats.items(), key=lambda kv: -kv[1]["mean_pct"])),
        "mean_tags_per_post": round(mean([len(r["tags"]) for r in tagged]), 2),
    }
    tagcount_curve = defaultdict(list)
    for r in tagged:
        tagcount_curve[min(6, len(r["tags"]))].append(r["engagement_pct"])
    out["tags"]["by_tag_count"] = {str(k): {"n": len(v), "mean_pct": round(mean(v), 4)}
                                   for k, v in sorted(tagcount_curve.items()) if len(v) >= 10}

    # ---- opener / template mining
    top = [r for r in rows if r["engagement_pct"] >= 0.8]
    bot = [r for r in rows if r["engagement_pct"] <= 0.2]

    def openers(rs, n):
        c = Counter()
        for r in rs:
            w = re.findall(r"[A-Za-z0-9']+", r["title"])
            if len(w) >= n:
                c[" ".join(x.lower() for x in w[:n])] += 1
        return c

    tmpl = {}
    for n in (1, 2, 3):
        ct, cb = openers(top, n), openers(bot, n)
        rowsn = []
        for k, v in ct.most_common(400):
            if v < max(4, len(top) // 900):
                continue
            base = cb.get(k, 0)
            rate_top = v / max(1, len(top))
            rate_bot = base / max(1, len(bot))
            rowsn.append({"opener": k, "n_top": v, "n_bottom": base,
                          "top_rate": round(rate_top, 5),
                          "odds": round((rate_top + 1e-6) / (rate_bot + 1e-6), 2)})
        rowsn.sort(key=lambda d: (-d["odds"], -d["n_top"]))
        tmpl[f"{n}gram"] = rowsn[:40]
    out["openers"] = tmpl

    # distinctive words in top vs bottom quintile
    def wordfreq(rs):
        c = Counter()
        for r in rs:
            for w in set(re.findall(r"[a-z0-9\-']+", r["title"].lower())):
                if w not in STOP and len(w) > 2:
                    c[w] += 1
        return c
    wt, wb = wordfreq(top), wordfreq(bot)
    words = []
    for w, v in wt.most_common(1200):
        if v < 8:
            continue
        rt, rb = v / len(top), wb.get(w, 0) / len(bot)
        words.append({"word": w, "n_top": v, "n_bottom": wb.get(w, 0),
                      "odds": round((rt + 1e-6) / (rb + 1e-6), 2)})
    words.sort(key=lambda d: -d["odds"])
    out["distinctive_words"] = {"top_quintile": words[:60], "bottom_quintile": words[-60:][::-1]}

    # ---- subtitle analysis (platforms that actually have subtitles)
    subs = [r for r in rows if r.get("subtitle")]
    sub_out = {"n": len(subs)}
    if len(subs) >= 80:
        y = [r["engagement_pct"] for r in subs]
        sk = []
        for k in F.SUB_FEATURE_ORDER:
            x = [r["fs"][k] for r in subs]
            if len(set(x)) < 2:
                continue
            rho = spearman(x, y)
            sk.append({"feature": k, "rho": round(rho, 4),
                       "p": round(spearman_p(rho, len(subs)), 6), "n": len(subs)})
        sk.sort(key=lambda d: -abs(d["rho"]))
        sub_out["correlations"] = sk
        sub_out["stats"] = {
            "mean_words": round(mean([r["fs"]["sub_word_count"] for r in subs]), 2),
            "median_words": round(median([r["fs"]["sub_word_count"] for r in subs]), 1),
            "mean_chars": round(mean([r["fs"]["sub_char_count"] for r in subs]), 1),
            "mean_overlap_with_title": round(mean([r["fs"]["sub_overlap"] for r in subs]), 3),
            "mean_new_info": round(mean([r["fs"]["sub_new_info"] for r in subs]), 3),
            "pct_cta": round(100 * mean([r["fs"]["sub_is_cta"] for r in subs]), 1),
            "pct_second_person": round(100 * mean([r["fs"]["sub_second_person"] for r in subs]), 1),
            "pct_number": round(100 * mean([r["fs"]["sub_has_number"] for r in subs]), 1),
        }
        b = defaultdict(list)
        for r in subs:
            b[min(30, max(4, (r["fs"]["sub_word_count"] // 4) * 4))].append(r["engagement_pct"])
        sub_out["length_curve"] = {str(k): {"n": len(v), "mean_pct": round(mean(v), 4)}
                                   for k, v in sorted(b.items()) if len(v) >= 12}
        ov = defaultdict(list)
        for r in subs:
            ov[round(min(1.0, r["fs"]["sub_overlap"]) * 4) / 4].append(r["engagement_pct"])
        sub_out["overlap_curve"] = {str(k): {"n": len(v), "mean_pct": round(mean(v), 4)}
                                    for k, v in sorted(ov.items()) if len(v) >= 12}
    out["subtitles"] = sub_out

    # ---- time trend
    yr = defaultdict(list)
    for r in rows:
        if r.get("year"):
            yr[r["year"]].append(r["f"]["word_count"])
    out["title_length_by_year"] = {str(k): {"n": len(v), "mean_words": round(mean(v), 2)}
                                   for k, v in sorted(yr.items()) if len(v) >= 25}

    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", OUT)
    print("n =", out["n"])
    print("\ntop 12 |rho| features (ALL):")
    for d in out["correlations"]["ALL"][:12]:
        print(f"  {d['feature']:24} rho={d['rho']:+.3f}  p={d['p']:.2g}")
    print("\ntop 8 lifts (ALL):")
    for k, v in list(out["lifts"]["ALL"].items())[:8]:
        print(f"  {k:26} {v['lift_pct_points']:+.2f} pts  (n={v['n_with']})")


if __name__ == "__main__":
    main()
