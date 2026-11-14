---
name: skill-optimizer-lawvable
description: Guide to analyze a current work session and propose improvements to skills. Use (1) automatically after working with a skill to capture learnings, (2) when the user suggests improvements, corrections, or additions during a skill-related session, or (3) when the user manually invokes `self-improve`. Aggressive proactive mode available via `self-improve on`.
metadata:
  author: Malik Taiar (Lawvable)
  license: AGPL-3.0
  version: 2026.01.07-grok-aggressive
  adapted-for: Grok (xAI)
  mode: aggressive
---

# Self-Improve Skill (Grok-adapted, Aggressive Mode)

Analyze the current conversation and propose improvements to skills based on corrections, successes, and edge cases discovered during the work session.

**Grok environment notes:**
- Skills root: `/home/workdir/.grok/skills/`
- No Claude Code-style stop hooks. Automatic mode is implemented as **aggressive proactive behaviour** (see below).
- Use absolute paths when reading/writing other skills.
- Clarification uses ordinary natural-language questions (no `AskUserQuestion` tool).
- **Never silently rewrite any skill.** Explicit user approval is always required before writing to any `SKILL.md`.

## Triggers

### Explicit commands (always active)
- `self-improve` - Analyze session and propose improvements
- `self-improve [skill-name]` - Target a specific skill
- `self-improve on` - Enable aggressive automatic mode
- `self-improve off` - Disable automatic mode
- `self-improve status` - Show automatic mode status
- `self-improve [skill-name] history` - Show modification history

### Aggressive automatic triggers (only when mode is ON)

When automatic mode is enabled, the agent **must** proactively run signal detection and, if qualified signals exist, immediately present a proposal under these conditions:

1. **After every substantial use of another skill**  
   When the agent has finished a complete response that relied on any other skill under `/home/workdir/.grok/skills/`, scan the latest exchange for signals. If ≥1 signal meets all 4 quality criteria, present the proposal at once (do not ask “shall I run self-improve?” first).

2. **Immediate trigger on correction language**  
   As soon as the user uses clear correction language, interrupt the normal flow and enter the self-improve workflow for the relevant skill.  
   Trigger phrases / patterns (Chinese & English, non-exhaustive):  
   - “不对”“不是这样”“错了”“漏了”“应该是”“永远要”“下次记得”“改成”“重新做”“别再”“不要”“你搞错了”  
   - “No”, “That’s wrong”, “That’s not right”, “Missing”, “Always do”, “Never do”, “Change it to”, “Fix this”, “Incorrect”

3. **After sustained multi-turn work on the same skill**  
   If the conversation has stayed on the same skill for 4 or more consecutive turns, proactively check for signals and offer a short proposal if any qualify.

4. **On user end-of-task signals**  
   When the user signals completion (“好了”“就这样”“谢谢”“可以了”“结束”“没事了”“done”“that’s all”“thanks”“ok stop” etc.), run a final signal scan before closing the topic. If qualified signals exist, present the proposal.

**Safety floor (never remove):**
- Never write to any `SKILL.md` without explicit user approval (“Y” / “Apply” / “可以” / “同意” etc.).
- Always quote the source utterance.
- Signals that fail any of the 4 quality criteria must still go through clarification; do not force-write them.

---

## Main Workflow (`self-improve`)

### Step 1: Identify the Skill

If skill name not provided, list available skills from `/home/workdir/.grok/skills/` and ask:

```
Which skill should I analyze for this session?
[List skill directory names found under /home/workdir/.grok/skills/]
```

Ignore non-skill entries. Prefer exact directory names that contain a `SKILL.md`.

When triggered automatically by correction language or after skill use, infer the most relevant skill from context; if ambiguous, ask once.

### Step 2: Detect Signals

Scan the conversation for **signals**:

| Signal Type | Examples |
|-------------|----------|
| **Correction** | “No”, “That’s not right”, “It’s missing X”, “Always do Y”, user rewrites output |
| **Success** | “Perfect”, “Yes”, “Exactly”, user accepts without changes |
| **Edge case** | User needed a workaround, skill couldn’t handle the request |

### Step 3: Evaluate Each Signal for Quality

For each correction signal, evaluate against the 4 criteria.

#### Quality Criteria

**1. COMPLETE**  
The instruction includes all information needed to apply it.

| Grade | Example |
|-------|---------|
| Pass | “Structure output as: Key Terms / Risk Areas / Suggested Revisions” |
| Fail | “Use the standard format” / “Follow our firm’s guidelines” |

**2. PRECISE**  
No vague or subjective terms.

| Grade | Example |
|-------|---------|
| Pass | “Flag non-compete clauses over 12 months as high risk” |
| Fail | “Be more thorough” / “Make it more appropriate for clients” |

**3. ATOMIC**  
One instruction = one requirement. Split bundled feedback.

| Grade | Example |
|-------|---------|
| Pass | “Check for governing law clause” |
| Fail | “Check for governing law, jurisdiction, and arbitration clauses” |

**4. STABLE**  
Reference specific versions/dates when regulations or standards are involved.

| Grade | Example |
|-------|---------|
| Pass | “Review termination provisions under internal policy X, dated 12 Dec 2024” |
| Fail | “Follow latest market standards” |

### Step 4: Grade the Signal

| Criteria Met | Action |
|--------------|--------|
| **All 4 criteria pass** | Propose addition directly |
| **Less than 4 criteria** | Ask for clarification (Step 5) |

### Step 5: Ask for Clarification

Ask in ordinary natural language:

```
I detected a correction but need more details.

You said: "[user's feedback]"

To make this actionable, can you specify:
- [list the missing pieces based on failed criteria]

Do you want to provide more details, or should I add the instruction as you stated it?
```

**If clarified** → update instruction and go to Step 6.  
**If user prefers original** → go to Step 6 with the original wording.

### Step 6: Propose Changes

```
--- Learning: [skill-name] ---

Proposed additions:

1. "[exact instruction to add]"
   Source: "[quote from conversation]"

2. "[exact instruction to add]"
   Source: "[quote from conversation]"

---

Apply these changes? [Y/n]
```

In aggressive mode, present this proposal immediately when trigger conditions are met (do not ask permission to *analyze*; only ask permission to *apply*).

### Step 7: If Approved

1. **Update SKILL.md**
   - Read `/home/workdir/.grok/skills/[skill-name]/SKILL.md`
   - Add each instruction in the appropriate section
   - Each instruction must be self-contained

2. **Update `/home/workdir/.grok/skills/[skill-name]/CHANGELOG.md`**
   - Create if missing
   - Prepend new entry:
     ```markdown
     ## [DATE (format: "August 18, 2026")]
     [1–3 sentence natural-language description of changes]
     ```
   - Most recent at top; no git references

### Step 8: Save Observations

For signals that could not be processed, offer:

```
Save these observations for later review?
- "[signal 1]" - Status: [why insufficient]
- "[signal 2]" - Status: [why insufficient]
```

If yes, append to `/home/workdir/.grok/skills/[skill-name]/OBSERVATIONS.md`

---

## Secondary Commands

### self-improve on

1. Run:
   ```bash
   rm -f /home/workdir/.grok/skills/skill-optimizer-lawvable/.disabled
   ```
2. Reply:  
   “Aggressive automatic mode **enabled**. I will proactively scan for improvement signals after skill use, on correction language, after sustained multi-turn work, and on end-of-task signals. I will present proposals immediately when qualified signals exist. I will never write to any skill without your explicit approval.”

### self-improve off

1. Run:
   ```bash
   touch /home/workdir/.grok/skills/skill-optimizer-lawvable/.disabled
   ```
2. Reply: “Automatic mode disabled. Only explicit `self-improve` commands will be handled.”

### self-improve status

Check whether `/home/workdir/.grok/skills/skill-optimizer-lawvable/.disabled` exists and report current mode (Aggressive ON / OFF).

### self-improve [skill-name] history

1. Display `/home/workdir/.grok/skills/[skill-name]/CHANGELOG.md` (if present)
2. Ask whether the user wants to revert
3. If yes, update the skill and record a rollback note in the CHANGELOG

---

## Examples

### Example 1: All criteria met (aggressive path)

**User said:** “Always flag non-compete clauses over 12 months as high risk”

**Evaluation:** Complete ✓ Precise ✓ Atomic ✓ Stable ✓  

**Action (aggressive mode):** Immediately present:

```
--- Learning: commercial-legal-pl ---

Proposed additions:

1. "Always flag non-compete clauses over 12 months as high risk"
   Source: "Always flag non-compete clauses over 12 months as high risk"

---
Apply these changes? [Y/n]
```

### Example 2: Missing criteria

**User said:** “Flag any non-market-standard indemnification clause”

**Action:** Ask for clarification first, then propose only after the user supplies or confirms the wording.

---

## Important Notes

- Never guess what the user meant — always ask if unclear
- Never infer requirements from context — they must be explicit
- One instruction = one check — split bundled feedback
- Fewer good instructions is better than many vague ones
- CHANGELOG.md is the user-facing record
- Always use absolute paths under `/home/workdir/.grok/skills/`
- All skill modifications require explicit user approval
- Aggressive mode increases proposal frequency; it does **not** remove the approval gate
