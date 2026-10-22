# Design questions — concrete choices, concise records

Follow [ask-style](../../_shared/ask-style.md). The examples show the conversation; ADR numbers,
section references and rejected alternatives are recorded in files after the answer.

## Behavior before architecture

“Should a booking still succeed if the email service is down? I'd keep bookings available.”

- **Save and email later (Recommended)** — The booking succeeds; email delivery retries later.
- **Require email delivery** — The booking waits and can fail when email is unavailable.

Once answered, derive the supported architecture from the repo and ask only remaining choices.
Do not repeat the same choice as “Approve async coupling and spawn ADR-0001?”

## A maintenance or cost decision

If the existing setup already meets the accepted requirements, use it without asking the user
to choose technologies. If there is a genuine maintenance or cost tradeoff, describe that instead:

“Keeping the current setup is simpler, but heavy email traffic could slow bookings. Is that
acceptable for now, or should we separate the email work even though it adds upkeep?”

Use this only when supported by project evidence; do not invent scale concerns or costs to create
a question. If the user asks how separation works, explain the queue/database alternatives then.
Name technical mechanisms earlier only if the practical choice cannot be understood without them.
Record the selected design and consequences in a concise ADR when the gate warrants one.

## A correction

User: “Actually, retries should stop after a day.”

Apply the clear correction, update affected records, and acknowledge it briefly. If an existing
requirement contradicts it, ask about that conflict alone. Do not require an Edit button, a formal
revision request or another approval of the same sentence.

## Deferral

User: “I'm not sure yet.”

“Okay—we'll leave email retry duration open. Who can decide it?”

After that answer, ask when it must be resolved if not already known. Missing ownership stays
pending; it does not mean the decision was dropped. Continue only work that doesn't depend on it.
