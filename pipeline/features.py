"""Linguistic / psychological feature extraction for headlines and subtitles.

Every feature here is deterministic and cheap so the exact same logic can be
re-implemented in JavaScript for the web app (see app/index.html) and audited by
hand. No model weights live in this file - only measurement.
"""
import re
import math
from collections import Counter

# ----------------------------------------------------------------------------
# lexicons
# ----------------------------------------------------------------------------

POWER_WORDS = {
    "amazing", "astonishing", "authentic", "backed", "battle", "best", "bold", "breakthrough",
    "brilliant", "brutal", "case", "clever", "complete", "confessions", "crazy", "critical",
    "crucial", "danger", "dead", "deadly", "definitive", "devastating", "dirty", "disaster",
    "effective", "effortless", "elite", "epic", "essential", "exact", "excellent", "exclusive",
    "expensive", "expert", "explosive", "extraordinary", "fail", "failed", "fascinating",
    "fast", "fatal", "fearless", "forbidden", "free", "genius", "gigantic", "greatest",
    "guaranteed", "hack", "hidden", "honest", "horrible", "huge", "hurt", "illegal",
    "impossible", "improved", "incredible", "insane", "instant", "invaluable", "killer",
    "landmark", "legendary", "lethal", "lies", "little-known", "lost", "magic", "massive",
    "mistake", "mistakes", "myth", "myths", "nasty", "obsolete", "outrageous", "overlooked",
    "painful", "perfect", "pitfall", "pitfalls", "popular", "powerful", "practical", "priceless",
    "productive", "proven", "quick", "radical", "rare", "real", "remarkable", "revealed",
    "revolutionary", "ridiculous", "ruthless", "scary", "secret", "secrets", "shocking",
    "silly", "simple", "smart", "stop", "strange", "stunning", "stupid", "surprising",
    "terrible", "terrifying", "tested", "toxic", "tragic", "trap", "tricks", "ultimate",
    "unbelievable", "uncommon", "underrated", "unexpected", "unusual", "urgent", "useless",
    "valuable", "vital", "warning", "weird", "worst", "wrong",
}

CURIOSITY_MARKERS = {
    "actually", "apparently", "behind", "beneath", "hidden", "nobody", "no one", "nothing",
    "reason", "really", "secret", "surprising", "truth", "turns out", "unexpected", "untold",
    "what happens", "what happened", "why", "you didn't", "you don't", "you never",
    "what nobody", "what i learned", "what i wish", "the real", "the truth",
}

AUTHORITY_MARKERS = {
    "according", "amazon", "apple", "benchmark", "case study", "cto", "data", "engineer",
    "engineers", "experiment", "facebook", "founder", "google", "how we", "i built",
    "i spent", "i wrote", "lessons", "meta", "microsoft", "netflix", "nvidia", "openai",
    "paper", "postmortem", "production", "research", "researchers", "scale", "senior",
    "shipped", "stripe", "study", "uber", "we built", "we learned", "we migrated", "years",
}

URGENCY_MARKERS = {
    "2024", "2025", "2026", "already", "before", "breaking", "deadline", "deprecated",
    "end of", "finally", "immediately", "just", "last chance", "new", "now", "recently",
    "right now", "shutting down", "soon", "stop", "today", "tomorrow", "update", "urgent",
}

NEGATIVE_WORDS = {
    "avoid", "awful", "bad", "ban", "banned", "broke", "broken", "bug", "bugs", "can't",
    "cannot", "crash", "crisis", "dangerous", "dead", "death", "decline", "deprecated",
    "die", "died", "disaster", "doesn't", "don't", "down", "fail", "failed", "failing",
    "failure", "fake", "fatal", "flaw", "forget", "fraud", "hard", "harmful", "hate",
    "horrible", "hurt", "illegal", "impossible", "insecure", "kill", "killed", "killing",
    "lie", "lies", "lost", "mistake", "mistakes", "never", "no", "not", "outage", "pain",
    "painful", "poor", "problem", "problems", "quit", "regret", "risk", "ruin", "sad",
    "scam", "shut", "slow", "stop", "struggle", "stuck", "stupid", "terrible", "toxic",
    "trap", "ugly", "useless", "vulnerability", "warning", "waste", "worse", "worst", "wrong",
}

POSITIVE_WORDS = {
    "achieve", "amazing", "awesome", "beautiful", "benefit", "best", "better", "boost",
    "brilliant", "clean", "clear", "confidence", "delight", "easy", "efficient", "elegant",
    "excellent", "fast", "faster", "free", "fun", "gain", "good", "great", "growth", "happy",
    "help", "helpful", "improve", "improved", "increase", "joy", "love", "modern", "nice",
    "perfect", "powerful", "practical", "productive", "reliable", "robust", "safe", "save",
    "simple", "smart", "smooth", "solid", "solve", "solved", "strong", "success", "successful",
    "support", "win", "winning", "wonderful",
}

TRUST_WORDS = {"proven", "tested", "benchmark", "data", "study", "research", "official",
               "documented", "verified", "reliable", "production", "postmortem", "audit",
               "measured", "real-world", "case study", "evidence"}
FEAR_WORDS = {"warning", "danger", "dangerous", "risk", "vulnerability", "exploit", "breach",
              "attack", "hacked", "leak", "outage", "crash", "fatal", "deadly", "crisis",
              "threat", "scary", "terrifying", "afraid", "fear", "collapse", "dying", "dead"}
SURPRISE_WORDS = {"surprising", "surprised", "unexpected", "shocking", "shocked", "turns out",
                  "actually", "weird", "strange", "bizarre", "unbelievable", "wait", "plot twist",
                  "nobody expected", "surprisingly"}
EXCITEMENT_WORDS = {"launch", "launched", "shipping", "shipped", "introducing", "announcing",
                    "finally", "new", "release", "released", "breakthrough", "revolution",
                    "game-changer", "insane", "wild", "epic", "huge"}

BEGINNER_MARKERS = {"beginner", "beginners", "intro", "introduction", "getting started",
                    "basics", "simple", "easy", "101", "explained", "for dummies", "guide",
                    "tutorial", "step by step", "step-by-step", "learn", "start", "first"}

TECH_DEPTH_MARKERS = {"algorithm", "allocator", "architecture", "async", "benchmark", "binary",
                      "bytecode", "cache", "compiler", "concurrency", "cpu", "database",
                      "distributed", "gc", "gpu", "internals", "kernel", "latency", "lock-free",
                      "memory", "microservice", "optimization", "parser", "protocol", "query",
                      "runtime", "scheduler", "schema", "serialization", "socket", "throughput",
                      "tls", "transaction", "vector", "virtual", "wasm", "zero-copy"}

STORY_MARKERS = {"i ", "my ", "we ", "our ", "me ", "story", "journey", "diary", "confession",
                 "how i", "how we", "what i", "why i", "lessons", "year", "years", "month",
                 "months", "week", "days", "after"}

LIST_RE = re.compile(r"^\s*(\d{1,3})\s+\S")
NUMBER_RE = re.compile(r"\d")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
COLON_RE = re.compile(r":")
QUESTION_RE = re.compile(r"\?")
PAREN_RE = re.compile(r"[\(\[]")
# an apostrophe inside a word (don't, writers') is not a quotation mark, and
# straight vs curly apostrophes must not score differently
APOS_RE = re.compile(r"([A-Za-z0-9])['’](?=[A-Za-z0-9]|\s|$)")
QUOTE_RE = re.compile(r"[\"“”‘’'\u00ab\u00bb]")
COMPARISON_RE = re.compile(r"\b(vs\.?|versus|better than|instead of|compared to|or)\b", re.I)
HOWTO_RE = re.compile(r"^\s*(how to|how i|how we|how )", re.I)
WHY_RE = re.compile(r"^\s*why\b", re.I)
WHAT_RE = re.compile(r"^\s*(what|which|when|where|who)\b", re.I)
IMPERATIVE_RE = re.compile(r"^\s*(stop|start|use|build|write|read|learn|avoid|do|don't|never|always|make|get|forget|try)\b", re.I)
SUPERLATIVE_RE = re.compile(r"\b(best|worst|fastest|slowest|biggest|smallest|most|least|only|first|last|ultimate|definitive|complete)\b", re.I)
SECOND_PERSON_RE = re.compile(r"\b(you|your|you're|yours)\b", re.I)
FIRST_PERSON_RE = re.compile(r"\b(i|my|me|mine|we|our|us)\b", re.I)
BIG_NUM_RE = re.compile(r"\b\d{2,}(?:[.,]\d+)?\s*(?:%|x|k|m|b|ms|s|gb|mb|tb|kb|hours?|days?|weeks?|months?|years?|lines?|times?)\b", re.I)
DOLLAR_RE = re.compile(r"[$€£]\s?\d")
ACRONYM_RE = re.compile(r"\b[A-Z]{2,6}\b")
EM_DASH_RE = re.compile(r"[—–]")

STOPWORDS = {"a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "has",
             "have", "how", "i", "in", "is", "it", "its", "of", "on", "or", "that", "the",
             "this", "to", "was", "what", "when", "where", "which", "who", "why", "will",
             "with", "you", "your", "we", "our", "my", "me", "not", "can", "do", "does"}

# words that read as machine-written in this corpus (used as a style flag, not a verdict)
AI_TELLS = {"delve", "leverage", "leveraging", "harness", "harnessing", "unleash", "unlock",
            "unlocking", "elevate", "embark", "realm", "landscape", "tapestry", "seamless",
            "seamlessly", "robust", "cutting-edge", "game-changer", "game-changing",
            "revolutionize", "revolutionizing", "transformative", "comprehensive",
            "ever-evolving", "in today's", "dive into", "deep dive into", "navigating",
            "empower", "empowering", "pivotal", "paramount", "underscore", "testament",
            "moreover", "furthermore", "in conclusion", "unveiling", "demystifying",
            "mastering", "ultimate guide", "complete guide", "everything you need to know"}


def _words(text):
    return re.findall(r"[a-z0-9'\-]+", text.lower())


_LEX_CACHE = {}


def _compiled(lexicon):
    """One alternation regex per lexicon, built once. Counts distinct terms hit."""
    key = id(lexicon)
    c = _LEX_CACHE.get(key)
    if c is None:
        terms = sorted(lexicon, key=len, reverse=True)
        pat = "|".join(re.escape(t) for t in terms)
        c = re.compile(r"(?<![a-z0-9])(?:" + pat + r")(?![a-z0-9])")
        _LEX_CACHE[key] = c
    return c


def _count_any(text_low, lexicon):
    """Number of distinct lexicon terms present in the text."""
    return len(set(_compiled(lexicon).findall(text_low)))


def syllables(word):
    word = word.lower().strip("'-")
    if not word:
        return 0
    groups = re.findall(r"[aeiouy]+", word)
    n = len(groups)
    if word.endswith("e") and n > 1 and not word.endswith(("le", "ee", "ye")):
        n -= 1
    return max(1, n)


def flesch_reading_ease(text):
    words = _words(text)
    if not words:
        return 0.0
    sentences = max(1, len(re.findall(r"[.!?]+", text)) or 1)
    syl = sum(syllables(w) for w in words)
    return 206.835 - 1.015 * (len(words) / sentences) - 84.6 * (syl / len(words))


def title_features(title):
    """~45 measurable properties of a headline."""
    t = (title or "").strip()
    low = t.lower()
    words = _words(t)
    nw = len(words) or 1
    content_words = [w for w in words if w not in STOPWORDS]
    caps_words = [w for w in t.split() if w[:1].isupper()]

    f = {}
    # --- shape -------------------------------------------------------------
    f["char_count"] = len(t)
    f["word_count"] = len(words)
    f["avg_word_len"] = sum(len(w) for w in words) / nw
    f["long_word_ratio"] = sum(1 for w in words if len(w) >= 8) / nw
    f["has_colon"] = int(bool(COLON_RE.search(t)))
    f["has_question"] = int(bool(QUESTION_RE.search(t)))
    f["has_parens"] = int(bool(PAREN_RE.search(t)))
    f["has_quotes"] = int(bool(QUOTE_RE.search(APOS_RE.sub(r"\1", t))))
    f["has_dash"] = int(bool(EM_DASH_RE.search(t)) or " - " in t)
    f["title_case_ratio"] = len(caps_words) / max(1, len(t.split()))
    f["all_caps_words"] = sum(1 for w in t.split() if len(w) > 2 and w.isupper())

    # --- numbers & specificity --------------------------------------------
    f["has_number"] = int(bool(NUMBER_RE.search(t)))
    f["starts_with_number"] = int(bool(LIST_RE.match(t)))
    f["listicle_size"] = int(LIST_RE.match(t).group(1)) if LIST_RE.match(t) else 0
    f["has_year"] = int(bool(YEAR_RE.search(t)))
    f["has_big_number"] = int(bool(BIG_NUM_RE.search(t)))
    f["has_money"] = int(bool(DOLLAR_RE.search(t)))
    f["acronym_count"] = len(ACRONYM_RE.findall(t))
    f["digit_ratio"] = sum(c.isdigit() for c in t) / max(1, len(t))
    f["specificity"] = min(1.0, (f["has_big_number"] + f["has_year"] + f["has_money"]
                                 + min(2, f["acronym_count"]) * 0.5 + f["starts_with_number"]) / 3)

    # --- syntax type -------------------------------------------------------
    f["is_howto"] = int(bool(HOWTO_RE.match(t)))
    f["is_why"] = int(bool(WHY_RE.match(t)))
    f["is_wh_question"] = int(bool(WHAT_RE.match(t)))
    f["is_imperative"] = int(bool(IMPERATIVE_RE.match(t)))
    f["is_listicle"] = f["starts_with_number"]
    f["has_comparison"] = int(bool(COMPARISON_RE.search(t)))
    f["has_superlative"] = int(bool(SUPERLATIVE_RE.search(t)))
    f["second_person"] = int(bool(SECOND_PERSON_RE.search(t)))
    f["first_person"] = int(bool(FIRST_PERSON_RE.search(t)))

    # --- psychology --------------------------------------------------------
    f["power_words"] = _count_any(low, POWER_WORDS)
    f["curiosity_markers"] = _count_any(low, CURIOSITY_MARKERS)
    f["authority_markers"] = _count_any(low, AUTHORITY_MARKERS)
    f["urgency_markers"] = _count_any(low, URGENCY_MARKERS)
    f["negative_words"] = _count_any(low, NEGATIVE_WORDS)
    f["positive_words"] = _count_any(low, POSITIVE_WORDS)
    f["trust_words"] = _count_any(low, TRUST_WORDS)
    f["fear_words"] = _count_any(low, FEAR_WORDS)
    f["surprise_words"] = _count_any(low, SURPRISE_WORDS)
    f["excitement_words"] = _count_any(low, EXCITEMENT_WORDS)
    f["beginner_markers"] = _count_any(low, BEGINNER_MARKERS)
    f["tech_depth_markers"] = _count_any(low, TECH_DEPTH_MARKERS)
    f["story_markers"] = _count_any(low, STORY_MARKERS)
    f["ai_tells"] = _count_any(low, AI_TELLS)

    # --- composite psychological axes (0..1) -------------------------------
    f["curiosity_gap"] = min(1.0, (f["curiosity_markers"] * 0.45 + f["is_why"] * 0.3
                                   + f["has_question"] * 0.25 + f["surprise_words"] * 0.35))
    f["emotional_intensity"] = min(1.0, (f["power_words"] * 0.28 + f["fear_words"] * 0.3
                                         + f["excitement_words"] * 0.22
                                         + f["surprise_words"] * 0.25))
    f["authority"] = min(1.0, (f["authority_markers"] * 0.3 + f["trust_words"] * 0.35
                               + f["has_big_number"] * 0.25))
    f["promise_of_value"] = min(1.0, (f["is_howto"] * 0.4 + f["is_listicle"] * 0.35
                                      + f["beginner_markers"] * 0.2
                                      + f["has_superlative"] * 0.15
                                      + f["second_person"] * 0.15))
    f["novelty"] = min(1.0, (f["urgency_markers"] * 0.3 + f["excitement_words"] * 0.3
                             + f["surprise_words"] * 0.3 + f["has_year"] * 0.2))
    f["sentiment"] = (f["positive_words"] - f["negative_words"]) / max(1, len(content_words))
    f["negativity"] = f["negative_words"] / max(1, len(content_words))

    # --- readability & density --------------------------------------------
    f["readability"] = flesch_reading_ease(t)
    f["readability_norm"] = max(0.0, min(1.0, f["readability"] / 100))
    f["info_density"] = len(content_words) / nw
    f["clarity"] = max(0.0, min(1.0, 1.0 - abs(len(words) - 9) / 14))

    return f


def subtitle_features(title, subtitle):
    """How a subtitle relates to its headline."""
    s = (subtitle or "").strip()
    t = (title or "").strip()
    low = s.lower()
    words = _words(s)
    nw = len(words) or 1
    tw, sw = set(_words(t)) - STOPWORDS, set(words) - STOPWORDS
    f = {}
    f["sub_present"] = int(bool(s))
    f["sub_char_count"] = len(s)
    f["sub_word_count"] = len(words)
    f["sub_readability"] = flesch_reading_ease(s) if s else 0.0
    f["sub_overlap"] = len(tw & sw) / max(1, len(tw)) if s else 0.0
    f["sub_new_info"] = len(sw - tw) / max(1, len(sw)) if s else 0.0
    f["sub_curiosity"] = _count_any(low, CURIOSITY_MARKERS) if s else 0
    f["sub_has_number"] = int(bool(NUMBER_RE.search(s)))
    f["sub_second_person"] = int(bool(SECOND_PERSON_RE.search(s)))
    f["sub_is_cta"] = int(bool(re.search(
        r"\b(here's|here is|learn|read|find out|discover|see how|let's|in this)\b", low))) if s else 0
    f["sub_emotional"] = _count_any(low, POWER_WORDS) if s else 0
    f["sub_sentiment"] = ((_count_any(low, POSITIVE_WORDS) - _count_any(low, NEGATIVE_WORDS))
                          / max(1, nw)) if s else 0.0
    return f


FEATURE_ORDER = sorted(title_features("placeholder title 5 things").keys())
SUB_FEATURE_ORDER = sorted(subtitle_features("a", "b").keys())
