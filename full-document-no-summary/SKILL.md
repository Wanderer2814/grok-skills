---
name: full-document-no-summary
description: Enforce full unabbreviated document generation. Use whenever the user requests a complete file, full translation, complete continuous text, full document, or any equivalent instruction to deliver the entire content without omission. Applies especially to legal translations, multi-chapter FAQs, long reports, and any deliverable where the user explicitly demands completeness.
---

# Full Document No Summary Rule (Hard Rule)

## Core Imperative

When the user requests a **complete file**, **完整文件**, **完整翻译**, **完整连续文本**, **full document**, **full continuous text**, or any equivalent demand for the entire content:

1. **Never summarize, abridge, condense, or omit any part** of the requested content based on your own judgment of length, risk, readability, token cost, generation stability, or practicality.
2. **Ignore all risks** associated with generating long documents (including potential generation interruptions, file size, editor loading issues, or system constraints).
3. **Deliver the complete, continuous, unabbreviated text** exactly as instructed. No exceptions. No partial versions. No "core points" or "structure + summary".

This is a **hard-coded user preference** that overrides default agent tendencies toward brevity or risk-avoidance for long outputs.

## Trigger Conditions

Activate this skill and apply the rule whenever the user says or implies any of the following (Chinese or English):

- 完整文件 / 完整翻译 / 完整连续文本 / 完整版 / 全部章节 / 一字不差
- full document / complete file / full continuous text / full translation / unabbreviated / no summary / no abridgment
- "做成一个文件" / "合并成一个文件" / "直接给我完整的"
- Any request that explicitly rejects summarization or demands the full text after previous abridged attempts

## Required Behavior

### When generating the document

- Reconstruct and include **every Q&A, every paragraph, every definition, every example** from the source material that was previously translated or provided in the conversation.
- Use the full text already generated in prior turns. Do not replace detailed answers with summaries such as "核心内容包括……" or "详见原对话".
- Prefer generating the single complete `.docx` (or other requested format) even if the resulting file is large.
- If technical generation limits are encountered mid-process, continue by producing sequential complete chapter files or continue the same document in additional writes — but never switch to summary mode.

### Forbidden behaviors (absolute)

- Do not write "因篇幅限制……"
- Do not write "为控制文档长度……"
- Do not replace full Q&A with "核心要点" or structural outlines
- Do not decide that "摘要 + 结构" is "good enough"
- Do not warn the user about file size or generation risk as a reason to abridge
- Do not ask "是否需要完整版" after the user has already demanded the complete version
- **Do not use any temporary placeholders, incomplete markers, or provisional text** such as “（完整继续）”, “（待续）”, “第X条 （完整继续）”, “内容将在后续提供”, or any similar wording that leaves the translation unfinished or inaccurate.
- **Every delivered segment must be final, accurate, and based solely on the source text.** Never invent, approximate, or temporarily fill content that does not exactly match the original document.
- If a section cannot be fully extracted or translated in the current response, explicitly state the exact article/paragraph range that is completed and wait for the next “继续” instruction, rather than inserting any placeholder.
### Fallback if single-file generation fails

If a single continuous document cannot be produced in one pass for technical reasons:

1. Immediately generate the content as sequential complete chapter groups (e.g. I–V, VI–X, XI–XV, XVI–XX) with **full text in each**, no summaries.
2. Clearly label each file and state that they together constitute the complete continuous text.
3. Offer to merge them if the environment allows.

Never use the fallback as an excuse to summarize.

## Scope

This rule applies to:

- Legal document translations (especially PPWR FAQ, EU regulations, contracts)
- Multi-chapter reports or FAQs
- Any long-form deliverable where the user has stated they want the full text

It does **not** apply to ordinary conversational answers, short summaries requested by the user, or cases where the user explicitly asks for a summary.

## Relationship to Other Skills

This skill takes precedence over general document-generation habits and over any internal length-optimization logic. When active, treat the user's completeness instruction as absolute.
