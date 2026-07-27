# 09 — Improving the model with more data

Yes, more data helps — but not uniformly, and not without conditions. This is the
playbook, ordered by measured return on effort.

## What we already know works

Two changes have been measured on this corpus, and the contrast is instructive.

| Change | Effect |
|---|---|
| Medium: floor 1 clap → 100 claps, recollected | same-author accuracy **55.9% → 67.3%**, R² 0.001 → 0.049 |
| Pooling all platforms into one model | **worse than every per-platform model** (R² 0.033 vs up to 0.134) |

The first is the headline lesson: **sampling quality beat everything else we tried.** No
feature engineering came close. The second is the guard rail: adding data that dilutes
platform-specific structure actively hurts.

## 1. More rows per platform — the biggest lever

Current n and what it buys:

| Platform | n | Holdout R² | Verdict |
|---|---|---|---|
| Dev.to | 965 | 0.134 | generalises well |
| Reddit | 973 | 0.066 | generalises |
| Medium | 1,058 | 0.049 | generalises |
| Hacker News | 5,204 | 0.047 | generalises, stable |
| Substack | 762 | −0.044 | **overfits — needs more data** |
| X | 847 | −0.449 | **unstable — needs more data** |

Substack and X both fail to generalise, and both are the smallest samples. Note that
Hacker News at n=5,204 has a *lower* R² than Dev.to at n=965 — so this is not simply
"more rows, better model". Sample size buys **stability**, not accuracy. Below roughly
1,500 rows a single 15% holdout is so small (~130 posts) that R² swings wildly between
random splits; the X figure above moved from +0.030 to −0.449 after removing three rows.

**Target: 3,000–5,000 rows per platform.** That is where the holdout gets large enough for
the estimate to stop being noise.

**Do this first:** replace the single train/test split with k-fold cross-validation in
`pipeline/model.py`. It costs nothing, uses every row for both training and evaluation, and
would immediately tell you whether X's negative R² is real or an artefact. Right now you
cannot distinguish those two cases, which is a worse problem than the negative number itself.

## 2. Widen the topic range, not just the row count

Every platform here was collected through technical keywords. That is a hidden ceiling:
the model has never seen the AI-culture, career-narrative or personal-essay genres that
dominate Medium's viral tail.

The measured symptom: a Medium post with ~15,000 claps
(*"I'll Instantly Know A Writer Used ChatGPT When I See This"*) scores 46/100 and ranks 5th
of 7 against weaker alternatives. It is not badly modelled so much as **out of domain**.

Fix by collecting across genre, not just topic — add keyword sets for career, opinion,
industry commentary and personal narrative. Diversity of *kind* matters more than volume
of the same kind.

## 3. Time-slice the corpus

Platform norms drift. The corpus already shows headline length shifting year over year.
Two things follow:

- **Refit monthly.** Without it the product decays silently and you get no signal that it has.
- **Keep the out-of-time test in CI.** `pipeline/validate_product.py` trains on ≤2023 and
  tests on ≥2024. HN passes it (ρ +0.284, 60.1% pairwise on unseen years), which is the
  strongest evidence in the project that the rules are durable rather than a snapshot.

If a refit ever fails the out-of-time test, the rules have changed and the reports need
rewriting — not just the weights.

## 4. Collect the contrast tier (the biggest structural upgrade)

Every row above the floor is a success. The model therefore learns "what makes a good post
better", never "what separates good from mediocre" — which is closer to the question a
writer is actually asking.

The upgrade is a **matched control tier**: for each high performer, collect a post from the
same platform, same tag and same month that did *not* take off. Then model the contrast
directly. This is a genuinely different and better experiment than more of the same rows,
and it is the single change most likely to push R² past 0.2.

Cost: roughly doubles collection. Worth it once the basics are stable.

## 5. Outcome data — the only thing that proves the product works

Everything above improves *fit*. None of it proves that using the tool makes content perform
better. For that you need users' own results:

1. Log every scored title, the score, and which candidate they shipped.
2. Follow up 2–4 weeks later with actual performance.
3. Randomise: half the time show the true ranking, half the time a shuffled one.
4. Compare outcomes.

That experiment is the only basis on which a commercial claim can honestly be made. It
requires real traffic, so it cannot be simulated — but the logging should exist from day one,
because retrofitting it means discarding months of evidence.

## What will *not* help

- **More features.** The feature set already explains what it can; the ceiling is data, not
  vocabulary. The one feature hypothesis tested — the cataphoric pointer ("…when I see
  **this**") — turned out to have no signal (Dev.to −4.9, HN −2.3, Reddit +2.1).
- **A bigger model.** With R² near 0.05 and n under 1,000 per platform, a neural net would
  overfit harder and be less auditable. Ridge on countable features is the right complexity.
- **Pooling platforms.** Measured to be worse. Keep models per platform.
- **Lowering floors to gain rows.** That is precisely what broke Medium the first time.

## Priority order

1. k-fold cross-validation (free, and you cannot trust the small-platform numbers without it)
2. Substack and X to 3,000+ rows each (fixes the two platforms that fail to generalise)
3. Genre diversity in collection (fixes the out-of-domain misses)
4. Monthly refit with the out-of-time test as a gate
5. Matched control tier (the structural upgrade)
6. Outcome logging (the only route to a defensible commercial claim)
