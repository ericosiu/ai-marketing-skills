import test from 'node:test';
import assert from 'node:assert/strict';
import { summarize } from '../scripts/funnel.mjs';

const config = { campaign: 'demo', start: '2026-01-01T00:00:00Z', asOf: '2026-01-10T00:00:00Z', coverage: { email: 'complete', chat: 'complete' } };
const event = (person, kind, extra = {}) => ({ person, campaign: 'demo', kind, channel: 'email', at: '2026-01-02T00:00:00Z', verified: true, ...extra });
const sent = event('p1', 'sent');
const reply = event('p1', 'reply', { at: '2026-01-03T00:00:00Z', human: true });
const meeting = event('p1', 'meeting', { at: '2026-01-04T00:00:00Z', meetingId: 'm1', createdAt: '2026-01-03T00:00:00Z', status: 'confirmed', attributed: true });

test('a relevant event channel must be declared in coverage', () => {
  assert.throws(() => summarize([sent, { ...reply, channel: 'chat' }], { ...config, coverage: { email: 'complete' } }));
});
test('multiple confirmed meetings for one person count one booked person', () => {
  assert.equal(summarize([sent, meeting, { ...meeting, meetingId: 'm2' }], config).booked, 1);
});
test('window includes exact endpoints and excludes outside events', () => {
  const r = summarize([
    { ...sent, at: config.start },
    { ...reply, at: config.asOf },
    event('p2', 'sent', { at: '2025-12-31T23:59:59Z' }),
    event('p3', 'sent', { at: '2026-01-10T00:00:01Z' }),
  ], config);
  assert.equal(r.contacted, 1); assert.equal(r.responded, 1);
});

test('deduplicate people across channels and preserve channel send counts', () => {
  const result = summarize([sent, event('p1', 'sent', { channel: 'chat' }), event('p2', 'sent'), reply, event('p1', 'reply', { channel: 'chat', human: true, at: reply.at }), meeting], config);
  assert.deepEqual(result, { contacted: 2, responded: 1, booked: 1, channelSends: { email: 2, chat: 1 }, responseRate: 0.5, bookingRate: 0.5, coverageComplete: true });
});
test('unavailable channel makes coverage incomplete without inventing replies', () => {
  const r = summarize([sent], { ...config, coverage: { email: 'complete', chat: 'unknown' } });
  assert.equal(r.coverageComplete, false); assert.equal(r.responded, 0);
});
test('latest declined or cancelled meeting is not booked', () => {
  for (const status of ['declined', 'cancelled']) {
    assert.equal(summarize([sent, { ...meeting, status, at: '2026-01-05T00:00:00Z' }, meeting], config).booked, 0);
  }
});
test('pre-campaign, unattributed and unverified meetings are excluded', () => {
  for (const extra of [{ createdAt: '2025-12-31T00:00:00Z' }, { attributed: false }, { verified: false }]) {
    assert.equal(summarize([sent, { ...meeting, ...extra }], config).booked, 0);
  }
});
test('pre-send, automated and uncontacted replies are excluded', () => {
  assert.equal(summarize([sent, { ...reply, at: '2026-01-01T00:00:00Z' }, { ...reply, human: false }, { ...reply, person: 'p2' }], config).responded, 0);
});
test('other campaigns and future records cannot inflate the cohort', () => {
  const r = summarize([sent, { ...reply, campaign: 'other' }, { ...reply, at: '2026-01-11T00:00:00Z' }, event('p2', 'sent', { verified: false })], config);
  assert.equal(r.contacted, 1); assert.equal(r.responded, 0);
});
test('zero denominator remains undefined', () => {
  const r = summarize([], config); assert.equal(r.responseRate, null); assert.equal(r.bookingRate, null);
});
test('missing identity and malformed time fail rather than count', () => {
  for (const extra of [{ person: '' }, { at: 'tomorrow' }, { at: '2026-01-02' }, { kind: 'opened' }, { verified: 'yes' }]) {
    assert.throws(() => summarize([{ ...sent, ...extra }], config));
  }
});
test('same-time contradictory meeting statuses and reused meeting identities fail', () => {
  assert.throws(() => summarize([sent, meeting, { ...meeting, status: 'declined' }], config));
  assert.throws(() => summarize([sent, meeting, { ...meeting, person: 'p2' }], config));
});
test('latest unverified status holds a previously confirmed meeting', () => {
  assert.equal(summarize([sent, meeting, { ...meeting, verified: false, at: '2026-01-06T00:00:00Z' }], config).booked, 0);
});
test('invalid coverage or window is rejected', () => {
  assert.throws(() => summarize([sent], { ...config, coverage: {} }));
  assert.throws(() => summarize([sent], { ...config, coverage: { email: 'probably' } }));
  assert.throws(() => summarize([sent], { ...config, start: '2026-02-01T00:00:00Z' }));
});
test('seeded naive sum and stale booking counts fail the literal oracle', () => {
  const r = summarize([sent, event('p1', 'sent', { channel: 'chat' }), meeting, { ...meeting, status: 'declined', at: '2026-01-05T00:00:00Z' }], config);
  assert.equal(r.contacted, 1); assert.equal(r.booked, 0);
  assert.throws(() => assert.equal(Object.values(r.channelSends).reduce((a, b) => a + b, 0), 1));
  assert.throws(() => assert.equal(1, r.booked));
});
test('contradictory older statuses throw regardless of input order', () => {
  const newer = { ...meeting, at: '2026-01-05T00:00:00Z' };
  const conflict = { ...meeting, status: 'declined' };
  for (const rows of [[newer, meeting, conflict], [meeting, conflict, newer], [conflict, newer, meeting]]) {
    assert.throws(() => summarize([sent, ...rows], config));
  }
});
test('simultaneous send and reply or creation do not prove conversion', () => {
  const r = summarize([sent, { ...reply, at: sent.at }, { ...meeting, createdAt: sent.at }], config);
  assert.equal(r.responded, 0); assert.equal(r.booked, 0);
});
test('impossible dates and midnight rollover are rejected; leap day works', () => {
  for (const at of ['2026-02-30T00:00:00Z', '2026-02-29T00:00:00Z', '2026-01-01T24:00:00Z']) {
    assert.throws(() => summarize([{ ...sent, at }], config));
  }
  assert.equal(summarize([{ ...sent, at: '2024-02-29T00:00:00Z' }], { ...config, start: '2024-02-01T00:00:00Z', asOf: '2024-03-01T00:00:00Z' }).contacted, 1);
});
