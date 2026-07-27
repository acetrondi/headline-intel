# 07 — The human attention model

## What was fitted

Ridge regression, target = within-platform engagement percentile.
70% train / 15% validation (λ selection) / 15% holdout. Every number below is
from the holdout set the model never saw.

| Model | n train | n holdout | R² train | R² holdout | Spearman ρ holdout |
|---|---|---|---|---|---|
| Pooled (with platform controls) | 8337 | 1472 | 0.0411 | 0.0331 | 0.1796 |
| Pooled, 9 axes only | 8337 | 1472 | 0.0075 | 0.0020 | 0.0726 |
| Pooled, no platform controls | 8337 | 1472 | 0.0388 | 0.0314 | 0.1733 |
| Dev.to (full) | 820 | 145 | 0.1449 | 0.1337 | 0.3342 |
| Hacker News (full) | 4423 | 781 | 0.0803 | 0.0469 | 0.2026 |
| Medium (full) | 899 | 159 | 0.1032 | 0.0487 | 0.2562 |
| Reddit (full) | 827 | 146 | 0.1186 | 0.0664 | 0.2795 |
| Substack (full) | 647 | 115 | 0.1848 | -0.0440 | 0.1905 |
| X / Twitter (full) | 719 | 128 | 0.0537 | -0.4490 | 0.0923 |

## Read this before using the score

The headline number is **R² ≈ 0.033 on holdout** for the best
model. That means title features explain roughly
3% of the variance in relative engagement. The other
~97% is content quality, author audience, timing, topic
cycle, algorithmic distribution and luck.

Anyone selling you a title scorer that claims to predict virality is
overselling. What this model *can* do is rank candidates — the rank correlation
on holdout is **ρ = 0.180**, which is a real and usable
signal for choosing between five drafts of the same article.

The decile test is the practical proof. Holdout posts sorted into ten bins by
predicted score, showing the actual mean engagement percentile of each bin:

| Predicted decile | Actual mean engagement percentile |
|---|---|
| 1 | 0.368 |
| 2 | 0.462 |
| 3 | 0.516 |
| 4 | 0.458 |
| 5 | 0.498 |
| 6 | 0.459 |
| 7 | 0.524 |
| 8 | 0.567 |
| 9 | 0.550 |
| 10 | 0.579 |

Bottom decile 0.368 → top decile 0.579. Monotonic enough to be
useful for A/B selection, nowhere near precise enough to be a forecast.

## The nine axes

The brief asks for a weighted scoring system over nine named axes. Fitted on the
pooled data with platform controls:

| Axis | Standardised weight | Share of |weight| | Direction |
|---|---|---|---|
| Curiosity | -0.0155 | 0.222 | negative |
| Specificity | -0.0141 | 0.202 | negative |
| Clarity | -0.0117 | 0.168 | negative |
| Promise of value | +0.0089 | 0.128 | positive |
| Authority | +0.0071 | 0.102 | positive |
| Novelty | +0.0056 | 0.081 | positive |
| Emotional impact | -0.0051 | 0.073 | negative |
| Information density | -0.0009 | 0.012 | negative |
| Readability | -0.0007 | 0.011 | negative |

Two of these signs will look wrong at first glance and are worth explaining.

**Specificity carries a negative pooled weight.** This is a composition effect,
not evidence that vagueness wins. The pooled sample is dominated by Hacker News,
where `has_colon`, `acronym_count` and `all_caps_words` — components that feed
the specificity composite — are strongly negative because they mark
press-release and vendor-blog titles. Where specificity is measured cleanly
(`big_number_specific` alone) it lifts engagement
+3.92 points pooled and
+4.07 on HN.
**Use per-platform weights, not pooled weights, in production.**

**Curiosity carries a negative pooled weight.** On technical platforms the
curiosity-gap construction ("the surprising reason…", "what nobody tells you
about…") reads as withholding. Curiosity is only positive on Substack
(+4.50 pts) and X
(+4.47 pts), where the reader
has already opted into a relationship with the writer.

## The strongest individual features

| Feature | Standardised weight |
|---|---|
| has_colon | -0.03296 |
| title_case_ratio | -0.03130 |
| has_question | -0.01701 |
| has_dash | -0.01676 |
| avg_word_len | +0.01342 |
| char_count | -0.01322 |
| listicle_size | +0.01267 |
| all_caps_words | +0.01221 |
| curiosity_markers | -0.01038 |
| authority_markers | +0.00904 |
| has_year | -0.00878 |
| urgency_markers | +0.00821 |
| acronym_count | -0.00814 |
| has_money | -0.00813 |
| readability | +0.00674 |
| has_big_number | +0.00665 |
| word_count | +0.00642 |
| negative_words | +0.00636 |
| is_why | +0.00634 |
| beginner_markers | +0.00618 |
| trust_words | -0.00612 |
| fear_words | +0.00492 |

## Which model to actually use

Pooling is the wrong default here, and the data says so loudly. The pooled model
scores **R² 0.033 / ρ 0.180** on holdout, while several
per-platform models beat it outright:

| Platform | n | R² holdout | ρ holdout | beats pooled? |
|---|---|---|---|---|
| Dev.to | 965 | 0.134 | 0.334 | yes |
| Hacker News | 5204 | 0.047 | 0.203 | yes |
| Medium | 1058 | 0.049 | 0.256 | yes |
| Reddit | 973 | 0.066 | 0.280 | yes |
| Substack | 762 | -0.044 | 0.191 | no |
| X / Twitter | 847 | -0.449 | 0.092 | no |

The reason is the central finding of this study: **the platform rules invert.**
A colon is worth −14 points on Hacker News and a question mark is worth −20 on
Dev.to; a pooled model has to average those against platforms where the same
features are neutral or positive, and the averaging destroys the signal. More
data made the pooled model *worse* and the per-platform models *better*, which is
exactly what you would expect if the effects are real and platform-specific.

The scorer therefore selects per platform:

| Platform | Model used |
|---|---|
| Dev.to | platform |
| Hacker News | platform |
| Medium | platform |
| Reddit | platform |
| Substack | pooled |
| X / Twitter | pooled |

Substack still fails to generalise (negative holdout R²) and falls back to the
pooled model, with its rank correlation used for ordering only. It needs roughly
3–5× more publications to fit cleanly — a collection problem, not a modelling one.
