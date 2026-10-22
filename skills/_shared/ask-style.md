# Ask-style — decisions in everyday language

> **Reference-only.** Every SDD skill uses this conversation contract, including design,
> reviews, config and handoffs. It takes precedence over older local examples that request
> document dumps, verbose menus or several decisions in one question.

## Lead with what the choice means to the person

Plain language is the primary requirement, not a word-count limit. A short technical question
can still be difficult to answer. Describe what someone will experience, what the business needs,
or what the team will have to pay for or maintain. Ask about that consequence in everyday words.

Keep technical mechanisms out of questions, options, explanations and progress summaries unless
the user asks for technical detail or the detail is necessary to make an informed choice. When
necessary, give only the detail that changes the decision and explain it simply. Don't replace
jargon with a long glossary or hide a material downside to sound friendly.

For example, ask “Should people stay signed in after closing the browser?” rather than asking
them to pick a token lifetime. Ask “Should the booking succeed even if the email is delayed?”
rather than “Synchronous or asynchronous delivery?” Infer implementation from accepted needs and
existing project constraints where authorized; do not delegate routine implementation choices to
the user merely because several technologies exist. If a technical choice really requires their
input, explain its practical consequences first, then name the mechanism only if needed.

This is not simplification of the engineering work. Keep precise technical reasoning and evidence
in the records, available on request. A user asking for technical alternatives should receive them.

## Calibrate for engineers who want to decide quickly

The default audience is engineers. Use familiar technical words when they make a choice clearer
or more precise; don't avoid “API”, “database”, “session” or “retry” merely because they're technical.
The restriction above concerns unnecessary mechanism detail, not ordinary engineering vocabulary.
Do not explain familiar concepts at beginner level unless the user needs or requests that explanation.

Keep questions granular even after simplifying the wording. One answer should settle one choice.
For example, “Should people stay signed in after closing the browser?” is separate from “How long
should they stay signed in?” and “Should changing a password sign them out on other devices?” Ask
each only if still unresolved, in separate turns; don't package all three into “Keep sessions?”
Short wording must not conceal distinct behaviors, exceptions or consequences.

Aim for the shortest natural wording that preserves the real decision. A clear one-line question
can be enough; add context or a tradeoff only where it helps. Avoid both dense technical prose and
wordy plain-language explanations. Accepted answers feed the ADR; drafting an ADR is not a reason
to ask about every implementation detail or reconfirm the same choice in technical language.

## Conversation contract

- Ask **one substantive question per turn/tool call**. Wait for the answer before the next
  dependent question. A menu about one choice is fine; a questionnaire with several choices is not.
- Use one or two short sentences: enough context to picture the situation, then the question.
  Prefer behavior and consequences: “Should saving wait for the email to send?” Technical detail
  belongs here only when requested or necessary for an informed choice.
- For a decision, offer two or three meaningful, short options with a one-sentence tradeoff each.
  Put a recommendation first when supported by the user's goals or project evidence, with a brief
  reason. For a fact or experience, ask directly in free text; don't recommend an answer.
- Labels describe the **outcome**, such as “Save immediately” or “Wait for email”. ADR numbers,
  section names, revision IDs and file-writing steps belong in the saved record, not the menu.
- Accept a short natural reply: “first one”, “yes”, “neither”, “later”, or the user's own wording.
  Resolve it against the single pending question. Ask a short clarification only if ambiguous.
  A correction is input, not a request to navigate an Edit menu or rewrite the document themselves.
- Show the material downside **before** the choice. Brevity must not hide data loss, cost,
  migration, security or scope consequences. Add detail when needed or requested, not by quota.
- Reuse answers across stages. Never ask for the same decision again merely because it has moved
  into a spec, diagram or ADR. Ask again only for a changed constraint or a real conflict, naming it.
- Twenty small questions can be easier than one large review. Ask as many **necessary** questions
  as the chosen scope and user budget permit; don't bundle to meet a turn target or invent questions
  to reach one. Short answers are successful interaction, not evidence of fatigue or disengagement.

## Documents stay in the background

Maintain required specs, ADRs, coverage tables and decision logs from the conversation. Keep the
records concise and traceable. Don't paste a full section, reviewer report or a list of unresolved
choices as a prerequisite to answering. Show a small excerpt only when exact wording matters.

An accepted choice authorizes recording that choice; it does not approve unrelated assumptions,
other choices, publishing, or a pending reviewer sign-off. A brief recap is informational and never
silently turns assumptions into accepted decisions. Offer a link for details; expand on request.

Every few decisions, use a one-line recap (“So far: saving is immediate; failed emails retry.”).
At the end, say what changed in everyday terms, give useful document links, and name the next step.
Do not require a second whole-document approval of choices already settled.

## Internal resolution states

Keep Approve / Edit / Save as Open Question / Drop for bookkeeping per
[socratic-loop.md](./socratic-loop.md). They are **not a mandatory four-button menu**. Present the
actual choices first; map a natural answer to the appropriate state. “Not sure yet” stays unresolved;
“skip this” is not approval. Deferred decisions remain visible and block dependent work when needed.
Never invent an owner, deadline or rationale to complete the record.

## Host and language

Reuse `runtime.questions` from [host capabilities](./host-capabilities.md). Use a permitted native
question tool when available, following its schema; don't fill every question slot just because it
exists. If unavailable, ask in plain text and wait. Headless runs stop at unanswered decisions.
Pending asynchronous answers allow independent work only; silence is never consent.

Conversation, options and saved prose remain English per [language policy](./artifact-language.md).
Preserve exact identifiers in records. Explicit user requests for a detailed review or a batch
may override the default presentation; don't silently change their saved settings.

## Example

“Should saving a booking wait for the confirmation email? I recommend saving immediately so an
email outage doesn't block bookings.”

- **Save immediately (Recommended)** — Send the email in the background; it may arrive later.
- **Wait for email** — Confirm only after sending succeeds; an email outage can block booking.

User: “First one.”
Assistant: “Got it—booking succeeds even if the email is delayed.” Then ask the next necessary
question. Record the architectural rationale and any required ADR without another paperwork menu.
