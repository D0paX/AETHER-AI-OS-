# ADR-012: SIMPLIFIED BRANCH MODEL FOR SOLO, SEQUENTIAL-PHASE DEVELOPMENT
### docs/architecture/decisions/ADR-012-SIMPLIFIED_BRANCH_MODEL.md

---

**Date:** 2025-11-15
**Status:** ACCEPTED — AMENDS ADR-010 SECTION 7.1
**Classification:** Constitutional Amendment
**Authority:** Principal Systems Engineer, via the Constitutional
Amendment Process defined in ADR-010 Section 16.4
**Amends:** ADR-010-AI_SAFETY_AND_CODE_GENERATION.md Section 7.1
(Repository Protection — Branch Structure)
**Also Corrects:** AETHER_PHASE_EXECUTION_WORKFLOW.md Step 25 (Phase
Closure), which currently assumes ADR-010's original branch model

---

## 1. CONTEXT

ADR-010 Section 7.1 specifies a branch model of `main` (stable,
production-ready), `develop` (integration branch), `phase/N` (active
phase work, branched from `develop`), and `feature/X`/`fix/X` (branched
from `phase/N`).

DEBT-016, discovered during Phase 2's remediation arc (specifically,
while committing and pushing the M2.1.5–M2.1.9 remediation work), found
that no `develop` branch has ever existed in this repository, across
either Phase 1 or Phase 2. `phase/2` was created directly off `main`,
with zero divergence until that push. This is not a recent regression —
it reflects how the repository has always actually been structured,
contradicting the Constitution's stated model since Phase 1.

## 2. DECISION

The branch model is simplified to `main` + `phase/N` +
`feature/X`/`fix/X`. The `develop` branch is retired as a requirement.
`phase/N` branches directly from `main`. `feature/X` and `fix/X` branch
from `phase/N`, for optional sub-efforts within a phase larger than a
single milestone, and merge back into `phase/N`. Phase Closure
(AETHER_PHASE_EXECUTION_WORKFLOW.md Step 25) merges `phase/N` directly
into `main` — the intermediate `develop` step is removed from that
procedure.

## 3. ALTERNATIVES CONSIDERED

**(a) Retroactively create `develop` and conform to the original
model.** Rejected. This would add an integration branch the project has
never needed and, given its actual working structure, never will.

**(b) Leave the Constitution mismatched with reality indefinitely.**
Rejected. An unenforced rule invites exactly the kind of silent gap this
entire remediation arc — DEBT-002, DEBT-007, DEBT-009, and now
DEBT-016 — has been about closing. A branch model nobody follows is
worse than no branch model at all, because it creates the appearance of
governance without its substance.

## 4. TRADEOFF ANALYSIS

`develop`'s value, in the standard branching pattern it's drawn from, is
integrating multiple concurrent branches before promotion to `main`.
This project has never had multiple concurrent phase branches, and its
entire governance structure guarantees it never will: AETHER_PHASE_
EXECUTION_WORKFLOW.md's Non-Negotiable Rules (Section 8) require exactly
one milestone in progress at a time, within exactly one active phase at
a time. Under that discipline, `develop` and `main` would always be
byte-identical at every merge — there is never a second branch waiting
to be integrated alongside `phase/N`. The branch adds process weight
with no corresponding integration-testing benefit in this project's
actual, established shape.

## 5. CONSEQUENCES

- ADR-010 Section 7.1 is amended to reflect the simplified model, in a
  dedicated commit per Section 16.4's required format.
- AETHER_PHASE_EXECUTION_WORKFLOW.md Step 25 is corrected: "Merge
  `phase/{N}` directly into `main`" replaces the original two-step
  `develop`-then-`main` sequence.
- No branch needs to be created to close this debt — the correction is
  to the Constitution's stated model, matching the repository's actual,
  working structure, not the other way around.
- This ADR does not affect ADR-010 Section 7.2 (branch protection rules)
  or Section 7.3 (commit standards), which apply identically to the
  simplified model.

## 6. APPROVAL RECORD

Approved by the developer, 2025-11-15, resolving DEBT-016.

---

*Document Version: 1.0*
*Status: ACCEPTED*
*Constitutional Tier: Tier 3 (Specific Decisions, per ADR-010 Section
16.1) — amends a Tier 2 document under the process that document itself
defines*
*Owner: Principal Systems Engineer*
*Last Updated: 2025-11-15*
