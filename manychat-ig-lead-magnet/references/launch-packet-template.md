# Launch Packet Template

Use this template before touching a live ManyChat automation.

## Resource

- Resource name:
- Resource slug:
- PDF path:
- PDF size:
- ManyChat delivery: direct PDF upload
- External hosting needed: no, unless over 25 MB or requested

## Instagram

- Account:
- Post/reel:
- Caption CTA:
- Primary keyword:
- Backup keywords:
- Keywords not to use:

## ManyChat

- Base automation to duplicate:
- New automation name:
- Post/reel trigger scope and case-insensitive keyword matching:
- Separate Story direct-reply trigger, Story target, expiry and CTA:
- Trigger:
- Tracking tag:
- Custom fields:
- Immediate comment/reply copy:
- DM copy:
- Required-newsletter exchange copy and approved change from prior promises:
- Explicit required newsletter consent copy and accept/decline routes:
- Validated System Email, consent evidence, no-resource decline routing:
- Verified subscription callback/readback, pending/failure and unsubscribe paths:
- Consent timestamp, text/version, campaign and source evidence:
- Existing Zap/native integration inspected, consumers and mapping:
- Single Beehiiv path, publication, deduplication and unsubscribe behavior:
- Beehiiv/CRM source attribution mapping and consent boundaries:
- Five independent Jev fit lanes (client ICP, partnership, sponsorship, M&A, recruiting), rubric/evidence and unknown labels:
- Approved S-tier Slack destination/audience, deduplication and readback:
- Email capture copy:
- PDF upload step:

## QA Checklist

- [ ] PDF opens.
- [ ] PDF is under 25 MB.
- [ ] Resource name matches automation name.
- [ ] Primary and backup keywords are entered.
- [ ] Broad/unsafe keywords are not used.
- [ ] DM copy names the correct resource.
- [ ] Email capture copy names the resource if email is requested.
- [ ] PDF upload step contains the correct PDF.
- [ ] Tracking tag/custom fields are applied or explicitly marked missing.
- [ ] ManyChat shows saved.
- [ ] Completed the case matrix in `email-and-story-checklist.md`; distinguish actual test, configuration inspection, dry-run, fail and blocked.
- [ ] Resource only after explicit consent and verified subscribed status.
- [ ] Decline, invalid email, pending confirmation and failed/unverified signup do not deliver resource.
- [ ] Existing subscribed/unsubscribed handling preserves suppression and confirmation settings.
- [ ] No newsletter consent and invalid-email paths never fire the newsletter event.
- [ ] Consent-button replies cannot overwrite the email mapped into the shared Zap.
- [ ] Campaign/source attribution verified independently in Beehiiv and CRM, or marked unavailable.
- [ ] Five-lane fit labels pass `lead-fit-and-routing.md` cases; unknown is not D; no automatic hiring or outreach.
- [ ] S-tier alert destination approved and evidence checked; missing destination holds the alert.
- [ ] Jev/CRM/Slack actual deployment and readbacks are distinguished from documented procedure.
- [ ] Post and Story entry paths do not cause duplicate sends/signups.
- [ ] Actual Beehiiv subscriber status checked, or explicitly unverified.
- [ ] Test comments removed when authorized; no production contact used as a test.
- [ ] Explicit approval received before `Update`.

## Approval Phrase

```text
Approve ManyChat update: <automation name> for <IG post/reel> with keywords <keywords>, uploading <PDF filename>, with tracking <tag/custom fields>.
```
