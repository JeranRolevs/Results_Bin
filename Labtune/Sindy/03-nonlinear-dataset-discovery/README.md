# 03 — Native Labtune nonlinear-dataset discovery

**Outcome: the full text-only scientist workflow completed; no nonlinear anomaly-detection advantage was measured.**

- [Findings](FINDINGS.md): scientist recommendations, objections and next gates.
- [Published protocol description](PROTOCOL.md): organization, inputs, scope and limits.
- [Sources](SOURCES.md): coordinator-checked metadata, not an exhaustive literature review.
- [API and budget observations](../../API-and-Budgets/README.md): failure history and successful settings.

The run used Labtune 0.5.0 with a local streaming/partial-output patch, now retained in the [experimental Results_Bin implementation](../../Experiments/native-streaming-and-partial-output/README.md), not Labtune main. It completed in approximately **5m45s**, making **11 requests** and retaining ten actor outputs. All requests received usage receipts. One extra request corrected a malformed JSON action; there were no HTTP errors or automatic transport retries in this run.

**Provenance:** this study is a native Labtune scientist workflow, unlike the earlier CAP numerical evaluations, which used standalone evaluators. Native workflow completion is not scientific verification: `verification_status` remained `not_evaluated`, and no numerical experiments ran. The candidate leads and evidence digest were supplied by the coordinator; these were not independently discovered by agents browsing the web.

Only curated documentation is published. Raw actor outputs, prompts, reasoning, trial journals, private freezes, checkpoints/audits and credentials are excluded. The experimental source, tests and migration notes live in that dedicated folder; no upstream adoption is implied. This new study preserves the current [Labtune license](LICENSE) and [licensing notice](LICENSING.md); historical CAP files retain their original Labton notices.
