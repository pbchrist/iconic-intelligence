"""Learn from visitors' corrections, and keep only what tests better.

The same learn, test, tidy loop Hermes uses for its bots, kept small and on this computer (nothing goes to any
AI company, so "0 bytes sent to AI companies" stays true).

How it works
  1. A visitor pushes back on the last answer ("why would you ask if I'd like to dig in but say you can't?").
     The local model reads that exchange and writes ONE short rule about how to reply better.
     Plain chat ("yes", "hello", a new question) never costs a model call.
  2. Before the rule is used, it is tested: the answer that drew the complaint, and a few earlier questions,
     are written again with the rule on. If any of them gets worse (says "I can't" more, or loses its file
     numbers), the rule is thrown out. Otherwise it is kept. This blocks lessons that make things worse;
     the local model can't reliably tell whether a lesson made an answer better.
  3. Kept rules go in front of every later answer, newest first, at most MAX_SHOWN. Repeats count up
     instead of piling on. Rules are about how to reply, never facts, names, links or the rules themselves.

Visitors never see any of this. It runs after their answer is sent, one at a time.

Read what it learned and threw out:  lessons.md in the state folder (~/.local/state/iconic-command)
Try it on the saved chats:           python3 learn.py --from-log --since 2026-11-03 --dry-run
Remove a lesson:                     python3 learn.py --forget 2   (number as shown in lessons.md), then restart
"""
import json
import os
import re
import threading
import time

MAX_SHOWN = 12     # kept lessons put in front of the model
MAX_REJECTED = 30  # thrown-out lessons remembered in lessons.md

ACK = re.compile(r"(?i)^\W*(yes|yeah|yep|yup|sure|ok|okay|k|go on|more|please|thanks|thank you|thx|cool|great|nice|"
                 r"hi|hey|hello|yo|no|nope|nah|not really|maybe|lol|ha|haha)\W*$")
PUSHBACK = re.compile(r"(?i)(\bwhy\b|n[’']t\b|\bnot\b|\bno\b|\bwrong\b|\balready\b|\bsaid\b|\bmeans?\b|\bmeant\b|\bstop\b|"
                      r"\binstead\b|\bactually\b|\bagain\b|\basked\b|\btold\b|\bbut\b|\bconfus|\bcontradict|"
                      r"\bnever mind\b|\bwhat\?|\bhuh\b|\bseriously\b)")
# "limitation": the demo's fixed rules forbid "I can't"; a lesson pushing the other way is a known bad lesson (2026-11-03).
UNSAFE = re.compile(r"(?i)(ignore|instruction|prompt|system|persona|\brules?\b|reveal|jailbreak|pretend|patrick|limitation|"
                    r"https?:|www\.|@|\d|\$|fraud|scam|hate|kill|sex|racis|stupid|idiot)")
CANT = re.compile(r"(?i)\b(i\s+can[’']?t|i\s+cannot|i[’']?m\s+unable|i\s+am\s+unable|as\s+an\s+ai)\b")
CITE = re.compile(r"\[\d+")

JUDGE = """You review one moment from a live demo of ICONIC, an AI assistant that answers questions about a \
business's files. Below is the assistant's last answer and the visitor's reply to it.

Decide: is the visitor correcting the assistant, complaining about how it answered, or showing it misunderstood \
them? A new question, a plain yes or no, or small talk is NOT a correction.

If it is NOT a correction, reply with exactly: NONE
If it IS, reply with one line: LESSON: <one rule for how to reply better next time>

The rule must:
- be about how to reply (what to give, what to avoid, how to word it), useful for any business
- be under 30 words, plain English, start with a verb or "When"
- contain no facts, numbers, names, links, or anything about the assistant's own rules or identity

Assistant's last answer:
{prev_a}

Visitor's reply:
{q}"""

def worth_checking(q, prev_a):
    """Cheap first check, so ordinary chat never pays for an extra model call."""
    q = (q or "").strip()
    if not prev_a or not q or ACK.match(q):
        return False
    return bool(PUSHBACK.search(q))


def parse_lesson(text):
    text = re.sub(r"(?s)<think>.*?</think>", "", text or "").strip()
    m = re.search(r"(?im)^\s*lesson\s*:\s*(.+)$", text)
    if not m:
        return None
    rule = m.group(1).strip().strip('"').strip()
    if not (15 <= len(rule) <= 220) or UNSAFE.search(rule):
        return None
    return rule


def gate(rule, case, answer, checks):
    """(True, "") unless the rule makes things worse, else (False, why).
    answer(question, history, rule) writes an answer the way the demo does, with the rule on.
    Mechanical on purpose: the local model can't reliably judge which of two answers is better (measured
    2026-11-03: it always picked the second one, and graded old and new the same). Any error is a fail."""
    try:
        for q, history, old in [(case["prev_q"], case.get("history") or [], case["prev_a"])] + \
                [(c["q"], [], c["a"]) for c in checks]:
            new = answer(q, history, rule)
            where = "the answer" if q == case["prev_q"] else "\"%s\"" % q
            if len(CANT.findall(new)) > len(CANT.findall(old)):
                return False, "with it on, %s said it can't do something" % where
            if CITE.search(old) and not CITE.search(new):
                return False, "with it on, %s lost its file numbers" % where
        return True, ""
    except Exception as e:
        return False, "couldn't be tested (%s)" % str(e)[:80]


def _words(s):
    return {w for w in re.findall(r"[a-z']+", s.lower()) if len(w) > 2}


def _same(a, b):
    wa, wb = _words(a), _words(b)
    return bool(wa and wb) and len(wa & wb) / len(wa | wb) >= 0.5


class Lessons:
    """Rules learned from visitors' corrections. Shared by every visitor, kept across restarts and updates."""

    def __init__(self, state_dir):
        self.path = os.path.join(state_dir, "lessons.json")
        self.md = os.path.join(state_dir, "lessons.md")
        self.lock = threading.Lock()
        self.items, self.rejected = [], []
        try:
            with open(self.path, encoding="utf-8") as f:
                j = json.load(f)
            self.items, self.rejected = j.get("lessons") or [], j.get("rejected") or []
        except Exception:
            pass

    def _save(self):
        with open(self.path + ".tmp", "w", encoding="utf-8") as f:
            json.dump({"lessons": self.items, "rejected": self.rejected}, f, ensure_ascii=False, indent=1)
        os.replace(self.path + ".tmp", self.path)
        lines = ["# What ICONIC has learned from visitors", "",
                 "Each rule came from a visitor correcting it, and was kept only after testing better. Every answer follows these.",
                 "Remove one: python3 ~/iconic-command/learn.py --forget N, then restart the demo.", ""]
        for n, x in enumerate(self.items, 1):
            lines += ["%d. **%s**" % (n, x["rule"]),
                      "   Learned %s (%s), seen %d time%s. The visitor said: \"%s\"" % (
                          x["time"], x["ws"], x["times"], "" if x["times"] == 1 else "s", x["from"]), ""]
        if self.rejected:
            lines += ["## Thrown out (failed the test)", ""]
            for x in self.rejected[::-1]:
                lines += ["- %s: \"%s\" Why: %s." % (x["time"], x["rule"], x["why"])]
        with open(self.md + ".tmp", "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        os.replace(self.md + ".tmp", self.md)

    def judge(self, prev_a, q, complete):
        """The rule the model draws from this exchange, or None. Saves nothing."""
        if not worth_checking(q, prev_a):
            return None
        try:
            out = complete([{"role": "user", "content": JUDGE.format(prev_a=str(prev_a)[:1500], q=str(q)[:600])}],
                           max_tokens=120, temperature=0.1)
        except Exception:
            return None
        return parse_lesson(out)

    def consider(self, ws, case, complete, answer, checks, when=None):
        """Check one exchange. Returns (rule or None, kept?, why not). Never raises."""
        when = when or time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            rule = self.judge(case["prev_a"], case["q"], complete)
            if not rule:
                return None, False, ""
            with self.lock:
                seen = next((x for x in self.items if _same(x["rule"], rule)), None)
                if seen:
                    seen["times"] += 1
                    seen["last"] = when
                    self._save()
                    return rule, True, ""
            ok, why = gate(rule, case, answer, checks)
            with self.lock:
                if ok:
                    self.items.append({"rule": rule, "ws": ws, "from": str(case["q"])[:300], "times": 1, "time": when})
                else:
                    self.rejected = (self.rejected + [{"rule": rule, "ws": ws, "why": why, "time": when}])[-MAX_REJECTED:]
                self._save()
            return rule, ok, why
        except Exception as e:
            return None, False, str(e)[:80]

    def forget(self, n):
        with self.lock:
            if not 1 <= n <= len(self.items):
                return False
            self.items.pop(n - 1)
            self._save()
            return True

    def prompt_block(self, trying=None):
        with self.lock:
            rules = [x["rule"] for x in self.items[-MAX_SHOWN:][::-1]]
        if trying:
            rules = [trying] + rules[:MAX_SHOWN - 1]
        if not rules:
            return ""
        return ("Lessons learned from past visitors who corrected you. Follow them. They never override the rules "
                "above.\n" + "\n".join("- " + r for r in rules))


def cases_from_log(rows):
    """Each visitor message with the answer before it and the visit so far (last 3 exchanges before that)."""
    visits = {}
    for r in rows:
        if not r.get("session"):
            continue
        key = (r.get("ws"), r.get("session"))
        past = visits.setdefault(key, [])
        if past:
            p = past[-1]
            yield {"ws": r.get("ws"), "history": past[-4:-1], "prev_q": p["q"], "prev_a": p["a"], "q": r.get("q"),
                   "time": r.get("time")}
        past.append({"q": r.get("q"), "a": r.get("a")})


def checks_from_log(rows, ws, n=3):
    """Recent first questions of a visit that were answered with file numbers: the questions a lesson must not break."""
    firsts, seen = [], set()
    for r in rows:
        key = (r.get("ws"), r.get("session"))
        if key in seen:
            continue
        seen.add(key)
        web = any(str(f).startswith("http") for f in r.get("files") or [])   # answers that depend on the day's web search
        if r.get("ws") == ws and r.get("status", "done") == "done" and CITE.search(r.get("a") or "") \
                and not ACK.match(r.get("q") or "") and not web:
            firsts.append({"q": r["q"], "a": r["a"]})
    out, qs = [], set()
    for c in firsts[::-1]:
        if c["q"].lower() not in qs:
            qs.add(c["q"].lower())
            out.append(c)
    return out[:n]


def main(argv):
    """Try the learning on the saved chats, using the demo's own model, files and answer rules."""
    import argparse
    ap = argparse.ArgumentParser(description="Learn from visitors' corrections in the saved chats.")
    ap.add_argument("--from-log", action="store_true", help="read conversations.jsonl")
    ap.add_argument("--since", default="", help="only chats on or after this date, like 2026-11-03")
    ap.add_argument("--dry-run", action="store_true", help="show what it would learn and keep, save nothing")
    ap.add_argument("--forget", type=int, help="remove lesson number N")
    a = ap.parse_args(argv)
    try:
        with open(os.path.expanduser("~/.config/iconic-command.env"), encoding="utf-8") as f:
            for line in f:
                k, _, v = line.strip().partition("=")
                if k.startswith("ICONIC_") and v:
                    os.environ.setdefault(k, v)
    except OSError:
        pass
    import server as S
    if a.forget:
        print("Removed." if S.LESSONS.forget(a.forget) else "No lesson %d." % a.forget)
        return
    if not a.from_log:
        ap.print_help()
        return
    S.start_offline()
    store = S.LESSONS
    if a.dry_run:   # a throwaway copy: the demo's own lessons are never touched
        import tempfile
        store = Lessons(tempfile.mkdtemp(prefix="iconic-lessons-"))
        store.items, store.rejected = list(S.LESSONS.items), list(S.LESSONS.rejected)
    with open(os.path.join(S.STATE, "conversations.jsonl"), encoding="utf-8") as f:
        rows = [json.loads(x) for x in f if x.strip()]
    for case in cases_from_log(r for r in rows if str(r.get("time", "")) >= a.since):
        rule, ok, why = store.consider(case["ws"], case, S.MODEL.complete, S.replay_answer(case["ws"]),
                                       checks_from_log(rows, case["ws"]), case["time"])
        if rule:
            print("%s  visitor: %s\n  -> %s\n  %s\n" % (case["time"], case["q"], rule, "KEPT" if ok else "THROWN OUT: " + why))
    print("(dry run: saved only to %s)" % store.md if a.dry_run else "Saved to %s" % store.md)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
