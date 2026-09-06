# Silent Gemini video checks

Read the current [video guide](https://ai.google.dev/gemini-api/docs/video-understanding) before selecting a model, processing mode, or media limits. Use Google's official SDK or documented REST API. Do not hardcode a model from an old example.

## Access and scope

Use `GEMINI_API_KEY`, `GOOGLE_API_KEY`, or a key location explicitly authorized by the user. Keep credentials out of chat, command arguments, saved requests, and public artifacts. Do not search unrelated credential stores.

Respect authorization for the chosen video, external transfer, and API spend. Installing this skill grants none of those permissions. Use a bounded request for the agreed video or range; do not repeat a full-video request merely to reformat its answer.

## Inputs

- For a supported public YouTube URL, submit the documented video URI input directly. No local player or media upload is needed.
- For a local file, inspect duration, size, and audio/video streams with `ffprobe`. Upload only that file through the Files API. Poll until usable, fail on processing errors, and impose a deadline.
- Prefer full media for a full-video request. For targeted checks, use supported start/end offsets and retain the original timeline. If segmentation is needed, disclose it and avoid counting overlap twice.
- Use static processing for an overview. Use agentic processing only when the task benefits from it and the model supports it. Claim agentic processing only when the response contains corresponding processing-call and processing-result evidence.

## Ground the request

Ask the model to examine the actual visuals and audio, answer the user's question, and cite useful timestamps. Require it to distinguish observations from interpretation, flag unreadable text or unclear speech, and state accessible modalities and coverage. If media access fails, it must report failure rather than infer content from a title.

For a clip boundary check, ask what is said and shown immediately before and after each proposed boundary. Estimated model timestamps remain estimates.

## Read back and clean up

Check the interaction's final status before reporting completion. Prefer the SDK's documented text accessor. For REST responses, inspect the documented response shape: this workflow has encountered text inside `steps` entries of type `model_output`, under `content` entries of type `text`. Do not assume a top-level `output_text` or `outputs` field always exists. Do not display thought records or opaque signatures.

Preserve the request scope, completion status, model, usage, and final text when an evidence artifact is useful. Exclude credentials. Video input accounting supports that video was submitted; it does not independently verify every scene claim or timestamp. Inspect conflicting metadata before accepting model conclusions.

For uploaded local media, use a `finally` cleanup path that deletes only files created for this analysis, within the authorized scope. Check deletion success and report failures. Preserve source footage. A direct public YouTube URI creates no Files API upload to delete.

References: [Video understanding](https://ai.google.dev/gemini-api/docs/video-understanding), [Files API](https://ai.google.dev/gemini-api/docs/files), [API keys](https://ai.google.dev/gemini-api/docs/api-key).
