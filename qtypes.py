import json, re
import pandas as pd

QTYPES = {
    "mcq": "Multiple Choice Questions",
    "fib": "Fill in the Blanks",
    "true_false": "True or False",
    "assertion_reason": "Assertion and Reason",
    "short": "Short Answer",
    "long": "Long Answer",
    "image": "Image-based Questions",
}
TYPE_ORDER = list(QTYPES)
GROUPS = {"descriptive": ["short", "long"],
          "objective": ["mcq", "fib", "true_false", "assertion_reason"]}
TYPE_ALIASES = {
    "multiple choice": "mcq", "multiple choice question": "mcq", "multiple choice questions": "mcq",
    "fill in the blank": "fib", "fill in the blanks": "fib", "fill blank": "fib", "blank": "fib",
    "true false": "true_false", "true or false": "true_false", "tf": "true_false",
    "assertion reason": "assertion_reason", "assertion and reason": "assertion_reason",
    "assertion": "assertion_reason", "ar": "assertion_reason",
    "short answer": "short", "long answer": "long",
    "image based": "image", "picture": "image",
}
AR_OPTIONS = [
    "Both A and R are true, and R is the correct explanation of A.",
    "Both A and R are true, but R is not the correct explanation of A.",
    "A is true, but R is false.",
    "A is false, but R is true.",
]
OPT_COLS = ["option_a", "option_b", "option_c", "option_d", "option_e"]
_MARK = re.compile(r"(?:(?<=\s)|^)\(?([A-Da-d])\)\s*")


def nn(v):
    """None for None / NaN / blank, else the stripped string."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    s = str(v).strip()
    return s or None


def norm_type(v):
    s = nn(v)
    if not s:
        return None
    s = s.lower().replace("-", " ").replace("_", " ").strip()
    s = TYPE_ALIASES.get(s, s).replace(" ", "_")
    return s if s in QTYPES else None


def split_inline_options(text):
    """'Which is LIFO? (A) Queue (B) Stack' -> ('Which is LIFO?', ['Queue', 'Stack'])."""
    ms = list(_MARK.finditer(text))
    for m in ms:
        if m.group(1).upper() != "A":
            continue
        run = [m]
        for want in "BCD":
            nxt = next((x for x in ms if x.start() > run[-1].start() and x.group(1).upper() == want), None)
            if nxt is None:
                break
            run.append(nxt)
        stem = text[:m.start()].strip()
        if len(run) >= 2 and stem:
            opts = [text[r.end(): run[j + 1].start() if j + 1 < len(run) else len(text)].strip()
                    for j, r in enumerate(run)]
            if all(opts):
                return stem, opts
    return text, []


def row_options(r):
    ex = r.get("options")
    if isinstance(ex, (list, tuple)):
        return [str(x).strip() for x in ex if str(x).strip()]
    ex = nn(ex)
    if ex:
        try:
            v = json.loads(ex)
            if isinstance(v, list):
                return [str(x).strip() for x in v if str(x).strip()]
        except ValueError:
            pass
        return [o.strip() for o in re.split(r"\s*\|\s*|\n", ex) if o.strip()]
    return [s for s in (nn(r.get(c)) for c in OPT_COLS) if s]


def detect_type(text, options=None, marks=5, has_image=False):
    t = text.lower()
    if "assertion" in t and "reason" in t:
        return "assertion_reason"
    if options:
        return "mcq"
    if re.search(r"_{2,}|\.{4,}|\[\s*blank\s*\]|fill in the blank", t):
        return "fib"
    if re.search(r"true or false|true/false|true \(t\)|state whether .{0,60}(true|false)", t):
        return "true_false"
    if has_image:
        return "image"
    return "short" if marks <= 5 else "long"


def expand_types(types):
    """['mcq', 'descriptive'] -> ['mcq', 'short', 'long']"""
    out = []
    for t in types or []:
        t = norm_type(t) or str(t).strip().lower()
        out += GROUPS.get(t, [t])
    return [t for t in dict.fromkeys(out) if t in QTYPES]


def enrich(df):
    """Fill qtype / options / answer / image_path for every row (detecting what is missing)."""
    df = df.copy()
    for c in ("qtype", "options", "answer", "image_path"):
        if c not in df.columns:
            df[c] = None
    out = {k: [] for k in ("question", "qtype", "options", "answer", "image_path")}
    for r in df.to_dict("records"):
        q = str(r["question"]).strip()
        opts = row_options(r)
        if not opts:
            q, opts = split_inline_options(q)
        img = nn(r.get("image_path"))
        try:
            marks = int(r.get("marks"))
        except (TypeError, ValueError):
            marks = 5
        t = norm_type(r.get("qtype")) or detect_type(q, opts, marks, bool(img))
        if t == "assertion_reason" and not opts:
            opts = list(AR_OPTIONS)
        out["question"].append(q)
        out["qtype"].append(t)
        out["options"].append(json.dumps(opts) if opts else None)
        out["answer"].append(nn(r.get("answer")))
        out["image_path"].append(img)
    for k, v in out.items():
        df[k] = v
    return df