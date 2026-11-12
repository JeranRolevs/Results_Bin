# Curated experiment log

## Why this exists

Long research calls first encountered HTTP 502/504 failures. Lowering the completion ceiling avoided one transport failure but exhausted a critical scientist's reasoning allowance, producing no final answer. A documented streaming replay later completed with adequate reasoning headroom. This motivated native streaming and better partial-output preservation, not a change in scientific model selection or a claim of anomaly-detection success.

## Development and testing

1. Implemented a local native patch against Labtune revision d0f462a28bcc4267f8767316d8c73c3c72201063.
2. Ran offline parser, transport, accounting, redaction, partial-wave and complete mocked-workflow checks; 156 main tests and seven example checks passed. Starter/wheel checks passed.
3. Ran the separately authorized full scientist workflow; it completed in approximately 5m45s. Research outputs remained proposals, not measured nonlinear effects.
4. Published curated API/budget and scientist-workflow reports in this hub. Implementation was briefly pushed to Labtune as ed8ec75.
5. The user requested deferring upstream adoption until more testing. This folder now holds the implementation snapshot, complete patch and migration documentation. Removing ed8ec75 from Labtune main restores the exact baseline above; no later commits existed at the time this relocation was prepared.

## Relocation completed

The experimental implementation and documents were first pushed to Results_Bin in commit `646d6cc33b7e39740ae58c445e2e9c51702ee5cb`. Labtune main was then restored to `d0f462a28bcc4267f8767316d8c73c3c72201063` using a force-with-lease guard that required the remote tip to still be the withdrawn experimental commit. Remote branch state was checked afterward; no later commits were overwritten. Historical Git objects may remain cached by the host, as noted in README.md.

## Current disposition

Experimental; canonical home is Results_Bin, not Labtune main. No package release, production-readiness claim, automatic resume or retry capability is implied. No new paid requests were made during relocation. See TESTING.md for what remains and MIGRATION.md for the approval-gated path back to Labtune.

This is a curated human-readable change log. It does not include private provider journals, raw actor outputs, prompts, reasoning or audit archives.
