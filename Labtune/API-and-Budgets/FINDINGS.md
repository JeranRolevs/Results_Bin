# Observed API outcomes

Provider/model: user-selected Ethux `qwen3.8-27b`, OpenAI-format `/v1/chat/completions`. Observed on 2026-11-11 UTC. Attempts occurred at different times and changed more than one setting; no single-factor or statistically powered comparison is claimed.

| Test | Settings | Outcome |
|---|---|---|
| Initial native workflow | Non-streaming; 65,536 configured output tokens; two concurrent requests | Explorer completed in about 237 seconds; critical peer returned HTTP 502 after about 360 seconds. Workflow incomplete. |
| Explicit manual retry | Same settings | Both initial requests returned HTTP 502 at about 304 seconds. No usage receipts for these two failures. |
| Small diagnostic | One sequential request; 1,024 output-token cap | Completed in 0.65 seconds; 63 input and 33 completion tokens. Connectivity/authentication check only. |
| Shorter native workflow | Non-streaming; 8,192-token cap; one request at a time | Explorer completed; critical peer returned `length` with no final content. Provider reported 8,192 completion tokens and an inconsistent 8,193 reasoning count. Workflow incomplete. |
| First streamed replay | Same critical prompt; 16,384-token cap; one request | HTTP 504 after 60.16 seconds, before any SSE event or successful response stream. No usage receipt. |
| User-authorized streamed retry | Exact same request body as the preceding streamed replay | HTTP 200; complete valid final action in 93.09 seconds; 3,391 input and 10,667 completion tokens, including 9,392 reasoning tokens. DONE and stop markers received. |
| Full native streamed workflow | Two scientists; one concurrent request; 16,384 tokens/response; two-hour maximum | Completed in about 5m45s: 11 requests, ten actor outputs, no HTTP errors, all usage receipts present; one malformed-action correction. |

Across this history, **20 requests were dispatched**: 16 received usage receipts, four did not. Missing receipts do not imply zero computation, free requests or known billing. Dollar cost was unavailable. Failed attempts remained preserved privately; retries of failed workflows were explicitly user-authorized, not an automatic retry policy.

## Full-workflow measurements

- Input tokens: 74,513.
- Completion tokens: 41,784, including 28,444 reported reasoning tokens.
- Per-request completion tokens: minimum 1,236; median 3,277; maximum 7,882.
- Per-request response duration: minimum 5.19s; median 25.98s; maximum 69.60s.
- Ten completed actor outputs; eleven requests because one malformed JSON action required correction.
- Status: completed_text_workflow; verification_status: not_evaluated. No numerical evaluation ran.

These are descriptive observations from one completed workflow, not a throughput guarantee or evidence that an 8,192-token cap is safe. The separate successful critical replay used more than 8,192 completion tokens.

## What the observations support

Small connectivity calls can succeed while substantive research calls fail. Reasoning can consume a completion allowance before any final answer. A three-hour orchestration budget cannot override a shorter request/gateway deadline. Identical streamed requests failed once and succeeded later, so streaming does not establish reliability by itself; transient service conditions, buffering, caching and load remain possible explanations rather than proven causes.

The documented streaming mode delivered reasoning events before the final answer on the successful retry. Its original first-answer timer was incorrectly triggered by an empty role/content delta; do not interpret its approximately 2.44-second first-event time as answer latency. Progress records bound nonempty answer onset between approximately 83.05 and 93.07 seconds. Total elapsed time, valid final text, markers and usage receipts were unaffected. Raw records were preserved and the diagnostic's future timing predicate corrected. This instrumentation issue was not present in the native integration's offline empty-delta regression test.

## Official documentation consulted

- https://docs.ethux.net/endpoints/#chat documents `stream: true`.
- https://docs.ethux.net/errors/ calls 5xx temporary and recommends short-backoff retries; it does not promise failed requests are unbilled.
- https://docs.ethux.net/models/ lists a 256K context and organization-specific pricing. Context length is not a completion-budget recommendation.

No separate reasoning-budget/disable-thinking parameter was found in the checked documentation. No undocumented reasoning option was used. The origin of the gateway errors was not established. One successful full workflow does not establish optimal organization, model choice or production reliability.

## Implementation disposition

The tested implementation is retained in the [experimental folder](../Experiments/native-streaming-and-partial-output/README.md) pending further testing, not on Labtune main. Historical outcomes above remain unchanged; they used the locally patched build.
