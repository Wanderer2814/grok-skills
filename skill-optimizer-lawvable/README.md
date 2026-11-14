# Self-Improve Skill (Grok-adapted, Aggressive Mode)

A self-improving skill system that analyzes work sessions and proposes improvements to other skills.

**Adapted for Grok (xAI)** — original by Malik Taiar (Lawvable), AGPL-3.0.  
Current version: **aggressive proactive mode**.

## Commands

| Command | Description |
|---------|-------------|
| `self-improve` | Analyze current session and propose skill improvements |
| `self-improve [skill-name]` | Target a specific skill |
| `self-improve on` | Enable aggressive automatic mode |
| `self-improve off` | Disable automatic mode |
| `self-improve status` | Check automatic mode status |
| `self-improve [skill-name] history` | View modification history |

## Manual Usage

```
> self-improve my-skill

--- Learning: my-skill ---

Proposed additions:

1. "Always check for X before proceeding"
   Source: User correction at 14:32

---

Apply these changes? [Y/n]
```

## Automatic Mode — Aggressive

Grok has no Claude Code-style stop hooks. When you run `self-improve on`, the agent switches to **aggressive proactive behaviour**:

1. **After every substantial use of another skill** → scan and, if qualified signals exist, present a proposal immediately.
2. **On clear correction language** (“不对”“漏了”“Always do…”, etc.) → enter the workflow at once.
3. **After 4+ consecutive turns on the same skill** → proactive check.
4. **On end-of-task signals** (“好了”“谢谢”“done”…) → final scan before closing the topic.

**Hard safety rule (never removed):**  
The agent will **never** write to any `SKILL.md` without your explicit approval.

Run `self-improve off` to return to pure manual mode.

## Paths

All operations use the absolute Grok skills root:

```
/home/workdir/.grok/skills/[skill-name]/
```

## Quality Criteria (unchanged)

Every proposed instruction must be:

1. **Complete** — no missing information  
2. **Precise** — no vague/subjective language  
3. **Atomic** — one check per instruction  
4. **Stable** — version/date-specific when needed  

Signals that fail any criterion go through clarification first.

## History

Changes are recorded in each skill’s `CHANGELOG.md`. Use `self-improve [skill-name] history` to view or request a revert.
