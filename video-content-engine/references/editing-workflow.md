# Complete editing and review workflow

This is an operating and implementation contract. The public package supplies instructions and validators, not a hosted application. Do not claim cloud editing, shared storage, persistent render jobs, or team access until implemented and verified.

## Choose the execution environment

Respect the user's storage and interruption preferences. Do not play media through their foreground apps or download full originals to their computer by default. Use the authorized source, available editor, and approved execution environment. Remote editing still needs source access, synchronized tracks, an editable timeline, full previews, revision control, and approval records.

When a required renderer or remote workspace is unavailable, name the gap and prepare the edit plan from available authorized evidence. Do not substitute another recording, silently upload footage, start a paid service, or claim a render happened.

## Complete loop

1. **Ingest:** resolve the exact recording and authorized track set. Preserve immutable originals with IDs, hashes, metadata, and synchronization offsets. A project-sharing page is not necessarily a downloadable media endpoint.
2. **Plan:** inventory candidates, select distinct promises, and write opening beats, cut maps, proof maps, and required repairs. Preserve source-to-output mappings.
3. **Edit:** maintain cuts, reorder decisions, layouts, captions, graphics, audio, and packaging as editable project data. Use available native tooling or an agreed structured edit format. Verify interchange imports in the actual destination editor before promising fidelity.
4. **Preview:** provide full-duration access to every selected asset. Load media on demand, avoid autoplay, and offer an explicit quality choice. Keep compact review proxies separate from full-quality exports. Show source, transcript, timeline, version, and feedback together where tooling supports them.
5. **Review:** bind comments to an asset, immutable revision and hash, output time or range, and optional frame location. Preserve unresolved notes across revisions. Make uncertain remapping explicit when footage moves or disappears.
6. **Revise:** assign an owner, implement the accepted notes, render a new immutable version, compare it with the previous version, and record resolved and unresolved issues.
7. **Approve:** distinguish technical checks from editorial, caption, claims, and rights acceptance. Record the approver and exact approved version. A later edit invalidates that version's approval for the new output.
8. **Export and hand off:** provide the editable project, dependency manifest, masters, captions, packages, and approval history. Verify the recipient can open the project and access authorized sources. Publication requires its own authorization and destination readback.

A compact player, hook sample, or folder of MP4s covers only part of this loop.

## Shared workspace design

For a future chat-led editing application, separate responsibilities:

| Component | Responsibility | Acceptance evidence |
| --- | --- | --- |
| Chat and editing UI | Brief, source library, transcript, timeline, layout controls, previews, comments | Users can inspect and change concrete edit decisions |
| Private object storage | Originals, proxies, project files, captions, masters | Only approved members can retrieve each project's objects |
| Preview delivery | Full-duration adaptive viewing and seeking | Authorized playback works for every selected asset |
| Shared database | Membership, assets, revisions, comments, assignments, approval and job state | State survives page closure and separate user sessions |
| Render workers | Versioned queued jobs, progress, retry and cancellation | Jobs survive UI closure; outputs bind to the intended revision |
| Export adapter | Native or tested interchange project and dependency package | Another editor opens the handoff successfully |

Choose actual providers only when implementing against current requirements and documentation. A ChatGPT-based interface does not itself supply video hosting, project authorization, background rendering, or a timeline editor. Adaptive preview streaming alone does not prove frame-accurate editing; verify a suitable frame-indexed proxy or frame service when precision is required.

Use server-side project membership checks. Sign-in alone is not permission to a recording. Use private media access and appropriate URL expiry. Treat producer, editor, reviewer, and approver as project roles; approval does not imply permission to publish.

Use revision checks to reject conflicting saves rather than silently accepting the last writer. Simultaneous comments and assignments can precede simultaneous timeline editing; state exactly which forms of collaboration are implemented. Render jobs should carry immutable input revisions and safe retry identifiers.

## Storage and handoff acceptance

Stream previews rather than duplicating full originals on each reviewer's computer when approved infrastructure supports it. Load one selected asset at a time and let users choose downloads. Define cache and retention limits; remove media only under the project's authorized retention policy. Keep full outputs available throughout the agreed review period.

Before calling a shared editor complete, verify with two authorized users in separate sessions: import, edit, full preview, timestamped comment, revision, comparison, assignment, approval, and editable export. Check that unauthorized access fails, comments remain bound to the correct version, conflicts are visible, and render jobs survive page closure. Until then, report the implemented subset and remaining gates.
