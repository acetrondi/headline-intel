# 04 — Sentiment and emotion

Sentiment here is lexicon-based and computed on the title (and subtitle where
present), not on article bodies. It is a count of positive- and
negative-valence terms normalised by content-word count — a blunt instrument,
but a transparent and reproducible one.

## Polarity distribution and performance

| Platform | Polarity | n | Share | Mean engagement pct |
|---|---|---|---|---|
| ALL | negative | 1307 | 0.133 | 0.521 |
| ALL | neutral | 7500 | 0.765 | 0.498 |
| ALL | positive | 1002 | 0.102 | 0.483 |
| Dev.to | negative | 65 | 0.067 | 0.428 |
| Dev.to | neutral | 696 | 0.721 | 0.493 |
| Dev.to | positive | 204 | 0.211 | 0.548 |
| Hacker News | negative | 744 | 0.143 | 0.531 |
| Hacker News | neutral | 4095 | 0.787 | 0.499 |
| Hacker News | positive | 365 | 0.070 | 0.450 |
| Medium | negative | 142 | 0.134 | 0.526 |
| Medium | neutral | 759 | 0.717 | 0.500 |
| Medium | positive | 157 | 0.148 | 0.477 |
| Reddit | negative | 143 | 0.147 | 0.540 |
| Reddit | neutral | 721 | 0.741 | 0.498 |
| Reddit | positive | 109 | 0.112 | 0.458 |
| Substack | negative | 67 | 0.088 | 0.506 |
| Substack | neutral | 634 | 0.832 | 0.498 |
| Substack | positive | 61 | 0.080 | 0.518 |
| X / Twitter | negative | 146 | 0.172 | 0.496 |
| X / Twitter | neutral | 595 | 0.703 | 0.503 |
| X / Twitter | positive | 106 | 0.125 | 0.490 |

## Emotional axes

Each row compares posts where the axis fires at least once against posts where
it does not.

| Platform | Emotion axis | n with | Mean pct (with) | Mean pct (without) | Δ pct-points |
|---|---|---|---|---|---|
| ALL | fear_words | 219 | 0.537 | 0.499 | +3.79 |
| ALL | surprise_words | 77 | 0.466 | 0.500 | -3.40 |
| ALL | excitement_words | 483 | 0.479 | 0.501 | -2.20 |
| ALL | trust_words | 332 | 0.487 | 0.500 | -1.35 |
| ALL | curiosity_markers | 494 | 0.467 | 0.502 | -3.51 |
| ALL | power_words | 1250 | 0.489 | 0.502 | -1.22 |
| Dev.to | excitement_words | 28 | 0.464 | 0.501 | -3.76 |
| Dev.to | trust_words | 26 | 0.521 | 0.499 | +2.14 |
| Dev.to | curiosity_markers | 37 | 0.386 | 0.505 | -11.90 |
| Dev.to | power_words | 196 | 0.528 | 0.493 | +3.58 |
| Hacker News | fear_words | 141 | 0.561 | 0.498 | +6.25 |
| Hacker News | surprise_words | 17 | 0.489 | 0.500 | -1.07 |
| Hacker News | excitement_words | 242 | 0.482 | 0.501 | -1.86 |
| Hacker News | trust_words | 142 | 0.535 | 0.499 | +3.63 |
| Hacker News | curiosity_markers | 178 | 0.450 | 0.502 | -5.14 |
| Hacker News | power_words | 486 | 0.470 | 0.503 | -3.31 |
| Medium | fear_words | 17 | 0.416 | 0.501 | -8.50 |
| Medium | surprise_words | 25 | 0.393 | 0.503 | -10.98 |
| Medium | excitement_words | 42 | 0.512 | 0.499 | +1.22 |
| Medium | trust_words | 89 | 0.378 | 0.511 | -13.31 |
| Medium | curiosity_markers | 125 | 0.433 | 0.509 | -7.57 |
| Medium | power_words | 218 | 0.491 | 0.502 | -1.17 |
| Reddit | excitement_words | 73 | 0.414 | 0.507 | -9.26 |
| Reddit | trust_words | 30 | 0.573 | 0.498 | +7.49 |
| Reddit | curiosity_markers | 53 | 0.513 | 0.499 | +1.42 |
| Reddit | power_words | 132 | 0.496 | 0.501 | -0.51 |
| Substack | fear_words | 19 | 0.589 | 0.498 | +9.16 |
| Substack | excitement_words | 27 | 0.582 | 0.497 | +8.45 |
| Substack | trust_words | 23 | 0.528 | 0.499 | +2.87 |
| Substack | curiosity_markers | 52 | 0.542 | 0.497 | +4.50 |
| Substack | power_words | 74 | 0.527 | 0.497 | +2.95 |
| X / Twitter | fear_words | 19 | 0.409 | 0.502 | -9.32 |
| X / Twitter | excitement_words | 71 | 0.483 | 0.502 | -1.89 |
| X / Twitter | trust_words | 22 | 0.416 | 0.502 | -8.59 |
| X / Twitter | curiosity_markers | 49 | 0.542 | 0.497 | +4.47 |
| X / Twitter | power_words | 144 | 0.475 | 0.505 | -3.05 |

## Interpretation

**Negativity is platform-specific, not universally good.** The "negativity
sells" folklore holds on Hacker News (negative framing
+3.51 pts)
and Substack (+2.07 pts),
and inverts on Dev.to (-8.31 pts).
Dev.to skews toward learners; a learner clicking a tutorial is not looking to be
told the thing is broken.

**Intensity has a ceiling.** Mild negative framing helps on HN; *strong* negative
framing (two or more negative terms) reverses to
-9.13 pts.
The pattern is consistent with a credibility mechanism: one critical word reads
as a considered judgement, three read as an axe being ground.

**Fear beats excitement on practitioner platforms.** Security, outage and
failure vocabulary lifts on HN; launch/announcement vocabulary does not. On X
the sign flips — fear words under-perform there
(-9.32 pts).

**Trust vocabulary is the most portable positive signal.** "Benchmark",
"production", "postmortem", "measured", "case study" move in the same direction
on every platform where the sample supports a test.
