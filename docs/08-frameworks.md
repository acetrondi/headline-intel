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

- **Hacker News** — favour: `authority_marker` (+7.0), `fear_word` (+6.2), `money_figure` (+4.2), `big_number_specific` (+4.1), `negative_framing` (+3.5), `short_title_<=7w` (+3.2). Avoid: `has_colon` (-14.2), `is_question` (-13.6), `ai_tell_phrasing` (-13.5), `strong_negative_framing` (-9.1), `mentions_year` (-8.5).
  Write it as if the artefact speaks for itself. No colon, no question mark, no
  "Ultimate".
- **Dev.to** — favour: `starts_with_number` (+14.0), `ai_tell_phrasing` (+7.6), `imperative_open` (+7.2), `contains_any_number` (+6.8), `short_title_<=7w` (+6.2), `superlative` (+5.1). Avoid: `money_figure` (-31.1), `is_question` (-20.1), `curiosity_marker` (-11.9), `has_colon` (-10.9), `urgency_marker` (-9.9).
  Short, positive, numbered, beginner-legible. Questions are the single worst
  move on this platform.
- **Medium** — favour: `short_title_<=7w` (+10.8), `starts_with_why` (+6.3), `starts_with_how` (+3.8), `addresses_you` (+2.9), `strong_negative_framing` (+2.9), `beginner_framing` (+2.3). Avoid: `surprise_word` (-11.0), `authority_marker` (-9.1), `ai_tell_phrasing` (-8.6), `fear_word` (-8.5), `comparison_vs` (-8.5).
  The one platform where conventional headline optimisation works.
- **Substack** — favour: `ai_tell_phrasing` (+15.5), `beginner_framing` (+10.7), `fear_word` (+9.2), `urgency_marker` (+8.4), `has_colon` (+5.0), `parenthetical` (+4.7). Avoid: `starts_with_number` (-9.2), `first_person_story` (-7.3), `authority_marker` (-7.2), `has_subtitle` (-6.8), `starts_with_how` (-5.5).
  Curiosity is licensed here because the reader already subscribed.
- **X / Twitter** — favour: `deep_technical` (+13.0), `urgency_marker` (+5.9), `comparison_vs` (+5.1), `curiosity_marker` (+4.5), `parenthetical` (+2.9), `short_title_<=7w` (+1.2). Avoid: `money_figure` (-22.2), `strong_negative_framing` (-9.6), `fear_word` (-9.3), `has_colon` (-7.6), `superlative` (-6.1).
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
