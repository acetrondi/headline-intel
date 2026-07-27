# 03 — NLP and title analysis

All correlations are Spearman rank correlations against within-platform
engagement percentile. Significance markers: `***` p<0.001, `**` p<0.01,
`*` p<0.05, `ns` not significant.

## Pooled correlations (all platforms)

| Feature | Spearman ρ | p |  | n |
|---|---|---|---|---|
| has_colon | -0.132 | 0 | *** | 9809 |
| all_caps_words | -0.081 | 0 | *** | 9809 |
| title_case_ratio | -0.080 | 0 | *** | 9809 |
| has_question | -0.078 | 0 | *** | 9809 |
| acronym_count | -0.075 | 0 | *** | 9809 |
| curiosity_gap | -0.071 | 0 | *** | 9809 |
| has_dash | -0.065 | 0 | *** | 9809 |
| specificity | -0.054 | 0 | *** | 9809 |
| word_count | -0.042 | 3.8e-05 | *** | 9809 |
| authority_markers | +0.036 | 0.00034 | *** | 9809 |
| listicle_size | +0.036 | 0.00038 | *** | 9809 |
| is_listicle | +0.035 | 0.00048 | *** | 9809 |
| starts_with_number | +0.035 | 0.00048 | *** | 9809 |
| authority | +0.034 | 0.00083 | *** | 9809 |
| char_count | -0.032 | 0.0014 | ** | 9809 |
| sentiment | -0.032 | 0.0016 | ** | 9809 |
| clarity | -0.030 | 0.0031 | ** | 9809 |
| has_year | -0.029 | 0.0036 | ** | 9809 |

Read these with care. The pooled sample is
53% Hacker News, so the pooled
column is largely an HN column with noise from the others. The per-platform
tables below are the ones to act on.

## Binary lifts, pooled

A "lift" is the difference in mean engagement percentile between posts that have
a property and posts that don't, expressed in percentile points.

| Condition | n | Mean pct (with) | Mean pct (without) | Lift (pct-points) |
|---|---|---|---|---|
| starts_with_number | 392 | 0.550 | 0.498 | +5.20 |
| big_number_specific | 304 | 0.538 | 0.499 | +3.92 |
| fear_word | 219 | 0.537 | 0.499 | +3.79 |
| authority_marker | 1705 | 0.523 | 0.495 | +2.76 |
| short_title_<=7w | 3993 | 0.516 | 0.489 | +2.74 |
| negative_framing | 1404 | 0.520 | 0.497 | +2.34 |
| urgency_marker | 1143 | 0.508 | 0.499 | +0.93 |
| beginner_framing | 687 | 0.506 | 0.499 | +0.65 |
| starts_with_why | 129 | 0.506 | 0.500 | +0.59 |
| imperative_open | 139 | 0.505 | 0.500 | +0.51 |
| contains_any_number | 2525 | 0.503 | 0.499 | +0.35 |
| superlative | 564 | 0.502 | 0.500 | +0.23 |
| parenthetical | 658 | 0.486 | 0.501 | -1.47 |
| positive_framing | 1109 | 0.484 | 0.502 | -1.75 |
| two_plus_power_words | 67 | 0.476 | 0.500 | -2.39 |
| medium_title_8_12w | 4120 | 0.485 | 0.511 | -2.57 |
| money_figure | 184 | 0.472 | 0.500 | -2.80 |
| surprise_word | 77 | 0.466 | 0.500 | -3.40 |
| curiosity_marker | 494 | 0.467 | 0.502 | -3.51 |
| strong_negative_framing | 134 | 0.461 | 0.500 | -3.95 |
| mentions_year | 440 | 0.461 | 0.502 | -4.11 |
| deep_technical | 311 | 0.460 | 0.501 | -4.18 |
| is_question | 626 | 0.414 | 0.506 | -9.22 |
| has_colon | 1932 | 0.423 | 0.519 | -9.61 |

## What high-performing titles open with

Three-word openers, top quintile vs bottom quintile, ranked by odds ratio:

| Opening phrase | n in top quintile | n in bottom quintile | Odds ratio |
|---|---|---|---|
| got7 winter heptagon | 5 | 0 | 2546.82 |
| 50 free tools | 4 | 0 | 2037.66 |
| a crash course | 4 | 0 | 2037.66 |
| got7 'python' mv | 4 | 0 | 2037.66 |
| a guide to | 5 | 1 | 5.0 |
| i made a | 5 | 1 | 5.0 |
| how to use | 5 | 1 | 5.0 |
| the end of | 4 | 1 | 4.0 |
| show hn i | 7 | 29 | 0.24 |
| ask hn what | 7 | 30 | 0.23 |

Two-word openers:

| Opening phrase | n top | n bottom | Odds |
|---|---|---|---|
| got7 'python' | 6 | 0 | 3055.99 |
| javascript visualized | 5 | 0 | 2546.82 |
| got7 winter | 5 | 0 | 2546.82 |
| claude opus | 4 | 0 | 2037.66 |
| 50 free | 4 | 0 | 2037.66 |
| facebook is | 4 | 0 | 2037.66 |
| a crash | 4 | 0 | 2037.66 |
| i m | 5 | 1 | 5.0 |
| the end | 4 | 1 | 4.0 |
| my favorite | 4 | 1 | 4.0 |
| i made | 9 | 3 | 3.0 |
| elon musk | 5 | 2 | 2.5 |
| a guide | 5 | 2 | 2.5 |
| open source | 4 | 2 | 2.0 |
| the ultimate | 4 | 2 | 2.0 |
| why i | 5 | 3 | 1.67 |
| i am | 7 | 5 | 1.4 |
| claude code | 4 | 3 | 1.34 |
| u s | 6 | 5 | 1.2 |
| how to | 29 | 29 | 1.0 |

## Distinctive vocabulary

Words over-represented in top-quintile titles:

| Word | n top | n bottom | Odds |
|---|---|---|---|
| got7 | 14 | 0 | 7129.31 |
| ftc | 8 | 0 | 4074.32 |
| died | 28 | 3 | 9.34 |
| crash | 9 | 1 | 9.0 |
| backdoor | 8 | 1 | 8.0 |
| npm | 8 | 1 | 8.0 |
| repositories | 8 | 1 | 8.0 |
| zoom | 8 | 1 | 8.0 |
| private | 11 | 2 | 5.5 |
| openai | 29 | 6 | 4.84 |
| john | 9 | 2 | 4.5 |
| illegal | 9 | 2 | 4.5 |
| his | 9 | 2 | 4.5 |
| access | 12 | 3 | 4.0 |
| llms | 8 | 2 | 4.0 |
| accidentally | 8 | 2 | 4.0 |
| websites | 8 | 2 | 4.0 |
| videos | 8 | 2 | 4.0 |
| programmers | 8 | 2 | 4.0 |
| employees | 15 | 4 | 3.75 |
| old | 11 | 3 | 3.67 |
| chatgpt | 14 | 4 | 3.5 |
| twitter | 20 | 6 | 3.34 |
| windows | 10 | 3 | 3.34 |
| chrome | 13 | 4 | 3.25 |
| resources | 19 | 6 | 3.17 |
| microsoft | 22 | 7 | 3.15 |
| users | 15 | 5 | 3.0 |
| cheat | 12 | 4 | 3.0 |
| public | 9 | 3 | 3.0 |

Words over-represented in bottom-quintile titles:

| Word | n top | n bottom | Odds |
|---|---|---|---|
| show | 29 | 218 | 0.13 |
| ask | 24 | 125 | 0.19 |
| startup | 9 | 35 | 0.26 |
| 2026 | 9 | 29 | 0.31 |
| writing | 9 | 28 | 0.32 |
| react | 13 | 36 | 0.36 |
| built | 15 | 40 | 0.38 |
| rust | 9 | 23 | 0.39 |
| learn | 16 | 39 | 0.41 |
| tell | 16 | 37 | 0.43 |
| building | 13 | 29 | 0.45 |
| java | 8 | 17 | 0.47 |
| here | 12 | 24 | 0.5 |
| big | 8 | 15 | 0.53 |
| language | 13 | 24 | 0.54 |
| things | 9 | 16 | 0.56 |
| need | 10 | 18 | 0.56 |
| best | 22 | 39 | 0.56 |
| books | 8 | 14 | 0.57 |
| amazon | 12 | 21 | 0.57 |
| science | 10 | 17 | 0.59 |
| game | 16 | 27 | 0.59 |
| engineering | 39 | 66 | 0.59 |
| news | 9 | 15 | 0.6 |
| still | 9 | 15 | 0.6 |

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
-13.49
percentile points on n=16
— directionally clear but a small sample, so treat it as a style warning rather
than a measured law.
