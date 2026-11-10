// Offline arithmetic only. Caller resolves identity, evidence and coverage.
function nonempty(value, field) {
  if (typeof value !== 'string' || !value.trim() || value !== value.trim()) throw new Error(`Invalid ${field}`);
}
function time(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(value) || !Number.isFinite(Date.parse(value))) throw new Error('Expected timestamp with timezone');
  const [year, month, day] = value.slice(0, 10).split('-').map(Number);
  const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (month < 1 || month > 12 || day < 1 || day > days[month - 1] || Number(value.slice(11, 13)) > 23) throw new Error('Invalid calendar timestamp');
  return Date.parse(value);
}

export function summarize(events, config) {
  nonempty(config.campaign, 'campaign');
  const start = time(config.start), end = time(config.asOf);
  if (start > end) throw new Error('Reversed window');
  const coverage = config.coverage;
  if (!coverage || Array.isArray(coverage) || typeof coverage !== 'object' || !Object.keys(coverage).length || Object.values(coverage).some(v => !['complete', 'unknown'].includes(v))) throw new Error('Explicit channel coverage required');
  if (!Array.isArray(events)) throw new Error('Expected event array');
  const rows = events.map(e => {
    for (const field of ['person', 'campaign', 'channel']) nonempty(e[field], field);
    if (!['sent', 'reply', 'meeting'].includes(e.kind) || typeof e.verified !== 'boolean') throw new Error('Invalid event');
    const observed = time(e.at);
    if (e.kind === 'reply' && typeof e.human !== 'boolean') throw new Error('Reply human status required');
    if (e.kind === 'meeting') {
      nonempty(e.meetingId, 'meetingId');
      if (!['confirmed', 'declined', 'cancelled'].includes(e.status) || typeof e.attributed !== 'boolean' || time(e.createdAt) > observed) throw new Error('Invalid meeting status');
    }
    return { ...e, observed };
  }).filter(e => e.campaign === config.campaign && e.observed >= start && e.observed <= end);
  if (rows.some(e => !Object.hasOwn(coverage, e.channel))) throw new Error('Missing channel coverage');

  const firstSent = new Map(), channelSends = new Map();
  for (const e of rows) if (e.kind === 'sent' && e.verified) {
    firstSent.set(e.person, Math.min(firstSent.get(e.person) ?? Infinity, e.observed));
    channelSends.set(e.channel, (channelSends.get(e.channel) ?? 0) + 1);
  }
  const respondents = new Set();
  for (const e of rows) if (e.kind === 'reply' && e.verified && e.human && firstSent.has(e.person) && e.observed > firstSent.get(e.person)) respondents.add(e.person);

  const meetings = new Map(), observations = new Map();
  for (const e of rows) if (e.kind === 'meeting') {
    const old = meetings.get(e.meetingId);
    if (old && (old.person !== e.person || time(old.createdAt) !== time(e.createdAt))) throw new Error('Conflicting meeting identity');
    const key = JSON.stringify([e.meetingId, e.observed]);
    const previous = observations.get(key);
    if (previous && (previous.status !== e.status || previous.verified !== e.verified || previous.attributed !== e.attributed)) throw new Error('Conflicting simultaneous meeting evidence');
    observations.set(key, e);
    if (!old || e.observed > old.observed) meetings.set(e.meetingId, e);
  }
  const booked = new Set();
  for (const e of meetings.values()) if (e.verified && e.status === 'confirmed' && e.attributed && firstSent.has(e.person) && time(e.createdAt) > firstSent.get(e.person)) booked.add(e.person);
  const contacted = firstSent.size;
  return {
    contacted, responded: respondents.size, booked: booked.size,
    channelSends: Object.fromEntries(channelSends),
    responseRate: contacted ? respondents.size / contacted : null,
    bookingRate: contacted ? booked.size / contacted : null,
    coverageComplete: Object.values(coverage).every(v => v === 'complete'),
  };
}
