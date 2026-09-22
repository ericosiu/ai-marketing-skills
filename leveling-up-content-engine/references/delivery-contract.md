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
