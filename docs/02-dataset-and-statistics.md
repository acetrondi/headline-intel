# 02 — Dataset and descriptive statistics

n = 9,809 posts.

## Headline shape by platform

| Platform | n | Median chars | Median words | Mean Flesch | % w/ number | % listicle | % question | % colon |
|---|---|---|---|---|---|---|---|---|
| Dev.to | 965 | 47 | 8 | 55.6 | 39.5 | 18.9 | 4.0 | 14.0 |
| Hacker News | 5204 | 46.0 | 8.0 | 56.0 | 20.0 | 0.2 | 6.7 | 22.0 |
| Medium | 1058 | 60.0 | 10.0 | 49.3 | 38.5 | 14.6 | 5.8 | 23.3 |
| Reddit | 973 | 64 | 11 | 60.4 | 25.4 | 0.4 | 7.4 | 8.8 |
| Substack | 762 | 45.0 | 7.0 | 55.5 | 28.7 | 3.9 | 7.5 | 25.2 |
| X / Twitter | 847 | 74 | 13 | 54.6 | 27.3 | 1.4 | 5.5 | 15.1 |

The spread is the first real finding. Substack headlines run a median of
7 words; X posts run
13. Medium sits at 10
words and 60 characters — the longest of the
long-form platforms, and the only one where the colon is near-ubiquitous
(23.3% of titles).

Hacker News is the outlier in the other direction: 0.2%
listicles and 6.7% questions. HN is dominated by
submitted links whose titles are the *original article's* title, and the
community's stated norm is to keep them unedited. That produces a corpus of
declarative, unadorned headlines.

## Title length vs engagement (all platforms pooled)

| Words | n | Mean engagement percentile |
|---|---|---|
| 3 | 680 | 0.51 |
| 4 | 693 | 0.548 |
| 5 | 799 | 0.501 |
| 6 | 857 | 0.532 |
| 7 | 964 | 0.497 |
| 8 | 934 | 0.492 |
| 9 | 925 | 0.491 |
| 10 | 875 | 0.493 |
| 11 | 743 | 0.478 |
| 12 | 643 | 0.463 |
| 13 | 440 | 0.491 |
| 14 | 337 | 0.478 |
| 15 | 207 | 0.473 |
| 16 | 153 | 0.505 |
| 17 | 102 | 0.541 |
| 18 | 70 | 0.45 |
| 19 | 40 | 0.543 |
| 20 | 347 | 0.53 |

Pooled, the curve is close to flat with a mild decline through the middle. This
is the single most important caution in the whole study: **there is no universal
optimal title length.** The per-platform picture (report 05) is completely
different — Dev.to punishes long titles hard, X rewards them.

## Headline length over time

| Year | n | Mean words |
|---|---|---|
| 2014 | 364 | 6.87 |
| 2015 | 390 | 7.22 |
| 2016 | 409 | 7.46 |
| 2017 | 478 | 8.37 |
| 2018 | 546 | 8.34 |
| 2019 | 683 | 8.55 |
| 2020 | 879 | 9.19 |
| 2021 | 823 | 9.29 |
| 2022 | 704 | 8.89 |
| 2023 | 722 | 8.49 |
| 2024 | 664 | 8.3 |
| 2025 | 1011 | 8.69 |
| 2026 | 1252 | 9.62 |

## Engagement distribution

Engagement is heavily right-skewed on every platform. Median vs P90 vs max:

| Platform | Metric | Median | P90 | Max |
|---|---|---|---|---|
| Dev.to | reactions | 533.0 | 1564.0 | 4737.0 |
| Hacker News | points | 960.5 | 1614.0 | 6015.0 |
| Medium | claps | 222.0 | 1073.0 | 69950.0 |
| Reddit | upvotes | 2375.0 | 6715.0 | 45091.0 |
| Substack | likes | 195.5 | 587.0 | 3488.0 |
| X / Twitter | likes | 4655.0 | 52067.0 | 354261.0 |

The top post on each platform is roughly an order of magnitude above the median
of an already top-selected sample. Whatever produces that tail is mostly not in
the headline.
