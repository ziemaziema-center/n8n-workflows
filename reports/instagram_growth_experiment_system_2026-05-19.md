# Instagram Growth Experiment System - 2026-05-19

## Goal

Turn the existing Instagram automation from "four approval candidates per morning" into a growth experiment system that learns from hooks, topics, retention, posting cadence, and approval outcomes.

## Current Problem Hypothesis

- Posting automation works, but the content loop is not yet optimized for audience pull.
- The system likely selects items that are informational, but not packaged with strong hooks, conflict, payoff, or follow reason.
- Approval messages may not expose enough growth-relevant data for the user to choose the best candidate.
- There is no structured experiment ledger tying topic, hook, caption, CTA, posting time, and result back into the next day's candidates.

## Experiment Axes

- Hook type: surprise, price shock, mistake warning, itinerary shortcut, status signal, deadline/urgency.
- Audience angle: budget traveler, Korea outbound traveler, Japan/SEA weekend traveler, luxury deal hunter, airline nerd.
- Video structure: first 1 second visual, first line, payoff timing, CTA position.
- Caption style: short actionable, story-led, checklist, contrarian.
- Posting time: morning approval post, lunch test, evening test, weekend test.
- CTA: save, share, comment keyword, follow for daily deal map.

## Department Split

- Growth Strategist: decides weekly experiment themes and success threshold.
- Content Strategist: writes hook/caption/CTA variants.
- Data Analyst: maintains experiment ledger and reads performance deltas.
- Automation Engineer: updates approval template and workflow draft safely.
- Reviewer: blocks low-signal, misleading, repetitive, or compliance-risk content.
- Publisher Ops: keeps live posting behind user approval.

## Data To Capture Per Reel

- source item id
- topic cluster
- hook type
- caption variant
- CTA variant
- proposed posting time
- approved/rejected
- actual post URL
- 1h/6h/24h views
- likes, saves, shares, comments, follows
- reviewer notes

## Safe Automation Improvements

- Add growth metadata to candidate approval messages.
- Generate two hook variants per candidate.
- Keep a daily experiment ledger.
- Rank candidates by novelty plus expected audience pull, not only availability.
- Add a weekly review report before changing live publishing rules.

## Deferred Gates

- Live Instagram publishing changes.
- Credentialed Instagram metric fetch.
- Production n8n workflow activation.
- Competitor monitoring that requires login or private data.
