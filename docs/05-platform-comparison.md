# 05 — Platform-by-platform comparison

This is the operational report. The rules below contradict each other across
platforms, and that is the point: a headline optimised for Dev.to will
under-perform on Hacker News and vice versa.


### Dev.to  — n=965, metric = reactions

Median headline: **8 words / 47 characters**.
Mean Flesch reading ease 55.6.
39.5% contain a number, 18.9% are listicles,
4.0% are questions, 14.0% use a colon,
19.1% address the reader as "you",
14.0% are written in first person.

**What lifts engagement here**

| Condition | n | Lift (pts) |
|---|---|---|
| starts_with_number | 182 | +14.04 |
| ai_tell_phrasing | 25 | +7.59 |
| imperative_open | 31 | +7.16 |
| contains_any_number | 381 | +6.81 |
| short_title_<=7w | 440 | +6.21 |
| superlative | 80 | +5.07 |
| addresses_you | 184 | +5.06 |
| positive_framing | 215 | +4.81 |

**What costs engagement here**

| Condition | n | Lift (pts) |
|---|---|---|
| long_title_>=13w | 82 | -6.51 |
| first_person_story | 135 | -8.01 |
| negative_framing | 76 | -8.31 |
| urgency_marker | 78 | -9.89 |
| has_colon | 135 | -10.88 |
| curiosity_marker | 37 | -11.90 |
| is_question | 39 | -20.11 |
| money_figure | 20 | -31.15 |

**Strongest rank correlations**

| Feature | ρ |  |
|---|---|---|
| listicle_size | +0.199 | *** |
| is_listicle | +0.190 | *** |
| starts_with_number | +0.190 | *** |
| promise_of_value | +0.158 | *** |
| has_money | -0.153 | *** |
| has_question | -0.137 | *** |
| curiosity_gap | -0.133 | *** |
| has_colon | -0.131 | *** |

### Hacker News  — n=5,204, metric = points

Median headline: **8 words / 46 characters**.
Mean Flesch reading ease 56.0.
20.0% contain a number, 0.2% are listicles,
6.7% are questions, 22.0% use a colon,
7.5% address the reader as "you",
16.0% are written in first person.

**What lifts engagement here**

| Condition | n | Lift (pts) |
|---|---|---|
| authority_marker | 1008 | +7.05 |
| fear_word | 141 | +6.25 |
| money_figure | 113 | +4.18 |
| big_number_specific | 188 | +4.07 |
| negative_framing | 780 | +3.51 |
| short_title_<=7w | 2487 | +3.24 |
| first_person_story | 834 | +2.78 |
| two_plus_power_words | 18 | +2.37 |

**What costs engagement here**

| Condition | n | Lift (pts) |
|---|---|---|
| curiosity_marker | 178 | -5.14 |
| addresses_you | 388 | -5.57 |
| deep_technical | 108 | -6.24 |
| mentions_year | 199 | -8.54 |
| strong_negative_framing | 53 | -9.13 |
| ai_tell_phrasing | 16 | -13.49 |
| is_question | 350 | -13.58 |
| has_colon | 1144 | -14.23 |

**Strongest rank correlations**

| Feature | ρ |  |
|---|---|---|
| has_colon | -0.204 | *** |
| all_caps_words | -0.155 | *** |
| acronym_count | -0.135 | *** |
| specificity | -0.118 | *** |
| has_question | -0.118 | *** |
| curiosity_gap | -0.108 | *** |
| authority_markers | +0.096 | *** |
| authority | +0.095 | *** |

### Medium  — n=1,058, metric = claps

Median headline: **10 words / 60 characters**.
Mean Flesch reading ease 49.3.
38.5% contain a number, 14.6% are listicles,
5.8% are questions, 23.3% use a colon,
14.4% address the reader as "you",
16.7% are written in first person.

**What lifts engagement here**

| Condition | n | Lift (pts) |
|---|---|---|
| short_title_<=7w | 247 | +10.76 |
| starts_with_why | 27 | +6.35 |
| starts_with_how | 52 | +3.81 |
| addresses_you | 152 | +2.94 |
| strong_negative_framing | 16 | +2.94 |
| beginner_framing | 113 | +2.27 |
| starts_with_number | 154 | +2.26 |
| negative_framing | 158 | +1.11 |

**What costs engagement here**

| Condition | n | Lift (pts) |
|---|---|---|
| deep_technical | 52 | -6.09 |
| two_plus_power_words | 23 | -7.08 |
| curiosity_marker | 125 | -7.57 |
| comparison_vs | 35 | -8.47 |
| fear_word | 17 | -8.50 |
| ai_tell_phrasing | 24 | -8.55 |
| authority_marker | 174 | -9.10 |
| surprise_word | 25 | -10.98 |

**Strongest rank correlations**

| Feature | ρ |  |
|---|---|---|
| char_count | -0.175 | *** |
| word_count | -0.169 | *** |
| authority | -0.134 | *** |
| trust_words | -0.128 | *** |
| authority_markers | -0.115 | *** |
| has_dash | -0.114 | *** |
| title_case_ratio | -0.092 | ** |
| info_density | -0.091 | ** |

### Reddit  — n=973, metric = upvotes

Median headline: **11 words / 64 characters**.
Mean Flesch reading ease 60.4.
25.4% contain a number, 0.4% are listicles,
7.4% are questions, 8.8% use a colon,
11.3% address the reader as "you",
40.3% are written in first person.

**What lifts engagement here**

| Condition | n | Lift (pts) |
|---|---|---|
| starts_with_how | 18 | +12.43 |
| big_number_specific | 39 | +11.95 |
| long_title_>=13w | 409 | +8.89 |
| strong_negative_framing | 27 | +8.30 |
| superlative | 76 | +7.41 |
| negative_framing | 154 | +5.16 |
| urgency_marker | 151 | +4.45 |
| beginner_framing | 92 | +4.36 |

**What costs engagement here**

| Condition | n | Lift (pts) |
|---|---|---|
| first_person_story | 392 | -2.05 |
| positive_framing | 124 | -2.06 |
| is_question | 72 | -2.07 |
| parenthetical | 179 | -2.93 |
| medium_title_8_12w | 315 | -4.92 |
| mentions_year | 28 | -5.19 |
| short_title_<=7w | 249 | -5.72 |
| deep_technical | 32 | -6.19 |

**Strongest rank correlations**

| Feature | ρ |  |
|---|---|---|
| word_count | +0.153 | *** |
| char_count | +0.136 | *** |
| clarity | -0.120 | *** |
| has_money | +0.103 | ** |
| specificity | +0.094 | ** |
| title_case_ratio | -0.089 | ** |
| excitement_words | -0.084 | ** |
| has_big_number | +0.081 | * |

### Substack  — n=762, metric = likes

Median headline: **7 words / 45 characters**.
Mean Flesch reading ease 55.5.
28.7% contain a number, 3.9% are listicles,
7.5% are questions, 25.2% use a colon,
6.8% address the reader as "you",
6.8% are written in first person.

**What lifts engagement here**

| Condition | n | Lift (pts) |
|---|---|---|
| ai_tell_phrasing | 17 | +15.51 |
| beginner_framing | 63 | +10.69 |
| fear_word | 19 | +9.16 |
| urgency_marker | 83 | +8.44 |
| has_colon | 192 | +4.95 |
| parenthetical | 32 | +4.66 |
| long_title_>=13w | 63 | +4.54 |
| curiosity_marker | 52 | +4.50 |

**What costs engagement here**

| Condition | n | Lift (pts) |
|---|---|---|
| short_title_<=7w | 391 | -1.83 |
| is_question | 57 | -2.11 |
| deep_technical | 42 | -4.90 |
| starts_with_how | 111 | -5.53 |
| has_subtitle | 645 | -6.83 |
| authority_marker | 160 | -7.25 |
| first_person_story | 52 | -7.30 |
| starts_with_number | 30 | -9.17 |

**Strongest rank correlations**

| Feature | ρ |  |
|---|---|---|
| title_case_ratio | -0.243 | *** |
| readability_norm | +0.141 | *** |
| readability | +0.139 | *** |
| novelty | +0.111 | ** |
| avg_word_len | -0.107 | ** |
| beginner_markers | +0.102 | ** |
| authority_markers | -0.102 | ** |
| long_word_ratio | -0.095 | ** |

### X / Twitter  — n=847, metric = likes

Median headline: **13 words / 74 characters**.
Mean Flesch reading ease 54.6.
27.3% contain a number, 1.4% are listicles,
5.5% are questions, 15.1% use a colon,
10.6% address the reader as "you",
29.6% are written in first person.

**What lifts engagement here**

| Condition | n | Lift (pts) |
|---|---|---|
| deep_technical | 16 | +13.02 |
| urgency_marker | 199 | +5.90 |
| comparison_vs | 29 | +5.06 |
| curiosity_marker | 49 | +4.47 |
| parenthetical | 48 | +2.90 |
| short_title_<=7w | 179 | +1.20 |
| first_person_story | 251 | +0.85 |
| negative_framing | 164 | +0.85 |

**What costs engagement here**

| Condition | n | Lift (pts) |
|---|---|---|
| beginner_framing | 62 | -2.53 |
| power_word_present | 144 | -3.05 |
| contains_any_number | 231 | -4.47 |
| superlative | 69 | -6.14 |
| has_colon | 128 | -7.64 |
| fear_word | 19 | -9.32 |
| strong_negative_framing | 27 | -9.63 |
| money_figure | 28 | -22.22 |

**Strongest rank correlations**

| Feature | ρ |  |
|---|---|---|
| has_money | -0.138 | *** |
| has_colon | -0.095 | ** |
| urgency_markers | +0.083 | * |
| promise_of_value | -0.083 | * |
| is_listicle | -0.082 | * |
| starts_with_number | -0.082 | * |
| listicle_size | -0.082 | * |
| specificity | -0.071 | * |


## The contradictions, side by side

| Tactic | Hacker News | Reddit | Dev.to | Medium | Substack | X / Twitter |
|---|---|---|---|---|---|---|
| Colon in title | -14.2 | -1.6 | -10.9 | -3.7 | +5.0 | -7.6 |
| Question headline | -13.6 | -2.1 | -20.1 | +0.6 | -2.1 | -0.0 |
| Starts with a number | n/a | n/a | +14.0 | +2.3 | -9.2 | n/a |
| Short title (<=7 words) | +3.2 | -5.7 | +6.2 | +10.8 | -1.8 | +1.2 |
| Long title (>=13 words) | -2.5 | +8.9 | -6.5 | -5.7 | +4.5 | -0.7 |
| Negative framing | +3.5 | +5.2 | -8.3 | +1.1 | +2.1 | +0.8 |
| Authority markers | +7.0 | +3.6 | +0.9 | -9.1 | -7.2 | -2.1 |
| Specific number + unit | +4.1 | +11.9 | n/a | -1.6 | n/a | -1.3 |
| Money figure | +4.2 | n/a | -31.1 | n/a | n/a | -22.2 |
| Beginner framing | -3.8 | +4.4 | +0.1 | +2.3 | +10.7 | -2.5 |
| Deep technical vocabulary | -6.2 | -6.2 | -2.0 | -6.1 | -4.9 | +13.0 |
| Curiosity gap | -5.1 | +1.4 | -11.9 | -7.6 | +4.5 | +4.5 |

*(lift in engagement percentile points; `n/a` = too few cases on that platform to test)*

The starkest contradiction in the whole study is title length. Reddit rewards
long titles (>=13 words: +8.9 points) and punishes short ones (-5.7).
Dev.to does the exact opposite (<=7 words: +6.2, >=13 words: -6.5).
A Reddit title carries the whole argument because the link preview does not;
a Dev.to title sits above a card with a subtitle, a cover image and tags doing
the rest of the work. **The surrounding interface, not the reader's psychology,
sets the optimal length.**

The single clearest generalisation: **audience expertise inverts the rules.**
Hacker News and X-technical reward evidence and understatement; Dev.to and
Substack's newsletter audience reward accessibility and explicit promises of
value. Medium sits between the two and is the only platform where a
conventionally "optimised" headline — number, superlative, year — reliably wins.
