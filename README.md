# Headline Intelligence

[![verify](https://github.com/acetrondi/headline-intel/actions/workflows/verify.yml/badge.svg)](https://github.com/acetrondi/headline-intel/actions/workflows/verify.yml)
[![code: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-green.svg)](LICENSE-DATA)

By [itsarises.com](https://itsarises.com) · [connectingdots.live](https://connectingdots.live)

What actually makes a technical headline work — measured on **9,809 high-performing
posts** across Hacker News, Reddit, Dev.to, Medium, Substack and X, then turned into a
scorer that runs entirely in your browser.

**[Live demo →](https://headlines.connectingdots.live/)**

No build step. No dependencies. No network calls. Open `index.html` and it works.

---

## The finding

There is no universal headline formula. The rules invert across platforms, and the
inversions are large — lift is in engagement percentile points:

| Tactic | HN | Reddit | Dev.to | Medium | Substack | X |
|---|---|---|---|---|---|---|
| Question headline | −13.6 | −2.8 | **−19.8** | +2.4 | +4.7 | +1.6 |
| Opens with a number | +2.1 | +2.6 | **+15.7** | **+13.1** | −3.6 | −4.5 |
| ≥13 words | −2.4 | **+9.4** | −6.2 | −0.6 | +1.4 | +2.7 |
| Colon | **−14.2** | −1.6 | −11.4 | −10.9 | +1.1 | −7.4 |
| Money figure | +4.2 | +2.7 | **−28.1** | +2.0 | −0.9 | **−22.0** |
| Deep technical vocabulary | −6.2 | −6.8 | +1.4 | +0.2 | −8.9 | **+13.2** |

Four things held direction on every platform:

1. **One concrete number with a unit** — "cut p99 from 900 ms to 40 ms", not "much faster",
   and not a listicle count.
2. **Evidence of first-hand work** — "we measured", "I built", "in production".
3. **Ornamentation is a tax** — ALL-CAPS, stacked acronyms, adjective stacking.
4. **Never restate the title in the subtitle.**

## Honest limits

The best per-platform model explains ~13% of variance in relative engagement; most explain
3–7%. **Headline text is a small lever.** Use this to rank your own drafts, not to predict
reach — the body, the timing and the author's audience are much larger factors.

Two more caveats: only high-performing posts were collected, so every effect size is a
*lower bound*; and five of six platforms don't expose view counts, so "engagement" means
votes, claps, reactions and likes.

| Platform | n | Metric | Floor | Median | Max | Holdout ρ |
|---|---|---|---|---|---|---|
| Hacker News | 5,204 | points | 498 | 961 | 6,015 | 0.20 |
| Medium | 1,058 | claps | 100 | 222 | 69,950 | 0.26 |
| Reddit | 973 | upvotes | 501 | 2,375 | 45,091 | 0.28 |
| Dev.to | 965 | reactions | 100 | 533 | 4,737 | **0.33** |
| X / Twitter | 847 | likes | 705 | 4,655 | 354,261 | pooled |
| Substack | 762 | likes | 50 | 196 | 3,488 | pooled |

Platforms deliberately excluded: Hashnode (GraphQL is POST-only), LinkedIn Articles, Quora
and Indie Hackers — no obtainable public engagement metric. Title-only rows would
contribute nothing to a model whose target *is* engagement.

## Repository layout

```
index.html            the app — hand-written, edit freely
assets/
  app.css             design tokens + styles
  app.js              feature extraction, scoring, UI (no dependencies)
  data.js             GENERATED — model + rules + lexicons
pipeline/             the Python that produces data/
data/                 model.json, analysis.json, validation.json
docs/                 reports 01–08, generated from the JSON
```

Only `assets/data.js` is generated. The HTML, CSS and JS are normal source files.

## Hosting

Live at **[headlines.connectingdots.live](https://headlines.connectingdots.live/)**.

### GitHub Pages

1. Push the repo.
2. Settings → Pages → Source: **Deploy from a branch**, branch `main`, folder `/ (root)`.
3. Settings → Pages → Custom domain: `headlines.connectingdots.live` → Save.
4. Tick **Enforce HTTPS** once the certificate is issued (can take ~15 minutes).

`.nojekyll` is included so `assets/` is served as-is, and `CNAME` binds the custom domain.

### DNS

One record at whoever hosts `connectingdots.live` DNS:

| Type | Name | Value | TTL |
|---|---|---|---|
| CNAME | `headlines` | `acetrondi.github.io.` | 3600 |

The value is the **user** subdomain, not the repo — no `/headline-intel` path. Propagation is
usually minutes but can take up to 24 hours.

This is a static site, so it also works on Netlify, Cloudflare Pages, S3, or straight from
disk via `file://`.

## Re-running the pipeline

```bash
pip install -r requirements.txt

python3 pipeline/harvest.py          # parse raw API payloads  -> data/corpus.jsonl
python3 pipeline/normalize.py        # clean, floor, featurize -> data/dataset.jsonl
python3 pipeline/analyze.py          # stats, NLP, sentiment   -> data/analysis.json
python3 pipeline/model.py            # fit the models          -> data/model.json
python3 pipeline/report.py           # write docs/
python3 pipeline/build_data.py       # regenerate assets/data.js
python3 pipeline/verify.py           # 40+ checks; non-zero exit on failure
python3 pipeline/validate_product.py # pairwise + out-of-time validation
```

Score a headline from the shell:

```bash
python3 pipeline/score.py devto "10 Postgres indexing mistakes I made"
```

### Adding your own data

`pipeline/harvest.py` reads raw API payloads from `raw/*.txt` (override with `HI_RAW_DIR`).
Each file is `<url>\n\n<response body>`. Add an adapter function for your source, register
it in the dispatcher, then re-run the pipeline. Engagement floors live in one place —
`FLOORS` at the top of `pipeline/normalize.py`.

## Why the floors matter

Medium originally had a floor of 1 clap and a median of 50, so the model learned what makes
a mediocre post slightly less mediocre. Raising the floor to 100 claps and recollecting moved
Medium's same-author accuracy from **55.9% → 67.3%** and its holdout R² from 0.001 → 0.049.
Same features, same code — only the sampling changed.

The opposite failure is just as real: a corpus where *everything* is viral has no variance
left to learn from. Floor high, then keep the full range above it.

## Verification

`pipeline/verify.py` runs 40+ checks: schema and range integrity, zero duplicate titles,
percentile monotonicity within each platform, independent recomputation of reported lifts and
correlations, holdout decile monotonicity, and **exact Python↔JavaScript parity on all 45
features**. That last one is not ceremonial — it caught a real bug where emoji count as one
character in Python and two in JavaScript, silently desyncing the browser from the model.

CI runs it on every push.

## Licensing

Two licences, deliberately:

| What | Licence | What it means |
|---|---|---|
| Code (`pipeline/`, `assets/`, `index.html`, `tests/`) | **MIT** — `LICENSE` | Use it, fork it, sell it. Keep the copyright notice in source copies. No credit required in a deployed app. |
| Research (`data/`, `docs/`) | **CC BY 4.0** — `LICENSE-DATA` | Reuse the weights, statistics and reports commercially — but **credit the source**. |

MIT on the code maximises adoption. CC BY on the research protects the part that actually
took the work, because attribution is the only thing worth enforcing here.

**Not covered by either:** the underlying corpus of collected titles. It is not in this
repository and is not licensed for redistribution — those titles belong to their authors.
Analysing public posts and republishing them are different things. If you re-collect, check
each platform's terms yourself.

If you reuse the research, credit it like this:

> Headline Intelligence — [Kailash Rathod](https://itsarises.com) /
> [Connecting Dots](https://connectingdots.live). Licensed CC BY 4.0.

## Credits

Built by **[itsarises.com](https://itsarises.com)** and
**[connectingdots.live](https://connectingdots.live)** — an evidence-based resource for SEO,
AEO and GEO.

Design system shared with Connecting Dots: OKLCH tokens, Raleway + Geist Mono, one accent per
view, evidence colours reserved for evidence UI.
