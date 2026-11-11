# Curated findings

## What actually passed

The native Labtune text-only workflow completed on 2026-11-11 UTC. Native execution took 343.85 seconds; the surrounding one-shot supervisor measured 345.49 seconds. It used 11 provider requests and retained ten actor outputs. One malformed JSON action required a budgeted format correction. There were no HTTP errors or network retries, all 11 usage receipts were present, and the two-hour maximum was not reached.

Reported usage: **74,513 input tokens**, **41,784 completion tokens**, including **28,444 reasoning tokens**. No separate decision model ran. Dollar cost was unavailable; token counts are not a currency estimate. The largest observed completion was 7,882 tokens. This does not establish that an 8,192-token cap is generally sufficient: a previous otherwise related critical response exhausted that cap, and a successful streamed replay used 10,667 completion tokens.

This is an operational workflow pass and a set of research proposals, **not a measured scientific success**. `verification_status` was `not_evaluated`; no numerical experiment ran. Peer agreement does not establish independent replication, correctness, an optimal organization, or hidden nonlinear effects.

## Recommendations from the scientists

| Candidate | Recommended role | Remaining blockers |
|---|---|---|
| Silverbox | Small nonlinear system-identification positive control; cubic feedback supplies a mechanistic hypothesis | Verify sampling, excitation, usable split and license; do not assume genuine anomaly labels |
| UCI hydraulic condition monitoring 447 | Conditional labeled-condition/fault test | Verify normal/fault definitions, whole-cycle/run grouping, measured versus commanded inputs, multirate alignment, operating regimes and terms |
| Additional Tennessee Eastman simulation data | Fallback anomaly-evaluation candidate | Verify this release's fault/run chronology, operating modes, inputs and exact split; do not treat simulation as plant measurements |
| Cascaded Tanks | Lower-priority nonlinear identification alternative | Verify which levels are observed, sampling and terms; overflow is not automatically a labeled fault |

Both scientists converged on **Silverbox for the mechanism positive control** and **hydraulics for a conditional fault test**. Their overall shortlist order differed according to the objective; there is no single experimentally established winner. These candidate leads were already in the coordinator's input pack, so the result is refinement and criticism, not discovery of previously unknown datasets.

## Objections retained

- Known nonlinear physics does not imply that sparse nonlinear residuals outperform strong linear or static fault detectors.
- An omitted forcing input or regime can create apparent nonlinear benefit; input-aware linear baselines and matched information are essential.
- Sparse coefficients and a fitted equation do not identify a causal physical law.
- Partial observations, correlated cycles and overlapping component conditions can make apparent detection performance misleading.
- Neither injected disturbances nor ordinary commanded operating changes should be passed off as naturally labeled anomalies.
- A quadratic-only library would not adequately test the documented cubic Silverbox hypothesis. Library choice must precede confirmation inspection.

## Next scientific step

Close Silverbox metadata/terms gates first, then propose a bounded cubic-versus-input-aware-linear positive-control protocol with development and untouched confirmation. Separately audit hydraulic labels and grouping before any fault-detection protocol. Retain a no-go if these gates cannot close.

No new numerical run, raw dataset download, paid lab or model-budget increase is launched by this publication. The full workflow did not discover a demonstrated SINDy anomaly-detection advantage.
