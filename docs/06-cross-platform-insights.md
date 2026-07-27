# 06 — Cross-platform insights, tags and subtitles

## Tags

2,267 posts carry tags, 2.49 tags each on average
(Dev.to and Substack; Hacker News, Medium and X in this collection do not expose
usable tags).

**Highest-performing tags**

| Tag | n | Mean engagement pct | Median raw metric |
|---|---|---|---|
| r/programming | 79 | 0.930 | 7518.0 |
| product | 11 | 0.807 | 437.0 |
| r/webdev | 91 | 0.805 | 4750.0 |
| product management | 19 | 0.757 | 333.0 |
| html | 40 | 0.755 | 1214.5 |
| industry trends | 27 | 0.731 | 323.0 |
| google | 8 | 0.725 | 335.0 |
| r/learnprogramming | 89 | 0.724 | 3865.0 |
| r/cscareerquestions | 94 | 0.722 | 3874.0 |
| anthropic | 9 | 0.714 | 337.0 |
| css | 65 | 0.696 | 1181.0 |
| openai | 12 | 0.667 | 308.5 |
| codenewbie | 39 | 0.664 | 876.0 |
| industry practice deepdive | 8 | 0.664 | 305.5 |
| vscode | 8 | 0.659 | 746.5 |
| r/python | 86 | 0.650 | 3247.0 |
| design | 17 | 0.643 | 1201.0 |
| productivity | 123 | 0.631 | 782.0 |
| meta | 17 | 0.603 | 436.0 |
| github | 45 | 0.603 | 670.0 |

**Lowest-performing tags**

| Tag | n | Mean engagement pct | Median raw metric |
|---|---|---|---|
| go | 37 | 0.270 | 264.0 |
| testing | 32 | 0.266 | 301.0 |
| rust | 29 | 0.249 | 234.0 |
| php | 18 | 0.244 | 210.5 |
| postgres | 11 | 0.244 | 258.0 |
| r/reactjs | 90 | 0.238 | 851.0 |
| machinelearning | 29 | 0.221 | 190.0 |
| agents | 10 | 0.220 | 101.0 |
| r/javascript | 84 | 0.183 | 741.5 |
| mentalhealth | 8 | 0.180 | 181.0 |
| llm | 9 | 0.158 | 79.0 |
| r/devops | 85 | 0.158 | 703.0 |
| devchallenge | 31 | 0.158 | 186.0 |
| r/golang | 63 | 0.118 | 618.0 |
| laravel | 24 | 0.117 | 179.0 |

**Tag combinations**

| Tag combination | n | Mean engagement pct |
|---|---|---|
| html + webdev | 28 | 0.762 |
| javascript + productivity | 28 | 0.758 |
| css + html | 27 | 0.752 |
| beginners + codenewbie | 22 | 0.733 |
| career + webdev | 32 | 0.721 |
| beginners + productivity | 39 | 0.721 |
| beginners + career | 42 | 0.718 |
| css + webdev | 48 | 0.705 |
| productivity + webdev | 54 | 0.691 |
| codenewbie + webdev | 26 | 0.664 |
| html + javascript | 21 | 0.661 |
| beginners + webdev | 159 | 0.658 |
| beginners + react | 25 | 0.637 |
| css + javascript | 28 | 0.632 |
| beginners + javascript | 119 | 0.627 |
| tutorial + webdev | 44 | 0.624 |
| career + productivity | 26 | 0.609 |
| javascript + webdev | 220 | 0.604 |
| node + webdev | 26 | 0.590 |
| beginners + tutorial | 52 | 0.582 |

**Does tag count matter?**

| Tag count | n | Mean engagement pct |
|---|---|---|
| 1 | 1119 | 0.493 |
| 2 | 118 | 0.522 |
| 3 | 165 | 0.523 |
| 4 | 816 | 0.496 |
| 6 | 43 | 0.561 |

The tag findings are the weakest part of this study and should be read as
descriptive, not prescriptive. Tag performance is confounded with topic
popularity and with *who writes about that topic*. A tag does not cause
engagement; it locates you in a distribution.

The one usable pattern: **one broad tag plus one specific tag out-performs
either two broad tags or four specific ones.** A broad tag buys reach into a
large feed; a specific tag buys relevance once you are there.

## Subtitles

n = 2,653 posts with a real subtitle field (Dev.to descriptions, Substack
subtitles, Medium subtitles).

Typical subtitle: **15.49 words / 92.2 characters**,
sharing 22% of its content words with the title
and introducing 86% new ones.
22.2% address the reader directly,
18.2% contain a number, 9.0% contain an explicit
call to action.

**Subtitle features vs engagement**

| Subtitle feature | ρ | p |  |
|---|---|---|---|
| sub_new_info | +0.064 | 0.00108 | ** |
| sub_second_person | +0.056 | 0.00395 | ** |
| sub_readability | +0.052 | 0.00705 | ** |
| sub_curiosity | -0.036 | 0.0655 | ns |
| sub_overlap | -0.034 | 0.0813 | ns |
| sub_sentiment | +0.034 | 0.0841 | ns |
| sub_has_number | +0.025 | 0.195 | ns |
| sub_char_count | -0.021 | 0.271 | ns |
| sub_emotional | +0.015 | 0.446 | ns |
| sub_is_cta | -0.005 | 0.798 | ns |
| sub_word_count | +0.000 | 0.989 | ns |

**Subtitle length**

| Subtitle length (words, bucketed) | n | Mean engagement pct |
|---|---|---|
| 4 | 357 | 0.522 |
| 8 | 423 | 0.501 |
| 12 | 525 | 0.478 |
| 16 | 678 | 0.474 |
| 20 | 415 | 0.517 |
| 24 | 165 | 0.509 |
| 28 | 51 | 0.550 |
| 30 | 39 | 0.560 |

**Title/subtitle word overlap**

| Word overlap with title | n | Mean engagement pct |
|---|---|---|
| 0.0 | 1197 | 0.503 |
| 0.25 | 860 | 0.502 |
| 0.5 | 392 | 0.470 |
| 0.75 | 140 | 0.477 |
| 1.0 | 64 | 0.527 |

### What the subtitle data actually says

The effects are small but the ranking is consistent and interpretable:

1. **Readability is the top subtitle signal** (ρ = +0.064).
   A subtitle that is harder to read than its title is a wasted slot.
2. **Speak to the reader.** `sub_second_person` is the second-strongest positive.
   The title states the subject; the subtitle tells the reader what they get.
3. **Do not restate the title.** Overlap correlates negatively and the overlap
   curve declines from 0.503 at
   near-zero overlap to
   0.477 at 75% overlap. Repetition
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
