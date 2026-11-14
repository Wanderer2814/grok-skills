# noisy-conference-asr-recovery

嘈杂会议录音二次识别技能。核心教训：**ASR 时间轴跳了 ≠ 没人说话。**

用户已允许访问原音频。原件在附件或项目文件里时，只对空白段做下面四步，不要先问。整场约 100 分钟以上经常只有自动转写、没有波形；允许访问不能补上这个文件，这时只请裁 10–16 分钟空白段。

1. 按秒扫能量
2. 不要强频谱降噪（`afftdn` 会抹辅音）
3. 只用高通 100 Hz + 增益 8–10 dB
4. 二次识别关闭 VAD，压低 no-speech 阈值

终稿（无时间戳、分人整段、英文在前中文在后）不在本技能里，见 `conference-paragraph-transcript`。识别完成后再走那一份。

## 安装

把本目录当作 Grok / Claude skill 安装（根目录必须有 `SKILL.md`）。

- 脚本：`scripts/`
- 配方：`references/recipes.md`
- 沙箱上传限制：`references/sandbox-audio-limits.md`
- 本场对照：`references/cupl-2026-case.md`
