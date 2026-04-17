# API Reference Notes

## Configuration

All API keys are configured via environment variables. See `.env.example` for the full list.

---

## People Search API (e.g., Apollo)

**Endpoint:** `POST https://api.apollo.io/api/v1/mixed_people/search`

**Auth:** API key in request body (`"api_key": "KEY"`)

**Request body:**
```json
{
  "api_key": "KEY",
  "person_titles": ["VP Marketing", "CMO"],
  "organization_num_employees_ranges": ["11,50", "51,200"],
  "person_locations": ["United States"],
  "q_organization_keyword_tags": ["SaaS", "B2B"],
  "per_page": 100,
  "page": 1
}
```

**Pagination:**
- Max 100 results per page
- Increment `page` starting from 1
- Response includes `pagination.total_entries` and `pagination.total_pages`
- Many search APIs cap results at ~10,000 even if more exist
- If you need more, narrow criteria and run multiple searches

**Response structure:**
- `people[]` — array of person objects
- Each person has: `email`, `first_name`, `last_name`, `title`, `organization.name`, `organization.primary_domain`
- Many contacts have `email: null` — filter these out

**Rate limits:** Varies by plan. Watch for 429s.

---

## Email Validation API (e.g., LeadMagic, ZeroBounce, NeverBounce)

**Endpoint:** `POST https://api.your-provider.com/v1/people/email-validation`

**Auth:** `X-API-Key` header (varies by provider)

**Request body:**
```json
{
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "email": "john@example.com",
  "email_status": "valid",
  "is_free_email": false,
  "is_disposable": false,
  "is_role_based": false,
  "domain": "example.com"
}
```

**Status values:**
- `valid` — deliverable, safe to use
- `invalid` — hard bounce, do NOT use
- `unknown` — inconclusive SMTP check

**Best practice:** Only use `valid` emails. Discard `invalid` and `unknown`.

---

## Campaign Tool API (e.g., Instantly, Lemlist, Smartlead)

**Base URL:** Configure via `CAMPAIGN_API_BASE_URL` environment variable.

**Auth:** `Authorization: Bearer API_KEY` header

### Create Lead
`POST /api/v2/leads`

```json
{
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "Acme Inc",
  "campaign": "CAMPAIGN_UUID",
  "custom_variables": {
    "title": "VP Marketing",
    "personalization": "Custom opening line here."
  }
}
```

### List Leads (for dedup)
`POST /api/v2/leads/list`

```json
{
  "limit": 100,
  "starting_after": "CURSOR_FROM_PREVIOUS_RESPONSE"
}
```

Paginate until `items` is empty or `next_starting_after` is null.

### Quirks & Gotchas

1. **No rate limit headers** — Some campaign tools don't return `X-RateLimit-*` headers. They silently block at high request rates. Always add delays.
2. **Silent failures** — Some requests return empty or timeout without error codes. Implement retry logic.
3. **Campaign must exist** — The campaign UUID must be valid or lead creation silently fails.
4. **Batch strategy** — Upload in batches of 25 with 1-second pauses between batches.
5. **Lead uniqueness** — Leads are typically unique per email+campaign.

---

## CRM API (e.g., HubSpot, Salesforce)

**Base URL:** Configure via `CRM_BASE_URL` environment variable.

**Auth:** `Authorization: Bearer API_KEY` header

### Search Contact by Email
```json
POST /crm/v3/objects/contacts/search
{
  "filterGroups": [{
    "filters": [{
      "propertyName": "email",
      "operator": "EQ",
      "value": "john@example.com"
    }]
  }],
  "properties": ["firstname", "lastname", "email", "company", "jobtitle", "annualrevenue"]
}
```

### Search Company by Domain
```json
POST /crm/v3/objects/companies/search
{
  "filterGroups": [{
    "filters": [{
      "propertyName": "domain",
      "operator": "EQ",
      "value": "example.com"
    }]
  }],
  "properties": ["name", "domain", "annualrevenue", "industry", "numberofemployees"]
}
```

---

## Error Handling Strategy

All APIs use exponential backoff:
- Start: 1 second
- Multiply by 2 each retry
- Max retries: 5
- Max backoff: 60 seconds
- On 429: respect `Retry-After` header if present, else backoff

Save intermediate state (sourced leads, verified leads) to disk so a crash mid-pipeline doesn't lose progress.

---

## BuiltWith API (Tech Stack Detection)

**Endpoint:** `GET https://api.builtwith.com/free1/api.json?KEY=free&LOOKUP=example.com`

Free tier provides basic technology detection. Paid tier gives deeper history and more data.

The account researcher parses BuiltWith responses to detect:
- **CRM tools** (Salesforce, HubSpot, Pipedrive, etc.)
- **Marketing tools** (Google Analytics, Segment, Hotjar, etc.)
- **Enterprise infrastructure** (AWS, Cloudflare, Datadog, etc.)
