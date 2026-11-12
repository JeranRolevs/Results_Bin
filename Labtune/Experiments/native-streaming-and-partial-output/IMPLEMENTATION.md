# What changes, where and why

All paths below are relative to the Labtune checkout; matching snapshots live under `implementation/` here.

| Target path | Change | Purpose |
|---|---|---|
| `src/labtune/providers/streaming.py` | New bounded SSE assembler | Separate reasoning from final text; require DONE/completion markers; retain usage when provided; report metadata-only progress |
| `src/labtune/providers/http.py` | Opt-in SSE HTTP path and async-safe progress dispatch | Use the existing authenticated transport, request reservation, semaphores, redaction and error handling without introducing retries |
| `src/labtune/providers/chat.py` | Boolean `stream` constructor option, default false | Explicit selection; keep output-limit/incomplete-response rejection after authoritative receipts are journaled |
| `src/labtune/providers/configuration.py` | Validate optional boolean provider `stream` | Reject malformed settings; do not silently change existing configurations |
| `src/labtune/study.py` | Forward stream setting and retain successful wave siblings on failure | Use native workflows rather than a diagnostic-only transport; prevent losing completed peer results from aggregate partial output |
| `tests/test_streaming.py` | Offline parser/transport/failure regressions | Exercise boundaries, empty-delta timing, missing usage, truncation, redaction and sibling preservation |
| `tests/test_providers.py` | Full mocked native streamed-workflow test | Verify the graph, stream setting, accounting and not_evaluated status without paid calls |
| `docs/PROVIDERS.md` | Public option/limitations documentation | Explain opt-in behavior, reasoning allowance, incomplete streams and missing receipts |
| `src/labtune/resources/starter/project/docs/PROVIDERS.md` | Generated synchronized guide | Keep wheel starter documentation aligned via `tools/sync_starter.py` |

## Important boundaries

The default remains non-streaming. `stream` is a top-level provider option, not a request_options override. No provider/model/account is selected automatically. The partial-output fix is not a resume facility: restarting can still regenerate and bill completed work. Missing usage is not interpreted as zero cost. A text workflow completing does not establish scientific correctness or measured anomaly-detection benefit.

Only general-purpose declared dependencies and standard-library protocol handling are used. No external research implementation or dataset is bundled. Apply the complete patch rather than selectively copying parser code without its validation, transport wiring, tests and starter-documentation update.
