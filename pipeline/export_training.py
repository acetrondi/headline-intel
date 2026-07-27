"""Export the AI learning dataset: one record per post, enriched for LLM prompting/training."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import features as F
import score as SC

M = json.load(open(os.path.join(ROOT, "data", "model.json"), encoding="utf-8"))
A = json.load(open(os.path.join(ROOT, "data", "analysis.json"), encoding="utf-8"))
rows = [json.loads(l) for l in open(os.path.join(ROOT, "data", "dataset.jsonl"), encoding="utf-8")]

OUT = os.path.join(ROOT, "data", "training_set.jsonl")
FEWSHOT = os.path.join(ROOT, "data", "fewshot_exemplars.json")


def claim_type(f, title):
    t = title.lower()
    if f["has_comparison"] and (" vs" in t or "versus" in t): return "comparison"
    if any(k in t for k in ("postmortem", "outage", "broke", "incident", "went down", "failure")):
        return "postmortem"
    if f["is_listicle"] or f["is_howto"] or f["beginner_markers"]: return "teaching"
    if f["first_person"] and any(k in t for k in ("built", "made", "wrote", "shipped", "created")):
        return "buildlog"
    if f["is_why"] or f["negative_words"] >= 1: return "position"
    if f["has_big_number"]: return "result"
    return "other"


def emotion_profile(f):
    return {k: f[k] for k in ["fear_words", "surprise_words", "excitement_words",
                              "trust_words", "curiosity_markers", "power_words",
                              "positive_words", "negative_words"]}


with open(OUT, "w", encoding="utf-8") as fh:
    for r in rows:
        f = r["f"]
        rec = {
            "platform": r["platform"],
            "title": r["title"],
            "subtitle": r.get("subtitle", ""),
            "tags": r.get("tags", []),
            "author": r.get("author", ""),
            "published": r.get("published", ""),
            "url": r.get("url", ""),
            "engagement": {
                "metric_name": r.get("primary_metric_name", ""),
                "metric_value": r["primary_metric"],
                "comments": r.get("comments", ""),
                "reading_time_min": r.get("reading_time", ""),
                "within_platform_percentile": r["engagement_pct"],
                "vs_platform_median": r.get("metric_vs_median"),
            },
            "attention_score": round(SC.score(r["title"], r["platform"])["pct"], 2),
            "axes": {a: round(f[a], 4) for a in M["axes"]},
            "sentiment": {"polarity": round(f["sentiment"], 4),
                          "negativity": round(f["negativity"], 4),
                          "emotions": emotion_profile(f)},
            "structure": {
                "words": f["word_count"], "chars": f["char_count"],
                "claim_type": claim_type(f, r["title"]),
                "is_howto": f["is_howto"], "is_listicle": f["is_listicle"],
                "is_question": f["has_question"], "has_colon": f["has_colon"],
                "has_specific_number": f["has_big_number"],
                "first_person": f["first_person"], "second_person": f["second_person"],
                "authority_markers": f["authority_markers"],
                "tech_depth": f["tech_depth_markers"],
                "ai_cliche_count": f["ai_tells"],
                "readability_flesch": round(f["readability"], 1),
            },
            "subtitle_relation": ({k: round(v, 4) if isinstance(v, float) else v
                                   for k, v in r["fs"].items()} if r.get("subtitle") else None),
            "label": ("top_decile" if r["engagement_pct"] >= 0.9 else
                      "top_quartile" if r["engagement_pct"] >= 0.75 else
                      "middle" if r["engagement_pct"] >= 0.25 else "bottom_quartile"),
        }
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

# few-shot exemplar pack: the best-performing, cleanest examples per platform per claim type
best = {}
for r in rows:
    if r["engagement_pct"] < 0.85: continue
    if r["f"]["ai_tells"]: continue
    ct = claim_type(r["f"], r["title"])
    k = (r["platform"], ct)
    best.setdefault(k, []).append(r)
pack = {}
for (p, ct), rs in best.items():
    rs.sort(key=lambda r: -r["engagement_pct"])
    pack.setdefault(p, {})[ct] = [
        {"title": r["title"], "subtitle": r.get("subtitle", ""),
         "tags": r.get("tags", [])[:4],
         "percentile": round(r["engagement_pct"], 3),
         "metric": f'{int(r["primary_metric"])} {r.get("primary_metric_name","")}'}
        for r in rs[:8]]
json.dump(pack, open(FEWSHOT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("wrote", OUT, os.path.getsize(OUT)//1024, "KB")
print("wrote", FEWSHOT, os.path.getsize(FEWSHOT)//1024, "KB")
import collections
c = collections.Counter(claim_type(r["f"], r["title"]) for r in rows)
print("claim types:", dict(c.most_common()))
