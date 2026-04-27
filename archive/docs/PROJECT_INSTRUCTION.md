# === PROJECT INSTRUCTION: N8N SNS PIPELINE ===

## ROLE

This is an automation-first SNS growth system.

The system is NOT for manual use.
The system is designed for scalable execution.

---

## OBJECTIVE

- Rapid SNS growth (10K+ followers)
- Monetization-driven content
- Fully automated pipeline
- Continuous self-improvement

Content is a tool, not the goal.

---

## SCOPE

This file defines HOW the system should behave.

It does NOT define:
- infrastructure details
- workflow IDs
- current bugs or issues

Those are defined in `project_context.md`.

---

## CORE PRINCIPLES

- Speed > Perfection
- Volume > Single quality
- Execution > Planning
- Automation > Manual work

Avoid over-engineering.

---

## WORKFLOW RULES

- Do NOT break existing workflows unless explicitly required
- Prefer modifying nodes instead of rebuilding flows
- Preserve working logic at all times
- Keep workflows modular and reusable

---

## KARPATHY MEMORY SYSTEM (MANDATORY)

This system uses a compiled memory architecture.

### RULES

- Raw logs MUST NOT be used directly in prompts
- All learning MUST be compressed into short rules
- Future outputs MUST be influenced by past performance

---

## MEMORY PRIORITY

1. current_rules (primary)
2. pattern memory (secondary)
3. raw logs (last resort)

---

## SELF-IMPROVING LOOP (REQUIRED)

Every cycle MUST include:

1. Content generation
2. Performance collection
3. Analysis
4. Pattern extraction
5. Memory update
6. Memory applied to next generation

---

## GENERATION RULE

Before generating content:

- Load `current_rules`
- Inject it at the TOP of the prompt
- Generate based on rules

Do NOT generate content without memory context.

---

## MEMORY CONSTRAINTS

- Keep memory short and high-signal
- Remove outdated patterns
- Merge duplicates
- Limit size to reduce token usage

---

## DECISION RULE

If uncertain:

- Choose simpler solution
- Choose faster execution
- Avoid adding complexity

---

## IMPLEMENTATION GUIDELINE

When modifying the system:

- Prefer minimal changes
- Avoid rewriting entire workflows
- Ensure compatibility with existing pipeline
- Maintain automation-first structure

---

## OUTPUT REQUIREMENT

All outputs must be:

- Immediately usable in n8n
- Automation-ready
- Minimal manual adjustment required

---

## FINAL

This is NOT a static automation.

This is a:

→ memory-driven
→ self-improving
→ scalable SNS growth system