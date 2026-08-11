# Project contract

Use one folder per original video concept.

```text
<project>/
├── raw/                 # original takes; never modify
├── transcript/          # optional SRT and source transcript
├── screens/             # optional screen recordings
├── assets/              # optional approved proof and brand assets
├── exports/             # rendered drafts
├── qa/                  # derived review frames and QA report
├── edit-brief.json
├── edit-plan-clean.json
└── edit-plan-aggressive.json
```

## Brief fields

`edit-brief.json` records the viewer, promise, spoken hook, desired duration, CTA, claim boundaries, required proof, and available assets. It guides judgment but never authorizes publishing.

## Plan schema

```json
{
  "version": 1,
  "source": "raw/take-1.mp4",
  "output": "exports/video-clean.mp4",
  "segments": [
    {"start": 0.4, "end": 8.2},
    {"start": 9.1, "end": 42.6}
  ],
  "format": {"width": 1080, "height": 1920, "fps": 30},
  "hook": {"text": "THE ONE-LINE PROMISE", "start": 0, "end": 3.5},
  "captions": {"file": "transcript/captions.srt"},
  "audio": {"lufs": -16, "true_peak": -1.5, "lra": 11},
  "notes": ["Explain every non-obvious cut or omission here."]
}
```

`source`, `output`, and caption paths must stay inside the project. Segments may reorder source moments, but they must not overlap unless repetition is deliberate and documented. The renderer uses the listed order.

Captions may instead use inline cues:

```json
"captions": {
  "cues": [
    {"start": 0.0, "end": 1.2, "text": "Short phrase"}
  ]
}
```

Cue times refer to the edited timeline, not the source timeline.

## Variant rule

Keep the clean version close to natural speech. Use the aggressive version for tighter pauses, faster proof, or a different opening treatment. Change one or two editing variables at a time so the variants remain comparable.
