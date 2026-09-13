# Delivery Contract

Create one self-contained folder:

```text
<project>-deliverables/
├── analysis/
├── longform/       # optional
├── midform/        # optional
├── shortform/      # optional
├── micro/          # optional
├── carousels/      # optional
├── packaging/      # optional
├── written/        # optional
├── distribution/   # optional
└── delivery-manifest.json
```

Use relative paths inside the folder. Record the absolute read-only source path and SHA-256 for a local source. The manifest uses schema version 1 and declares `project`, `source`, `requested_modules`, `opportunity_inventory`, `outputs`, and `documents`.

Every rendered video declares its master path, hash, render version, caption state, edit mode, edit record or script, exact-source transcript, boundary audit when cuts were made, post-render join audit, caption and hook-overlay QC, package, and media QC.

Every carousel declares editable source, slides, hashes, dimensions, contact sheet, copy, caption, sources, alt text, and QC.

After external delivery, save a readback beside—never inside—the delivery folder. Record the account, destination, sharing state, observed status, expected and observed counts, basenames, and representative preview. Delivery never authorizes publication.

## Editable review handoff

Keep a private project record beside the delivery package with source IDs and hashes, synchronized track offsets, cut/reorder map, output-to-source time mapping, layouts, captions, graphics, audio choices, packages, version history, comments, owners, and approval evidence. Deliver a tested native project or agreed interchange format when requested; an MP4 alone is not an editable project.

Comments bind to the exact asset version and hash. Preserve old comments; when a cut moves, mark any uncertain remapping for review. Keep source access restricted to the approved team. Do not put private source paths or media access URLs into a public skill export.

The bundled delivery validator verifies file existence, confinement, hashes, and selected manifest fields. It does not enforce every field described here or establish semantic, visual, audio, rights, or approval quality. Record those gates separately and never present its PASS as release approval.
