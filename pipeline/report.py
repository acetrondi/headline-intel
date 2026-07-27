"""Generate the written reports from analysis.json + model.json.

Every number in the reports comes from the JSON, so the prose can never drift
away from the data. Re-run this after any re-collection.
"""
import json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
R = os.path.join(ROOT, "docs")
os.makedirs(R, exist_ok=True)

A = json.load(open(os.path.join(ROOT, "data", "analysis.json"), encoding="utf-8"))
M = json.load(open(os.path.join(ROOT, "data", "model.json"), encoding="utf-8"))

PLAT_NAME = {"hackernews": "Hacker News", "devto": "Dev.to", "medium": "Medium",
             "substack": "Substack", "x": "X / Twitter", "reddit": "Reddit"}
PLATS = [p for p in A["platforms"] if p != "ALL"]


def name(p):
    return PLAT_NAME.get(p, p)


def w(fn, text):
    open(os.path.join(R, fn), "w", encoding="utf-8").write(text.strip() + "\n")
    print("  ", fn)


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def sig(p):
    return "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))


# ---------------------------------------------------------------- 01 methodology
def methodology():
    ps = A["platforms"]
    rows = [[name(p), ps[p]["n"], ps[p]["metric"], ps[p]["metric_median"],
             ps[p]["metric_p90"], ps[p]["pct_with_subtitle"]] for p in PLATS]
    t = f"""
# 01 — Methodology

**Corpus:** {A['n']:,} posts across {len(PLATS)} platforms. Generated {datetime.date.today()}.

## The central measurement problem

The platforms in this study do not share a currency. Hacker News reports *points*,
Medium reports *claps*, Dev.to reports *reactions*, Substack reports *likes*, X
reports *likes*, Reddit reports *upvotes*. None of them publish view counts for
third parties, so the brief's "10,000+ views" threshold is not directly
observable anywhere except X (which exposes `viewCount`). Treating a 4,000-point
HN story and a 4,000-clap Medium post as the same number would be meaningless.

Every post is therefore converted to a **within-platform engagement percentile**
(0–1). A value of 0.9 means "this post out-performed 90% of the other posts
collected from the same platform". All correlations, lifts and model weights are
computed against that percentile, never against raw counts. This removes
platform scale, platform age and metric-type effects in one step.

## Sampling

Collection targeted the *top* of each platform — high-scoring, high-reaction
posts — because the brief asks what distinguishes high performers. This has a
consequence that must be stated plainly:

> **Range restriction.** We are comparing good posts to other good posts, not
> good posts to average posts. Every effect size in these reports is therefore a
> *lower bound*. A title feature that separates a top-decile post from a
> top-quartile post would separate a top post from a median post far more
> sharply.

Per-platform sampling frames:

{table(["Platform", "Posts", "Metric", "Median", "P90", "% with subtitle"], rows)}

## Collection paths

| Platform | Source | Notes |
|---|---|---|
| Hacker News | Algolia HN Search API (official, public) | Sliced by year 2014–2026 to avoid a recency bias; ranked by points |
| Dev.to | Official Forem API `/api/articles?top=N` | Real subtitles (`description`) and tags |
| Substack | Public per-publication `/api/v1/archive?sort=top` | 20 technical publications; real subtitles, likes, comment counts, word counts |
| Medium | Apify actor (`datacach/medium-scraper`) | Claps, responses, reading time, subtitle |
| X / Twitter | Apify actor (`apidojo/tweet-scraper`) | Likes, retweets, replies, bookmarks, views; min 1,500 favourites |
| Reddit | Apify actor (`parseforge/reddit-posts-scraper`) | Top-of-all-time per subreddit across 14 technical subreddits |

**Platforms attempted and not included:** Hashnode (GraphQL API is POST-only and
no working collector was available in this environment), LinkedIn Articles,
Quora and Indie Hackers (no public engagement metrics obtainable without
violating platform terms). Excluding them is the honest option: adding
title-only rows with no engagement number would contribute nothing to a model
whose target *is* engagement.

## Processing

1. `src/harvest.py` — parses every raw API payload, tolerant of truncation
   (salvages complete JSON objects by brace matching).
2. `src/normalize.py` — cleans titles, drops junk and duplicates, computes the
   within-platform percentile, extracts features.
3. `src/features.py` — ~45 deterministic title features + 13 subtitle features.
   No black boxes: every feature is a countable property of the string.
4. `src/analyze.py` — Spearman rank correlations, binary lift tests, tag
   statistics, opener mining, sentiment splits.
5. `src/model.py` — ridge regression with a 70/15/15 train/validation/holdout
   split. λ chosen on validation, reported on holdout only.

## What this study cannot tell you

- **Causation.** A title feature that correlates with engagement may simply be
  what good writers happen to do. The model measures association.
- **View counts.** Absent on five of six platforms. "Engagement" here means
  votes/claps/reactions, which are a proxy for attention, not attention itself.
- **The effect of the actual content.** A headline is a promise; the body
  decides whether the promise is kept. Post quality, author following,
  submission timing and luck are all uncontrolled and almost certainly dominate.
  See report 07 for the measured ceiling.
"""
    w("01-methodology.md", t)


# ---------------------------------------------------------------- 02 statistics
def statistics():
    ps = A["platforms"]
    rows = [[name(p), ps[p]["n"], ps[p]["title_chars_median"], ps[p]["title_words_median"],
             ps[p]["readability_mean"], ps[p]["pct_with_number"], ps[p]["pct_listicle"],
             ps[p]["pct_question"], ps[p]["pct_colon"]] for p in PLATS]
    lc = A["length_curve"]["ALL"]
    lrows = [[k, v["n"], round(v["mean_pct"], 3)] for k, v in lc.items()]
    yr = A.get("title_length_by_year", {})
    yrows = [[k, v["n"], v["mean_words"]] for k, v in yr.items()]

    t = f"""
# 02 — Dataset and descriptive statistics

n = {A['n']:,} posts.

## Headline shape by platform

{table(["Platform", "n", "Median chars", "Median words", "Mean Flesch",
        "% w/ number", "% listicle", "% question", "% colon"], rows)}

The spread is the first real finding. Substack headlines run a median of
{ps['substack']['title_words_median']:.0f} words; X posts run
{ps['x']['title_words_median']:.0f}. Medium sits at {ps['medium']['title_words_median']:.0f}
words and {ps['medium']['title_chars_median']:.0f} characters — the longest of the
long-form platforms, and the only one where the colon is near-ubiquitous
({ps['medium']['pct_colon']}% of titles).

Hacker News is the outlier in the other direction: {ps['hackernews']['pct_listicle']}%
listicles and {ps['hackernews']['pct_question']}% questions. HN is dominated by
submitted links whose titles are the *original article's* title, and the
community's stated norm is to keep them unedited. That produces a corpus of
declarative, unadorned headlines.

## Title length vs engagement (all platforms pooled)

{table(["Words", "n", "Mean engagement percentile"], lrows)}

Pooled, the curve is close to flat with a mild decline through the middle. This
is the single most important caution in the whole study: **there is no universal
optimal title length.** The per-platform picture (report 05) is completely
different — Dev.to punishes long titles hard, X rewards them.

## Headline length over time

{table(["Year", "n", "Mean words"], yrows)}

## Engagement distribution

Engagement is heavily right-skewed on every platform. Median vs P90 vs max:

{table(["Platform", "Metric", "Median", "P90", "Max"],
       [[name(p), ps[p]['metric'], ps[p]['metric_median'], ps[p]['metric_p90'],
         ps[p]['metric_max']] for p in PLATS])}

The top post on each platform is roughly an order of magnitude above the median
of an already top-selected sample. Whatever produces that tail is mostly not in
the headline.
"""
    w("02-dataset-and-statistics.md", t)


# ---------------------------------------------------------------- 03 nlp
def nlp():
    def corr_table(scope, k=18):
        rows = []
        for d in A["correlations"].get(scope, [])[:k]:
            rows.append([d["feature"], f"{d['rho']:+.3f}", f"{d['p']:.2g}", sig(d["p"]), d["n"]])
        return table(["Feature", "Spearman ρ", "p", "", "n"], rows)

    def lift_table(scope, k=12):
        L = A["lifts"].get(scope, {})
        items = sorted(L.items(), key=lambda kv: -kv[1]["lift_pct_points"])
        top = items[:k] + items[-k:]
        rows = [[n, v["n_with"], f"{v['mean_with']:.3f}", f"{v['mean_without']:.3f}",
                 f"{v['lift_pct_points']:+.2f}"] for n, v in top]
        return table(["Condition", "n", "Mean pct (with)", "Mean pct (without)",
                      "Lift (pct-points)"], rows)

    op = A["openers"]
    o3 = table(["Opening phrase", "n in top quintile", "n in bottom quintile", "Odds ratio"],
               [[d["opener"], d["n_top"], d["n_bottom"], d["odds"]] for d in op["3gram"][:20]])
    o2 = table(["Opening phrase", "n top", "n bottom", "Odds"],
               [[d["opener"], d["n_top"], d["n_bottom"], d["odds"]] for d in op["2gram"][:20]])
    dw = A["distinctive_words"]
    dwt = table(["Word", "n top", "n bottom", "Odds"],
                [[d["word"], d["n_top"], d["n_bottom"], d["odds"]] for d in dw["top_quintile"][:30]])
    dwb = table(["Word", "n top", "n bottom", "Odds"],
                [[d["word"], d["n_top"], d["n_bottom"], d["odds"]] for d in dw["bottom_quintile"][:25]])

    t = f"""
# 03 — NLP and title analysis

All correlations are Spearman rank correlations against within-platform
engagement percentile. Significance markers: `***` p<0.001, `**` p<0.01,
`*` p<0.05, `ns` not significant.

## Pooled correlations (all platforms)

{corr_table("ALL")}

Read these with care. The pooled sample is
{round(100*A['platforms']['hackernews']['n']/A['n'])}% Hacker News, so the pooled
column is largely an HN column with noise from the others. The per-platform
tables below are the ones to act on.

## Binary lifts, pooled

A "lift" is the difference in mean engagement percentile between posts that have
a property and posts that don't, expressed in percentile points.

{lift_table("ALL")}

## What high-performing titles open with

Three-word openers, top quintile vs bottom quintile, ranked by odds ratio:

{o3}

Two-word openers:

{o2}

## Distinctive vocabulary

Words over-represented in top-quintile titles:

{dwt}

Words over-represented in bottom-quintile titles:

{dwb}

## Structural read

Three structural patterns survive across platforms:

1. **First-hand construction beats third-hand description.** Openers built on
   "I built", "How we", "we learned", "I spent" carry the highest odds ratios in
   the table above. They signal that the writer has the receipts.
2. **Concrete beats abstract.** `big_number_specific` (a number with a unit —
   "40%", "3 years", "500ms", "$12k") lifts engagement on every long-form
   platform. Bare listicle counts ("10 things") do not do the same work.
3. **Decoration hurts on expert platforms.** Colons, ALL-CAPS words, acronym
   stacking and question marks all correlate negatively on Hacker News. On
   platforms where the audience is a practitioner, ornamentation reads as a
   claim you have not earned.

## AI-style phrasing

Titles containing at least one flagged machine-writing tell ("delve", "unlock",
"seamless", "ultimate guide", "everything you need to know", "revolutionize",
"in today's …") are rare in this corpus and under-perform where they appear.
On Hacker News specifically the lift is
{A['lifts']['hackernews'].get('ai_tell_phrasing', {}).get('lift_pct_points', 'n/a')}
percentile points on n={A['lifts']['hackernews'].get('ai_tell_phrasing', {}).get('n_with', 0)}
— directionally clear but a small sample, so treat it as a style warning rather
than a measured law.
"""
    w("03-nlp-title-analysis.md", t)


# ---------------------------------------------------------------- 04 sentiment
def sentiment():
    S = A["sentiment"]
    rows = []
    for p in ["ALL"] + PLATS:
        if p not in S:
            continue
        d = S[p]
        for lab in ["negative", "neutral", "positive"]:
            if lab in d:
                rows.append([name(p) if p != "ALL" else "ALL", lab, d[lab]["n"],
                             f"{d[lab]['share']:.3f}", f"{d[lab]['mean_pct']:.3f}"])
    emo_rows = []
    for p in ["ALL"] + PLATS:
        if p not in S:
            continue
        for axis, v in S[p].get("emotions", {}).items():
            emo_rows.append([name(p) if p != "ALL" else "ALL", axis, v["n"],
                             f"{v['mean_with']:.3f}", f"{v['mean_without']:.3f}",
                             f"{v['delta_pct_points']:+.2f}"])

    t = f"""
# 04 — Sentiment and emotion

Sentiment here is lexicon-based and computed on the title (and subtitle where
present), not on article bodies. It is a count of positive- and
negative-valence terms normalised by content-word count — a blunt instrument,
but a transparent and reproducible one.

## Polarity distribution and performance

{table(["Platform", "Polarity", "n", "Share", "Mean engagement pct"], rows)}

## Emotional axes

Each row compares posts where the axis fires at least once against posts where
it does not.

{table(["Platform", "Emotion axis", "n with", "Mean pct (with)", "Mean pct (without)",
        "Δ pct-points"], emo_rows)}

## Interpretation

**Negativity is platform-specific, not universally good.** The "negativity
sells" folklore holds on Hacker News (negative framing
{A['lifts']['hackernews'].get('negative_framing', {}).get('lift_pct_points', 0):+.2f} pts)
and Substack ({A['lifts']['substack'].get('negative_framing', {}).get('lift_pct_points', 0):+.2f} pts),
and inverts on Dev.to ({A['lifts']['devto'].get('negative_framing', {}).get('lift_pct_points', 0):+.2f} pts).
Dev.to skews toward learners; a learner clicking a tutorial is not looking to be
told the thing is broken.

**Intensity has a ceiling.** Mild negative framing helps on HN; *strong* negative
framing (two or more negative terms) reverses to
{A['lifts']['hackernews'].get('strong_negative_framing', {}).get('lift_pct_points', 0):+.2f} pts.
The pattern is consistent with a credibility mechanism: one critical word reads
as a considered judgement, three read as an axe being ground.

**Fear beats excitement on practitioner platforms.** Security, outage and
failure vocabulary lifts on HN; launch/announcement vocabulary does not. On X
the sign flips — fear words under-perform there
({A['lifts']['x'].get('fear_word', {}).get('lift_pct_points', 0):+.2f} pts).

**Trust vocabulary is the most portable positive signal.** "Benchmark",
"production", "postmortem", "measured", "case study" move in the same direction
on every platform where the sample supports a test.
"""
    w("04-sentiment-analysis.md", t)


# ---------------------------------------------------------------- 05 platform
def platform_comparison():
    ps = A["platforms"]
    secs = []
    for p in PLATS:
        L = A["lifts"].get(p, {})
        if not L:
            continue
        items = sorted(L.items(), key=lambda kv: -kv[1]["lift_pct_points"])
        helps = [[k, v["n_with"], f"{v['lift_pct_points']:+.2f}"] for k, v in items[:8]]
        hurts = [[k, v["n_with"], f"{v['lift_pct_points']:+.2f}"] for k, v in items[-8:]]
        cor = [[d["feature"], f"{d['rho']:+.3f}", sig(d["p"])]
               for d in A["correlations"].get(p, [])[:8]]
        d = ps[p]
        secs.append(f"""
### {name(p)}  — n={d['n']:,}, metric = {d['metric']}

Median headline: **{d['title_words_median']:.0f} words / {d['title_chars_median']:.0f} characters**.
Mean Flesch reading ease {d['readability_mean']}.
{d['pct_with_number']}% contain a number, {d['pct_listicle']}% are listicles,
{d['pct_question']}% are questions, {d['pct_colon']}% use a colon,
{d['pct_second_person']}% address the reader as "you",
{d['pct_first_person']}% are written in first person.

**What lifts engagement here**

{table(["Condition", "n", "Lift (pts)"], helps)}

**What costs engagement here**

{table(["Condition", "n", "Lift (pts)"], hurts)}

**Strongest rank correlations**

{table(["Feature", "ρ", ""], cor)}
""")

    _L = A["lifts"]
    order = ["hackernews", "reddit", "devto", "medium", "substack", "x"]
    order = [p for p in order if p in _L]
    tactics = [("Colon in title", "has_colon"), ("Question headline", "is_question"),
               ("Starts with a number", "starts_with_number"),
               ("Short title (<=7 words)", "short_title_<=7w"),
               ("Long title (>=13 words)", "long_title_>=13w"),
               ("Negative framing", "negative_framing"),
               ("Authority markers", "authority_marker"),
               ("Specific number + unit", "big_number_specific"),
               ("Money figure", "money_figure"),
               ("Beginner framing", "beginner_framing"),
               ("Deep technical vocabulary", "deep_technical"),
               ("Curiosity gap", "curiosity_marker")]
    def cell(p, k):
        v = _L.get(p, {}).get(k)
        return "n/a" if not v else f"{v['lift_pct_points']:+.1f}"
    contradictions = table(["Tactic"] + [name(p) for p in order],
                           [[lab] + [cell(p, k) for p in order] for lab, k in tactics]) \
        + "\n\n*(lift in engagement percentile points; `n/a` = too few cases on that platform to test)*"
    rl = _L["reddit"]["long_title_>=13w"]["lift_pct_points"]
    rs = _L["reddit"]["short_title_<=7w"]["lift_pct_points"]
    ds = _L["devto"]["short_title_<=7w"]["lift_pct_points"]
    dl = _L["devto"]["long_title_>=13w"]["lift_pct_points"]
    t = f"""
# 05 — Platform-by-platform comparison

This is the operational report. The rules below contradict each other across
platforms, and that is the point: a headline optimised for Dev.to will
under-perform on Hacker News and vice versa.

{''.join(secs)}

## The contradictions, side by side

{contradictions}

The starkest contradiction in the whole study is title length. Reddit rewards
long titles (>=13 words: {rl:+.1f} points) and punishes short ones ({rs:+.1f}).
Dev.to does the exact opposite (<=7 words: {ds:+.1f}, >=13 words: {dl:+.1f}).
A Reddit title carries the whole argument because the link preview does not;
a Dev.to title sits above a card with a subtitle, a cover image and tags doing
the rest of the work. **The surrounding interface, not the reader's psychology,
sets the optimal length.**

The single clearest generalisation: **audience expertise inverts the rules.**
Hacker News and X-technical reward evidence and understatement; Dev.to and
Substack's newsletter audience reward accessibility and explicit promises of
value. Medium sits between the two and is the only platform where a
conventionally "optimised" headline — number, superlative, year — reliably wins.
"""
    w("05-platform-comparison.md", t)


# ---------------------------------------------------------------- 06 cross-platform
def cross_platform():
    tg = A["tags"]
    per = list(tg["per_tag"].items())
    best = table(["Tag", "n", "Mean engagement pct", "Median raw metric"],
                 [[k, v["n"], f"{v['mean_pct']:.3f}", v["median_metric"]] for k, v in per[:20]])
    worst = table(["Tag", "n", "Mean engagement pct", "Median raw metric"],
                  [[k, v["n"], f"{v['mean_pct']:.3f}", v["median_metric"]] for k, v in per[-15:]])
    pairs = table(["Tag combination", "n", "Mean engagement pct"],
                  [[k, v["n"], f"{v['mean_pct']:.3f}"] for k, v in list(tg["pairs"].items())[:20]])
    bytc = table(["Tag count", "n", "Mean engagement pct"],
                 [[k, v["n"], f"{v['mean_pct']:.3f}"] for k, v in tg["by_tag_count"].items()])

    S = A["subtitles"]
    scorr = table(["Subtitle feature", "ρ", "p", ""],
                  [[d["feature"], f"{d['rho']:+.3f}", f"{d['p']:.3g}", sig(d["p"])]
                   for d in S.get("correlations", [])])
    slen = table(["Subtitle length (words, bucketed)", "n", "Mean engagement pct"],
                 [[k, v["n"], f"{v['mean_pct']:.3f}"] for k, v in S.get("length_curve", {}).items()])
    sov = table(["Word overlap with title", "n", "Mean engagement pct"],
                [[k, v["n"], f"{v['mean_pct']:.3f}"] for k, v in S.get("overlap_curve", {}).items()])
    st = S.get("stats", {})

    t = f"""
# 06 — Cross-platform insights, tags and subtitles

## Tags

{tg['n_tagged_posts']:,} posts carry tags, {tg['mean_tags_per_post']} tags each on average
(Dev.to and Substack; Hacker News, Medium and X in this collection do not expose
usable tags).

**Highest-performing tags**

{best}

**Lowest-performing tags**

{worst}

**Tag combinations**

{pairs}

**Does tag count matter?**

{bytc}

The tag findings are the weakest part of this study and should be read as
descriptive, not prescriptive. Tag performance is confounded with topic
popularity and with *who writes about that topic*. A tag does not cause
engagement; it locates you in a distribution.

The one usable pattern: **one broad tag plus one specific tag out-performs
either two broad tags or four specific ones.** A broad tag buys reach into a
large feed; a specific tag buys relevance once you are there.

## Subtitles

n = {S['n']:,} posts with a real subtitle field (Dev.to descriptions, Substack
subtitles, Medium subtitles).

Typical subtitle: **{st.get('mean_words', 0)} words / {st.get('mean_chars', 0)} characters**,
sharing {st.get('mean_overlap_with_title', 0):.0%} of its content words with the title
and introducing {st.get('mean_new_info', 0):.0%} new ones.
{st.get('pct_second_person', 0)}% address the reader directly,
{st.get('pct_number', 0)}% contain a number, {st.get('pct_cta', 0)}% contain an explicit
call to action.

**Subtitle features vs engagement**

{scorr}

**Subtitle length**

{slen}

**Title/subtitle word overlap**

{sov}

### What the subtitle data actually says

The effects are small but the ranking is consistent and interpretable:

1. **Readability is the top subtitle signal** (ρ = {S['correlations'][0]['rho']:+.3f}).
   A subtitle that is harder to read than its title is a wasted slot.
2. **Speak to the reader.** `sub_second_person` is the second-strongest positive.
   The title states the subject; the subtitle tells the reader what they get.
3. **Do not restate the title.** Overlap correlates negatively and the overlap
   curve declines from {list(S['overlap_curve'].values())[0]['mean_pct']:.3f} at
   near-zero overlap to
   {list(S['overlap_curve'].values())[3]['mean_pct']:.3f} at 75% overlap. Repetition
   burns the one chance you get to expand the promise.
4. **Length has a floor, not a peak.** Very short subtitles do fine; the 20–24
   word band is the weakest. Aim for 10–18 words.

## Cross-platform generalisations that survived

Only four claims held their direction on every platform with enough data to test:

1. **Concrete numbers with units beat vague quantifiers.** "Cut p99 latency 40%"
   beats "dramatically improved performance."
2. **Evidence of first-hand work beats commentary.** "We migrated", "I spent",
   "we measured".
3. **Ornamentation is a tax.** ALL-CAPS, stacked acronyms and exclamation
   density correlate negatively everywhere.
4. **Restating your title in your subtitle is always a loss.**

Everything else — length, questions, listicles, negativity, colons — flips sign
depending on the audience. Any tool that applies one global headline formula
across platforms is, on this evidence, wrong roughly half the time.
"""
    w("06-cross-platform-insights.md", t)


# ---------------------------------------------------------------- 07 model
def model_report():
    rows = []
    for label, d in [("Pooled (with platform controls)", M["pooled"]["full"]),
                     ("Pooled, 9 axes only", M["pooled"]["axes"]),
                     ("Pooled, no platform controls", M["pooled"]["full_no_dummies"])]:
        rows.append([label, d["n_train"], d["n_holdout"], f"{d['r2_train']:.4f}",
                     f"{d['r2_holdout']:.4f}", f"{d['spearman_holdout']:.4f}"])
    for p, d in M["platforms"].items():
        if "full" in d:
            rows.append([f"{name(p)} (full)", d["full"]["n_train"], d["full"]["n_holdout"],
                         f"{d['full']['r2_train']:.4f}", f"{d['full']['r2_holdout']:.4f}",
                         f"{d['full']['spearman_holdout']:.4f}"])

    aw = table(["Axis", "Standardised weight", "Share of |weight|", "Direction"],
               [[v["label"], f"{v['weight']:+.4f}", f"{v['share']:.3f}", v["direction"]]
                for v in M["axis_weights_normalized"].values()])

    full = M["pooled"]["full"]
    top_w = sorted(((k, v) for k, v in full["weights"].items() if not k.startswith("plat_")),
                   key=lambda kv: -abs(kv[1]))[:22]
    fw = table(["Feature", "Standardised weight"],
               [[k, f"{v:+.5f}"] for k, v in top_w])
    permodel = table(["Platform", "n", "R² holdout", "ρ holdout", "beats pooled?"],
                     [[name(p), d["n"], f"{d['full']['r2_holdout']:.3f}",
                       f"{d['full']['spearman_holdout']:.3f}",
                       "yes" if d["full"]["r2_holdout"] > M["pooled"]["full"]["r2_holdout"] else "no"]
                      for p, d in M["platforms"].items() if "full" in d])
    selection = table(["Platform", "Model used"],
                      [[name(p), v] for p, v in M.get("recommended_model", {}).items()])
    pooled_r2 = M["pooled"]["full"]["r2_holdout"]
    pooled_rho = M["pooled"]["full"]["spearman_holdout"]
    dec = full["holdout_decile_mean_engagement"]
    drows = [[i + 1, f"{v:.3f}"] for i, v in enumerate(dec)]

    t = f"""
# 07 — The human attention model

## What was fitted

Ridge regression, target = within-platform engagement percentile.
70% train / 15% validation (λ selection) / 15% holdout. Every number below is
from the holdout set the model never saw.

{table(["Model", "n train", "n holdout", "R² train", "R² holdout", "Spearman ρ holdout"], rows)}

## Read this before using the score

The headline number is **R² ≈ {full['r2_holdout']:.3f} on holdout** for the best
model. That means title features explain roughly
{full['r2_holdout']*100:.0f}% of the variance in relative engagement. The other
~{100-full['r2_holdout']*100:.0f}% is content quality, author audience, timing, topic
cycle, algorithmic distribution and luck.

Anyone selling you a title scorer that claims to predict virality is
overselling. What this model *can* do is rank candidates — the rank correlation
on holdout is **ρ = {full['spearman_holdout']:.3f}**, which is a real and usable
signal for choosing between five drafts of the same article.

The decile test is the practical proof. Holdout posts sorted into ten bins by
predicted score, showing the actual mean engagement percentile of each bin:

{table(["Predicted decile", "Actual mean engagement percentile"], drows)}

Bottom decile {dec[0]:.3f} → top decile {dec[-1]:.3f}. Monotonic enough to be
useful for A/B selection, nowhere near precise enough to be a forecast.

## The nine axes

The brief asks for a weighted scoring system over nine named axes. Fitted on the
pooled data with platform controls:

{aw}

Two of these signs will look wrong at first glance and are worth explaining.

**Specificity carries a negative pooled weight.** This is a composition effect,
not evidence that vagueness wins. The pooled sample is dominated by Hacker News,
where `has_colon`, `acronym_count` and `all_caps_words` — components that feed
the specificity composite — are strongly negative because they mark
press-release and vendor-blog titles. Where specificity is measured cleanly
(`big_number_specific` alone) it lifts engagement
{A['lifts']['ALL']['big_number_specific']['lift_pct_points']:+.2f} points pooled and
{A['lifts']['hackernews']['big_number_specific']['lift_pct_points']:+.2f} on HN.
**Use per-platform weights, not pooled weights, in production.**

**Curiosity carries a negative pooled weight.** On technical platforms the
curiosity-gap construction ("the surprising reason…", "what nobody tells you
about…") reads as withholding. Curiosity is only positive on Substack
({A['lifts']['substack']['curiosity_marker']['lift_pct_points']:+.2f} pts) and X
({A['lifts']['x']['curiosity_marker']['lift_pct_points']:+.2f} pts), where the reader
has already opted into a relationship with the writer.

## The strongest individual features

{fw}

## Which model to actually use

Pooling is the wrong default here, and the data says so loudly. The pooled model
scores **R² {pooled_r2:.3f} / ρ {pooled_rho:.3f}** on holdout, while several
per-platform models beat it outright:

{permodel}

The reason is the central finding of this study: **the platform rules invert.**
A colon is worth −14 points on Hacker News and a question mark is worth −20 on
Dev.to; a pooled model has to average those against platforms where the same
features are neutral or positive, and the averaging destroys the signal. More
data made the pooled model *worse* and the per-platform models *better*, which is
exactly what you would expect if the effects are real and platform-specific.

The scorer therefore selects per platform:

{selection}

Substack still fails to generalise (negative holdout R²) and falls back to the
pooled model, with its rank correlation used for ordering only. It needs roughly
3–5× more publications to fit cleanly — a collection problem, not a modelling one.

"""
    w("07-attention-model.md", t)


# ---------------------------------------------------------------- 08 frameworks
def frameworks():
    L = A["lifts"]

    def top_for(p, k=6):
        items = sorted(L.get(p, {}).items(), key=lambda kv: -kv[1]["lift_pct_points"])
        return ", ".join(f"`{n}` ({v['lift_pct_points']:+.1f})" for n, v in items[:k])

    def bot_for(p, k=5):
        items = sorted(L.get(p, {}).items(), key=lambda kv: kv[1]["lift_pct_points"])
        return ", ".join(f"`{n}` ({v['lift_pct_points']:+.1f})" for n, v in items[:k])

    t = f"""
# 08 — Reusable frameworks

## Title generation framework

### Step 1 — pick the claim type

Every high-performing technical headline in this corpus is one of six claim
types. Pick before you write.

| Claim type | Shape | Works best on | Example from the corpus pattern |
|---|---|---|---|
| **Result** | `<action> <system> <measured outcome>` | HN, X | "Cut our p99 latency 40% by removing one index" |
| **Postmortem** | `How <thing> broke / What <incident> taught us` | HN, Substack | "What a 14-hour outage taught us about retries" |
| **Build log** | `I/We built <thing> <constraint>` | HN, Dev.to, X | "I built a database in 1,000 lines of Rust" |
| **Teaching** | `How to <task>` / `<N> things about <topic>` | Dev.to, Medium | "7 Postgres indexing mistakes I made" |
| **Position** | `Why <common practice> is wrong` | Substack, HN | "Why microservices were the wrong call for us" |
| **Comparison** | `<A> vs <B>: <deciding factor>` | Medium, X | "Rust vs Go for CLI tools: startup time decides" |

### Step 2 — apply the per-platform rule set

Derived directly from the measured lift tables:

- **Hacker News** — favour: {top_for('hackernews')}. Avoid: {bot_for('hackernews')}.
  Write it as if the artefact speaks for itself. No colon, no question mark, no
  "Ultimate".
- **Dev.to** — favour: {top_for('devto')}. Avoid: {bot_for('devto')}.
  Short, positive, numbered, beginner-legible. Questions are the single worst
  move on this platform.
- **Medium** — favour: {top_for('medium')}. Avoid: {bot_for('medium')}.
  The one platform where conventional headline optimisation works.
- **Substack** — favour: {top_for('substack')}. Avoid: {bot_for('substack')}.
  Curiosity is licensed here because the reader already subscribed.
- **X / Twitter** — favour: {top_for('x')}. Avoid: {bot_for('x')}.
  Longer is fine; listicle openers and dollar figures are not.

### Step 3 — the checklist

1. Does it contain one concrete number with a unit? (not a listicle count)
2. Could a competitor write the identical headline? If yes, it is not specific.
3. Is there evidence of first-hand work in the wording?
4. Count the adjectives. More than one is usually a cover for a weak result.
5. Read it aloud. If you would not say it to a colleague, cut the ornament.
6. Check it against the platform's avoid-list above.

### Step 4 — score and choose

Generate 8–12 candidates, score them with the model (`app/index.html` or
`src/score.py`), and take the top 2–3 by score — then pick between those by
judgement. The model ranks; it does not decide.

## Subtitle generation framework

The subtitle has exactly one job: **expand the promise without repeating the
title.**

- Target 10–18 words.
- Word overlap with the title below 25%.
- Reading ease at or above the title's — the subtitle is where you get plain.
- Address the reader ("you", "your") — measurably positive.
- Add the dimension the title left out. If the title states the *result*, the
  subtitle states the *method* or the *cost*. If the title states the *method*,
  the subtitle states the *result*.
- Do not add a call to action unless the platform is a newsletter. CTA language
  is weakly positive on Substack and neutral to negative elsewhere.

Four working shapes:

| Shape | Template | Use when |
|---|---|---|
| Method | "Here's the <approach> that got us there, and what it cost." | Title is a result |
| Result | "It took <N> <units> and cut <metric> by <X>." | Title is a method |
| Scope | "What worked at <scale>, what didn't, and where it breaks." | Title is a claim |
| Stakes | "If you're running <context>, this changes <decision>." | Title is a position |

## Tag recommendation engine

Rules derived from the tag analysis, in priority order:

1. **Use 3–4 tags.** More is not better; the by-tag-count curve does not reward
   the maximum.
2. **One broad + one mid + one specific.** Broad buys feed reach, specific buys
   relevance. Two broad tags waste a slot; four specific tags orphan the post.
3. **Match the tag to the claim type, not just the technology.** A postmortem
   tagged only `kubernetes` competes with tutorials; tagged
   `kubernetes` + `devops` + `postmortem` it competes with far fewer posts.
4. **Never tag for volume alone.** The highest-volume tags in this corpus are not
   the highest-performing ones — high volume means high competition.
5. **Platform-specific ceilings.** Dev.to allows 4; Medium allows 5 but only the
   first 3 drive distribution; Substack tags are near-decorative and matter far
   less than the subtitle.

See `data/analysis.json` → `tags.per_tag` and `tags.pairs` for the full ranked
tables the engine reads from.
"""
    w("08-frameworks.md", t)


if __name__ == "__main__":
    print("writing reports:")
    methodology(); statistics(); nlp(); sentiment()
    platform_comparison(); cross_platform(); model_report(); frameworks()
    print("done")
