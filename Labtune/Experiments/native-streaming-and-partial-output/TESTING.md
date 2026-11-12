# Completed validation and remaining work

## Completed observations

- 156 main offline Labtune tests passed, including the new native streaming cases and a complete mocked workflow.
- Seven memory-example checks passed.
- Starter synchronization and public source/built-wheel privacy checks passed.
- During relocation, the exported patch was independently applied to a pristine baseline worktree. All nine implementation snapshots matched byte-for-byte; 156 main tests, seven example checks, starter synchronization and source privacy checks passed again.
- The package was built from Labtune's pyproject.toml and installed outside its checkout.
- One full native text-only research workflow completed in approximately 5m45s with 11 requests and ten saved actor outputs. All usage receipts were present; one malformed-action correction consumed an additional call. No HTTP errors or network retries occurred in that successful run.
- Its settings were user-selected Ethux qwen3.8-27b, streamed responses, 16,384 tokens/response, one concurrent request and a two-hour maximum. Usage: 74,513 input and 41,784 completion tokens, including 28,444 reported reasoning tokens. Actual dollar cost was unavailable.
- Earlier failures, one failed streamed diagnostic and a successful identical streamed retry are retained in the curated API findings. A single successful workflow does not establish provider reliability, optimal settings or scientific performance.

Setup, tests, packaging and relocation made no paid provider calls. Live observations came from separately authorized tests. Raw journals, reasoning, private freezes and audit records are not distributed.

## Coverage before promotion

Retain the existing tests and expand coverage as appropriate before deciding to move this into Labtune:

- Clean offline builds/installations on supported Python versions/platforms.
- SSE comments/heartbeats, fragmented records, malformed/error events, premature closure and missing DONE/finish markers.
- Empty initial content deltas must not be mistaken for a visible answer; reasoning must never be promoted to final text.
- Usage receipt absence, authoritative accounting on `length`, and documented streaming receipt variants.
- Cancellation and shared deadlines, including a slow or stalled response; ensure no unintended additional calls after stopping.
- Semaphore behavior and progress attribution with concurrency greater than one if a user elects to test it.
- Successful peers retained on a sibling failure across multiple dependency waves; no duplicate outputs or accidental exposure of unpublished peer work.
- Non-streaming compatibility, redaction, redirect protection and bounded input/output size.
- Confirm any provider-specific behavior before adopting it; do not add unsupported reasoning parameters.

Automatic checkpoint/resume, automatic HTTP retries and a reliable provider-default budget have **not** been implemented or validated. Do not publish those capabilities as completed.

## Offline reproduction

Use MIGRATION.md to apply the patch to an isolated checkout. Then run the package and example tests, starter check and release check. Do not run `doctor --live`, `study run`, or a live connectivity probe as part of setup/testing. Additional paid tests, model changes, retry policies or budget increases require explicit authorization.
