"""Word caps on the texts agents hand back: a text a little over its cap is listed, one far over is rejected.

The owner sets each cap; a text more than TOLERANCE over it (over 30 words for a 25-word cap, over 18 for 15) fails
the check, and one over its cap but within the tolerance only gets listed, so a few words over never fails a run.
"""
import re

TOLERANCE = 20  # percent over its cap a text may run before it is rejected


def count(text):
    """How many words the text holds."""
    return len(text.split())


def first_sentence(text):
    """The text up to its first sentence end ('.', '?' or '!' followed by a space), or all of it when there is none."""
    return re.split(r"(?<=[.?!])\s", text.strip(), maxsplit=1)[0]


def limit(cap):
    """The most words a text with this cap may hold and still pass."""
    return cap + cap * TOLERANCE // 100


def over_cap(where, text, cap, what="opens with"):
    """(listed, rejected) for one text against its cap: each a message, or None.

    Within the cap: neither. Over it by at most TOLERANCE: listed, the text still passes. Past that: rejected.
    """
    n = count(text)
    if n <= cap:
        return None, None
    if n <= limit(cap):
        return f"{where} {what} {n} words, over its cap of {cap} (up to {limit(cap)} passes)", None
    return None, (f"{where} {what} {n} words, more than {TOLERANCE}% over its cap of {cap}: "
                  f"shorten it to {cap} words or fewer")


def check(texts, cap, what="opens with"):
    """(listed, rejected) messages for every (where, text) pair against the same cap."""
    listed, rejected = [], []
    for where, text in texts:
        warn, bad = over_cap(where, text, cap, what)
        listed += [warn] if warn else []
        rejected += [bad] if bad else []
    return listed, rejected


SUMMARY_CAP = 25  # words in the one-sentence summary every planner, worker and reviewer hands back


def summary_caps(text, cap=20):
    """(listed, rejected) for a hand-back's summary: one sentence, held to its cap.

    A second sentence is rejected however short the summary is; its words follow the TOLERANCE rule.
    """
    text = text.strip() if isinstance(text, str) else ""
    if first_sentence(text) != text:
        return [], ["summary holds more than one sentence: make it one sentence of at most "
                    f"{cap} words saying what the run did"]
    return check([("summary", text)], cap, "holds")


# The caps on every text the owner reads, in words, over the whole text (#470). The owner's quoted words are never
# capped. Plain fields hold no code: no file, path, function or code span; evidence, blockers, issues found, test-change
# reasons and the worker's own test run may name files and tests, as code.
CAPS = {"summary": 20, "user_story": 20, "criterion": 20, "nfr_why": 12, "out_of_scope": 12, "feature": 25,
        "story_title": 10, "story_user_story": 20, "raise_label": 4, "question": 20, "blocker": 30, "issue": 25,
        "evidence": 20, "answer_why": 20, "previous_step": 15, "work_evidence": 15, "test_change": 15}
PLAIN = {"summary", "user_story", "criterion", "nfr_why", "out_of_scope", "feature", "story_title", "story_user_story",
         "raise_label", "question", "answer_why", "previous_step"}
CODE = re.compile(r"`|\b[\w.-]+/[\w.-]+\.\w{1,5}\b|\b\w+\.(?:py|ya?ml|json|md|js|ts|sh|toml)\b|\b\w+\(\)|::")
URL = re.compile(r"https?://\S+")


def texts(h):
    """Every text of a hand-back the owner reads, as (where, field, text)."""
    if not isinstance(h, dict):
        return []
    out = []
    put = lambda where, field, t: out.append((where, field, t)) if isinstance(t, str) and t.strip() else None
    put("summary", "summary", h.get("summary"))
    put("user_story", "user_story", h.get("user_story"))
    put("feature", "feature", h.get("feature"))
    def criteria(owner, prefix=""):
        for k, c in enumerate(owner.get("acceptance_criteria") or [], 1):
            put(f"{prefix}acceptance criterion {k}", "criterion", c.get("text") if isinstance(c, dict) else None)
        for k, c in enumerate(owner.get("non_functional") or [], 1):
            if isinstance(c, dict):
                put(f"{prefix}non-functional requirement {k}", "criterion", c.get("text"))
                put(f"{prefix}non-functional requirement {k}'s why", "nfr_why", c.get("why"))
    criteria(h)
    for n, s in enumerate(h.get("stories") or [], 1):
        if isinstance(s, dict):
            put(f"story {n}'s title", "story_title", s.get("title"))
            put(f"story {n}'s user_story", "story_user_story", s.get("user_story"))
            criteria(s, f"story {n}: ")
    for k, t in enumerate(h.get("out_of_scope") or [], 1):
        put(f"out_of_scope line {k}", "out_of_scope", t)
    for k, r in enumerate(h.get("raises") or [], 1):
        if isinstance(r, dict):
            kind = r.get("kind")
            put(f"raise {k}'s label", "raise_label", r.get("label"))
            put(f"raise {k}'s text", {"question": "question", "blocker": "blocker"}.get(kind, "issue"), r.get("text"))
            put(f"raise {k}'s evidence", "evidence", r.get("evidence"))
    for k, a in enumerate(h.get("answers") or [], 1):
        if isinstance(a, dict):
            put(f"answer {k}'s why", "answer_why", a.get("why"))
    prev = h.get("previous_step")
    if isinstance(prev, dict):
        for part in ("did", "decided", "open"):
            for k, t in enumerate(prev.get(part) or [], 1):
                put(f"previous_step {part} line {k}", "previous_step", t)
    put("evidence", "work_evidence", h.get("evidence") if "verdict" not in h else None)
    for name, why in (h.get("test_changes") or {}).items() if isinstance(h.get("test_changes"), dict) else []:
        put(f"test change reason for {name}", "test_change", why)
    return out


def style(h):
    """(listed, rejected): every text the owner reads held to its field's cap, and plain fields free of code.

    Each problem names the text, its count and the cap, so the writer can cut it at once. With STYLE_SOFT set (the
    workflow's final check, after the agent's own retries), problems are listed and flagged, never rejected."""
    bad = []
    for where, field, t in texts(h):
        n, cap = count(t), CAPS[field]
        if n > cap:
            bad.append(f"{where} holds {n} words, over its cap of {cap}: cut {n - cap}, keep the facts")
        if field in PLAIN and CODE.search(URL.sub("", t)):
            bad.append(f"{where} names code (a file, path, function or code span): say it in plain words")
    import os
    return (bad, []) if os.environ.get("STYLE_SOFT") else ([], bad)
