# Provisional API and budget guidance

## A tested configuration, not a universal default

For the **user-selected Ethux qwen3.8-27b text-only workflow**, the following settings completed one full run:

```yaml
# Merge these fields into an otherwise configured provider mapping.
provider:
  stream: true
  max_output_tokens: 16384
  max_parallel_requests: 1

# Also keep the runtime request resource consistent.
base_overrides:
  resources:
    max_llm_requests: 1
```

This is an incomplete configuration fragment, not a runnable account configuration. Do not copy it as a service/model recommendation or substitute it for explicit choices. The package default remains non-streaming. No account or credential is provided.

**16,384 tokens supplied useful headroom in these observations; it is not a guarantee.** One successful critical response used 10,667 completion tokens, 9,392 of them reasoning. A visible word limit alone does not control internal reasoning. Do not invent a thinking-disable or separate reasoning-budget request field without provider documentation.

## Budget controls that must remain separate

- **Overall duration:** maximum runtime, not a requirement to keep generating until it expires. A complete workflow may finish early.
- **Request ceiling:** counts generations, semantic decisions, malformed-action corrections and dispatched failures. It is not the number of scientists or saved outputs.
- **Completion ceiling:** includes provider-accounted reasoning as well as final text. Too small can produce an empty answer; too large does not prevent timeouts or ensure better reasoning.
- **Concurrency:** affects simultaneous traffic; sequential operation is a conservative starting test here, not proof that concurrency caused the earlier failures.
- **Dollar ceiling:** time alone is not a cost ceiling. Choose one if required and verify account-specific prices. Do not estimate exact cost from missing receipts or assume failed calls are free.
- **Retry allowance:** if desired, explicitly select a finite count/backoff within the shared remaining request/time/cost allowance. No automatic network retry policy was introduced by this work.

The authorized two-hour test used a framework-required, intentionally nonbinding integer request ceiling of 1,000,000,000 and no specified dollar ceiling. **That is a description of this user's test, not a recommended starter budget.** A finite phase graph completed after about six minutes and did not spend the remainder.

## Failure and recovery discipline

Treat `length`, absent final text, missing DONE/completion markers and interrupted streams as incomplete; never promote partial reasoning to a scientific finding. Record authoritative usage when supplied, and make missing receipts visible. Reject redirects carrying credentials and preserve private journals outside Git.

The native patch preserves successful peer results when a sibling fails before wave aggregation. It does **not** implement automatic checkpoint/resume. Do not claim a new workflow is a resumed or independent scientific trial when it repeats earlier work. A future resume facility must preserve configuration, conversation state, actor/node identity and permitted peer exposure.

One small paid probe may check connectivity only when authorized; it cannot qualify long agent workloads. Test the parser, HTTP path, usage accounting, redaction, incomplete-output handling and the full graph offline before live calls. All setup/tests/packaging should remain free of paid calls.

## Questions still requiring provider clarification

Ask about first-byte/absolute gateway deadlines, early streaming headers/reasoning or heartbeat behavior, documented reasoning controls, failed-request billing and streaming usage receipts. Streaming may help idle connections but cannot guarantee against upstream errors or hard deadlines. Repeatability across more workloads remains untested; do not spend additional budget solely to manufacture a reliability claim.
