# === MEMORY SPEC (KARPATHY SYSTEM) ===

## PURPOSE

Define how memory is stored, updated, and used
for self-improving SNS automation.

---

## STORAGE STRUCTURE

### RAW (DO NOT USE DIRECTLY IN PROMPTS)

raw/
- performance_logs/
- post_results/
- engagement_data/
- error_logs/

---

### COMPILED MEMORY (PRIMARY USAGE)

memory/

- winning_patterns.md
- failure_patterns.md
- hook_patterns.md
- format_patterns.md
- system_rules.md
- current_rules.md

---

## MEMORY ROLES

### winning_patterns.md
- patterns from high-performing posts
- repeatable structures

### failure_patterns.md
- what to avoid
- weak hooks / poor engagement cases

### hook_patterns.md
- top-performing opening lines
- curiosity triggers

### format_patterns.md
- structure templates (reels / feed)

### system_rules.md
- meta improvements (timing, style, CTA)

### current_rules.md (CRITICAL)
- compressed top rules used in generation
- max 5~10 rules only

---

## UPDATE FLOW (AUTOMATED)

1. Collect performance data
2. Send to GPT analyzer
3. Extract:
   - winning patterns
   - failure patterns
4. Append to memory files
5. Compress into current_rules.md

---

## GENERATION FLOW

Before generating content:

1. Load current_rules.md
2. Inject into GPT prompt (TOP)
3. Generate content based on rules
4. Output content

---

## COMPRESSION LOGIC (IMPORTANT)

- Remove duplicates
- Merge similar rules
- Keep only high-impact patterns
- Limit size (token control)

---

## USAGE PRIORITY

1. current_rules.md (ALWAYS)
2. hook_patterns.md (OPTIONAL)
3. raw data (ONLY IF NEEDED)

---

## SYSTEM BEHAVIOR

- Memory MUST evolve
- Weak patterns MUST be removed
- Strong patterns MUST dominate

---

## FINAL

This system ensures:

→ lower token usage
→ higher content quality
→ continuous improvement