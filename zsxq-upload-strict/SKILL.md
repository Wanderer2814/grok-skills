---
name: zsxq-upload-strict
description: "Strict rules for uploading files to 知识星球 (ZSXQ). Use whenever the user asks to upload, post, or send files (with or without summaries) to a ZSXQ group or column. Enforce 100% execution: never post summary/text alone if attachment upload fails."
type: workflow
lifecycle: active
---

# ZSXQ Upload Strict — No Partial Posts

When the user asks to upload files to 知识星球 (ZSXQ) with summaries or text, the attachment and text must go out together. Partial posts are forbidden.

## Absolute Rule

**If file upload fails (TLS timeout, network error, any reason), stop immediately and tell the user. Do not post the summary or text alone.**

- Do not create a text-only topic "for now".
- Do not post a separate attachment topic later.
- Do not improvise, split, or work around.
- Report the exact error and wait for the user's instruction.

The user has stated: partial posts create a mess in the group and are useless. Execute 100% of the request or report failure.

## Workflow

1. Prepare the summary/text exactly as requested (~200 characters or as specified).
2. Attempt a single `zsxq-cli topic +create` that includes both `--text` and `--files`.
3. **On success**: confirm the topic ID to the user.
4. **On any upload failure**:
   - Stop.
   - Report the error clearly (e.g. "qiniu upload: TLS handshake timeout").
   - State that nothing was posted.
   - Do not post text-only content.
   - Ask whether to retry or wait.

## Group / Column

- Use the group ID the user has previously confirmed (currently `88884525414112` for 「硅基法学家」 unless told otherwise).
- If a column or hashtag is requested and does not exist, note it and still follow the absolute rule above. Do not create extra topics to compensate.

## What Not To Do

| Forbidden | Why |
|-----------|-----|
| Post summary, then try file separately | Creates orphan text topics |
| Post file-only topic after text failed | Splits the content the user asked to keep together |
| Retry multiple times then fall back to text-only | Still violates the rule |
| Add notes like "attachment failed, please upload manually" in a text post | Still a partial post |

## Success Condition

A single topic containing both the requested text/summary and the file attachment. Anything less is failure and must be reported without posting.
