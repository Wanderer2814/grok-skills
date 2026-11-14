---
name: noisy-conference-asr-recovery
description: >
  Recover speech that a recording-to-text pass could not read. Open this skill
  automatically from conference-paragraph-transcript when the user gave a
  recording to transcribe and a stretch is unrecognizable for 60 seconds or more:
  no usable words, a timestamp jump of 60 seconds or more, or a long hallucination
  loop. Also open it when the user reports 空白段/无有效转写/听不清/VAD/噪音, when
  <AUDIO> tags jump in time but the file is missing from disk, or when the user
  authorizes access to the original recording (允许访问原音频). Second-pass only
  the blank stretches. Authorization does not create a file the platform did not
  deliver. Never treat a
  timestamp jump as an empty room. Do not ask permission to start. After recovery,
  return to conference-paragraph-transcript for the paragraph manuscript.
---

# 嗨杂会议录音：禁止把人声当静音

会场话筒、空调、翻页、远处发言会被 **VAD / no-speech 阈值** 判成静音。Grok 聊天里的 `<AUDIO>` 转写尤其如此。**再传同一份整场文件，内置 ASR 仍会丢掉同一段。**

**铁律：时间轴跳了 ≠ 没人说话。空白往往不是没录到。先扫能量，再决定要不要二次识别。禁止按议程题目补写发言。**

收回来的字只是工作底稿。交给用户的终稿另走 `conference-paragraph-transcript`：分发言人、收成整段、终稿不带时间戳；正文是英文时，整篇中文接在全部英文之后。不要把两份技能并成一份。

---

## 有效做法（已在下午场验证）

1. **按秒扫能量。** 所谓空白段 RMS 并不低，人声还在。
2. **不要做强频谱降噪。** `afftdn` 会抹辅音，比不处理更差。
3. **只用高通 100 Hz + 增益 8–10 dB**（可加低通 7 kHz）。单声道 16 kHz PCM。
4. **二次识别时关闭 VAD，把 no-speech 阈值压低**（`vad_filter=False`，`no_speech_threshold=0.2`，仍丢则 0.1）。

命令见 `references/recipes.md`。沙箱上传限制见 `references/sandbox-audio-limits.md`。本场对照见 `references/cupl-2026-case.md`。

---

## 问题 → 途径

| 当场现象 | 错误判断 | 正确途径 |
|---|---|---|
| ASR 从 `30:27` 跳到 `42:13` | 「没录到 / 无有效转写」 | 人声被噪声和 VAD 当静音丢掉了 |
| 用户说「其实录到了，只是噪音大」 | 先做强频谱降噪再识别 | **不要** `afftdn`；只做高通 + 增益 |
| 二次识别仍大段空 | 「这段真没人说话」 | 检查是否还开着 VAD；阈值再降到 0.1 |
| `<AUDIO>` 有文本，磁盘没有 m4a，用户允许访问原音频 | 「允许了就能下载整场」 | 允许不等于文件已送达。再找一遍附件和项目文件；仍没有，就只请裁 10–16 分钟空白段 |
| 同一长文件再传一次，空洞还在 | 「系统这次会转全」 | 内置 ASR 的 VAD 是稳定的；空洞不会自己消失 |
| 凭文件名猜上下午 | 尾缀 3 当下午场 | 问用户或对议程。本场：**尾缀 3 = 上午场** |
| 空白段还没波形 | 按题目用模型「补写」发言 | 禁止伪造会议记录 |

---

## 硬规则

1. **`<AUDIO>` 标签 ≠ 磁盘上的原文件。** 每次先查附件和项目文件。只有转写文本、没有波形时，不能做二次识别。用户允许访问原音频时也同样先找文件，不要把它当成已经能听。
2. **时间戳跳跃 ≥ 60 秒，或连续 ≥ 60 秒没有可用词 = 大段无法识别。** 录音转文字时由 `conference-paragraph-transcript` 自动启用本技能，不要先问用户。禁止写成终稿「无有效转写 / 未录到」。不足 60 秒的零星听不清不启用。
3. **先扫 RMS，再处理。** 能量不低 → 走上面四步；接近底噪 → 才可标「可能话筒未开」，仍不编造内容。
4. **禁止把强频谱降噪当第一步。** 禁 `afftdn`、`arnndn`、重 `dynaudnorm`、激进 `noisereduce`。
5. **二次识别必须关 VAD。** 默认阈值会再次丢掉同一段。
6. **大文件常常进不了沙箱。** 约 70 分钟 / 68 MB 级可以；约 100 分钟以上整场经常只有 `<AUDIO>`。用户说「允许访问原音频」时，先在附件和项目文件里再找一次原件；找到就只对空白段二次识别。仍没有，不要反复要整场，改为请用户 **裁 10–16 分钟片段**（约 10–15 MB）。允许访问不是一条新的下载通道。
7. **场次不要靠文件名猜。** 用时长 + 议程 PDF + 用户确认。不确定就问一句。
8. **发言人：** 先对议程 PDF；对不上就用「发言人 + 编号」，不要猜名字。
9. **空白段未恢复前，不得用大模型补写发言内容。** 只标时段、议程上谁在讲、能量是否仍在。
10. **工作底稿用原整场时间轴**，不要用切片内 00:00。终稿不带时间戳，改按 `conference-paragraph-transcript` 收成整段。英文终稿的中文译文放在全部英文之后，结构对应，不摘要。

---

## 工作流

脚本路径相对于本技能根目录。

### 0. 文件是否在磁盘

```bash
ls -lah /workspace/attachments/
find /workspace /tmp -iname '*.m4a' -o -iname '*.mp3' -o -iname '*.wav'
```

| 现象 | 含义 | 下一步 |
|---|---|---|
| 有 m4a，大小与时长匹配 | 可做能量扫描 + 二次识别。用户已允许访问原音频，不要再问 | 只切空白段，步骤 1 |
| 聊天有 `<AUDIO>`，磁盘和项目文件都没有原件 | 平台只送了转写。允许访问不能把文件变出来 | 请用户裁空白段再传，**不要再要整场** |
| 有文件但 ASR 时间轴跳号 | 典型 VAD 丢弃 | 步骤 1–4 |

整场太大时，请用户只传空白段前后各留约 10 秒的切片：

```bash
ffmpeg -ss 00:30:20 -t 00:12:00 -i "源.m4a" -c copy gap_3020_4220.m4a
```

已验证能进磁盘：约 7 MB 短片、约 68 MB / 73 分钟。整场 ~100 分钟+ 经常失败。

### 1. 按秒扫能量

从 Grok `<AUDIO>` 或已有文稿里找出时间戳跳跃。对每个跳跃：

```bash
python3 scripts/scan_energy.py --input "/path/to.m4a" --start 1827 --end 2533
```

- RMS **不接近静音** → 人声在，进入步骤 2
- RMS **接近底噪** → 才可以标「可能确实无发言 / 话筒未开」，仍不编造内容

无 Python 依赖时：`ffmpeg -ss START -t DUR -i "$IN" -af volumedetect -f null -`  
`mean_volume` 在 -40 dB 以上就不要当静音。

### 2. 轻处理切片（不要降噪）

```bash
python3 scripts/extract_light.py \
  --input "/path/to.m4a" \
  --start 1827 --duration 706 \
  --gain 10 \
  --output /tmp/audio_work/gap_light.wav
```

等价 ffmpeg（**禁止**加 `afftdn` / `arnndn` / 重压缩）：

```bash
ffmpeg -y -ss 1827 -t 706 -i "源.m4a" \
  -af "highpass=f=100,lowpass=f=7000,volume=10dB" \
  -ar 16000 -ac 1 -c:a pcm_s16le -f wav -bitexact /tmp/audio_work/gap_light.wav
```

增益 8–10 dB 为默认；削波再降到 6 dB。12 分钟以上切成 **重叠 10–15 秒** 的 3–4 分钟块，避免识别器中段再丢。

### 3. 二次识别（关 VAD）

```bash
python3 scripts/retranscribe.py --input /tmp/audio_work/gap_light.wav --language en
```

要点：`vad_filter=False`；`no_speech_threshold=0.2`（仍丢则 0.1）；`beam_size=5`；`initial_prompt` 填本场术语（见 `references/recipes.md`）。优先 `faster-whisper`，模型至少 `small.en` / `small`。

### 4. 贴回工作底稿，再出终稿

工作底稿：

- 时间码用 **原整场时间轴**
- 发言人对议程；吃不准就「发言人 + 编号」
- 仍听不清的词标 `[unclear]`，不补法律观点
- 挽回后标明「本段为轻处理 + 关 VAD 二次识别」

然后按 `conference-paragraph-transcript` 出终稿：去掉时间戳，同一人收成完整段落；正文为英文时，整篇中文接在英文后面。用户没再要时间戳，就不要把底稿直接交出去。

贴稿用语：

错误：`［约 30:27–42:13 无有效转写，约12分钟。按议程此时段主要为叶斌发言。］`

正确（尚未拿到波形时）：

> ［30:27–42:13 自动转写空白，约 12 分钟。议程此时段为叶斌。会场噪声下人声应仍在，属 VAD 丢弃，待原音频或切片二次识别。禁止按题目补写正文。］

---

## 禁止清单

| 不要 | 为什么 |
|---|---|
| 把 ASR 跳号写成「没录到」 | 下午场 RMS 证明人声还在 |
| 先 `afftdn` / 强去噪再识别 | 辅音被抹掉，比原声更差 |
| 二次识别仍开 VAD | 会再次丢掉同一段 |
| 要求用户反复上传 100 分钟整场 | 沙箱经常只收转写不收原文件；内置 ASR 空洞不变 |
| 用模型按议程「补写」发言 | 伪造会议记录 |
| 凭文件名断定上下午 | 尾缀 3 是上午场，须以用户/议程为准 |
