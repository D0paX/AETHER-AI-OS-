# AETHER DEFINITION OF DONE
### docs/architecture/AETHER_DEFINITION_OF_DONE.md
### The Official Engineering Acceptance Standard for Aether AI OS

---

**Date:** 2025-11-15
**Status:** ACCEPTED — ENFORCED
**Classification:** Project Governance — Acceptance Standard
**Constitutional Tier:** Tier 2 (per ADR-010 Section 16.1)
**Authority:** Principal Systems Engineer / Chief Architect
**Applies To:** Every phase, milestone, feature, module, service, API, and
implementation produced for Aether AI OS, without exception

---

## THE DEFINITION OF DONE MANDATE

**"Done" is not a feeling. It is not a developer's confidence that something
probably works. It is not a single checkbox. Done is a formally staged
climb through twelve distinct, evidenced, independently-reviewed levels,
and no milestone, feature, or phase is permitted to claim any level it has
not actually earned. This document is the only authority in Aether AI OS
that may declare something Done.**

This is not a checklist. A checklist can be skimmed, half-completed, or
rubber-stamped. What follows is an acceptance standard: a hierarchy in
which each level is the load-bearing foundation for the level above it,
where skipping a level does not merely leave a gap — it invalidates every
level built on top of it.

---

## TABLE OF CONTENTS

**Part One — Foundations**
1. [Purpose and Philosophy](#1-purpose-and-philosophy)
2. [Constitutional Integration](#2-constitutional-integration)
3. [Scope: Milestone-Level Versus Phase-Level Done](#3-scope-milestone-level-versus-phase-level-done)

**Part Two — The Twelve Levels of Done**
4. [The Pyramid](#4-the-pyramid)
5. [Level 1 — Developer Done](#level-1--developer-done)
6. [Level 2 — Implementation Done](#level-2--implementation-done)
7. [Level 3 — Architecture Done](#level-3--architecture-done)
8. [Level 4 — Testing Done](#level-4--testing-done)
9. [Level 5 — Security Done](#level-5--security-done)
10. [Level 6 — Performance Done](#level-6--performance-done)
11. [Level 7 — Documentation Done](#level-7--documentation-done)
12. [Level 8 — AI Compliance Done](#level-8--ai-compliance-done)
13. [Level 9 — Review Done](#level-9--review-done)
14. [Level 10 — Production Ready](#level-10--production-ready)
15. [Level 11 — Release Ready](#level-11--release-ready)
16. [Level 12 — Phase Complete](#level-12--phase-complete)

**Part Three — Non-Bypassable Acceptance Criteria**
17. [The Rules That Cannot Be Waived](#5-the-rules-that-cannot-be-waived)

**Part Four — The Seven Reusable Phase-Closure Templates**
18. [How These Templates Are Used](#6-how-these-templates-are-used)
19. [Template 1: Phase Review Report](#template-1-phase-review-report)
20. [Template 2: Technical Debt Report](#template-2-technical-debt-report)
21. [Template 3: Risk Review Report](#template-3-risk-review-report)
22. [Template 4: Lessons Learned Report](#template-4-lessons-learned-report)
23. [Template 5: Phase Definition of Done Report](#template-5-phase-definition-of-done-report)
24. [Template 6: GO / NO-GO Decision Report](#template-6-go--no-go-decision-report)
25. [Template 7: Phase Complete Report](#template-7-phase-complete-report)

**Part Five — Enforcement**
26. [Constitutional Status](#7-constitutional-status)

---

## PART ONE: FOUNDATIONS

---

## 1. PURPOSE AND PHILOSOPHY

### 1.1 Why "Done" Needs a Definition

Every engineer believes they know what "done" means until two engineers
compare notes. One means "it compiles." Another means "it compiles, is
tested, is documented, and has been reviewed by someone else." On a solo,
AI-assisted project — where the person who wrote the code, the person who
reviews it, and the person who decides whether to ship it can all too
easily be the same tired person on the same rushed evening — this ambiguity
is not a minor inconvenience. It is the exact failure mode that turns a
personal AI operating system into an unmaintainable pile of "should work"
code within eighteen months.

This document exists to remove the ambiguity permanently. It defines,
without room for interpretation, what "Done" means at every scale in this
project — from a single function to an entire ten-phase roadmap.

### 1.2 Why a Hierarchy, Not a List

A flat checklist invites partial completion: an engineer under time
pressure checks nine of twelve boxes and calls it done. A hierarchy does
not permit this. Each level in this document is the **entry criteria** for
the level above it. Architecture Done cannot be claimed before
Implementation Done is true, because architecture compliance is meaningless
against an implementation that does not yet match its own specification.
Security Done cannot be claimed before Testing Done is true, because a
security review of untested code is a review of code whose actual behavior
is still unknown. The hierarchy is not bureaucratic decoration — it reflects
the genuine logical dependency between these concerns.

### 1.3 What This Document Replaces

Every milestone in `PHASE_1_FOUNDATION_IMPLEMENTATION_PLAN.md` already
carries its own brief "Definition of Done" section and a "Milestone Gate."
Those sections are not superseded by this document — they are given their
full, formal meaning by it. From this point forward, any milestone's
"Definition of Done" is understood to mean: **Levels 1 through 9 of this
document, achieved in full, for that milestone's specific scope.** Any
milestone's "Milestone Gate" is understood to mean **Level 10 of this
document.** `AETHER_PHASE_EXECUTION_WORKFLOW.md` Step 22 ("Definition of
Done Verification") is the point in the phase lifecycle at which this
entire document is applied at the phase scope — Levels 11 and 12.

---

## 2. CONSTITUTIONAL INTEGRATION

This document does not introduce new standards. It organizes the standards
already established elsewhere in the Constitution into a single, ordered,
non-bypassable acceptance hierarchy. The table below is the map between
each Level and the document that actually defines its substance.

| Level | Primary Governing Document(s) |
|---|---|
| 1 — Developer Done | (Informal; no external document — see Section 5) |
| 2 — Implementation Done | The milestone's own implementation prompt; AI_GENERATION_RULES_V2.md Section 16 |
| 3 — Architecture Done | V1_TECHNICAL_SPECIFICATION.md; ARCHITECTURE_RULES.md; `pyproject.toml` import-linter contracts |
| 4 — Testing Done | ADR-011 Section 3.4 (Mandatory Testing Standards); ADR-011 Section 4, Gate Q-3 |
| 5 — Security Done | ADR-010 Section 3 (Forbidden Operations); ADR-011 Section 4, Gate Q-5 |
| 6 — Performance Done | ADR-011 Section 10 (Performance Baseline Standards) |
| 7 — Documentation Done | ADR-011 Section 3.6 (Mandatory Documentation); ADR-011 Section 4, Gate Q-4 |
| 8 — AI Compliance Done | AI_GENERATION_RULES_V2.md (in full); AI_SKILLS_INTEGRATION.md Section 7 |
| 9 — Review Done | ADR-011 Section 5.2 (Code Review Checklist); AETHER_PHASE_EXECUTION_WORKFLOW.md Steps 7–8 |
| 10 — Production Ready | AETHER_PHASE_EXECUTION_WORKFLOW.md, Milestone Cycle (Section 5) |
| 11 — Release Ready | AETHER_PHASE_EXECUTION_WORKFLOW.md Steps 19–20, 22 |
| 12 — Phase Complete | AETHER_PHASE_EXECUTION_WORKFLOW.md Steps 23, 25, 26 |

This document is a **Tier 2 Constitutional document**, joining ADR-010,
ADR-011, AI_GENERATION_RULES_V2.md, AI_SKILLS_INTEGRATION.md, and
AETHER_PHASE_EXECUTION_WORKFLOW.md at that tier, per ADR-010 Section 16.1.

---

## 3. SCOPE: MILESTONE-LEVEL VERSUS PHASE-LEVEL DONE

Not every level applies at every scale. Levels 1 through 10 apply to a
**single milestone**, and are climbed once per milestone, repeating for
every milestone the phase contains — the same inner cycle already defined
as Steps 4–14 in `AETHER_PHASE_EXECUTION_WORKFLOW.md`. Levels 11 and 12
apply to the **whole phase**, and are only attempted once every milestone
in that phase has independently reached Level 10.

A milestone that has reached Level 10 (Production Ready) is finished. A
phase is not finished until every one of its milestones has reached Level
10 **and** the phase itself has separately climbed Levels 11 and 12.

---

## PART TWO: THE TWELVE LEVELS OF DONE

---

## 4. THE PYRAMID

```
SCOPE: PHASE — attempted once, after every milestone below has finished
┌────────────────────────────────────────────────────────────┐
│  LEVEL 12 — PHASE COMPLETE                                  │
├────────────────────────────────────────────────────────────┤
│  LEVEL 11 — RELEASE READY                                   │
└────────────────────────────────────────────────────────────┘
                              ▲
                              │  requires EVERY milestone in the
                              │  phase to have independently
                              │  reached Level 10
                              │
SCOPE: MILESTONE — climbed once per milestone, repeated for every
       milestone in the phase (AETHER_PHASE_EXECUTION_WORKFLOW.md
       Steps 4–14, run once per milestone)
┌────────────────────────────────────────────────────────────┐
│  LEVEL 10 — PRODUCTION READY            (the Milestone Gate)│
├────────────────────────────────────────────────────────────┤
│  LEVEL 9  — REVIEW DONE                                     │
│  LEVEL 8  — AI COMPLIANCE DONE                               │
│  LEVEL 7  — DOCUMENTATION DONE                                │
│  LEVEL 6  — PERFORMANCE DONE                                   │
│  LEVEL 5  — SECURITY DONE                                       │
│  LEVEL 4  — TESTING DONE                                          │
│  LEVEL 3  — ARCHITECTURE DONE                                        │
│  LEVEL 2  — IMPLEMENTATION DONE                                         │
│  LEVEL 1  — DEVELOPER DONE                                                │
└────────────────────────────────────────────────────────────┘
```

Each level below states its **Entry Criteria** (what must already be true
to attempt this level), **Exit Criteria** (what must be true to pass it),
**Validation** (the exact procedure used to check it), **Evidence
Required** (the artifact that proves it was checked, not merely believed),
and **Responsible Reviewer** (per the roles defined in
AETHER_PHASE_EXECUTION_WORKFLOW.md Section 4).

---

### LEVEL 1 — DEVELOPER DONE

**Definition:** The immediate coding task is believed, by the person or
process that performed it, to be functionally complete.

**Maps to Workflow Step:** 6 (Antigravity Implementation Workflow)

| Field | Requirement |
|---|---|
| **Entry Criteria** | A specific, scoped task exists — an Antigravity implementation prompt has been issued per Workflow Step 5, or an equivalent scoped instruction for a manual change. |
| **Exit Criteria** | Every file listed in the task's "Files to Create" / "Files to Modify" exists. The code imports without error. The primary happy path has been exercised once, manually. |
| **Validation** | `python -c "import aether"` (or the relevant module) succeeds; one manual smoke test of the specific feature. |
| **Evidence Required** | None formal — this is a provisional, self-declared level. Its only artifact is the fact that Level 2 was subsequently attempted. |
| **Responsible Reviewer** | Developer (self-assessment only; no external sign-off exists at this level). |

---

### LEVEL 2 — IMPLEMENTATION DONE

**Definition:** The generated output exactly matches everything specified
in the task, with nothing missing and nothing extra.

**Maps to Workflow Step:** 6–7

| Field | Requirement |
|---|---|
| **Entry Criteria** | Level 1 achieved. |
| **Exit Criteria** | Every item in the prompt's "Expected Deliverables" section exists. Nothing outside the prompt's "Files to Create" / "Files to Modify" list was touched — no scope creep, no hidden complexity, per AI_GENERATION_RULES_V2.md Section 16. |
| **Validation** | Diff the actual changed file set against the prompt's declared file list. Confirm zero extraneous files and zero missing deliverables. |
| **Evidence Required** | The prompt's own "Expected Deliverables" checklist, marked complete item by item. |
| **Responsible Reviewer** | Developer (Workflow Step 7, first pass). |

---

### LEVEL 3 — ARCHITECTURE DONE

**Definition:** The implementation respects every module boundary and
locked API contract defined in the Constitution.

**Maps to Workflow Step:** 9

| Field | Requirement |
|---|---|
| **Entry Criteria** | Level 2 achieved. |
| **Exit Criteria** | Zero import-linter violations. Zero unauthorized cross-module imports (no `qdrant_client`/`sqlalchemy` outside `aether/memory/_stores/`; no `anthropic`/`openai`/`litellm` outside `aether/llm/_providers/`). Every locked contract touched by this task (`MemoryAPI`, `LLMRouter`, `BaseTool`, `BaseAgent`, `AetherEvent`) matches V1_TECHNICAL_SPECIFICATION.md exactly. |
| **Validation** | `uv run lint-imports`; `uv run mypy aether/ services/ --strict`; the boundary `grep` patterns defined in Workflow Step 9. |
| **Evidence Required** | Recorded command output showing zero violations on all three checks. |
| **Responsible Reviewer** | Claude (Principal Architect). |

---

### LEVEL 4 — TESTING DONE

**Definition:** Every required test exists and passes, including any
milestone-specific critical test.

**Maps to Workflow Step:** 12

| Field | Requirement |
|---|---|
| **Entry Criteria** | Level 3 achieved. |
| **Exit Criteria** | Unit, contract, architecture, and integration suites all pass. Any milestone-specific critical test named in the originating prompt — the cross-session memory persistence test in M1.5, the six-step Voice Milestone sequence in M1.10, or the equivalent for any future milestone — explicitly passes. Test requirements from ADR-011 Section 3.4 (one test minimum for every new public function, unit and integration for every new agent or tool) are met. |
| **Validation** | `uv run pytest tests/unit/ tests/contracts/ tests/architecture/ tests/integration/ -v --tb=short`, run in that order. |
| **Evidence Required** | Full test run output. Explicit written confirmation that the milestone's critical test passed, quoting its result. |
| **Responsible Reviewer** | Developer (executes); Claude (confirms coverage matches the requirement). |

---

### LEVEL 5 — SECURITY DONE

**Definition:** No forbidden pattern, secret, or unsafe operation exists
anywhere in the task's code.

**Maps to Workflow Step:** 10

| Field | Requirement |
|---|---|
| **Entry Criteria** | Level 4 achieved. |
| **Exit Criteria** | Zero matches on the forbidden-pattern scan (ADR-010 Section 8.2). The manual Security Gate checklist (ADR-011 Section 4, Gate Q-5) is fully checked: no secrets, no unscoped `DELETE`/`UPDATE`, no raw-string SQL, no unvalidated external input, no bypassed permission check. |
| **Validation** | `grep -rn "DROP TABLE\|TRUNCATE\|rm -rf\|flushall\|drop_all"` across `aether/`, `services/`, `migrations/`; manual Gate Q-5 checklist walkthrough. |
| **Evidence Required** | Scan output (zero matches); completed Gate Q-5 checklist. |
| **Responsible Reviewer** | Developer (executes the scan); Claude (reviews for subtler issues — prompt injection surface, permission bypass, credential handling). |

---

### LEVEL 6 — PERFORMANCE DONE

**Definition:** No measured path has regressed beyond an acceptable
threshold.

**Maps to Workflow Step:** 11

| Field | Requirement |
|---|---|
| **Entry Criteria** | Level 5 achieved. |
| **Exit Criteria** | For any milestone touching a path listed in ADR-011 Section 10.3, the measured value is within target, or any regression is under the 20% P2 threshold defined in ADR-011 Section 10.5. A regression exceeding 100% blocks this level unconditionally. |
| **Validation** | Informal spot-check at milestone scope, per ADR-011 Section 10.2 methodology (10 runs, p50/p95). A comprehensive, phase-wide baseline is not required at this level — that belongs to Level 11. |
| **Evidence Required** | Recorded measurement, even if brief, for any path the milestone affects. |
| **Responsible Reviewer** | Developer. |

---

### LEVEL 7 — DOCUMENTATION DONE

**Definition:** Every document a reader would consult reflects the actual,
current state of the system, not an aspiration for what it will contain
later.

**Maps to Workflow Step:** 15

| Field | Requirement |
|---|---|
| **Entry Criteria** | Level 6 achieved. |
| **Exit Criteria** | `CHANGELOG.md` entry exists (ADR-010 Section 17.5 format). `README.md` milestone checkbox updated. `V1_TECHNICAL_SPECIFICATION.md` (or the phase's own Technical Specification) synchronized wherever the implementation diverged from what was originally specified. Every new public function, class, and module carries the required docstring per ADR-011 Section 3.6. |
| **Validation** | ADR-011 Section 4, Gate Q-4 (Documentation Gate) checklist, walked in full. |
| **Evidence Required** | Completed Gate Q-4 checklist. |
| **Responsible Reviewer** | Developer. |

---

### LEVEL 8 — AI COMPLIANCE DONE

**Definition:** The generation *process* itself — not merely its output —
followed every AI governance rule in the Constitution.

**Maps to Workflow Step:** 4–5, 8

| Field | Requirement |
|---|---|
| **Entry Criteria** | Level 7 achieved. |
| **Exit Criteria** | The correct skill categories were loaded before the prompt was drafted, per AI_SKILLS_INTEGRATION.md Section 7. The prompt itself followed the fifteen-section format and was checked against the Formal AI Decision Framework in AI_GENERATION_RULES_V2.md Section 19. No Zero-Tolerance Violation (ADR-011 Section 2) is present anywhere in the output. No Level 4 Prohibited Action (AI_GENERATION_RULES_V2.md Section 7) occurred during generation. Antigravity's own self-verification statement (AI_GENERATION_RULES_V2.md Section 21) was produced and reviewed. |
| **Validation** | Review the originating prompt against the fifteen-section template and the skill-loading declaration; review the self-verification statement Antigravity attached to its output. |
| **Evidence Required** | The prompt itself (already an artifact of Workflow Step 5) plus Antigravity's self-verification statement. |
| **Responsible Reviewer** | Claude (Principal Architect) — this level audits the AI-assisted *process*, distinct from Level 3's audit of the code's structure. |

---

### LEVEL 9 — REVIEW DONE

**Definition:** Both required independent reviews — human and AI — have
been completed and have each returned a passing verdict.

**Maps to Workflow Step:** 7–8

| Field | Requirement |
|---|---|
| **Entry Criteria** | Level 8 achieved. |
| **Exit Criteria** | The developer's full forty-item Code Review Checklist (ADR-011 Section 5.2) is complete with zero unresolved items. The Claude Review Workflow (Workflow Step 8) returned a verdict of APPROVED or APPROVED WITH NOTES. Neither review alone is sufficient — both are required. |
| **Validation** | Both checklists/verdicts exist as recorded artifacts. |
| **Evidence Required** | The signed forty-item checklist; the Claude Review verdict statement. |
| **Responsible Reviewer** | Developer **and** Claude — dual sign-off, non-substitutable. |

---

### LEVEL 10 — PRODUCTION READY

**Definition:** A single milestone has satisfied every one of Levels 1
through 9, simultaneously and completely. This is the Milestone Gate.

**Maps to Workflow Step:** end of the Steps 4–14 milestone cycle

| Field | Requirement |
|---|---|
| **Entry Criteria** | Level 9 achieved for this milestone. |
| **Exit Criteria** | All nine prior levels' exit criteria are simultaneously true for this milestone. The milestone's own Definition of Done, as stated in its originating implementation prompt, is satisfied in full. |
| **Validation** | A single consolidated checklist referencing all nine prior levels' evidence artifacts. |
| **Evidence Required** | The Milestone Gate record — the GO/NO-GO statement already embedded at the end of every Phase 1 implementation prompt ("GO: ... / NO-GO: ..."). |
| **Responsible Reviewer** | Developer — final milestone approval authority, per AETHER_PHASE_EXECUTION_WORKFLOW.md Section 4.3. |

**This is the level that unlocks the next milestone's Step 4 (AI Skill
Loading Workflow) in the phase's inner cycle.**

---

### LEVEL 11 — RELEASE READY

**Definition:** Every milestone in the phase has independently achieved
Production Ready, and the phase-wide integration checks pass.

**Maps to Workflow Step:** 19–20

| Field | Requirement |
|---|---|
| **Entry Criteria** | Every milestone in the phase's Implementation Plan has reached Level 10. |
| **Exit Criteria** | The full-phase regression suite (Workflow Step 14, run at phase scope per Step 19) passes. A phase-wide performance baseline is measured and compared to the prior phase (ADR-011 Section 10, in full). The Phase Review Report (Template 1, below) records an overall verdict of ARCHITECTURALLY COMPLIANT. The Phase Definition of Done Report (Template 5, below) confirms every milestone independently reached Level 10. |
| **Validation** | Workflow Steps 19, 20, and 22, executed in full, across the entire phase's scope — not merely its final milestone. |
| **Evidence Required** | `PHASE_{N}_REVIEW_REPORT.md` and `PHASE_{N}_DEFINITION_OF_DONE_REPORT.md`. |
| **Responsible Reviewer** | Claude (produces the report); Developer (accepts it). |

---

### LEVEL 12 — PHASE COMPLETE

**Definition:** The phase has been formally reviewed, decided upon, closed,
tagged, and archived.

**Maps to Workflow Step:** 21, 23, 25, 26

| Field | Requirement |
|---|---|
| **Entry Criteria** | Level 11 achieved. |
| **Exit Criteria** | A GO decision is recorded (Workflow Step 23). Phase Closure is executed — `phase/{N}` merged to `develop` to `main`, phase tag pushed (Step 25). Phase Archive is executed (Step 26). Lessons Learned is documented (Step 21). |
| **Validation** | All mandatory phase documents (Section 6, below) exist, are committed, and are internally consistent with one another. |
| **Evidence Required** | `PHASE_{N}_GO_NO_GO_REPORT.md` showing GO; the phase completion git tag, pushed and visible in repository history. |
| **Responsible Reviewer** | Developer — sole GO/NO-GO authority, per AETHER_PHASE_EXECUTION_WORKFLOW.md Section 4.3. No other party may grant this level. |

---

## PART THREE: NON-BYPASSABLE ACCEPTANCE CRITERIA

---

## 5. THE RULES THAT CANNOT BE WAIVED

The twelve levels above describe a normal, healthy climb. The rules below
describe the floor beneath that climb — conditions that block progress
absolutely, regardless of schedule pressure, developer confidence, or how
close to Done everything else appears to be. No level, at any scale, may
be marked achieved while any applicable rule below is violated.

**NB-1 — Zero-Tolerance Violations block everything.**
Any Zero-Tolerance Violation (ADR-011 Section 2, ZT-1 through ZT-10) found
anywhere in a task's output means Level 1 itself is void. Code containing
one of these ten violations is not "Developer Done with an issue" — it is
not Done at any level until the violation is removed.

**NB-2 — A milestone's critical test is never skipped, mocked, or waived.**
Where a milestone's originating prompt names a specific defining test — the
cross-session memory persistence test in M1.5, the six-step Voice Milestone
sequence in M1.10, or the equivalent for a future milestone — Level 4
(Testing Done) is not achieved until that exact test explicitly passes.
Substituting a simpler test, mocking the dependency it validates, or
declaring it "effectively passing" does not satisfy this requirement.

**NB-3 — Import boundary violations block Architecture Done unconditionally.**
There is no threshold of "just one small boundary crossing." A single
unauthorized import blocks Level 3 exactly as completely as a hundred would.

**NB-4 — Level 4/5 destructive operations never shortcut a Done level.**
A destructive or Level 5 operation under ADR-010 Section 3 is never
performed in service of reaching a Done level faster. The override process
in ADR-010 Section 3.8 is followed in full, every time, with no exception
made because a deadline is close.

**NB-5 — Open P1 technical debt blocks Phase Complete unconditionally.**
Per ADR-010 Section 13.3, any P1 debt item discovered during a phase is
resolved within that same phase. Level 12 is never achieved with a P1 item
still open in `DEBT_REGISTER.md`.

**NB-6 — A GO decision requires the developer's own explicit confirmation.**
No volume of AI review, however thorough, substitutes for this. Claude may
recommend a verdict; only the developer's affirmative confirmation
constitutes a recorded GO at Level 12.

**NB-7 — Documentation Done is never satisfied by a promise to document later.**
The `CHANGELOG.md` entry and specification synchronization happen before
Level 7 is marked complete, not after. "I'll document this in the next
milestone" does not close this level.

**NB-8 — AI Compliance Done cannot be reconstructed retroactively.**
The evidence for Level 8 is the actual prompt used and the actual
self-verification statement Antigravity produced at generation time.
Describing after the fact what a prompt "was meant to do" is not evidence.

---

## PART FOUR: THE SIX REUSABLE PHASE-CLOSURE TEMPLATES

---

## 6. HOW THESE TEMPLATES ARE USED

Every template below is designed to be copied, verbatim, into a new file
for each new phase — replacing only the `{N}`, date, and blank-field
placeholders. No structural modification is needed or permitted; a
template that must be restructured for a given phase has failed its
purpose. Each is presented as a fenced code block so it can be copied
directly.

The templates are ordered by when they are produced in the phase
lifecycle: the **Phase Review Report** is the comprehensive audit produced
at Workflow Step 20. The **Technical Debt Report** and **Risk Review
Report** are its two supporting inputs, extracted and finalized at the
same step. The **Lessons Learned Report** follows at Step 21. The **Phase
Definition of Done Report** is produced at Step 22, and is the artifact
that formally verifies Level 11 (Release Ready) has been reached before
any GO decision is attempted. The **GO / NO-GO Decision Report** is
produced at Step 23, informed by everything before it. The **Phase
Complete Report** is the short closing summary produced at Step 25, after
GO has already been recorded, and links out to every document that
preceded it rather than repeating their content.

Storage location for a completed set:
```
docs/phases/phase-{N}/
  PHASE_{N}_REVIEW_REPORT.md
  PHASE_{N}_TECHNICAL_DEBT_REPORT.md
  PHASE_{N}_RISK_REVIEW_REPORT.md
  PHASE_{N}_LESSONS_LEARNED.md
  PHASE_{N}_DEFINITION_OF_DONE_REPORT.md
  PHASE_{N}_GO_NO_GO_REPORT.md
  PHASE_{N}_COMPLETE_REPORT.md
```

---

### TEMPLATE 1: PHASE REVIEW REPORT

```markdown
# PHASE {N} REVIEW REPORT
### docs/phases/phase-{N}/PHASE_{N}_REVIEW_REPORT.md

**Phase:** {N} — {Phase Name, e.g., "PC Control"}
**Review Date:** {YYYY-MM-DD}
**Reviewed By:** Claude (Principal Architect) / Developer
**Milestones Covered:** {list every milestone in this phase}
**Overall Verdict:** ARCHITECTURALLY COMPLIANT / DEFICIENCIES FOUND

## Dimension 1: Architecture

- [ ] Every module's public `__init__.py` matches V1_TECHNICAL_SPECIFICATION.md (or this phase's own Technical Specification)
- [ ] `uv run lint-imports` — zero violations
- [ ] `uv run mypy aether/ services/ --strict` — zero errors
- [ ] Every locked contract touched this phase matches specification exactly

Notes: _______________

## Dimension 2: Security

- [ ] Full forbidden-pattern scan — zero matches
- [ ] Gate Q-5 manual checklist — complete, phase-wide
- [ ] No unresolved ADR-010 Section 3 violation anywhere in the phase

Notes: _______________

## Dimension 3: Testing

- [ ] Full suite (unit, contract, architecture, integration) passes for the entire phase
- [ ] Every milestone's critical test explicitly re-confirmed passing
- [ ] Full-phase regression suite (Workflow Step 14/19) passes

Notes: _______________

## Dimension 4: Performance

- [ ] `docs/performance/phase-{N}-baseline.md` complete
- [ ] Compared against prior phase baseline — no regression exceeding the P1 threshold (ADR-011 Section 10.5)

Notes: _______________

## Dimension 5: Documentation

- [ ] All phase documentation current and accurate
- [ ] `CHANGELOG.md` phase-level entry complete
- [ ] `V1_TECHNICAL_SPECIFICATION.md` synchronized with actual implementation

Notes: _______________

## Dimension 6: Maintainability

- [ ] ADR-011 Section 8 complexity standards hold across the phase (function length, file size, cyclomatic complexity, nesting depth)
- [ ] Zero open P1 technical debt (see Technical Debt Report)

Notes: _______________

## Dimension 7: Governance

- [ ] Every milestone in this phase independently reached Level 10 (Production Ready)
- [ ] Every milestone's five checklists (Build, Test, Validation, Architecture Compliance, Security) are on record

Notes: _______________

## Dimension 8: Code Quality

- [ ] Zero Zero-Tolerance Violations (ADR-011 Section 2) anywhere in the phase's code
- [ ] Zero unresolved rookie-mistake patterns (ADR-011 Section 3.2.6)

Notes: _______________

## Deficiencies Found (if any)

| # | Deficiency | Severity (P1/P2/P3) | Resolution Required Before GO |
|---|---|---|---|
| | | | |

## Overall Verdict

[ ] ARCHITECTURALLY COMPLIANT — proceed to Level 11 (Release Ready)
[ ] DEFICIENCIES FOUND — return to the affected milestone's Bug Fix Workflow (Step 13)
```

---

### TEMPLATE 2: TECHNICAL DEBT REPORT

```markdown
# PHASE {N} TECHNICAL DEBT REPORT
### docs/phases/phase-{N}/PHASE_{N}_TECHNICAL_DEBT_REPORT.md

**Phase:** {N} — {Phase Name}
**Report Date:** {YYYY-MM-DD}
**Source:** Extracted from docs/technical-debt/DEBT_REGISTER.md

## Debt Opened During This Phase

| ID | Title | Priority | Milestone Opened | Status |
|---|---|---|---|---|
| DEBT-{NNN} | | P1/P2/P3 | | Open/Resolved |

## Debt Resolved During This Phase

| ID | Title | Priority | Opened In Phase | Resolution |
|---|---|---|---|---|
| DEBT-{NNN} | | | | |

## Debt Carried Forward Into Next Phase

| ID | Title | Priority | Carry-Forward Reason | Target Resolution |
|---|---|---|---|---|
| DEBT-{NNN} | | P2/P3 only — P1 may never carry forward | | |

## Summary Counts

- P1 opened this phase: {count} — **must be 0 to proceed to Level 12**
- P2 opened this phase: {count}
- P3 opened this phase: {count}
- Total resolved this phase: {count}

## Statement

[ ] Zero P1 technical debt items remain open. This report satisfies
    Non-Bypassable Rule NB-5 of AETHER_DEFINITION_OF_DONE.md.
```

---

### TEMPLATE 3: RISK REVIEW REPORT

```markdown
# PHASE {N} RISK REVIEW REPORT
### docs/phases/phase-{N}/PHASE_{N}_RISK_REVIEW_REPORT.md

**Phase:** {N} — {Phase Name}
**Review Date:** {YYYY-MM-DD}
**Next Phase:** {N+1} — {Next Phase Name}

## Risks That Materialized During This Phase

| Risk | Category | Impact | How It Was Handled |
|---|---|---|---|
| | Technical/Security/Maintenance/AI-Dependency/Scalability/Solo-Developer | | |

## Risks Identified For The Next Phase

| Risk | Category | Likelihood | Impact | Proposed Mitigation |
|---|---|---|---|---|
| | | Low/Medium/High | Low/Medium/High | |

## AI Model Dependency Risk

- Current LOCAL/CHEAP/STANDARD/PREMIUM tier mapping: _______________
- Any provider instability observed this phase: _______________
- Ollama local-model reliability this phase: _______________

## Solo Developer Sustainability Check

- Away Protocol invoked this phase: Yes/No — if yes, reference context-log.md entry
- Scope Management Rules (ADR-010 Section 18.5) held without violation: Yes/No
- Estimated vs actual phase duration: {planned} vs {actual}

## Overall Risk Posture Entering Next Phase

[ ] LOW — proceed to next phase without additional mitigation
[ ] MEDIUM — proceed with the mitigations listed above tracked as debt
[ ] HIGH — do not proceed; escalate to an ADR before Phase {N+1} begins
```

---

### TEMPLATE 4: LESSONS LEARNED REPORT

```markdown
# PHASE {N} LESSONS LEARNED
### docs/phases/phase-{N}/PHASE_{N}_LESSONS_LEARNED.md

**Phase:** {N} — {Phase Name}
**Report Date:** {YYYY-MM-DD}

## What Went Well

- 

## What Was Difficult

- 

## What Would Be Done Differently

- 

## Estimation Accuracy

| Milestone | Planned Duration | Actual Duration | Variance |
|---|---|---|---|
| | | | |

## Technical Debt Incurred This Phase

See PHASE_{N}_TECHNICAL_DEBT_REPORT.md for the full accounting.
Summary: {P1 count} P1, {P2 count} P2, {P3 count} P3.

## Process Improvements For The Next Phase

- 

## Carry Into Phase {N+1} Initialization

These specific improvements are to be applied at Phase {N+1}'s own Step 2
(Phase Initialization):

- 
```

---

### TEMPLATE 5: PHASE DEFINITION OF DONE REPORT

```markdown
# PHASE {N} DEFINITION OF DONE REPORT
### docs/phases/phase-{N}/PHASE_{N}_DEFINITION_OF_DONE_REPORT.md

**Phase:** {N} — {Phase Name}
**Report Date:** {YYYY-MM-DD}
**Verified By:** Claude (Principal Architect) / Developer

This report is the formal proof that Level 11 (Release Ready) of
AETHER_DEFINITION_OF_DONE.md has been reached. It is produced at
AETHER_PHASE_EXECUTION_WORKFLOW.md Step 22, after Lessons Learned (Step
21) and before the GO / NO-GO Decision (Step 23) is attempted.

## Milestone-Level Verification (Levels 1–10, per milestone)

| Milestone | Level 10 (Production Ready) Achieved | Evidence Reference |
|---|---|---|
| | Yes/No | {link to that milestone's own Milestone Gate record} |

Every row above must read "Yes" before this report may proceed further.

## Phase-Level Verification (Level 11)

- [ ] Every milestone above independently reached Level 10
- [ ] Full-phase regression suite passed (Workflow Step 14, run at Step 19)
- [ ] Phase-wide performance baseline recorded (`docs/performance/phase-{N}-baseline.md`)
- [ ] `PHASE_{N}_REVIEW_REPORT.md` verdict: ARCHITECTURALLY COMPLIANT

## Non-Bypassable Rules Check

Confirm none of NB-1 through NB-8 (AETHER_DEFINITION_OF_DONE.md Section 5)
were violated anywhere in this phase:

- [ ] NB-1 — No Zero-Tolerance Violation present anywhere
- [ ] NB-2 — Every milestone's critical test explicitly passed, never mocked or waived
- [ ] NB-3 — Zero import boundary violations anywhere in the phase
- [ ] NB-4 — No Level 4/5 destructive operation bypassed its override process
- [ ] NB-5 — Zero open P1 technical debt (`PHASE_{N}_TECHNICAL_DEBT_REPORT.md`)
- [ ] NB-6 — (Confirmed at Step 23, not here — GO requires the developer's own signature)
- [ ] NB-7 — Documentation was never deferred; Level 7 was satisfied before being marked complete, for every milestone
- [ ] NB-8 — Every Level 8 (AI Compliance Done) claim has its prompt and self-verification statement on record

## Overall Determination

[ ] LEVEL 11 (RELEASE READY) ACHIEVED — proceed to
    `PHASE_{N}_GO_NO_GO_REPORT.md` (Template 6)
[ ] LEVEL 11 NOT ACHIEVED — return to the specific milestone or step that
    failed; do not attempt a GO decision until this report reads ACHIEVED
```

---

### TEMPLATE 6: GO / NO-GO DECISION REPORT

```markdown
# PHASE {N} GO / NO-GO DECISION REPORT
### docs/phases/phase-{N}/PHASE_{N}_GO_NO_GO_REPORT.md
### (Template 6 — requires Template 5, the Definition of Done Report, to read ACHIEVED first)

**Phase:** {N} — {Phase Name}
**Decision Date:** {YYYY-MM-DD}
**Decision Authority:** Developer (sole authority, per
AETHER_PHASE_EXECUTION_WORKFLOW.md Section 4.3)

## GO Criteria — ALL must be true

### Milestone Completion
- [ ] Every milestone in this phase's Implementation Plan reached Level 10
      (Production Ready)

### Defining Tests
- [ ] Every milestone-specific critical test explicitly passed
- [ ] {List each critical test by name and milestone}

### Quality Gates
- [ ] `uv run lint-imports` — zero violations, full phase
- [ ] `uv run mypy aether/ services/ --strict` — zero errors, full phase
- [ ] `uv run ruff check .` — zero warnings, full phase
- [ ] Full test suite passes, full phase
- [ ] Full forbidden-pattern scan — zero matches, full phase

### Architecture
- [ ] PHASE_{N}_REVIEW_REPORT.md verdict: ARCHITECTURALLY COMPLIANT
- [ ] PHASE_{N}_DEFINITION_OF_DONE_REPORT.md overall determination: LEVEL 11 ACHIEVED
- [ ] Zero open P1 technical debt (PHASE_{N}_TECHNICAL_DEBT_REPORT.md)

### Operational
- [ ] `start.ps1` brings the system up cleanly from cold state
- [ ] `stop.ps1` shuts down cleanly
- [ ] Backup verified current (`backup.ps1` manifest shows `verified: true`)
- [ ] Every capability this phase introduced has been used interactively,
      not merely tested automatically

### Documentation
- [ ] `CHANGELOG.md` phase entry complete
- [ ] `V1_TECHNICAL_SPECIFICATION.md` synchronized
- [ ] `README.md` milestone table fully checked for this phase
- [ ] PHASE_{N}_LESSONS_LEARNED.md complete
- [ ] PHASE_{N}_RISK_REVIEW_REPORT.md complete
- [ ] PHASE_{N}_DEFINITION_OF_DONE_REPORT.md complete, reading ACHIEVED

## NO-GO Triggers — ANY ONE triggers NO-GO

- [ ] Any milestone below Level 10
- [ ] Any critical test failing
- [ ] Any quality gate failing
- [ ] PHASE_{N}_REVIEW_REPORT.md shows DEFICIENCIES FOUND
- [ ] Any open P1 technical debt
- [ ] Backup not verified

## If NO-GO

Per AETHER_PHASE_EXECUTION_WORKFLOW.md Step 23: development stops on the
failing item, the defect is corrected, and **all** checklists above are
re-run from the beginning — not merely the item that failed.

Failing item(s): _______________
Corrective action taken: _______________
Re-verification date: _______________

## Decision Statement

```
PHASE {N} GO DECISION

Date: {YYYY-MM-DD}
All milestone gates: PASSED
Defining test(s): ACHIEVED on {date}
Architecture audit: ARCHITECTURALLY COMPLIANT
Technical debt: {P2 count} P2, {P3 count} P3, 0 P1
All quality gates: PASSED

PHASE {N} IS COMPLETE.
PHASE {N+1} PLANNING MAY BEGIN.
```

**Developer confirmation (required — no other party may supply this):**

Signed: _______________  Date: _______________
```

---

### TEMPLATE 7: PHASE COMPLETE REPORT

```markdown
# PHASE {N} COMPLETE REPORT
### docs/phases/phase-{N}/PHASE_{N}_COMPLETE_REPORT.md

**Phase:** {N} — {Phase Name}
**Started:** {YYYY-MM-DD}
**Completed:** {YYYY-MM-DD}
**Total Duration:** {X weeks / Y working days}
**Git Tag:** `v0.x.x-phase{N}-complete`

## Milestones Completed

| Milestone | Codename | Completion Date |
|---|---|---|
| | | |

## Headline Capabilities Delivered

- 

## Supporting Documents

- Technical Specification: {link or "N/A — covered by V1_TECHNICAL_SPECIFICATION.md"}
- Implementation Plan: `PHASE_{N}_IMPLEMENTATION_PLAN.md`
- Review Report: `PHASE_{N}_REVIEW_REPORT.md`
- Technical Debt Report: `PHASE_{N}_TECHNICAL_DEBT_REPORT.md`
- Risk Review Report: `PHASE_{N}_RISK_REVIEW_REPORT.md`
- Lessons Learned: `PHASE_{N}_LESSONS_LEARNED.md`
- Definition of Done Report: `PHASE_{N}_DEFINITION_OF_DONE_REPORT.md`
- GO / NO-GO Decision: `PHASE_{N}_GO_NO_GO_REPORT.md`

## Final Status

**PHASE {N}: COMPLETE**
**Definition of Done Level Achieved: 12 (Phase Complete)**

## Next Phase

Phase {N+1} — {Next Phase Name} — entry criteria satisfied. Awaiting
explicit developer approval to begin Phase {N+1}, Step 1, per
AETHER_PHASE_EXECUTION_WORKFLOW.md Step 27.
```

---

## PART FIVE: ENFORCEMENT

---

## 7. CONSTITUTIONAL STATUS

This document is a Tier 2 Constitutional document. No milestone, feature,
module, service, API, or phase may be described as "done," "complete," or
"finished" in any commit message, review, or conversation about this
project unless the specific level being claimed has been achieved in full,
per this document, with its required evidence on record.

No generated code, and no schedule pressure, may override, contradict, or
abbreviate any level or any non-bypassable rule in this document. Where a
task appears finished but this document has not been satisfied, the task
is not finished — it is merely written.

---

*Document Version: 1.1*
*Status: ACCEPTED — ENFORCED*
*Constitutional Tier: Tier 2*
*Governs: Every phase from Phase 1 forward, applied retroactively to the
remainder of Phase 1 from this document's adoption*
*Amendment History: v1.1 — added Template 5 (Phase Definition of Done
Report), correcting a gap where AETHER_PHASE_EXECUTION_WORKFLOW.md Step 22
had no named artifact of its own; renumbered the former Templates 5–6 to
6–7 accordingly*
*Review Trigger: Any acceptance-standard dispute, or at the completion of
each phase*
*Owner: Principal Systems Engineer*
*Last Updated: 2025-11-15*
