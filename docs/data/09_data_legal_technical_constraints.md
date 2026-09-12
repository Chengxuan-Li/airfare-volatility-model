# Data legal and technical constraints

Checked 2026-09-12. This is a research data-governance assessment, not legal
advice. Recheck source terms when acquisition is rerun because pages and service
policies can change.

## Access and reuse

### BTS / U.S. DOT

DB1B, T-100, ASQP, and Delay Causes are published by BTS for public download
without an account or API key. The official Delay Causes page says summary and
raw data are made public with the Air Travel Consumer Report. U.S. government
works are generally not protected by U.S. copyright, but a public download is
not itself a complete license statement for every embedded element. Preserve
agency attribution, source URLs, retrieval dates, table/readme definitions, and
any notices shipped inside archives. The DOT [Managing Rights](https://ntl.bts.gov/ntl/public-access/managing-rights)
page encourages CC BY for deposited research data; it should not be misquoted as
the specific license for every TranStats file.

Raw BTS archives can be reacquired and are large, so keep them in ignored local
storage. Commit acquisition recipes, selected schemas, checksums/manifests, and
derived aggregates only after reviewing disclosure and redistribution needs.
DB1B is sampled ticket data without direct passenger identifiers in the selected
tables, but small-cell and carrier/route disclosure should still be reviewed
before publishing derived panels.

### Open-Meteo and NOAA

Open-Meteo's [terms](https://open-meteo.com/en/terms) restrict the free endpoint
to non-commercial use and state limits of 10,000 calls/day, 5,000/hour, and
600/minute. Its [license page](https://open-meteo.com/en/license) places API data
under CC BY 4.0 and requires credit, a license link, and indication of changes.
This public research pilot fits the stated free-use examples and needs only a
handful of batched calls, but must retain attribution to Open-Meteo and relevant
upstream provider(s). No paid plan is authorized.

NOAA/NWS states that its server information is public domain unless otherwise
annotated, requests attention to product timestamps, and prohibits presenting
modified content as official government material; see the
[NWS disclaimer](https://www.weather.gov/disclaimer). Third-party layers and
provider-specific notices remain subject to their own terms.

## Reproducibility and provenance requirements

- Use explicit HTTPS URLs and ordinary documented GET/POST requests. Do not
  bypass authentication, CAPTCHAs, robots controls, or access restrictions.
- Record retrieval UTC time, request parameters, HTTP metadata when useful,
  content length, SHA-256, archive member names, schema, and transformations.
- Cache successful permitted downloads. Use bounded timeouts/retries and validate
  ZIP CRCs before assigning final filenames.
- Pin airport coordinates, time zone, weather variables, units, model selection,
  and lag rules. An API's default "best match" can change as models change.
- Keep raw and interim data out of Git unless redistribution rights, size, and
  disclosure are affirmatively reviewed. Never commit credentials or cookies.
- Preserve source failures and schema/coverage breaks. A 404 is not permission
  to substitute a guessed file or silently interpolate a missing period.

## Technical constraints observed

| Constraint | Evidence and response |
| --- | --- |
| DB1B size | 2024 Market CSVs are about 1.87 GB and 2.16 GB uncompressed. Stream ZIP members and filter columns/routes early. |
| DB1B schema artifact | Verified Market header has an empty trailing column. Handle and test explicitly. |
| DB1B cutoff | 2025 Q2 endpoint returned 200; Q3 returned 404. BTS says DB1C replaced DB1B in July 2025. Do not silently pool the regimes. |
| BTS aggregate link stability | Delay Causes raw URLs contain obfuscated query text. Reproduce the normal form POST and extract the returned link rather than treating the encoded URL as a permanent API. |
| BTS legacy host behavior | HEAD to three linked legacy ASQP files returned 403, while TranStats PREZIP returned 200. Record method/host and use GET or PREZIP; do not infer absence from the 403 alone. |
| Weather-vintage risk | Open-Meteo archive and historical-forecast products are not interchangeable with forecasts issued at a chosen lead. Store endpoint and product class. |
| Revision risk | BTS traffic and weather reanalysis can be revised. A retrieval checksum identifies the used vintage but does not recreate an earlier information set. |
| Cross-source keys | DB1B itinerary markets, T-100 flight segments, and Delay Causes airports have different units. Audit DOT IDs, airport codes, carriers, direction, and time aggregation before joining. |

## Publication language

Use "observed passenger quantity," "retrospectively retrieved reanalysis," and
"strictly lagged seasonal risk proxy." Reserve "quote," "demand shock," and
"ex-ante forecast" for data that actually carry those meanings. Publish negative
access findings and identification limits alongside any result.

