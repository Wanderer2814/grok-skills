---
name: conference-paragraph-transcript
description: >
  Use only when the user gives a recording (m4a, mp3, wav, or an audio message)
  and asks to turn it into text (转为文字, 转写, 转录, 文字稿, 录音转文字).
  Do not use for editing an existing transcript, translation-only, or proofreading.
  Produce speaker-separated complete paragraphs with no timestamps. If that
  transcript is English, append a full Chinese translation after the entire
  English text. If the first pass has a large unrecognizable stretch — continuous
  60 seconds or more with no usable words, a timestamp jump of 60 seconds or more,
  or a long hallucination loop — automatically run noisy-conference-asr-recovery
  on those stretches before the final manuscript. Do not ask whether to denoise
  or whether the original audio may be read. The user has authorized that.
  Second-pass only the blank stretches. If the full file was not delivered,
  ask for 10–16 minute clips of the blanks, not another full upload.
---

# 会议录音终稿：分人、整段、无时间戳

## 触发

只在用户**给出录音**（m4a / mp3 / wav，或一条音频消息）并要求**转成文字**时启用。

已经有文字稿，只是改格式、去时间戳、翻译、校对、区分发言人：不启用本技能，按用户当次的话做。

## 大段无法识别：自动对原音频做二次识别

先做一遍识别。出现下面任一情况，写终稿之前**自动**按 `noisy-conference-asr-recovery` 处理这些段落。不要问用户要不要降噪，也不要问能不能听原音频。用户已经允许访问原音频。不要把空洞留在终稿里写成「无有效转写」。

- 连续 **≥ 60 秒**没有可用词
- 时间轴一次跳过 **≥ 60 秒**
- 连续 **≥ 60 秒**几乎是同一句空转（例如反复 Thank you），没有新内容
- 用户指出某一大段听不清、空白、无法识别

个别词听不清、零星 `[unclear]`，不启动二次识别。只切空白段（前后各留约 10 秒），不要把已经转清的部分重跑一遍。大段占了大部分时长，才整场重做。二次识别的步骤不要抄进本技能。

原音频按这个顺序找：本次消息带来的文件、项目文件、磁盘上任何同名或同时长的 m4a / mp3 / wav。找到就立刻做。聊天里的 `<AUDIO>` 只是第一遍文字，不等于原文件已经在手里。

「允许访问原音频」不能把平台没送来的文件变出来。整场大约 100 分钟以上，经常只有自动转写、没有波形。这时用一句话说明，请用户把空白段裁成 10–16 分钟再传。不要把整场再要一遍，也不要假装已经听过原声。

与降噪技能分开：它只负责把人声收回来（工作底稿可以带时间轴）；本技能负责终稿。

---

## 终稿（每次都这样）

1. **先辨语种。** 现场主要是英文，终稿正文用英文。现场主要是中文，终稿正文用中文。不要把英文发言改写成中文发言再当原文。
2. **区分发言人。** 用议程 PDF、自我介绍、上下文对名字。对不上，或姓名听不清，写「发言人」加编号。不要用误听名（例如把程保志听成 Paul Puchin）。不确定的对应要在文首说明，并写明可改回编号。
3. **同一人的一段连续发言收成完整段落。** 合并重叠、重复的识别句，只留一次，用较清楚的那句。不要一行一个时间戳。一段发言可以有多段，按意思分段，不要拆成碎片，也不要收成摘要。
4. **终稿不出现时间戳。** 工作底稿里的时间轴只用于自己对齐，不要写进交给用户的 docx / txt。
5. **正文是英文时，中文译文整篇接在全部英文之后。** 先做完英文段落稿，再翻译。中文与英文段落对应，不摘要、不夹在英文句子中间、不另起一套结构。正文已是中文时，不要自动再附英文，除非用户另外要求。
6. **不编造。** 不按议程题目补写没说过的论点。听不清标 `[unclear]`，中文标［听不清］。法律术语只在听得准或上下文不可能是别的词时才改（如 anti-coercion → Anti-Coercion Instrument）；改不准就保留原词或标听不清。

输出 Word。文件名带场次，例如 `上午场转写_段落稿_英中.docx`。文首用几行写明会议、日期、主持人、发言人对照和「无时间戳 / 英文在前」。

细节与反例见 `references/output-contract.md`。

---

## 顺序

1. 找原音频。顺序：本次附件、项目文件、磁盘上的 m4a / mp3 / wav。只有 `<AUDIO>` 文字、没有波形时，不能假装已经听过。有大段无法识别时：文件在，就自动二次识别空白段；文件不在，按降噪技能请用户只裁空白段，不要反复要整场。用户说「允许访问原音频」时同样如此，不要把它当成新的下载通道。
2. 做第一遍识别。出现上文的大段无法识别，自动跑 `noisy-conference-asr-recovery`，把字贴回工作底稿。底稿可留时间轴。
3. 对议程，标发言人。分不清就编号。
4. 去掉时间戳，合并重复句，写成英文（或源语）整段。
5. 通读：有没有把摘要写成发言、有没有残留 `[00:00]`、有没有把两个人并进一段。
6. 若第 4 步的正文是英文，再整篇译成中文，接在英文后面。术语前后一致。
7. 交付 docx，并说明听不清和姓名不确定的地方。

---

## 不要

| 不要 | 为什么 |
|---|---|
| 终稿保留 `[00:12–00:18]` 这类时间戳 | 用户明确不要；时间轴只留在工作底稿 |
| 中英逐句交替 | 中文是整篇接在英文后面 |
| 大段空白却先问「要不要降噪」或「能不能听原音频」 | 录音转文字时，≥ 60 秒无法识别必须自动对原音频做二次识别；用户已经允许 |
| 按题目补写叶斌、Cuyvers 等「应当讲了什么」 | 伪造会议记录 |
| 强行猜发言人真名 | 错名比编号更难改 |
| 中文发言自动再译成英文 | 本约定只在终稿正文为英文时加中文 |
