# Experimental native streaming and partial-output preservation

**Status: experimental, deferred from Labtune main pending more testing. Not a release or a production recommendation.** This Results_Bin folder is the canonical home for the proposed changes and their migration documentation. Do not assume they are installed by cloning unmodified Labtune.

## Purpose and location

The experiment adds opt-in OpenAI-format SSE streaming to Labtune's generation provider and preserves successful peer outputs when a sibling fails before dependency-wave aggregation. It does not add automatic network retries, model switching, budget increases or checkpoint/resume.

- `implementation/`: nine changed/new files, retaining their intended Labtune repository paths. This is a partial source snapshot, not a standalone package.
- `patches/labtune-streaming.patch`: complete implementation/test/docs patch against the exact base revision in MIGRATION.md.
- [IMPLEMENTATION.md](IMPLEMENTATION.md): what changes and where each file belongs.
- [TESTING.md](TESTING.md): completed validation and missing coverage.
- [MIGRATION.md](MIGRATION.md): safe application, verification and later promotion steps.
- [CHANGELOG.md](CHANGELOG.md): curated provenance and disposition, not private trial logs.
- [API findings](../../API-and-Budgets/README.md) and [scientist-workflow findings](../../Sindy/03-nonlinear-dataset-discovery/README.md): outcomes and scope limitations.

The source was briefly committed upstream as `ed8ec75`. The user requested its removal from Labtune main and retention here until testing is sufficient. Labtune main was restored to the upstream baseline `d0f462a28bcc4267f8767316d8c73c3c72201063`; do not use the withdrawn commit as a dependency. Git hosting may retain old objects, so branch removal is not a promise of purging every cached historical object.

No credentials, raw prompts, reasoning, trial outputs/journals, datasets, private freezes or audit archives are included. The patch and source snapshot contain implementation, offline fixtures and public documentation only. Full [LICENSE](LICENSE) and [LICENSING.md](LICENSING.md) are preserved unchanged: copyright Pioneertown B.V.; author Goran Mitevski.
