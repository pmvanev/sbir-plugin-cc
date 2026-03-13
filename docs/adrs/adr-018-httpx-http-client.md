# ADR-018: httpx as HTTP Client for DSIP API

## Status

Accepted

## Context

The DSIP API adapter needs an HTTP client for fetching topic listings (paginated JSON) and individual topic PDFs. Requirements: timeout control, retry logic, connection pooling, rate-limiting compliance (1-2 second delays between requests).

The project already uses Python 3.12+ with no existing HTTP client dependency.

## Decision

Use httpx (BSD-3-Clause, v0.27+) as the HTTP client library.

## Alternatives Considered

### Alternative 1: requests

- **Evaluation**: De facto Python HTTP library. Simple API, massive community. 50K+ GitHub stars.
- **Rejection**: Timeout handling requires per-request configuration (no transport-level defaults). No built-in connection pooling via `Client` context manager pattern. No async support without separate library (httpx is drop-in replacement with async built-in). requests is viable but httpx is strictly better for this use case.

### Alternative 2: urllib3 directly

- **Evaluation**: Lower-level. Used internally by requests. Good connection pooling.
- **Rejection**: Verbose API for simple GET requests. No high-level response handling. Would require writing boilerplate that httpx provides out of the box.

### Alternative 3: Python stdlib urllib.request

- **Evaluation**: Zero dependencies. Built into Python.
- **Rejection**: No connection pooling, no timeout defaults, no retry support, verbose error handling. Would require significant wrapper code for production-quality HTTP calls.

## Consequences

### Positive

- Transport-level timeout configuration (connect, read, pool timeouts)
- Built-in `Client` with connection pooling for paginated requests
- Async-ready if batch PDF fetching needs parallelization later
- BSD-3-Clause license (permissive)
- Similar API to requests (low learning curve)
- 13K+ GitHub stars, active maintenance

### Negative

- New dependency added to the project
- Slightly less battle-tested than requests (though widely adopted)
