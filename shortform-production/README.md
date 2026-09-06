# Shortform Production

Create readable shorts with a consistent design, useful B-roll, hook previews, and verified API delivery.

## Start

Install the complete directory as a skill, then ask:

> Use $shortform-production on this recording. Make three four-second opening previews, choose the clearest, and finish one short. Include captions and the source CTA. Do not publish.

The skill defines editorial rules; use an available video renderer. The API client needs Python 3.10+ and `python3 -m pip install -r requirements.txt`.

## Workflow

1. Choose evidence, workflow, or operator story.
2. Preview three openings within the same V5 design.
3. Finish one master and review it with sound at phone size.
4. Package the video, captions, CTA, and review evidence.
5. Schedule through Metricool only when authorized; verify the result.

Read [API setup](references/metricool.md) before delivery. Account settings and credentials are user-supplied. Dry runs make no network calls. Public examples contain no working account or private media.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Tests use synthetic accounts and mocked writes. They cover duplicate prevention, account verification, upload authentication boundaries, media readback, and rescheduling.

---

<p align="center">
  Built by <a href="https://www.singlegrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Grain</a>. Powered by <a href="https://www.singlebrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Brain</a>.
</p>
