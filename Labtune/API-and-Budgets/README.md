# Labtune API calls and budget observations

Curated, provider-specific operational observations—not a reliability benchmark, universal default or scientific result. Source implementation and offline tests are published in [Labtune commit `ed8ec75`](https://github.com/JeranRolevs/labtune/commit/ed8ec75250c74fe6a7add1154ddb7bcd84e91be8). No API key, prompt, reasoning text, raw provider reply or journal is included.

- [Findings](FINDINGS.md): observed failures, diagnostics and full-workflow success.
- [Recommendations](RECOMMENDATIONS.md): conservative starting settings and budget cautions.
- [Native research study](../Sindy/03-nonlinear-dataset-discovery/README.md): separate scientific scope and limitations.

The successful full workflow used a locally patched Labtune 0.5.0 build, now committed upstream. This is not a new release tag. Validation included **156 main offline tests**, **7 example checks**, synchronized starter resources and a built-wheel export check. Setup, tests, packaging and validation made no paid provider calls.

Native streaming is opt-in; non-streaming remains the default. Successful peers are now preserved in partial aggregate output if another peer fails. This is **not automatic checkpoint/resume**. No transport retry or automatic model selection was introduced. Current Labtune [license](../LICENSE) and [licensing notice](../LICENSING.md) apply; prior CAP material retains its historical notices.
