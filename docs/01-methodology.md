# 01 — Methodology

**Corpus:** 9,809 posts across 6 platforms. Generated 2026-07-26.

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

| Platform | Posts | Metric | Median | P90 | % with subtitle |
|---|---|---|---|---|---|
| Dev.to | 965 | reactions | 533.0 | 1564.0 | 100.0 |
| Hacker News | 5204 | points | 960.5 | 1614.0 | 0.0 |
| Medium | 1058 | claps | 222.0 | 1073.0 | 98.6 |
| Reddit | 973 | upvotes | 2375.0 | 6715.0 | 0.0 |
| Substack | 762 | likes | 195.5 | 587.0 | 84.6 |
| X / Twitter | 847 | likes | 4655.0 | 52067.0 | 0.0 |

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
