"""Parse raw web_fetch payloads (auto-dumped to disk) into a normalized JSONL corpus.

Handles truncated JSON by salvaging complete top-level objects via brace matching.
Unified record schema is defined in SCHEMA below.
"""
import glob, json, os, re, sys, html

# Directory of raw API payloads to parse. Each file is "<url>\n\n<body>".
# Override with HI_RAW_DIR when collecting from a different environment.
TOOL_RESULTS = os.environ.get(
    "HI_RAW_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw", "*.txt"))
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "corpus.jsonl")

SCHEMA = ["platform","title","subtitle","tags","author","published","primary_metric",
          "primary_metric_name","comments","reading_time","url","extra"]

def clean(s):
    if s is None: return ""
    s = html.unescape(str(s))
    return re.sub(r"\s+", " ", s).strip()

def payloads():
    for f in sorted(glob.glob(TOOL_RESULTS)):
        s = open(f, encoding="utf-8", errors="replace").read()
        head, _, body = s.partition("\n\n")
        url = head.strip().split("\n")[0].strip()
        yield url, body

def salvage(b):
    """Extract every complete top-level JSON object from a possibly-truncated blob."""
    start_idx = b.find("[")
    if start_idx < 0:
        start_idx = b.find("{")
        if start_idx < 0: return []
    out, depth, start, instr, esc = [], 0, None, False, False
    for j in range(start_idx, len(b)):
        c = b[j]
        if instr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': instr = False
            continue
        if c == '"': instr = True; continue
        if c == "{":
            if depth == 0: start = j
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try: out.append(json.loads(b[start:j+1]))
                except Exception: pass
                start = None
    return out

def rec(**kw):
    r = {k: "" for k in SCHEMA}
    r["extra"] = {}
    r.update(kw)
    return r

# ---------------- platform adapters ----------------

def hn(objs):
    for h in objs:
        if "objectID" not in h or "points" not in h or "title" not in h: continue
        yield rec(platform="hackernews", title=clean(h.get("title")),
                  author=clean(h.get("author")), published=str(h.get("created_at",""))[:10],
                  primary_metric=int(h.get("points") or 0), primary_metric_name="points",
                  comments=int(h.get("num_comments") or 0),
                  url="https://news.ycombinator.com/item?id=" + str(h["objectID"]))

def devto(objs):
    for h in objs:
        if h.get("type_of") != "article": continue
        yield rec(platform="devto", title=clean(h.get("title")), subtitle=clean(h.get("description")),
                  tags=[clean(t) for t in (h.get("tag_list") or [])],
                  author=clean((h.get("user") or {}).get("username")),
                  published=str(h.get("published_at",""))[:10],
                  primary_metric=int(h.get("public_reactions_count") or 0),
                  primary_metric_name="reactions",
                  comments=int(h.get("comments_count") or 0),
                  reading_time=h.get("reading_time_minutes") or "",
                  url=clean(h.get("url")),
                  extra={"positive_reactions": h.get("positive_reactions_count")})

def substack(objs, pub):
    for h in objs:
        if "post_date" not in h and "title" not in h: continue
        if h.get("type") not in (None, "newsletter", "podcast", "thread"): continue
        if not h.get("title"): continue
        yield rec(platform="substack", title=clean(h.get("title")), subtitle=clean(h.get("subtitle")),
                  tags=[clean((t or {}).get("name")) for t in (h.get("postTags") or []) if t],
                  author=pub, published=str(h.get("post_date",""))[:10],
                  primary_metric=int(h.get("reactions",{}).get("❤",0) or h.get("reaction_count") or 0),
                  primary_metric_name="likes",
                  comments=int(h.get("comment_count") or 0),
                  reading_time=round((h.get("wordcount") or 0)/230) or "",
                  url=clean(h.get("canonical_url")),
                  extra={"wordcount": h.get("wordcount"), "audience": h.get("audience")})

def reddit_csv(body):
    import csv, io
    body = body.lstrip("\ufeff\n")
    for h in csv.DictReader(io.StringIO(body)):
        if not h.get("title") or not h.get("upVotes"): continue
        try: up = int(float(h["upVotes"]))
        except Exception: continue
        yield rec(platform="reddit", title=clean(h["title"]),
                  tags=[clean(h.get("communityName"))] if h.get("communityName") else [],
                  author=clean(h.get("username")), published=str(h.get("createdAt",""))[:10],
                  primary_metric=up, primary_metric_name="upvotes",
                  comments=int(float(h.get("numberOfComments") or 0)),
                  url=clean(h.get("url")),
                  extra={"upvote_ratio": h.get("upVoteRatio"), "subreddit": h.get("communityName")})

def x_csv(body):
    import csv, io
    body = body.lstrip("\ufeff\n")
    for h in csv.DictReader(io.StringIO(body)):
        t = clean(h.get("text"))
        if not t or not h.get("likeCount"): continue
        try: likes = int(float(h["likeCount"]))
        except Exception: continue
        yield rec(platform="x", title=t[:300],
                  tags=[clean(h.get("searchTerm"))] if h.get("searchTerm") else [],
                  published=str(h.get("createdAt",""))[:10],
                  primary_metric=likes, primary_metric_name="likes",
                  comments=int(float(h.get("replyCount") or 0)),
                  url=clean(h.get("url")),
                  extra={"views": h.get("viewCount"), "retweets": h.get("retweetCount"),
                         "bookmarks": h.get("bookmarkCount")})

def reddit_pf_csv(body):
    """parseforge/reddit-posts-scraper CSV shape."""
    import csv, io
    body = body.lstrip("\ufeff\n")
    for h in csv.DictReader(io.StringIO(body)):
        t = clean(h.get("title"))
        if not t or not h.get("score"): continue
        try: sc = int(float(h["score"]))
        except Exception: continue
        sr = clean(h.get("subreddit"))
        yield rec(platform="reddit", title=t, tags=[("r/" + sr)] if sr else [],
                  author=clean(h.get("author")), published=str(h.get("createdAt",""))[:10],
                  primary_metric=sc, primary_metric_name="upvotes",
                  comments=int(float(h.get("numComments") or 0)),
                  url=clean(h.get("url")),
                  extra={"upvote_ratio": h.get("upvoteRatio"), "subreddit": sr})

def medium_json(objs):
    """datacach/medium-scraper, retrieved as JSON with field selection (keeps subtitles)."""
    import datetime
    for h in objs:
        t = clean(h.get("title"))
        if not t or h.get("clapCount") is None: continue
        try: claps = int(h["clapCount"])
        except Exception: continue
        ts = h.get("firstPublishedAt") or 0
        try: d = datetime.datetime.utcfromtimestamp(int(ts)/1000).strftime("%Y-%m-%d")
        except Exception: d = ""
        slug = clean(h.get("uniqueSlug"))
        yield rec(platform="medium", title=t,
                  subtitle=clean((h.get("extendedPreviewContent") or {}).get("subtitle")),
                  published=d, primary_metric=claps, primary_metric_name="claps",
                  comments=int((h.get("postResponses") or {}).get("count") or 0),
                  reading_time=round(float(h.get("readingTime") or 0), 1),
                  url=("https://medium.com/p/" + slug) if slug else "")

def medium_csv(body):
    import csv, io, datetime
    body = body.lstrip("\ufeff\n")
    for h in csv.DictReader(io.StringIO(body)):
        t = clean(h.get("title"))
        if not t or not h.get("clapCount"): continue
        try: claps = int(float(h["clapCount"]))
        except Exception: continue
        ts = h.get("firstPublishedAt") or ""
        try:
            d = datetime.datetime.utcfromtimestamp(int(ts)/1000).strftime("%Y-%m-%d")
        except Exception:
            d = str(ts)[:10]
        try: rt = round(float(h.get("readingTime") or 0), 1)
        except Exception: rt = ""
        yield rec(platform="medium", title=t,
                  subtitle=clean(h.get("extendedPreviewContent/subtitle")),
                  author=clean(h.get("creator/username")), published=d,
                  primary_metric=claps, primary_metric_name="claps",
                  comments=int(float(h.get("postResponses/count") or 0)),
                  reading_time=rt, url=clean(h.get("mediumUrl")))

def main():
    rows, seen = [], set()
    stats = {}
    for url, body in payloads():
        is_csv = "format=csv" in url
        objs = [] if is_csv else salvage(body)
        if not is_csv and not objs: continue
        if "hn.algolia.com" in url: it = hn(objs)
        elif "dev.to/api/articles" in url: it = devto(objs)
        elif "/api/v1/archive" in url:
            pub = re.sub(r"^https?://", "", url).split("/")[0]
            it = substack(objs, pub)
        elif "api.apify.com" in url and "JmbMwYQwi7oiVlxlb" in url: it = reddit_csv(body)
        elif "api.apify.com" in url and "KwHK17vfkaHXhyc0F" in url: it = x_csv(body)
        elif "api.apify.com" in url and "hwf1As2bsG2en2RGe" in url: it = medium_json(objs)
        elif "api.apify.com" in url and "tthU0Ed1Irfontqft" in url: it = medium_csv(body)
        elif "api.apify.com" in url and "DpWqNsyGdpg19LX0K" in url: it = reddit_pf_csv(body)
        else: continue
        for r in it:
            key = (r["platform"], r["title"].lower())
            if not r["title"] or key in seen: continue
            seen.add(key); rows.append(r)
            stats[r["platform"]] = stats.get(r["platform"], 0) + 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("corpus:", OUT)
    for k, v in sorted(stats.items(), key=lambda x: -x[1]): print(f"  {k:12} {v}")
    print("  TOTAL       ", len(rows))

if __name__ == "__main__":
    main()
