"""Source-verified owner and deadline reminders.

Uses only explicit due-date entries of the form
- Month day: Action (Accountable Person)
Never invents or reassigns a responsible person.
"""
import re

ENTRY = re.compile(r"(?im)^\s*[-*]\s*([A-Za-z]+\s+\d{1,2}):\s*(.+?)\s*\(([^()]+)\)\s*$")
DATE = re.compile(r"(?i)\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b")
REMINDER = re.compile(r"(?i)\b(reminder|remind|draft a note|send a note|due on|deadline owner)\b")


def draft_from_deadline(question, sources):
    q = str(question or "")
    if not REMINDER.search(q):
        return None
    when = DATE.search(q)
    if not when:
        return None
    want = when.group(0).lower()
    for src in sources:
        for m in ENTRY.finditer(str(src.get("chunk") or "")):
            date, task, owner = m.groups()
            if date.lower() != want:
                continue
            # A date alone is insufficient when a file has multiple tasks due on
            # the same day. Require a meaningful topic-word overlap.
            important = {w for w in re.findall(r"[a-z]{5,}", task.lower())
                         if w not in {"response", "deadline", "notice", "client", "draft"}}
            if important and not any(w in q.lower() for w in important):
                continue
            citation = "[%d]" % int(src["n"])
            first = owner.split()[0]
            wrong = re.search(r"(?i)\b(?:to|for)\s+([A-Za-z]+)\b",q)
            mistaken = wrong.group(1) if wrong and wrong.group(1).lower() != first.lower() else None
            if mistaken and mistaken.lower() in {"the", "this", "our", "a", "an"}:
                mistaken = None
            correction = ("Correction: The source assigns this to **{}**, not {} {}.\n"
                          .format(owner,mistaken,citation)) if mistaken else ""
            return (
                correction +
                "Draft for {}: {} is due {} {}. Please confirm the response is ready."
                .format(owner,task,date,citation)
            )
    return None
