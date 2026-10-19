"""Raises: questions, blockers and issues an agent hands up, sent only where one table allows.

The kinds and the table live here alone, read-only: adding a kind or a row is a code change the owner approves, never
something a hand-back carries. An agent writes a raise as {"kind", "to", "label", "text", "evidence"}; label and
evidence are optional, a label never changes how a raise is checked or routed, and an issue has no "to". Code stamps
who raised it and an ID; an agent that writes either is rejected. Whoever a raise is sent to answers it by its ID.
"""
from types import MappingProxyType

KINDS = ("question", "blocker", "issue")
# Who may send a question or blocker to whom. An issue is for no one.
TABLE = MappingProxyType({
    "planner": ("owner",),
    "worker": ("planner",),
    "reviewer": ("planner", "worker", "owner"),
})
# A worker's raise to the planner goes through the reviewer, who answers it first.
THROUGH = MappingProxyType({("worker", "planner"): "reviewer"})
# An issue the planner or the worker raises is filed only once the reviewer confirms it.
CONFIRMS = "reviewer"
FIELDS = ("kind", "to", "label", "text", "evidence")
# An issue may also name the open issues searched for the same cause, by number, each from the reviewer's pack (#621).
SEARCHED = "searched"
# Every issue the reviewer files, its own or one it confirms, also gives its verdict, one of these (#622).
VERDICT = "verdict"
VERDICTS = MappingProxyType({"symptom": "Symptom of a known cause", "root cause": "Root cause found", "new": "New"})
# A symptom names its cause, one open issue; a root cause names its symptoms, the open issues it explains (#623).
CAUSE = "cause"
SYMPTOMS = "symptoms"
# An issue may say whose fault it is: Dokima's, filed in the upstream repo the settings name, or unclear (#745).
FAULT = "fault"
FAULTS = ("dokima", "unsure")
STAMPED = ("raised_by", "id")
ANSWERS = ("done", "disagree")
PREFIX = MappingProxyType({"planner": "P", "worker": "W", "reviewer": "R"})


def _kinds():
    return ", ".join(KINDS[:-1]) + " or " + KINDS[-1]


def _verdicts():
    names = list(VERDICTS)
    return ", ".join(names[:-1]) + " or " + names[-1]


def filing_problems(where, decided):
    """What a reviewer's filing lacks: the open issues it searched, and a verdict."""
    problems = []
    searched = decided.get(SEARCHED)
    if not is_numbers(searched) or not searched:
        problems.append(f"{where} files an issue, so {SEARCHED} must list the open issues searched for the same "
                        f"cause, not {searched!r}")
    if decided.get(VERDICT) not in VERDICTS:
        problems.append(f"{where} files an issue, so {VERDICT} must be {_verdicts()}, not {decided.get(VERDICT)!r}")
    cause = decided.get(CAUSE)
    if decided.get(VERDICT) == "symptom" and not (isinstance(cause, int) and not isinstance(cause, bool)):
        problems.append(f"{where} is a symptom, so {CAUSE} must name its cause, an open issue by number, not {cause!r}")
    symptoms = decided.get(SYMPTOMS)
    if decided.get(VERDICT) == "root cause" and (not is_numbers(symptoms) or not symptoms):
        problems.append(f"{where} is a root cause, so {SYMPTOMS} must list the open issues it explains, not "
                        f"{symptoms!r}")
    return problems


def is_numbers(v):
    """True for a list of whole numbers, true and false left out."""
    return isinstance(v, list) and all(isinstance(n, int) and not isinstance(n, bool) for n in v)


def check_raises(role, raises):
    """The problems with the raises an agent of `role` wrote; empty when they are fine."""
    if not isinstance(raises, list):
        return [f"the raises must be a list, not {type(raises).__name__}"]
    problems = []
    allowed = TABLE.get(role, ())
    for n, r in enumerate(raises, 1):
        where = f"raise {n}"
        if not isinstance(r, dict):
            problems.append(f"{where} is not an object")
            continue
        for field in STAMPED:
            if field in r:
                problems.append(f"{where} carries {field}, which only code writes")
        extra = sorted(k for k in r if k not in FIELDS and k not in STAMPED
                       and not (k in (SEARCHED, VERDICT, CAUSE, SYMPTOMS, FAULT) and r.get("kind") == "issue"))
        if extra:
            problems.append(f"{where} carries fields no raise has: {', '.join(map(str, extra))}")
        kind = r.get("kind")
        if kind not in KINDS:
            problems.append(f"{where}: the kind {kind!r} is not a kind of raise; only {_kinds()} can be raised")
            continue
        to = r.get("to")
        if kind == "issue":
            if to is not None:
                problems.append(f"{where}: the {role}'s issue is for no one, but names {to!r}")
            if SEARCHED in r and not is_numbers(r[SEARCHED]):
                problems.append(f"{where}: {SEARCHED} must be a list of issue numbers, not {r[SEARCHED]!r}")
            if VERDICT in r and r[VERDICT] not in VERDICTS:
                problems.append(f"{where}: {VERDICT} must be {_verdicts()}, not {r[VERDICT]!r}")
            if FAULT in r and r[FAULT] not in FAULTS:
                problems.append(f"{where}: {FAULT} must be {' or '.join(FAULTS)}, or left out for the repo's own, "
                                f"not {r[FAULT]!r}")
            continue
        if not isinstance(to, str) or not to.strip():
            problems.append(f"{where}: the {role}'s {kind} names no one; it must be sent to someone")
        elif to not in allowed:
            rows = ", ".join(allowed) or "no one"
            problems.append(f"{where}: the {role}'s {kind} for the {to} is outside the table; the {role} raises to "
                            f"{rows}")
    return problems


def sent_to(raise_):
    """The one who must answer a stamped raise first.

    None for an issue, unless code sent it to the reviewer to confirm (for_review)."""
    if raise_.get("kind") == "issue":
        return CONFIRMS if raise_.get("to") == CONFIRMS else None
    to = raise_.get("to")
    return THROUGH.get((raise_.get("raised_by"), to), to)


def for_review(raise_):
    """A planner's or worker's issue as code lists it for the reviewer to confirm.

    Code files it only once the reviewer confirms it. None for any other raise, the reviewer's own issue included."""
    if raise_.get("kind") != "issue" or raise_.get("raised_by") not in ("planner", "worker"):
        return None
    return {**raise_, "to": CONFIRMS}


def passes_on(raise_, answer):
    """The reviewer's blocker that its answer to a raise sent through it passes on.

    Done sends the raise on to whom it was for; disagree sends the one who raised it the reviewer's why. None for a
    raise that did not go through the reviewer, or an answer that is neither."""
    if raise_.get("kind") == "issue" or THROUGH.get((raise_.get("raised_by"), raise_.get("to"))) is None:
        return None
    word, why, text = answer.get("answer"), answer.get("why") or "", raise_.get("text") or ""
    if word == "done":
        to, said = raise_.get("to"), f"{text} The reviewer confirmed it: {why}"
    elif word == "disagree":
        to, said = raise_.get("raised_by"), f"The reviewer disagrees with your raise \"{text}\": {why}"
    else:
        return None
    out = {"kind": "blocker", "to": to, "label": raise_.get("label"), "text": said, "evidence": raise_.get("evidence"),
           "raised_by": THROUGH[(raise_.get("raised_by"), raise_.get("to"))], "id": f"R{raise_.get('id')}"}
    return {k: v for k, v in out.items() if v is not None}


def stamp(role, raises, taken):
    """Copies of the raises stamped with the role that ran and a new ID.

    Each ID is unique among `taken` (the IDs already on the issue) and each other.
    """
    used = set(taken)
    prefix = PREFIX.get(role, "X")
    out, n = [], 0
    for r in raises:
        n += 1
        while f"{prefix}{n}" in used:
            n += 1
        rid = f"{prefix}{n}"
        used.add(rid)
        out.append({**r, "raised_by": role, "id": rid})
    return out


def check_answers(role, answers, open_raises):
    """The problems with an agent's answers to the open raises; empty when fine."""
    if not isinstance(answers, list):
        return [f"the answers must be a list, not {type(answers).__name__}"]
    known = {r.get("id") for r in open_raises}
    owed = [r["id"] for r in open_raises if sent_to(r) == role]
    problems, answered = [], set()
    for n, a in enumerate(answers, 1):
        where = f"answer {n}"
        if not isinstance(a, dict):
            problems.append(f"{where} is not an object with raise, answer and why")
            continue
        rid = a.get("raise")
        if not isinstance(rid, str) or not rid.strip():
            problems.append(f"{where} names no raise by its ID")
        elif rid not in known:
            problems.append(f"{where} names {rid!r}, which no open raise has")
        if a.get("answer") not in ANSWERS:
            problems.append(f"{where} says {a.get('answer')!r}; it must say done or disagree")
        why = a.get("why")
        if not isinstance(why, str) or not why.strip():
            problems.append(f"{where} does not say why")
        if isinstance(rid, str) and rid in known:
            answered.add(rid)
    for rid in owed:
        if rid not in answered:
            problems.append(f"raise {rid}, sent to the {role}, is not answered")
    return problems
