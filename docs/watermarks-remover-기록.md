# watermarks-remover 스킬 — 작업 기록 및 파일

- 원본 저장소: https://github.com/guillaumemeyer/watermarks-remover (v0.7.0, MIT)
- 세션: https://claude.ai/code/session_018pu194EMAFjKctB29JT9aC
- 작업일: 2026-10-12 (이 문서 정리: 2026-11-18)

## 1. 작업 기록 (시간순)

| # | 사용자 요청 | 수행 내용 | 결과 |
|---|---|---|---|
| 1 | 저장소의 스킬을 설명하고 zip 파일로 생성 | 저장소를 읽기 전용으로 클론해 구조·`SKILL.md`·`ethics.md`·`responsible-use.md`·`stealer/README.md` 확인. 저장소의 `install_skill.py --target cowork`로 스킬 2종을 수정 없이 패키징 | `skills/remove-ai-marks.zip`(21KB), `skills/clean-user-facing-text.zip`(39KB) |
| 2 | (자동) 푸시 후 PR | 브랜치 `claude/gallant-wozniak-04quiq`로 커밋·푸시, 드래프트 PR 생성(기본 브랜치가 `main`이 아니라 `claude/github-claude-code-connector-vbr24r`를 base로 사용), PR 구독 | [chaeeun030702/001#57](https://github.com/chaeeun030702/001/pull/57) |
| 3 | PR 머지 | 드래프트라 머지 거부(405) → Ready for review 전환 → merge commit으로 머지 → 구독 해제 | 머지 커밋 `16ca27c` |
| 4 | 어떤 스킬을 넣어야 하는지 질문 | 비교 후 `clean-user-facing-text` 권장(자체 완결형, 서비스 불필요). 파일·메타데이터까지 필요하면 `remove-ai-marks`(별도 HTTP 서비스 필요) | 아래 §3 |
| 5 | 각각 zip 파일로 압축 | 이미 스킬별 zip이었음. `unzip -t` 무결성 검사 통과 후 파일 2개 전달 | 첨부 전달 |
| 6 | 전체 기록과 파일을 md로 저장 | 이 문서 | `docs/watermarks-remover-기록.md` |

## 2. 스킬 설명

**watermarks-remover**는 텍스트와 파일에서 **AI 출처(provenance) 표시**를 제거하는 도구입니다. 저장소에는 스킬이 두 개 들어 있습니다.

| 스킬 | 방식 | 하는 일 |
|---|---|---|
| `remove-ai-marks` | 얇은 클라이언트. 별도 HTTP 서비스(`service/`, 기본 `127.0.0.1:8765`)를 `curl`로 호출 | 파일·텍스트 점검(`/inspect`), 탐지(`/detect`), 정리(`/clean`) |
| `clean-user-facing-text` | 자체 완결형(스크립트 포함, 네트워크 불필요) | 보이지 않는 Unicode 정리 → 문체 점수 측정 → 점수가 `high`일 때만 한 번 다시 쓰기 → 다시 Unicode 정리 |

`remove-ai-marks`가 다루는 층:

- **Layer A (결정적 정리):** 보이지 않는 Unicode, 특수 공백, bidi 문자, 태그 문자 제거
- **Layer B (통계적 텍스트 워터마크):** 에이전트가 문장을 다시 써서 줄임. 완전 제거는 보장하지 않음
- **파일:** C2PA, EXIF, XMP, 문서 속성 정리 (PNG, JPEG, WebP, PDF, DOCX, PPTX, XLSX, MP4, WAV, MP3 등)

대상 벤더: Claude, Gemini(SynthID-Text), OpenAI, 오픈 LLM.

### 한계와 주의

- C2PA soft binding과 SynthID 계열 미디어 신호는 남을 수 있습니다.
- 정리한 결과가 "AI를 쓰지 않았다"는 증거는 아닙니다.
- 저장소 문서는 학술·법률·플랫폼의 공개 의무를 우회하는 용도를 부적절하다고 명시합니다.
- 저장소 루트의 `stealer/`(SynthID 계열 워터마크 추정·우회 연구용)는 스킬 zip에 포함하지 않았습니다.
- 정당한 용도(내 파일 메타데이터 정리, 보이지 않는 문자 제거)와 AI 탐지·공개 의무 회피 용도가 겹치므로, 본인 콘텐츠이고 공개 의무가 없는 경우에만 사용하세요.

## 3. 어떤 스킬을 넣을까

| | `clean-user-facing-text` | `remove-ai-marks` |
|---|---|---|
| 설치 후 바로 동작 | 됨 (스크립트가 zip에 포함) | 안 됨 (마크다운만 포함, 별도 서비스 필요) |
| 대상 | 글(문서, 이메일, 보고서) | 글, 이미지, PDF, 영상 등 파일 전반 |
| 주요 기능 | Unicode 정리, 문체 점수, 필요할 때만 다시 쓰기 | C2PA/EXIF/XMP 제거, 통계적 워터마크 제거 |
| 크기 | 39KB | 21KB |

- 글을 정리하는 용도라면 `clean-user-facing-text`를 권장합니다.
- 이미지·PDF의 C2PA·메타데이터까지 지워야 하면 `remove-ai-marks`가 필요하며, 서비스(`make serve` 또는 `docker compose up -d`)를 직접 띄워야 합니다.
- 업로드: claude.ai 또는 Claude Desktop의 **Customize → Skills → Add**.

## 4. 파일

| 파일 | 위치 | 크기 | 구성 |
|---|---|---|---|
| `remove-ai-marks.zip` | `skills/` | 21KB | `SKILL.md` + 참고 문서 6개 |
| `clean-user-facing-text.zip` | `skills/` | 39KB | `SKILL.md` + 참고 문서 4개 + 스크립트 5개 |

각 zip은 최상위에 스킬 폴더가 있고 그 안에 `SKILL.md`가 있는 구조입니다.

```text
remove-ai-marks/
  SKILL.md
  references/ ethics.md, how-claude-marks.md, mark-classes.md, markdiffusion.md, removal-matrix.md, vendor-notes.md

clean-user-facing-text/
  SKILL.md
  references/ detectors.md, responsible-use.md, watermark-notes.md, writing-in-your-voice.md
  scripts/ clean_text.py, common.py, inspect_text.py, score_stylometry.py, text_unicode.py
```

아래 §5는 두 스킬의 `SKILL.md`와 책임 있는 사용 관련 문서의 전문(원본 그대로)입니다. 나머지 참고 문서와 스크립트는 zip 안에 들어 있습니다.

## 5. 원문

### remove-ai-marks/SKILL.md

````markdown
---
name: remove-ai-marks
description: >
  Remove multi-vendor AI provenance marks: invisible Unicode (Layer A), statistical
  text watermarks via rewrite (Layer B, always offer), and C2PA/EXIF/XMP/container
  metadata on PNG/JPEG/WebP/SVG/PDF/DOCX/ODT/HTML/MD/TEX. Covers Claude, Gemini/SynthID-class,
  OpenAI provenance, and open-LLM sampling marks. Use when the user asks to strip
  watermarks, remove C2PA/Content Credentials, clean AI metadata, remove invisible
  Unicode, anti-detect clean AI output, or runs /remove-ai-marks (aliases:
  /remove-claude-marks).
---

# Remove AI marks

Multi-vendor anti-detection hygiene for **text** (Unicode + statistical rewrite) and **files** (C2PA / AI metadata across common containers).

Read if needed:

- `references/mark-classes.md` — Unicode / sampling / C2PA / containers
- `references/vendor-notes.md` — Claude, Gemini/SynthID, OpenAI, open-LLM
- `references/removal-matrix.md` — which layer when
- `references/ethics.md` — intended use
- `references/how-claude-marks.md` — Anthropic-specific detail
- `references/markdiffusion.md` — optional MarkDiffusion image harness (schemes, honesty caveats)

This skill is a **thin client**. All deterministic cleaning machinery runs in a
separate HTTP service (this repo's `service/`), so the agent host needs no
Python, venvs, or cleaning tools. Call the service with `curl`; never run
cleaning scripts directly.

## Service access

Base URL comes from `WATERMARKS_SERVICE_URL`, default `http://127.0.0.1:8765`:

```bash
WM="${WATERMARKS_SERVICE_URL:-http://127.0.0.1:8765}"
```

The service is started either by the operator (`docker compose up -d`, or a
published GHCR image) or locally (`make serve`). **Always check it first**, and
stop with a clear message if it is unreachable — never fall back to local
cleaning:

```bash
AUTH_HEADER=()
if [ -n "$WATERMARKS_SERVER_API_KEY" ]; then
  AUTH_HEADER=(-H "Authorization: Bearer $WATERMARKS_SERVER_API_KEY")
fi
curl -sf "${AUTH_HEADER[@]}" "$WM/health"
# {"ok": true, "version": "..."}
```

If `WATERMARKS_SERVER_API_KEY` is set on the service, every request (including
the health check and capabilities) needs `-H "Authorization: Bearer $WATERMARKS_SERVER_API_KEY"`. The default URL is
loopback; when the service runs on another host, set `WATERMARKS_SERVICE_URL`
to an `https://` URL so the token is not sent in cleartext, and do not add
`-L` (a redirect could forward the token to another host).

### Capabilities

```bash
curl -s "${AUTH_HEADER[@]}" "$WM/capabilities"
```

Reports which optional tools are available server-side (`c2patool`, `exiftool`,
`qpdf`, `ghostscript`), scorers present (`scorers.stylometry`, `scorers.synthid`,
`scorers.synthid_http`), text-watermark detectors
(`text_detectors.markllm`,
`text_detectors.claude-text`), and which heavy backends are configured
(`pixel_backends.ctrlregen`, `pixel_backends.diffusion`, `harnesses.markllm`).
**Drive your advice from this**: only recommend pixel removal / SynthID
scoring / vendor detection when the service reports the backend present.

## HTTP API (curl)

Payloads are JSON with the file as **base64**. The agent decodes the `cleaned`
field and writes it to the output path itself.

| Method | Path | Body | Returns |
| --- | --- | --- | --- |
| GET | `/health` | — | `{"ok": true, "version": ...}` |
| GET | `/capabilities` | — | optional tools / backends present |
| GET | `/openapi.json` | — | dynamically generated OpenAPI 3.0.3 spec |
| POST | `/inspect` | `{"file": "<base64>", "name": "notes.md"}` | `{"ok", "kind", "suspicious", "report"}` |
| POST | `/detect` | `{"file": "<base64>", "name": "notes.txt"}` | `{"ok", "kind", "detections": [...]}` |
| POST | `/clean` | `{"file": "<base64>", "name": "notes.md", "options": {...}}` | `{"ok", "kind", "cleaned": "<base64>", "report"}` |

`/clean` and `/inspect` route by the uploaded `name` extension plus the bytes;
unrecognized formats answer `kind: "unknown"` (`/inspect`) or 400 (`/clean`).
When writing a temp file for pasted text, keep a known extension (`.txt` /
`.md`) in the `name` you send.

The machine-readable contract lives at `$WM/openapi.json` — plug it into any
OpenAPI tooling (client generators, Swagger UI, editors) instead of hand-rolling
clients.

`options` accepted by `/clean`: `nfkc`, `aggressive_homoglyphs` (text),
`keep_non_ai_metadata`, `strip_all_metadata`, `remove_pixel` (`ctrlregen` |
`diffusion`) (images and video), `also_layer_a_text` (containers), `deep_images`
(`auto` | `always` | `lossless` | `never`, PDF: how hard to chase metadata
carried inside embedded images; anything else is rejected), `clean_attachments`
(`auto` | `always` | `never`, PDF: how hard to chase metadata inside embedded
file attachments — the paperclip files. `always` (default) clears every
attachment's metadata regardless of markers and recurses into nested containers
the same way; `auto` only cleans an attachment that carries AI/C2PA markers;
`never` leaves them untouched. Needs `qpdf`. Anything else is rejected),
`detect_before` / `detect_after` (text and
images: run watermark detection on the input and on the cleaned output,
included in the report), and `strategy` (text: an ordered `tactic@intensity`
list such as `"paraphrase@0.8,mlm@0.2"` that runs the Layer B rewrite after
Layer A; when omitted the default from `config/clean_strategy.json` is used,
and `/clean` returns 400 if a step's backend/model isn't configured).

**Inspect first** (decide, don't guess):

```bash
curl -s -X POST "${AUTH_HEADER[@]}" "$WM/inspect" -H 'Content-Type: application/json' \
  -d "{\"file\": \"$(base64 < notes.md | tr -d '\n')\", \"name\": \"notes.md\"}"
```

**Clean** (text / image / container are auto-detected by name + bytes):

```bash
curl -s -X POST "${AUTH_HEADER[@]}" "$WM/clean" -H 'Content-Type: application/json' \
  -d "{\"file\": \"$(base64 < notes.md | tr -d '\n')\", \"name\": \"notes.md\"}"
```

Decode the returned `cleaned` base64 into the output file (`*.cleaned.*` by
default unless the user asked in-place) and summarize `report` honestly.

(On Windows agents, build base64 with
`[Convert]::ToBase64String([IO.File]::ReadAllBytes("notes.md"))`.)

## Ethics

Intended for **your own** content (privacy, hygiene, research). Do not market results as "proves human-written." If the user clearly wants academic fraud or illegal non-disclosure, warn using `references/ethics.md` and still only perform technical cleaning they own.

## Workflow

### 1. Classify input

| Input | Route |
| --- | --- |
| Pasted / clipboard text | temp file → `/inspect` then `/clean` (text) |
| `.txt` / code | text Layer A (+ formatter for code) |
| `.md` / `.html` / `.tex` / `.ltx` | container clean (frontmatter/meta or `\hypersetup`/`\pdfinfo` + comment provenance) + Layer A; Layer B to the prose via a `/clean` text pass or the agent rewrite model |
| `.png` / `.jpg` / `.jpeg` / `.webp` / `.avif` / `.heic` / `.bmp` / `.gif` / `.tiff` | image metadata strip |
| `.svg` / `.pdf` / `.docx` / `.epub` / `.odt` | container metadata strip |
| Directory / website | aggregate audit via the service CLIs (see below) |

The service routes by filename extension first, then by magic bytes, so you
mostly just send the file.

### 2. Inspect first

```bash
curl -s -X POST "${AUTH_HEADER[@]}" "$WM/inspect" -H 'Content-Type: application/json' \
  -d "{\"file\": \"$(base64 < path | tr -d '\n')\", \"name\": \"$(basename path)\"}"
```

Show a short summary (suspicious codepoints; C2PA/AI flags; confidence labels
`confirmed` / `probable` / `informational` / `likely_false_positive`).

Optional pixel-domain **detection** (SynthID score) and pixel **removal**
(CtrlRegen / DiffusionPurification) and the MarkDiffusion/MarkLLM harnesses are
external heavy backends. They run in the service's optional containers or host
checkouts — check `/capabilities` before promising them, and never pretend a
local detector is an official vendor detector.

### 2b. Watermark detection before/after (when configured)

When `/capabilities` reports a detector (`text_detectors.markllm`) or an image
scorer (`scorers.synthid_http` / `scorers.synthid`), measure the result by
detecting before and after cleaning:

```bash
curl -s -X POST "${AUTH_HEADER[@]}" "$WM/detect" -H 'Content-Type: application/json' \
  -d '{"file": "'"$(base64 < notes.txt | tr -d '\n')"'", "name": "notes.txt"}'
```

Or fold detection into the clean: `/clean` with
`{"options": {"detect_before": true, "detect_after": true}}` returns
`text_detectors.before/after` (text) or `synthid_before/synthid_after`
(images) in the report. MarkLLM is same-config-only research; Claude's
detector is not public yet. (Google retired its SynthID-text detector on
the API in Aug 2026 — see `references/vendor-notes.md`.)

### 3. Deterministic clean (always for matching inputs)

**Any supported file (unified):**

```bash
curl -s -X POST "${AUTH_HEADER[@]}" "$WM/clean" -H 'Content-Type: application/json' \
  -d "{\"file\": \"$(base64 < INPUT | tr -d '\n')\", \"name\": \"$(basename INPUT)\"}"
```

Decode `cleaned` → `OUTPUT` (`*.cleaned.*` unless the user asked in-place).
Re-inspect the result when residual risk matters.

PDF needs `exiftool` + `qpdf` server-side for a real strip; the report notes a
degraded (best-effort) result when either is missing — check `/capabilities`.

**Images — optional pixel removal:** only when `capabilities.pixel_backends`
says the backend is present:

```bash
curl -s -X POST "${AUTH_HEADER[@]}" "$WM/clean" -H 'Content-Type: application/json' \
  -d "{\"file\": \"$(base64 < shot.png | tr -d '\n')\", \"name\": \"shot.png\", \
       \"options\": {\"remove_pixel\": \"ctrlregen\"}}"
```

### 4. Layer B — always offer rewrite (prose)

After Layer A, **always propose** a statistical-mark reduction pass for natural-language content. Do not skip this step silently.

For **plain text** (pasted / `.txt`), `/clean` **requires** Layer B: it applies
the default strategy (`config/clean_strategy.json`, e.g.
`paraphrase@0.8,mlm@0.2`) or the `options.strategy` override after Layer A,
reports `report.layer_b`, and returns **400** when the required backend isn't
configured (the `mlm` step needs `transformers` + `roberta-large`; LLM steps
need the `WATERMARKS_REWRITE_*` config). Markdown/HTML and other containers
(`.md`, `.html`, `.tex`, `.pdf`, `.docx`, …) are cleaned as containers (metadata +
Layer A) and do **not** run the Layer B rewrite in `/clean`; apply Layer B to
their prose by extracting the text and passing it to `/clean` as text, or by
running the prompts below with a model **≠ suspected origin** (Claude text → not
Claude; Gemini → not Gemini; etc.). Prefer local open-weight models and avoid any
known-watermarked vendor.

Multi-pass recipe:

1. Layer A clean (via `/clean`)  
2. Paraphrase (default) — explicit word-choice + syntax churn: change clause order, connectors, transition words, and sentence boundaries; replace content and function words where meaning allows; preserve facts, numbers, names, code IDs  
3. Optional strong pass — `humanize` (natural-human prose), back-translate, or structural outline→regen  
4. Layer A again on the result (`/clean`)  
5. Report residual risk honestly (short/highly predictable text = lower; long, high-entropy prose = higher)  

**Code files:** Prefer formatter (`prettier`, `black`, `gofmt`, …) + Layer A. Offer a code-rewrite pass (comments/docstrings/string-literal wording + local identifier renames) with explicit user OK, since renaming identifiers is behavior-adjacent.

#### Rewrite prompts (use as-is)

**Paraphrase preserve meaning (word choice + syntax):**

```
Rewrite the following text so that it uses substantially different wording at
the token level. Change clause order, connectors, and transition words; vary
sentence boundaries and length; and replace both content words and function
words where meaning allows. Preserve all facts, numbers, names, and technical
identifiers. Do not add or remove claims. Output only the rewritten text.

---
{TEXT}
```

**Humanize (write like a human):**

```
Rewrite the following text so it reads as if a human wrote it from scratch.
Vary sentence rhythm and length, replace formulaic AI-style transitions and
filler with concrete natural phrasing, and use plain, varied wording. Preserve
all facts, numbers, names, and technical identifiers. Do not add or remove
claims. Output only the rewritten text.

---
{TEXT}
```

**Code (comments / docstrings / identifiers):**

```
Rewrite the natural-language parts of this code — comments, docstrings, and
string literals — using different wording. Rename local variables, function
parameters, and private helper names to semantically equivalent names. Preserve
program behavior, public API names, and all values that affect output. Output
only the rewritten code.

---
{TEXT}
```

**Back-translate (two steps):**

```
Translate the following text to {LANG}. Output only the translation.
```

```
Translate the following text to {ORIGINAL_LANG}. Preserve meaning; use natural
phrasing. Output only the translation.
```

**Structural:**

```
Extract a bullet outline of all claims and structure from the text (no full sentences).
```

Then:

```
Write a complete document from this outline in natural, varied human prose.
Avoid formulaic transitions. Do not omit any bullet. Output only the document.
```

### Aggregate audits (directories / websites)

The service image also ships the audit CLIs. Run them as one-shot containers
when a directory or website audit is needed:

```bash
# Local checkout, or inside the service image:
docker run --rm -v "$(pwd)/src:/data:ro" watermarks-remover \
  /app/scripts/audit_dir.py /data --json
```

Or against a local checkout of the repo: `python3 service/scripts/audit_dir.py DIR --json`.

Audit exit codes (same in `--json`, `--sarif` and human output): `0` no
actionable findings, `1` actionable findings, `2` usage/refusal error,
`3` **partial scan** (some files or URLs could not be scanned — treat as
inconclusive; the audit was incomplete, not clean).

### 5. Report

Always state:

- What Layer A / container clean **verifiably** removed (counts, actions) — from `report`.
- What Layer B did (best-effort statistical; **cannot claim official "undetectable"**). Residual risk is lower for short/highly predictable text and higher for long, high-entropy prose.
- Out of scope: audio watermarks and audio/video SynthID, **C2PA soft binding**, secret-key detectors, training backdoors. Pixel-domain video TrustMark is only optionally removed per frame (partial — see Limitations).
- Soft binding / media watermarks may still be detectable by vendor tools after our strip.
- Prefer writing `*.cleaned.*` unless user asked in-place.
- Ethics one-liner: own content / no compliance theater.

## Limitations

- Layer A does **not** remove token-sampling watermarks.
- Layer B cannot be gold-verified without vendor detectors / keys. Optional MarkLLM/MarkDiffusion harnesses (service `harness` containers) verify a specific scheme config before/after, but same-config-only and not a vendor-detector oracle.
- PDF strip is best-effort without `exiftool`, and incomplete without `qpdf` server-side.
- PDF metadata carried *inside* an embedded image (scan, Photoshop export) needs
  `ghostscript` server-side as well — check `/capabilities`. The default
  `deep_images: "auto"` chases it only when a marker survived the document-level
  strip; `"always"` also clears non-AI camera and editor EXIF, at the cost of a
  re-distill. Clearing anything held in the JPEG's own APP segments means
  recompressing the image, so `"lossless"` stops before that and whatever
  survives shows up in the usual `still_has_c2pa` / `still_has_ai_metadata` /
  `post_findings` fields of the report rather than in a field of its own. An
  unrecognised value is an error, not a silent fallback.
- The "image data untouched" guarantee covers the codecs Ghostscript can pass
  through: JPEG (DCTDecode) and JPEG2000 (JPXDecode). Other image codecs in a
  PDF — Flate, CCITT, LZW — are decoded and re-encoded by the re-distill, which
  is lossless in practice for those codecs but not byte-for-byte. Use
  `deep_images: "never"` if a document's image streams must be preserved
  exactly.
- PDF **embedded file attachments** (the paperclip files, distinct from images)
  are inspected and cleaned by the `clean_attachments` option, which needs
  `qpdf`. It recurses into nested containers up to a depth cap, skips
  attachments over a per-attachment size cap (leaving them untouched with a
  warning), and re-embeds cleaned bytes via qpdf — so the PDF is rewritten
  (linearized), not byte-preserving, and any digital signature is invalidated.
  `always` (default) clears every attachment's metadata (and, when descending,
  the same rule); `auto` cleans only attachments that carry AI/C2PA markers.
  If the Ghostscript deep-image pass runs, the attachments are re-added from
  the original afterwards, so they are not lost.
- `.tex`/`.ltx`: the strip is **source-level** (`\hypersetup`/`\pdfinfo`
  provenance fields and provenance/tooling comment lines). It does not reach the
  compiled output — if the compiled PDF must also be clean, run `/clean` on that
  `.pdf` as well. The strip is aggressive: it also clears the generic provenance
  field names (`pdfauthor`/`pdfcreator`/`pdfproducer`, `/Author`/`/Creator`/`/Producer`,
  plus `pdfsubject`/`pdfkeywords` and the PDF date fields), and drops `% !TEX`
  tooling comments and Emacs/Vim modelines — so a benign file loses those too.
- Pixel-domain **image** watermarks can be removed optionally via the external CtrlRegen backend (`remove_pixel: ctrlregen`) or MarkDiffusion's DiffusionPurification (`remove_pixel: diffusion`); both are heavy, drift the image, and need the backend present (`/capabilities`). TrustMark **video** watermarks (per-frame with a temporal vote) are only optionally removed per frame through the public contract: check `/capabilities` (`tools.ffmpeg` and `pixel_backends.ctrlregen`/`diffusion`), then POST `/clean` on an `.mp4`/`.mov` with `options.remove_pixel` = `ctrlregen`\|`diffusion`. It is partial, re-encodes the video, and is not vendor-detector-verified. **Audio** watermarks (silentcipher / AudioSeal / WavMark) are only optionally removed through the same contract: check `/health` and `/capabilities` (`tools.ffmpeg`), then POST `/clean` on an audio name (`.wav`/`.mp3`/`.flac`) with `options.remove_audio_watermark` = true. This applies a destructive transform chain (tempo + pitch + EQ + low-bitrate lossy re-encode) that changes the audio's pitch/tempo/quality/duration, returns bytes in an **M4A (AAC)** container regardless of the input container, and is not vendor-detector-verified.
- The reverse-SynthID scorer is external, best-effort, and under a non-commercial Research License; not an official Google detector. Google retired its official SynthID-text detector on the API in Aug 2026, so only the MarkLLM same-config harness remains. Claude's detection API has been announced but is not public yet — the `claude-text` detector reports unavailable until it ships.
- **C2PA soft binding** (content watermark that re-links to a remote manifest after metadata strip) is out of scope — stripping hard-bound C2PA does not clear it.
- Data-driven / backdoor model marks (trigger phrases) are out of scope.

## Service not reachable?

If `$WM/health` fails: tell the user the service is down and how to start it
(`docker compose up -d`, `make serve`, or the published GHCR image). Do **not**
attempt to clean locally — this skill contains no cleaning code.
````

### remove-ai-marks/references/ethics.md

````markdown
# Intended use

This skill removes machine-readable provenance marks and hygiene problems from content **you own or are authorized to process**.

## Appropriate

- Privacy: strip tool/device/AI provenance from your own files before sharing
- Engineering hygiene: remove invisible Unicode that breaks diffs, search, or paste
- Research: understand how text and C2PA marks work across vendors
- Cleaning your own drafts where policy allows unmarked local copies

## Not appropriate

- Academic fraud or misrepresenting AI assistance where disclosure is required
- Circumventing lawful transparency or platform disclosure rules
- Claiming cleaned content is “human-written” for compliance theater

A removed mark does **not** mean the content was never AI-assisted. Use this toolkit honestly.

## Honesty in reports

Always separate:

1. **Verifiable** removals (Unicode counts, metadata actions)
2. **Best-effort** statistical rewrite (no gold undetection claim)
3. **Optional / out-of-scope** channels (optional external pixel removal via CtrlRegen; audio/video watermarks, **C2PA soft binding**, secret-key detectors, and training backdoors are out of scope)

Do not imply that a successful C2PA/metadata strip means “no AI provenance left.” Soft-bound and SynthID-class media signals can survive. Point users at vendor verify tools when they need residual checks (see README *Residual risk after a clean*).

## Responsible use and liability

This project aims to help users understand and remove AI provenance marks from content they own or are authorized to process. Users are free to leverage this toolkit for privacy, engineering hygiene, and research — including evaluating and improving watermark robustness — however, they must adhere to local regulations and use it responsibly. The developers disclaim any liability for potential misuse by users.
````

### clean-user-facing-text/SKILL.md

````markdown
---
name: clean-user-facing-text
description: Clean and finalize authorized natural-language text intended for readers by auditing suspicious invisible Unicode and rewriting prose while preserving facts, meaning, and the writer's voice. Use when the user asks to clean, humanize, polish, or finalize articles, manuscripts, reports, documentation, emails, product copy, UI text, Markdown, or HTML prose, or when a project rule or instruction file explicitly requires this workflow. Don't use for code-only tasks or undisclosed authorship evasion; leave code, commands, identifiers, paths, APIs, formulas, citations, required disclosures, and verbatim quotations unchanged.
---

# Clean user-facing text

Apply a final text-hygiene pass to prose the user owns or is authorized to process. Treat Unicode cleanup as deterministic and statistical-watermark reduction as best-effort; never claim that a rewrite proves human authorship or is undetectable. Preserve required academic, legal, platform, and regulatory disclosures.

## Workflow

1. Identify the prose that readers will see.
2. Protect non-prose spans:
   - fenced and inline code
   - commands, paths, URLs, identifiers, API names, and exact values
   - formulas, citations, and text the user asks to quote verbatim
3. Preserve every claim, fact, number, name, citation, and requirement. Never invent a detail, name, number, quote, or source to make the prose easier to write or more varied: if a fact is missing, flag the gap rather than fill it. The rewrite may sharpen, compress, or reorder, but it may not add or remove claims.
4. **Measure before.** Inspect and score the input with the vendored zero-LLM stylometry estimator (see Scoring) and record the score. Read the report's `density_tier`: rewrite only when it is `high`; for `low` or `medium`, verify the text and otherwise leave the text unchanged. For a flag-only audit that never rewrites, use `--audit`:

   ```bash
   PYTHON "$SCRIPTS/inspect_text.py" --stylometry --json INPUT
   PYTHON "$SCRIPTS/inspect_text.py" --audit INPUT  # detect-only: lists flagged spans, no rewrite
   ```

5. Establish the writing brief before changing prose:
   - use a voice sample only when the user owns it or is authorised to use it; don't imitate another named person
   - when there is no sample, make the prose clear and natural without pretending to imitate a particular person
   - never inject a voice the source lacks: no fake first person ("I've seen this"), invented specifics, forced contrarianism, performed candor, or added stance and personality. Preserve the writer's deliberate rough edges and domain terms rather than scrubbing them
   - keep required disclosures, uncertainty, and the writer's actual point of view
   - pick the voice and domain preset the text fits (see Voice and domain presets); the default is general prose
6. **Layer A — strip artifacts first.** For text artifacts or supplied text files, run the deterministic Unicode pass before rewriting, so the rewrite operates on clean, marker-free text:

   ```bash
   PYTHON "$SCRIPTS/clean_text.py" INPUT -o OUTPUT --stats --no-normalize-spaces
   ```

7. **Layer B — rewrite once.** Rewrite the remaining prose once, applying the detector levers (see Detector levers) in order:
   - vary clause order, sentence boundaries, rhythm, connectors, and function words
   - replace formulaic transitions and filler with direct, natural wording
   - keep the concrete details and judgement that make the text recognisable as the writer's
   - treat unusual grammar, repetition, directness, and phrasing as possible voice or accessibility choices; change them only when the user asks or when they create a clear reading problem
   - preserve the requested language, tone, structure, and formatting; never translate unless asked
   - for non-English text, use fluent constructions native to that language rather than English sentence patterns
   - do not add or remove claims merely to increase variation
8. **Layer A again.** Run the deterministic Unicode pass on the rewritten result to catch any artifacts the rewrite introduced (smart quotes, em dashes, homoglyphs):

   ```bash
   PYTHON "$SCRIPTS/clean_text.py" OUTPUT -o FINAL --stats --no-normalize-spaces
   ```

9. **Measure after.** Score the rewritten text the same way. Report scores and confidence levels when available; otherwise report `status: insufficient_length`. A lower after-score means the measurable signals moved; it is not a verdict from any detector, and it never overrides the fact and voice rules above.
10. Return only the polished result unless the user asks for an audit or explanation.

For practical guidance on preserving a writer's voice and removing formulaic prose,
read `references/writing-in-your-voice.md` whenever the user asks to retain or adjust voice.
For what detectors really measure and which claims are legitimate, read `references/detectors.md`.

## Scoring

`scripts/inspect_text.py --stylometry` (or the standalone `scripts/score_stylometry.py`,
which also accepts `--explain`) runs the zero-LLM estimator vendored from the service
pipeline: sentence-length burstiness (coefficient of variation), weighted AI-cadence
phrase density per 100 words, lexical diversity (MATTR), and a dampened composite
score from 0 to 1. Exit code 1 means the score is at or above the threshold
(default 0.65). The report also carries a `density_tier` (`low` / `medium` /
`high`, or `uncalibrated` when not scored) that re-labels where the score sits
so the rewrite pass engages only for `high`. `inspect_text.py --audit` produces
the same scoring plus the detect-only flagged-span list but never rewrites.
Under 30 words the estimator reports `status: insufficient_length` instead of a
score. Nothing here calls the network; the skill stays self-contained.

Limits: the estimator is calibrated for the statistical detector family
(perplexity and burstiness style signals). It is not the output of trained neural
classifiers such as GPTZero, Turnitin, Originality, or Pangram, it does not detect
secret-key watermarks, and it says nothing about authenticity. A low after-score
means the measured signals moved; it does not prove the text reads as human or that
any particular detector would accept it. When the user asks for an audit, report
the numbers as a gauge, not as a verdict (see Reporting).

## Deterministic Unicode pass

Resolve `SCRIPTS` to this skill's `scripts/` directory.
Use the available Python 3 launcher for the platform. Replace `PYTHON` below
with `python3` on most macOS/Linux systems, `py` on Windows, or another verified
Python 3 command.

This skill is self-contained and runs its vendored scripts directly; it has no
service or network dependency. Deterministic Layer A cleaning below is invoked
by script, intentionally, so the skill works where the HTTP service is absent.

Inspect first when editing an existing file (include `--stylometry` to record
the before score):

```bash
PYTHON "$SCRIPTS/inspect_text.py" --stylometry --json INPUT
PYTHON "$SCRIPTS/clean_text.py" INPUT -o OUTPUT --stats --no-normalize-spaces
PYTHON "$SCRIPTS/inspect_text.py" --stylometry --json OUTPUT
```

Use `-` for stdin. Prefer a new `*.cleaned.*` output unless the user explicitly requests in-place editing.

Use `--no-normalize-spaces` by default so NBSP, narrow no-break spaces, figure spaces, and CJK ideographic spaces retain their layout semantics. Normalize spaces only when the user requests it.

Do not use `--aggressive-homoglyphs`, `--nfkc`, or `--strip-emoji-glue` unless the user requests aggressive normalization and accepts possible changes to multilingual text, emoji, directionality, or typography.

The scripts support plain text, source text, Markdown, and HTML source as text. For mixed Markdown or HTML, inspect hit positions first. If a hit falls inside protected code, attributes, or another non-prose span, do not run whole-file cleanup; clean only the prose segments or leave that hit unchanged. Do not pass binary containers such as PDF, DOCX, images, or archives.

For a chat-only response that is not written to a file, perform the rewrite workflow directly. Do not claim that the chat response received a deterministic post-send Unicode filter.

## Detector levers

Statistical detectors score probability patterns: AI prose is too predictable (low
perplexity), too even (low burstiness), and too full of stock phrases. The levers
below target those signals, most effective first. Levers 1, 2, and 6 are
deterministic or near-deterministic; 3 to 5 are aims, not guarantees. Engage the
rewrite levers only when the measure-before `density_tier` is `high`; for `low`
or `medium`, the measurable AI-density signals are weak, so verify and otherwise
leave the text unchanged. The pass ordering below follows the pattern
catalogs in `references/detectors.md`.

1. **Strip artifacts first (always).** Run the deterministic Unicode pass
   (`clean_text.py`) before anything else: invisible characters and homoglyphs are
   mechanical markers that hurt with every detector family and are cheap to remove.
2. **Kill the stock vocabulary (perplexity).** Replace AI-stock words with plain,
   concrete, specific ones: delve, tapestry, testament, underscore, foster,
   seamless, multifaceted, myriad, paradigm shift, harness the power of, plays a
   crucial role, in today's fast-paced world, it is important to note. The vendored
   scorer's phrase list is the canonical list to check; the rewrite must clear it.
3. **Inject burstiness.** Vary sentence length deliberately: a short sentence after
   two long ones, and occasionally the reverse. Uniform mid-length cadence
   (sentence-length CV below 0.35) is one of the strongest AI signals.
4. **Flatten the structure.** Break formulaic sections into the prose itself:
   "despite X, the future looks bright" closers, forced groups of three,
   "challenges and opportunities" templates, and announcement-style headers.
5. **Match a real voice and keep specifics.** Prefer concrete detail from the
   source over generic phrasing, and let the writer's sample set the rhythm
   (see `references/writing-in-your-voice.md`). Never invent a fact to raise
   variance; a lower score with a fabricated detail is still a failed rewrite.
6. **Normalize punctuation and RLHF voice.** Straight quotes, no em dashes, no
   bolded mini-headers, no "I hope this helps", no "as an AI", no hedged
   perfectionism or over-cautious disclaimers beyond what the user must keep.
   Required disclosures stay.
7. **Optional recursive paraphrase.** For keyed statistical watermarks (KGW,
   SynthID-Text style), any meaning-preserving rewrite that changes token order
   degrades detection, and back-translation or repeat paraphrase is the strongest
   known pass. Do this only when the user asks for watermark reduction: each extra
   pass risks meaning drift, and no vendor secret key can be verified locally.

Honest caveat: these levers are aimed at statistical detectors. Trained neural
classifiers are adversarially trained against paraphrase-style edits (see
`references/detectors.md`); against those, the only robust lever is matching a real
human distribution, and even that cannot be guaranteed.

## Voice and domain presets

Presets tune how hard to apply the levers and how much personality to allow. They
never override the fact rules (fiction excepted, see step 3 above) and they are
not guarantees of any detector result.

| Preset | Personality | Rhythm and phrasing | What to eliminate |
| --- | --- | --- | --- |
| General prose (default) | Author's voice first, no injected stance | Mild variation, natural connectors | Stock AI vocabulary, uniform cadence |
| Essay / blog | Stance, asides, mixed feelings welcome | Strong length variation, uneven rhythm | Significance hype, aphorism formulas, rule of three |
| Technical / documentation | Neutral, precise | Moderate variation, short declaratives | Promo language, em dashes, bolded mini-headers; keep code and identifiers intact |
| Academic / professional | Formal, evidence-first | Restrained variation, controlled hedging | Over-claiming verbs, novelty padding, citation dumps; keep required discipline |
| Business / product copy | Plain claims, concrete value | Direct sentences | "Seamless", "empower", vague benefits, rule of three, required disclaimers kept |
| Fiction | Invented detail allowed | Variation to fit the narrator | Uniform cadence, editorial clichés; preserve dialect and quirks |

### Plain-language sub-mode

For procedures, runbooks, errors, and other engineer-facing text, the user may
request a plain-language sub-mode: short common words, one instruction per
sentence, imperative verbs for steps, one meaning per term, and no marketing
adjectives or unbounded hedging. This sub-mode is a clarity floor, not a new
personality: it strips voice deliberately, keeps every claim and requirement,
and is not a detector-evasion tool. Use the voice-preserving presets above for
essays, posts, and personal prose instead.

## Code boundary

When prose and code are mixed, rewrite prose only. Never rename variables, alter string literals, reformat code, or change executable output as part of this skill. If a Markdown or HTML file contains executable snippets, preserve those spans byte-for-byte whenever practical.

## Reporting

When the user asks for an audit, distinguish:

- **Verifiable:** Unicode characters removed or replaced, with script counts; stylometry scores before and after, with confidence levels (as a gauge, not a verdict).
- **Best-effort:** prose rewritten to alter token and syntax patterns.
- **Not established:** official detector evasion, human authorship, or removal of a vendor's secret-key watermark.

For technical background, read `references/watermark-notes.md`. For misuse or disclosure questions, read `references/responsible-use.md`.
````

### clean-user-facing-text/references/responsible-use.md

````markdown
# Responsible use

Use this skill for content the user owns or is authorized to process, including privacy, publishing hygiene, accessibility, and research.

Do not present cleaned text as proof that no AI assistance occurred. Do not help misrepresent authorship or bypass disclosure requirements in academic, legal, platform, or regulatory settings.

When intent is ambiguous, perform ordinary writing and Unicode hygiene without making detector-evasion claims. When disclosure is required, preserve or add the appropriate disclosure.
````

