# ADR-001: Use Go for Core Services and Python for Users Service

## Status

**Accepted** — adopted at project inception.

## Context

Bazaar is a microservices marketplace platform that must satisfy several competing constraints:

1. **Academic requirement** — The project must use at least two different programming languages across its services to demonstrate polyglot architecture competence.
2. **Developer skill profile** — The primary developer has strong proficiency in Python (particularly FastAPI) and is actively building Go skills. Go is the language they want to deepen — it is not yet at the same comfort level as Python.
3. **Performance characteristics** — The platform includes a checkout saga orchestrator, a real-time API gateway, and an edge service for Raspberry Pi. These components benefit from low-latency, high-concurrency runtimes. Meanwhile, the users/auth service is a standard CRUD + auth-flow service where raw throughput is less critical.
4. **Ecosystem maturity** — Python has a mature, battle-tested ecosystem for authentication: `passlib` for password hashing, `python-jose` for JWT, `authlib` for OAuth flows. Go's auth libraries exist but require more manual wiring.
5. **Edge deployment** — The warehouse service runs on a Raspberry Pi with limited resources. Deployability (single static binary, small memory footprint) matters.

## Decision

Use the following language assignments:

| Service | Language | Framework |
|---|---|---|
| **Gateway** | Go | Chi or Gin |
| **Catalog** | Go | Chi or Gin |
| **Commerce** | Go | Chi or Gin |
| **Notifications** | Go | (event-driven, no HTTP framework) |
| **Edge/Warehouse** | Go | Bubble Tea (TUI), gRPC |
| **Users** | Python | FastAPI |

Go is the **primary** language, used for 5 out of 6 services. Python is used for exactly one service — the users/auth service.

## Rationale

### Why Go for the majority of services

1. **Concurrency model.** Go's goroutines and channels are a natural fit for the checkout saga orchestrator (`commerce/internal/saga/`). The saga runner executes steps concurrently where possible and coordinates compensation logic — a pattern that maps directly to Go's concurrency primitives. Writing the equivalent in Python would require `asyncio` task groups with less intuitive cancellation and error propagation.

2. **API gateway performance.** The gateway proxies every inbound request to a downstream service. Go's `net/http` and `httputil.ReverseProxy` provide high-throughput, low-allocation proxying out of the box. This is a problem that Go was designed to solve (see: every major Go project at Google, Cloudflare, etc.).

3. **Explicit error handling.** The commerce service manages financial transactions, stock locking with `SELECT ... FOR UPDATE`, and idempotent payment processing. Bugs in this code mean lost money or oversold stock. Go's explicit `if err != nil` pattern forces every error path to be considered. Python's exception-based model makes it too easy to miss an error case in a `try/except` that's too broad.

4. **Static binary for edge deployment.** The warehouse service must run on a Raspberry Pi. Go cross-compiles to `linux/arm64` with `GOOS=linux GOARCH=arm64 go build`, producing a single binary with zero runtime dependencies. No Python interpreter, no virtualenv, no `pip install` on the Pi.

5. **Learning investment.** The developer is actively growing Go skills. Putting Go on the most complex and varied services (gateway middleware, saga orchestration, gRPC servers, TUI applications) maximises the breadth and depth of learning.

### Why Python for the users service

1. **Auth ecosystem maturity.** The users service handles password hashing, JWT token issuance/validation, OAuth2 flows, and role-based access control. Python's ecosystem for this is superb:
   - `passlib` — Supports bcrypt, argon2, and automatic algorithm migration.
   - `python-jose` — Standards-compliant JWT implementation with key rotation support.
   - `authlib` — Full OAuth2/OIDC client and server implementation.
   
   These libraries have years of production hardening. The equivalent Go implementations exist but require more glue code.

2. **FastAPI's productivity features.** FastAPI provides automatic OpenAPI documentation, request/response validation via Pydantic, and a dependency injection system that makes auth middleware elegant. For the users service specifically, the ratio of business logic to boilerplate is very favourable. The auth endpoints are essentially self-documenting.

3. **Comfortable fallback.** Having one service in a language the developer is already proficient in provides a safe fallback. When the Go services are blocked on a tricky concurrency bug, work can shift to the users service without a context-switch tax. This keeps development velocity consistent.

4. **CRUD-shaped workload.** The users service is fundamentally a CRUD service with auth middleware. It does not need goroutines, channels, or the ability to handle 10,000 concurrent connections. FastAPI's async support (`asyncio` + `uvicorn`) provides more than enough throughput for user authentication and profile operations.

### Why not the reverse (Python for everything, Go for users)?

The commerce service's saga orchestrator and the gateway's reverse proxy are the two most concurrency-intensive components. These are Go's sweet spot. Putting Python there and Go on the CRUD auth service would invert the strengths — asyncio for saga coordination is painful, and Go's auth libraries, while functional, would negate the learning benefit of having a Python service at all.

### Why not a third language?

Adding a third language (e.g., TypeScript for the notifications service) was considered but rejected. Two languages are enough to demonstrate polyglot competence. A third would increase operational overhead (more CI pipelines, more Dockerfiles, more dependency management) without proportional learning benefit. If a third language is added later, the notifications service is the best candidate — it is the simplest and most self-contained.

## Consequences

### Positive

- **Maximised learning.** Go is used in the most architecturally challenging contexts: saga orchestration, reverse proxying, gRPC bidirectional streaming, TUI applications, and edge deployment. This produces the broadest Go skill development.
- **Right tool for the job.** Authentication in Python is genuinely more ergonomic than in Go. The users service benefits from this.
- **Demonstrates polyglot competence.** The project proves ability to design, build, test, and deploy services in two different language ecosystems with different paradigms (explicit errors vs. exceptions, compiled vs. interpreted, static vs. dynamic typing).
- **Clean service boundary.** The language boundary aligns perfectly with a service boundary. There is zero shared code between the Python and Go services — they communicate exclusively over HTTP via the API gateway.

### Negative

- **Two Dockerfiles, two base images.** The Python service uses a `python:3.12-slim` base image while Go services use `scratch` or `alpine`. CI must build and cache both.
- **Two test frameworks.** Go services use `go test` + `testify`. The Python service uses `pytest` + `httpx` for async test clients. Developers must be comfortable with both.
- **Two dependency management systems.** Go uses `go.mod`/`go.sum`. Python uses `requirements.txt` (or `pyproject.toml` with `pip-tools`). Dependency audit tooling must cover both ecosystems.
- **Two linters.** Go uses `golangci-lint`. Python uses `ruff`. Both are configured in CI but require separate configuration files and separate CI steps.
- **Context switching.** Moving between Go and Python codebases requires a mental gear-shift (error handling patterns, type system, project layout conventions). This is mitigated by the fact that only one service is in Python, and it is the most self-contained.

### Mitigations

The negative consequences are explicitly accepted — and even valued. The operational overhead of maintaining two ecosystems is itself a learning outcome. The CI pipeline, Docker build matrix, and test harness must handle polyglot services, which mirrors real-world platform engineering.

To reduce friction:

- The `Makefile` at the repository root abstracts language-specific commands behind unified targets (`make test`, `make lint`, `make build`).
- The CI pipeline uses a matrix strategy that runs the correct toolchain per service directory.
- Docker Compose hides all language differences — `docker compose up` starts everything regardless of implementation language.

## References

- [ADR-002: Saga over 2PC](002-saga-over-2pc.md) — Depends on Go's concurrency model (this decision).
- [ADR-005: Edge offline strategy](005-edge-offline-strategy.md) — Depends on Go's static binary compilation (this decision).
