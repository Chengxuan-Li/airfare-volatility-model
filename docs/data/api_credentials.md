# API credentials and usage budget

The user has a Flightradar24 API Explorer plan with a reported allocation of
60,000 credits for one month (reported 2026-09-12). The billing period boundaries
and live remaining balance have not been verified.

## Local setup

An empty `.env` has been created at the repository root. Paste the API key into
`FLIGHTRADAR24_API_KEY` and save it locally. Git ignores this file. On another
machine, copy the tracked `.env.example` to `.env` before adding the key.
The template must always contain an empty key value.

This is a plaintext local configuration file, not an encrypted credential vault.
No API client or automatic environment loading has been implemented yet.
Never print the key, include it in logs or manifests, or commit it.

## Usage planning

- No API calls were made during credential setup.
- Treat 60,000 as the total planning ceiling, not evidence of remaining credits.
- Before acquisition, verify current endpoint credit costs and available balance,
  estimate the proposed batch cost, and document a budget with a reserve.
- Start with a small validation request, cache reusable results where permitted,
  and avoid duplicate queries and unbounded polling or retries.
- Record actual or estimated credit consumption and stop before exceeding the
  available budget. Credentials do not authorize purchases or paid upgrades.

The availability of this API does not yet establish feasibility of historical
fare quotes or demand measurement; those still require source assessment.
