# 轻处理 + 关 VAD 配方

## 为什么强降噪更差

会议室噪声不是平稳白噪声。`afftdn`、重 `dynaudnorm`、高 `prop_decrease` 的 `noisereduce` 会把摩擦音、词尾辅音抹成糊状，Whisper 更难认。

下午场对比（海淀校区 2）：

- 轻处理（高通 100 Hz + 增益 8–10 dB）能读出李光麒关于补贴追溯 / CRRC / Article 16 的句子。
- 强降噪后辅音糊掉，识别更差。

## ffmpeg（默认）

```bash
ffmpeg -y -ss START_SEC -t DUR_SEC -i "$IN" \
  -af "highpass=f=100,lowpass=f=7000,volume=10dB" \
  -ar 16000 -ac 1 -c:a pcm_s16le -f wav -bitexact "$OUT"
```

- 增益默认 10 dB，削波则改为 8 或 6。
- `-bitexact` 避免 `WAVE_FORMAT_EXTENSIBLE`，方便后续工具读。
- **不要**加：`afftdn`、`arnndn`、`agate`、重 `acompressor`、`dynaudnorm=f=150`。

## 能量扫描

按秒算 RMS。假空白的特征：ASR 无字，但 RMS 明显高于文件头尾纯噪声底。

```bash
python3 scripts/scan_energy.py --input "$IN" --start 1827 --end 2533
```

无 Python 依赖时：

```bash
ffmpeg -ss 1827 -t 706 -i "$IN" -af volumedetect -f null -
```

看 `mean_volume` / `max_volume`：若 mean 在 -40 dB 以上，不要当静音。

`scan_energy.py` 把音频解成 raw s16le 再算，避免 WAV 头把 PCM 偏移、假报静音底。

## faster-whisper

```python
from faster_whisper import WhisperModel
model = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=2)
segments, info = model.transcribe(
    "gap_light.wav",
    language="en",
    vad_filter=False,
    no_speech_threshold=0.2,
    beam_size=5,
    word_timestamps=False,
    initial_prompt=(
        "EU trade law conference. Terms: Foreign Subsidies Regulation, FSR, "
        "CSDDD, CBAM, ACI, NIS2, Cyber Resilience Act, Brussels effect, "
        "open strategic autonomy, WTO, state aid, distortion, China."
    ),
)
```

中英夹杂会场把 `language` 去掉或设 `zh` 试一段，取可读性高的。仍大段空则 `no_speech_threshold=0.1`。

`retranscribe.py` 已写好上述参数。

## 长空白切块

12 分钟以上切成 3–4 分钟块，块间重叠 10–15 秒，贴稿时用原整场时间轴去重。
