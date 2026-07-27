"""Generate assets/data.js — the only generated file the site loads.

index.html, assets/app.css and assets/app.js are hand-written and checked in.
This script emits just the data: fitted model, mined per-platform rules,
lexicons and headline stats. Run it after any refit.

    python3 pipeline/build_data.py
"""
import json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import features as F

A = json.load(open(os.path.join(ROOT, "data", "analysis.json"), encoding="utf-8"))
M = json.load(open(os.path.join(ROOT, "data", "model.json"), encoding="utf-8"))
OUT = os.path.join(ROOT, "assets", "data.js")

PLAT_NAME = {"hackernews": "Hacker News", "reddit": "Reddit", "devto": "Dev.to",
             "medium": "Medium", "substack": "Substack", "x": "X / Twitter"}

LEX = {
    "POWER": sorted(F.POWER_WORDS), "CURIOSITY": sorted(F.CURIOSITY_MARKERS),
    "AUTHORITY": sorted(F.AUTHORITY_MARKERS), "URGENCY": sorted(F.URGENCY_MARKERS),
    "NEGATIVE": sorted(F.NEGATIVE_WORDS), "POSITIVE": sorted(F.POSITIVE_WORDS),
    "TRUST": sorted(F.TRUST_WORDS), "FEAR": sorted(F.FEAR_WORDS),
    "SURPRISE": sorted(F.SURPRISE_WORDS), "EXCITEMENT": sorted(F.EXCITEMENT_WORDS),
    "BEGINNER": sorted(F.BEGINNER_MARKERS), "TECHDEPTH": sorted(F.TECH_DEPTH_MARKERS),
    "STORY": sorted(F.STORY_MARKERS), "AITELLS": sorted(F.AI_TELLS),
    "STOP": sorted(F.STOPWORDS),
}

RULES = {}
for p, L in A["lifts"].items():
    if p == "ALL":
        continue
    items = sorted(L.items(), key=lambda kv: -kv[1]["lift_pct_points"])
    RULES[p] = {
        "do": [{"k": k, "v": v["lift_pct_points"], "n": v["n_with"]} for k, v in items[:7]],
        "avoid": [{"k": k, "v": v["lift_pct_points"], "n": v["n_with"]} for k, v in items[-7:]][::-1],
        "median_words": A["platforms"][p]["title_words_median"],
        "median_chars": A["platforms"][p]["title_chars_median"],
        "n": A["platforms"][p]["n"],
    }

COND_LABEL = {
    "starts_with_number": "open with a number", "contains_any_number": "include a number",
    "has_colon": "use a colon", "is_question": "phrase as a question",
    "starts_with_how": 'open with "How"', "starts_with_why": 'open with "Why"',
    "imperative_open": "open with a verb", "addresses_you": 'address the reader as "you"',
    "first_person_story": "write in first person", "superlative": "use a superlative",
    "comparison_vs": "frame as a comparison", "negative_framing": "use negative framing",
    "strong_negative_framing": "pile on negative words",
    "positive_framing": "use positive framing", "power_word_present": "use a power word",
    "two_plus_power_words": "use two or more power words",
    "curiosity_marker": "use a curiosity gap", "authority_marker": "signal first-hand authority",
    "urgency_marker": "signal urgency or recency", "fear_word": "name a risk or failure",
    "surprise_word": "signal surprise", "beginner_framing": "frame for beginners",
    "deep_technical": "use deep technical vocabulary",
    "big_number_specific": "use a specific number with a unit",
    "mentions_year": "mention a year", "money_figure": "include a money figure",
    "parenthetical": "add a parenthetical", "ai_tell_phrasing": "use AI-cliché phrasing",
    "short_title_<=7w": "keep it to 7 words or fewer",
    "medium_title_8_12w": "use 8-12 words", "long_title_>=13w": "use 13+ words",
    "has_subtitle": "add a subtitle",
}

TEMPLATES = {
    "result": [
        "How we cut {M} by {N}% in {T}", "{N}% faster {T} after one change",
        "We reduced {M} from {N} to {N2} in {T}", "Cutting {M} in {T}: what actually worked",
        "One {T} change that moved {M} by {N}%",
    ],
    "build log": [
        "I built {X} in {N} lines of {T}", "Building {X} with {T}, start to finish",
        "I spent {N} months building {X}", "{X}: what I learned building it in {T}",
        "We rewrote {X} in {T} and here is the diff",
    ],
    "postmortem": [
        "What a {N}-hour outage taught us about {T}", "How {T} broke in production",
        "The {T} bug that cost us {N} hours", "Postmortem: {T} at {N}x scale",
        "We got {T} wrong for {N} years",
    ],
    "teaching": [
        "{N} {T} mistakes I made so you don't have to", "How to {T} without breaking things",
        "{N} things about {T} nobody explains", "A practical guide to {T}",
        "{T}, explained by building one",
    ],
    "position": [
        "Why {T} was the wrong call for us", "{T} is not the problem",
        "Stop using {T} for {X}", "The case against {T}", "You probably don't need {T}",
    ],
    "comparison": [
        "{T} vs {X}: {M} decides", "We tried {T} and {X}. Here is what broke.",
        "{T} or {X}? We measured both", "Choosing between {T} and {X} at {N}x scale",
    ],
}

SUBTITLE_SHAPES = [
    ("Method", "The approach that got us there, and what it cost."),
    ("Result", "It took {N} weeks and moved {M} by {N2}%."),
    ("Scope", "What worked at scale, what didn't, and where it breaks."),
    ("Stakes", "If you run {T} in production, this changes the call."),
]

TAGS = {t: {"n": v["n"], "mean": v["mean_pct"]} for t, v in A["tags"]["per_tag"].items()}

best_rho = max(d["full"]["spearman_holdout"] for d in M["platforms"].values() if "full" in d)
META = {
    "n_posts": f"{A['n']:,}",
    "n_platforms": str(len(RULES)),
    "best_rho": f"{best_rho:.2f}",
    "updated": datetime.date.today().isoformat(),
}

payload = {"LEX": LEX, "MODEL": M, "RULES": RULES, "COND": COND_LABEL,
           "TEMPLATES": TEMPLATES, "SUBSHAPES": SUBTITLE_SHAPES, "TAGS": TAGS,
           "PLAT_NAME": PLAT_NAME, "META": META}

banner = ("/* GENERATED FILE — do not edit by hand.\n"
          "   Produced by pipeline/build_data.py from data/model.json + data/analysis.json.\n"
          f"   Corpus: {META['n_posts']} posts · generated {META['updated']} */\n")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(banner + "window.HI = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n")

print(f"wrote {OUT} ({os.path.getsize(OUT)/1024:.0f} KB)")
print(f"  corpus {META['n_posts']} posts · {META['n_platforms']} platforms · best rho {META['best_rho']}")
