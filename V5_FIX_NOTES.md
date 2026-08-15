# PSX Hub v5 — Safari/iPad API request fix

## Problem observed
On the Render deployment, pressing **Run Scan** produced:

`Request failed: The string did not match the expected pattern.`

The wording is characteristic of Safari's Fetch API rejecting a URL before the HTTP request is sent. The previous frontend built the polling URL by string concatenation and passed relative URLs directly to `fetch()`.

## Fix
- Added `apiUrl()` to resolve every API URL against `window.location.origin` with the standard `URL` constructor.
- `getJSON()` now:
  - uses fully qualified same-origin API URLs;
  - disables browser/service-worker caching for API calls;
  - uses an AbortController timeout;
  - parses response text explicitly and reports malformed JSON with the exact endpoint/status;
  - reports transport failures distinctly from HTTP/API errors.
- PSX divergence polling validates the UUID returned by the server and URL-encodes it before requesting `/status/<job_id>`.
- Start/status endpoints now return `Cache-Control: no-store` to prevent stale polling responses.
- Start endpoint now catches server-side startup exceptions and returns structured JSON.
- Service-worker shell cache bumped from v4 to v5 so the old JavaScript is not retained.

## Important
This build does not claim that PSX outbound connectivity is available inside this coding sandbox. The fix addresses the client-side Safari URL/Fetch failure shown in the screenshot and adds diagnostics that distinguish client URL errors, transport errors, invalid JSON, HTTP errors, and actual background scan failures.
