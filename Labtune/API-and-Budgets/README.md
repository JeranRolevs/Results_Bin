# Labtune API calls and budget observations

Curated, provider-specific operational observations—not a reliability benchmark, universal default or scientific result. Source implementation, offline tests and migration notes are held in the [experimental Results_Bin folder](../Experiments/native-streaming-and-partial-output/README.md), deferred from Labtune main pending more testing. No API key, prompt, reasoning text, raw provider reply or journal is included.

- [Findings](FINDINGS.md): observed failures, diagnostics and full-workflow success.
- [Recommendations](RECOMMENDATIONS.md): conservative starting settings and budget cautions.
- [Native research study](../Sindy/03-nonlinear-dataset-discovery/README.md): separate scientific scope and limitations.

The successful full workflow used a locally patched Labtune 0.5.0 build, now archived as an experimental Results_Bin implementation rather than an upstream feature. This is not a new release tag. Validation included **156 main offline tests**, **7 example checks**, synchronized starter resources and a built-wheel export check. Setup, tests, packaging and validation made no paid provider calls.

In the experimental patch, native streaming is opt-in and non-streaming remains the default. The patch preserves successful peers in partial aggregate output if another peer fails. These changes are not currently part of unmodified Labtune main. This is **not automatic checkpoint/resume**. No transport retry or automatic model selection was introduced. Current Labtune [license](../LICENSE) and [licensing notice](../LICENSING.md) apply; prior CAP material retains its historical notices.
