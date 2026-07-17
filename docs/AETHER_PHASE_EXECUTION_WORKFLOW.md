# AETHER PHASE EXECUTION WORKFLOW
### docs/architecture/AETHER_PHASE_EXECUTION_WORKFLOW.md
### Permanent Engineering Workflow for Every Phase of Aether AI OS

---

**Date:** 2025-11-15
**Status:** ACCEPTED — ENFORCED
**Classification:** Project Governance — Operational
**Constitutional Tier:** Tier 2 (per ADR-010 Section 16.1)
**Authority:** Principal Systems Engineer / Chief Architect
**Applies To:** Every phase of Aether AI OS, Phase 1 through Phase 10 and beyond, without exception
**Governs:** Claude (Principal Architect), Antigravity IDE (Implementer), Developer (Approver)

---

## THE PHASE EXECUTION MANDATE

**Every phase of Aether AI OS — from Phase 1 through Phase 10 and any phase added
thereafter — follows this exact twenty-seven-step lifecycle without exception.
No phase begins before the prior phase has recorded an explicit GO decision.
No step in this lifecycle is skipped, reordered, or abbreviated. Every phase
ends with STOP, and the next phase does not begin until the developer has
given explicit, affirmative approval.**

This document formalizes a workflow that Phase 1 has already been following
in practice — one milestone prompt at a time, each reviewed, tested, and
approved before the next is generated. What Phase 1 did informally, every
future phase does as a matter of written law. This document is that law.

---

## TABLE OF CONTENTS

**Part One — Foundations**
1. [Purpose and Authority](#1-purpose-and-authority)
2. [Constitutional Integration](#2-constitutional-integration)
3. [The Phase Concept](#3-the-phase-concept)
4. [Roles and Authority](#4-roles-and-authority)

**Part Two — The Twenty-Seven-Step Phase Lifecycle**
5. [Step 1: Phase Entry Criteria](#step-1-phase-entry-criteria)
6. [Step 2: Phase Initialization](#step-2-phase-initialization)
7. [Step 3: Repository Preparation](#step-3-repository-preparation)
8. [Step 4: AI Skill Loading Workflow](#step-4-ai-skill-loading-workflow)
9. [Step 5: Antigravity Prompt Generation Workflow](#step-5-antigravity-prompt-generation-workflow)
10. [Step 6: Antigravity Implementation Workflow](#step-6-antigravity-implementation-workflow)
11. [Step 7: Human Review Workflow](#step-7-human-review-workflow)
12. [Step 8: Claude Review Workflow](#step-8-claude-review-workflow)
13. [Step 9: Architecture Compliance Review](#step-9-architecture-compliance-review)
14. [Step 10: Security Review](#step-10-security-review)
15. [Step 11: Performance Review](#step-11-performance-review)
16. [Step 12: Testing Workflow](#step-12-testing-workflow)
17. [Step 13: Bug Fix Workflow](#step-13-bug-fix-workflow)
18. [Step 14: Regression Testing](#step-14-regression-testing)
19. [Step 15: Documentation Updates](#step-15-documentation-updates)
20. [Step 16: ADR Update Rules](#step-16-adr-update-rules)
21. [Step 17: Git Commit Strategy](#step-17-git-commit-strategy)
22. [Step 18: Git Tag Strategy](#step-18-git-tag-strategy)
23. [Step 19: Release Candidate Workflow](#step-19-release-candidate-workflow)
24. [Step 20: Phase Review](#step-20-phase-review)
25. [Step 21: Lessons Learned](#step-21-lessons-learned)
26. [Step 22: Definition of Done Verification](#step-22-definition-of-done-verification)
27. [Step 23: GO / NO-GO Decision](#step-23-go--no-go-decision)
28. [Step 24: Rollback Procedure](#step-24-rollback-procedure)
29. [Step 25: Phase Closure](#step-25-phase-closure)
30. [Step 26: Phase Archive](#step-26-phase-archive)
31. [Step 27: Next Phase Initialization](#step-27-next-phase-initialization)

**Part Three — Nested Workflow Structure**
32. [The Milestone Cycle Within the Phase Cycle](#5-the-milestone-cycle-within-the-phase-cycle)

**Part Four — Mandatory Artifacts**
33. [The Mandatory Phase Document Set](#6-the-mandatory-phase-document-set)

**Part Five — Enforcement**
34. [The STOP Protocol](#7-the-stop-protocol)
35. [Non-Negotiable Rules](#8-non-negotiable-rules)

---

## PART ONE: FOUNDATIONS

---

## 1. PURPOSE AND AUTHORITY

### 1.1 Why This Document Exists

Phase 1 of Aether AI OS has been executed one milestone at a time: the
Principal Architect generates a single, exhaustively detailed implementation
prompt; the developer carries it into Antigravity IDE; Antigravity implements
exactly what was specified; the developer reviews and tests the result; the
prompt ends with STOP; and only after explicit approval does the next prompt
get generated. Fourteen prompts have followed this pattern — Repository
Bootstrap through Milestone M1.11 — without a single milestone being combined,
skipped, or anticipated ahead of its turn.

This document exists to convert that working practice from an informal habit
into a permanent, written, mandatory law that governs every phase of this
project for as long as it exists. A project expected to run five or more
years cannot rely on a pattern that lives only in the flow of a single
conversation. It must live in a document that outlives any single session,
any single developer mood, and any single moment of urgency.

### 1.2 Authority

This document is issued under the authority of the Principal Systems Engineer
/ Chief Architect role, consistent with the authority under which ADR-010,
ADR-011, AI_GENERATION_RULES_V2.md, and AI_SKILLS_INTEGRATION.md were issued.
It carries the same enforceability as those documents.

### 1.3 Scope

This document applies to every phase defined in the Aether Master Blueprint's
ten-phase roadmap — Phase 1 (Foundation) through Phase 10 (Holographic
Interface) — and to any phase added to that roadmap in the future. It applies
retroactively to the remainder of Phase 1 from the point of this document's
adoption forward. It does not require Phase 1's already-approved milestones
to be redone; it governs everything from here on.

---

## 2. CONSTITUTIONAL INTEGRATION

This document does not stand alone. It is the operational layer that
executes the rules already established by the rest of the Aether Project
Constitution. The table below states exactly how each governing document
feeds into this workflow.

| Constitutional Document | Role in This Workflow |
|---|---|
| **Master Blueprint** | Defines the ten phases this workflow cycles through. Step 1 (Phase Entry Criteria) confirms the next phase matches the Blueprint's sequence. |
| **AI OS Master Blueprint / Critical Architecture Audit** | Inform the risk posture and MVP-first discipline applied during Step 2 (Phase Initialization) and Step 20 (Phase Review). |
| **V1 Foundation Architecture Decision / V1 Technical Specification** | The architectural "what" that every phase's implementation must conform to. Step 9 (Architecture Compliance Review) checks conformance against these documents directly. |
| **ADR-010 (AI Safety and Code Generation)** | Governs backup requirements (Step 3), forbidden operations (Step 6, Step 13), repository protection and branch strategy (Steps 17–18, 25), rollback and recovery (Step 24), and the Constitutional Amendment Process (Step 16). |
| **ADR-011 (Production Engineering Standards)** | Supplies the Quality Gates executed at Steps 9–12 and 20, the Code Review Checklist executed at Step 7, and the Performance Baseline methodology executed at Step 11. |
| **AI_GENERATION_RULES_V2.md** | Governs every Antigravity prompt generated at Step 5 and every review performed at Step 8. The Formal AI Decision Framework in that document is the checklist the Principal Architect runs before finalizing any prompt. |
| **AI_SKILLS_INTEGRATION.md** | Governs Step 4 (AI Skill Loading Workflow) directly — which skills load before which prompts, and how. |
| **Phase Technical Specification / Phase Implementation Plan** | The phase-specific artifacts produced at Step 2 and consumed throughout Steps 5–14. |

This document is a **Tier 2 Constitutional document**, joining ADR-010,
ADR-011, AI_GENERATION_RULES_V2.md, and AI_SKILLS_INTEGRATION.md at that
tier, per the tier definitions established in ADR-010 Section 16.1. No
generated code, and no phase execution, may override, contradict, or
circumvent this document.

---

## 3. THE PHASE CONCEPT

### 3.1 Definition

A **Phase** is one of the ten major capability increments defined in the
Aether Master Blueprint (Phase 1: Foundation, Phase 2: PC Control, Phase 3:
Browser Automation, and so forward through Phase 10: Holographic Interface).
Each phase delivers a coherent, testable increase in what Aether can do.

A **Milestone** is a single unit of implementation work within a phase.
Phase 1 contains thirteen milestones: Repository Bootstrap, M0 (Environment
Validation), and M1.0 through M1.11. Every phase has its own milestone
breakdown, defined in that phase's Implementation Plan (Step 2).

### 3.2 The Two Nested Cycles

This workflow operates at two nested levels simultaneously:

```
PHASE CYCLE (runs once per phase)
  Steps 1–3   — run once, at the start of the phase
  Steps 4–14  — run once PER MILESTONE, repeated for every milestone in the phase
  Steps 15–27 — run once, at the close of the phase
```

Part Three of this document (Section 5) diagrams this nesting in full. The
short version: a phase does not execute Steps 1 through 27 in a single
straight line. It executes Steps 1–3 once, then cycles Steps 4–14 for every
milestone the phase contains — exactly as Phase 1 has done fourteen times
already — and only after every milestone in the phase has passed does the
phase proceed to Steps 15–27 to formally close.

### 3.3 No Phase Skipping, No Milestone Combining

These rules, already given as explicit Implementation Rules for Phase 1, are
hereby made permanent for every phase:

- No phase may begin before the prior phase's Step 23 (GO/NO-GO Decision)
  has recorded GO.
- No milestone within a phase may be combined with another milestone in a
  single implementation prompt.
- No milestone may be skipped.
- No future phase or future milestone may be anticipated or partially
  implemented ahead of its turn.
- No approved architecture may be violated in the name of expedience.

---

## 4. ROLES AND AUTHORITY

### 4.1 Principal Architect (Claude)

Generates phase specifications, implementation plans, and — one at a time —
the detailed implementation prompts consumed by Antigravity IDE. Conducts
the Claude Review Workflow (Step 8) on every milestone's output. Applies
architectural judgment, escalates constitutional conflicts, and drafts new
ADRs when a genuine architectural decision is required (Step 16).

**The Principal Architect never writes application source code directly for
Aether and never unilaterally approves a phase or milestone transition.**

### 4.2 Antigravity IDE (Implementer)

Receives one implementation prompt at a time and generates exactly the files
specified — no more, no less. Is bound in full by AI_GENERATION_RULES_V2.md
and by the Architecture Constraints, Coding Standards, and explicit
prohibitions stated in each prompt. Has no authority to deviate from a
prompt's Scope, and no authority to combine, skip, or anticipate milestones.

### 4.3 Developer (Approver)

The sole and final approval authority for every gate in this workflow: every
milestone's completion, every phase's GO/NO-GO decision, and every Level 4
or Level 5 operation under ADR-010. Performs the Human Review Workflow
(Step 7), runs validation commands locally, and is the only party who may
execute a destructive operation, a Level 5 override, or a rollback.

**No phase, and no milestone within a phase, advances without the
developer's explicit, affirmative approval.**

---

## PART TWO: THE TWENTY-SEVEN-STEP PHASE LIFECYCLE

---

### Step 1: Phase Entry Criteria

**Purpose:** Confirm the project is genuinely ready to begin the next phase.

**Criteria — all must be true:**
- The immediately prior phase recorded an explicit GO decision (Step 23 of
  that phase's cycle). Phase 1's entry criterion was instead: all
  Constitutional governance documents ratified and the repository bootstrap
  complete.
- The Master Blueprint confirms this phase is the next phase in sequence.
  No phase is entered out of order.
- Zero open P1 technical debt items remain from the prior phase (per
  ADR-010 Section 13.3).
- Any hardware, dependency, or external-account prerequisites specific to
  the new phase (for example, a new API key or a new local model) are
  identified and available, or a plan exists to obtain them during Step 2.

**Exit condition:** All criteria confirmed. The developer explicitly
authorizes phase initialization to begin.

---

### Step 2: Phase Initialization

**Purpose:** Establish the phase's own governing documents before any
implementation prompt is written.

**Process:**
1. The Principal Architect re-reads the Master Blueprint's section for this
   phase, every frozen Constitutional document, and the prior phase's
   Lessons Learned document (Step 21 of the prior cycle).
2. Determine whether the phase requires new architectural surface not
   already covered by V1_TECHNICAL_SPECIFICATION.md. If yes: draft
   `PHASE_{N}_TECHNICAL_SPECIFICATION.md`. If the phase fits entirely
   within the existing architecture, this document is skipped and the
   Implementation Plan references V1_TECHNICAL_SPECIFICATION.md directly.
3. Draft `PHASE_{N}_IMPLEMENTATION_PLAN.md` — mandatory for every phase,
   without exception. This document breaks the phase into its exact
   milestone sequence, following the structure established by
   `PHASE_1_FOUNDATION_IMPLEMENTATION_PLAN.md`: for every milestone, an
   overview, prerequisites, duration, exact files to create, an
   implementation sequence, and five checklists (Build, Test, Validation,
   Architecture Compliance, Security), a Definition of Done, and a
   Milestone Gate.
4. Both documents are presented to the developer for review before any
   Antigravity prompt is generated.

**Exit condition:** `PHASE_{N}_IMPLEMENTATION_PLAN.md` is reviewed and
approved by the developer.

---

### Step 3: Repository Preparation

**Purpose:** Prepare the repository's branch and tracking state before
implementation begins.

**Process:**
1. Per ADR-010 Section 7.1, create branch `phase/{N}` from `develop`.
2. Confirm `main` and `develop` both reflect the fully closed state of the
   prior phase (Step 25 of the prior cycle already merged and tagged).
3. Confirm a current, verified backup exists per ADR-010 Section 4 before
   any new-phase work begins.
4. Update `README.md`'s milestone status table with the new phase's
   milestones, all unchecked.
5. Update `docs/architecture/context-log.md` with a phase-start snapshot
   (per ADR-010 Section 18.2 format).

**Exit condition:** `phase/{N}` branch exists, backup is verified current,
tracking documents updated.

---

### Step 4: AI Skill Loading Workflow

**Purpose:** Determine which skill packs govern each upcoming milestone
before its implementation prompt is drafted.

**Process:**
1. For the milestone about to be specified, the Principal Architect
   consults the task-type mapping table in AI_SKILLS_INTEGRATION.md
   Section 7.3 to determine applicable Mandatory, Recommended, and
   Optional skill categories.
2. This determination populates the "Skills to Load" section (item 9 of
   the fifteen-section prompt format) of the milestone's implementation
   prompt, exactly as has been done for every Phase 1 prompt.
3. Mandatory skills for the category always load. Recommended skills load
   when the milestone's domain matches. Optional skills load only when the
   milestone explicitly touches that domain (voice, browser, automation,
   design, and so on).

**Exit condition:** The skill list for the upcoming milestone is finalized
and ready for inclusion in the prompt drafted at Step 5.

---

### Step 5: Antigravity Prompt Generation Workflow

**Purpose:** Produce exactly one implementation prompt for exactly one
milestone.

**Process:**
1. The Principal Architect runs the Formal AI Decision Framework from
   AI_GENERATION_RULES_V2.md Section 19 against the milestone's scope
   before drafting a single word of the prompt: parse the task, classify
   every required action by risk level, check for prohibited operations,
   check for ambiguity, confirm scope, check architecture, check
   prerequisites.
2. Draft the prompt using the fifteen-section format established across
   every Phase 1 prompt: Objective, Scope, Files to Create, Files to
   Modify, Exact Folder Locations, Architecture Constraints, Coding
   Standards, AI Generation Rules to Follow, Skills to Load, Expected
   Deliverables, Validation Requirements, Testing Requirements, Security
   Requirements, Definition of Done, and Explicit Things Antigravity Must
   Not Do.
3. The prompt covers exactly one milestone. It is never combined with
   another milestone and never anticipates a future one.
4. The prompt ends with the STOP Protocol (Section 7 of this document).

**Exit condition:** One complete, self-contained implementation prompt is
delivered to the developer.

---

### Step 6: Antigravity Implementation Workflow

**Purpose:** Turn the prompt into actual files inside the repository.

**Process:**
1. The developer pastes the prompt into Antigravity IDE, which already has
   the repository open at its root.
2. Antigravity is bound in full by AI_GENERATION_RULES_V2.md (loaded via
   the prompt's own embedded rules and skill references) and by
   `ARCHITECTURE_RULES.md`.
3. Antigravity generates exactly the files listed in the prompt's Files to
   Create and Files to Modify sections — nothing outside that list, per
   AI_GENERATION_RULES_V2.md Section 16 (Never Introduce Hidden
   Complexity, Never Assume Requirements).
4. The developer does not permit Antigravity to improvise beyond the
   prompt's stated Scope, even when Antigravity suggests it would be
   convenient to do so.

**Exit condition:** All files specified in the prompt exist in the
repository, matching the prompt's specification.

---

### Step 7: Human Review Workflow

**Purpose:** The developer's own manual review pass — the first line of
defense against AI-generated defects.

**Process:**
1. The developer performs the full forty-item Code Review Checklist from
   ADR-011 Section 5.2 against every changed file.
2. The developer runs the milestone's own Validation Requirements
   checklist, taken directly from the prompt that produced this output.
3. Every changed line is read, not scanned — per ADR-010 Section 3.7 Rule
   AG-1 (Review Before Execute). Rubber-stamping AI-generated code is not
   a review.

**Exit condition:** The developer has read every generated file and
completed the Code Review Checklist without unresolved items.

---

### Step 8: Claude Review Workflow

**Purpose:** A second, independent architectural review pass performed by
the Principal Architect on Antigravity's actual output.

**Process:**
1. The developer delivers Antigravity's output — full files, a diff, or a
   summary — back to the Principal Architect.
2. The Principal Architect checks the output against three things: does it
   match the prompt's Expected Deliverables exactly; does it violate any
   item in the prompt's Explicit Things Antigravity Must Not Do; and does
   it show any sign of scope creep, hidden complexity, or an unrequested
   architectural decision, per AI_GENERATION_RULES_V2.md Section 16.
3. The Principal Architect returns one of three verdicts:
   - **APPROVED** — proceeds to Step 9.
   - **APPROVED WITH NOTES** — proceeds to Step 9, with observations
     logged as technical debt (ADR-010 Section 13) rather than blocking.
   - **CHANGES REQUIRED** — returns to Step 13 (Bug Fix Workflow); does
     not proceed until resolved.

**Exit condition:** A recorded verdict of APPROVED or APPROVED WITH NOTES.

---

### Step 9: Architecture Compliance Review

**Purpose:** Automated verification that no module boundary was crossed.

**Process — run and record the exact output of each command:**
```
uv run lint-imports
uv run mypy aether/ services/ --strict
grep -rn "qdrant_client\|sqlalchemy\|aiosqlite" [outside memory/_stores/]
grep -rn "import anthropic\|import openai\|import litellm" [outside llm/_providers/]
```
This mirrors the Architecture Compliance Checklist embedded in every Phase 1
milestone prompt, and Gate Q-2 of ADR-011 Section 4.

**Exit condition:** Zero violations across all four checks.

---

### Step 10: Security Review

**Purpose:** Verify no forbidden pattern, secret, or unsafe operation
entered the codebase.

**Process:** Execute the full Security Gate checklist from ADR-011 Section
4, Gate Q-5, plus the forbidden-pattern scan defined in ADR-010 Section
8.2. This is already embedded as the Security Requirements section of
every Phase 1 prompt; at this step it is re-verified against the actual
generated output, not just the prompt's instructions.

**Exit condition:** Zero matches on the forbidden pattern scan; all manual
Security Gate items checked.

---

### Step 11: Performance Review

**Purpose:** Confirm the milestone did not silently degrade performance,
and — at the phase level — establish or update the baseline.

**Process:**
- At the milestone level: if the milestone introduces or modifies a
  measured path from ADR-011 Section 10.3, spot-check it informally.
- At the phase level (fully, once per phase, during Step 20): run the
  complete Performance Baseline procedure from ADR-011 Section 10.2,
  producing or updating `docs/performance/phase-{N}-baseline.md`, and
  compare against the prior phase's baseline per the Degradation Policy
  in ADR-011 Section 10.5.

**Exit condition:** No path has degraded beyond the P1 threshold (>100%
regression) defined in ADR-011 Section 10.5.

---

### Step 12: Testing Workflow

**Purpose:** Execute the full, layered test suite for the milestone.

**Process — in this exact order:**
```
uv run pytest tests/unit/ -v --tb=short
uv run pytest tests/contracts/ -v --tb=short
uv run pytest tests/architecture/ -v --tb=short
uv run pytest tests/integration/ -v --tb=short
```
This mirrors Gate Q-3 of ADR-011 Section 4 and the Test Checklist embedded
in every Phase 1 milestone prompt. Any milestone-specific "critical test"
called out in the prompt (for example, the cross-session memory test in
M1.5, or the six-step Voice Milestone sequence in M1.10) is executed and
its result recorded explicitly.

**Exit condition:** All tests pass, including any milestone-specific
critical test.

---

### Step 13: Bug Fix Workflow

**Purpose:** Correct any defect found at Steps 7 through 12 without
treating the correction as a new milestone.

**Process:**
1. Progress on the current milestone stops immediately upon defect
   discovery.
2. The defect is documented: what failed, where, and why.
3. The fix is scoped as a corrective follow-up prompt or a direct
   developer edit — never as a new milestone, and never bundled with the
   next milestone's work.
4. Once fixed, execution returns to Step 7 and re-runs Steps 7 through 12
   in full — not just the step that originally failed.

**Exit condition:** The defect is resolved and Steps 7–12 pass cleanly on
the corrected code.

---

### Step 14: Regression Testing

**Purpose:** Confirm a fix did not break anything that was previously
working.

**Process:**
- After any Step 13 correction: re-run the complete test suite from Step
  12, not merely the test that originally failed.
- At the phase level, before Step 19 (Release Candidate): re-run the
  complete suite across the entire phase's scope, not just the final
  milestone.

**Exit condition:** Full suite passes with zero regressions.

---

### Step 15: Documentation Updates

**Purpose:** Keep every documentation artifact synchronized with what was
actually built.

**Process:**
1. `CHANGELOG.md`: a milestone-level entry at every milestone close, and a
   comprehensive phase-level entry at phase close (Step 20), both
   following the format defined in ADR-010 Section 17.5.
2. `README.md`: milestone checkbox updated at every milestone close.
3. `V1_TECHNICAL_SPECIFICATION.md` (or the phase's own Technical
   Specification): updated wherever the actual implementation differs from
   what was originally specified, per Gate Q-4 of ADR-011 Section 4.
4. Any guide document (`docs/guides/adding-a-tool.md` and similar) updated
   if the milestone introduced or changed a reusable pattern.

**Exit condition:** All affected documentation reflects the current,
actual state of the codebase.

---

### Step 16: ADR Update Rules

**Purpose:** Ensure any genuine architectural decision is captured, and
that no informal edit is made to a frozen Constitutional document.

**Process:**
1. If the milestone or phase reveals an architectural decision not
   already covered by an existing ADR: draft a new ADR (`ADR-012` and
   onward) using the required structure from ADR-010 Section 10.4 —
   Context, Decision, Alternatives Considered, Tradeoff Analysis,
   Consequences, Approval Record.
2. If an existing frozen document (ADR-010 or ADR-011) genuinely requires
   amendment: follow the Constitutional Amendment Process in ADR-010
   Section 16.4 exactly. A frozen document is never informally edited.
3. Convenience or short-term preference is explicitly excluded as grounds
   for amendment, per ADR-010 Section 16.3.

**Exit condition:** Any new architectural decision has a committed ADR;
no frozen document has been informally altered.

---

### Step 17: Git Commit Strategy

**Purpose:** Maintain a clean, meaningful commit history on the phase
branch.

**Process:**
1. Follow the commit message format and permitted commit types from
   ADR-010 Section 7.3: `type(scope): description`, one logical change
   per commit.
2. Commits accumulate on `phase/{N}` during milestone implementation.
3. At milestone completion, a pull request is opened into `develop`; per
   ADR-010 Section 7.2, the solo developer may self-merge once all CI
   checks pass — required checks are `ci / lint`, `ci / architecture-check`,
   `ci / test`.

**Exit condition:** Milestone's changes are merged into `develop` with a
clean, correctly formatted commit history.

---

### Step 18: Git Tag Strategy

**Purpose:** Mark permanent, referenceable points in project history.

**Process:**
- Milestone tags: `v0.x.x-m{N.N}-{label}`, created after each milestone
  gate passes, per ADR-010 Section 7.4 and the Versioning Policy in
  ADR-010 Section 17.
- Phase completion tags: `v0.x.x-phase{N}-complete`, created only after
  the phase's Step 23 GO decision is recorded — never before.
- Tags, once pushed, are permanent. They are never deleted, per ADR-010
  Section 7.4.

**Exit condition:** The appropriate tag exists and is pushed.

---

### Step 19: Release Candidate Workflow

**Purpose:** Formally mark the point at which a phase's implementation is
complete and ready for final review.

**Process:**
1. Triggered once the final milestone of the phase passes its own gate
   (Step 12 through Step 14 clean).
2. The full regression suite (Step 14) is re-run against the entire
   phase's scope, not just the final milestone — for Phase 1, this is
   exactly what Milestone M1.11 performs.
3. The phase enters Release Candidate status: no new milestone work is
   added; only Steps 20–23 remain before the phase can close.

**Exit condition:** Full-phase regression suite passes; phase enters
Release Candidate status.

---

### Step 20: Phase Review

**Purpose:** A comprehensive, phase-wide audit, producing the phase's
formal review record.

**Process:**
Produce `PHASE_{N}_REVIEW_REPORT.md`, covering — at minimum — these eight
dimensions, mirroring the architecture audit structure already established
in Milestone M1.11:

| Dimension | What Is Verified |
|---|---|
| Architecture | Every module's public API matches specification; zero boundary violations across the full phase |
| Security | Full forbidden-pattern scan; Security Gate re-run across the entire phase scope |
| Testing | Full suite (unit, contract, architecture, integration) passes for the entire phase |
| Performance | Baseline measured and compared against the prior phase (Step 11) |
| Documentation | All phase documentation is current and accurate |
| Maintainability | Code complexity standards (ADR-011 Section 8) hold across the phase; no P1 debt open |
| Governance | Every milestone in the phase completed its own five checklists and gate |
| Code Quality | Zero Zero-Tolerance violations (ADR-011 Section 2) anywhere in the phase's code |

**Exit condition:** `PHASE_{N}_REVIEW_REPORT.md` is complete, with an
overall verdict of ARCHITECTURALLY COMPLIANT or a documented list of
deficiencies that must be resolved before Step 23.

---

### Step 21: Lessons Learned

**Purpose:** Capture what the phase taught, independent of what it
delivered.

**Process:**
Produce `PHASE_{N}_LESSONS_LEARNED.md`, covering:
- What went well
- What was difficult, and why
- What would be done differently in the next phase
- Estimation accuracy: planned duration versus actual duration, per
  milestone
- Technical debt incurred during the phase (cross-referenced against
  `DEBT_REGISTER.md`)
- Specific process improvements to carry into the next phase's Step 2

**Exit condition:** `PHASE_{N}_LESSONS_LEARNED.md` is complete and
committed.

---

### Step 22: Definition of Done Verification

**Purpose:** Confirm every deliverable promised for this phase in the
Master Blueprint has actually been implemented, and formally verify that
Level 11 (Release Ready) of AETHER_DEFINITION_OF_DONE.md has been reached.

**Process:**
1. Enumerate every capability the Master Blueprint's phase description
   promised.
2. For each: confirm a specific milestone delivered it, and that
   milestone reached Level 10 (Production Ready) per
   AETHER_DEFINITION_OF_DONE.md.
3. Produce `PHASE_{N}_DEFINITION_OF_DONE_REPORT.md` (Template 5 in
   AETHER_DEFINITION_OF_DONE.md Section 6), recording every milestone's
   Level 10 status, the phase-wide checks, and the Non-Bypassable Rules
   confirmation.
4. This is the phase-level analog of the Definition of Done that already
   exists at the end of every individual milestone prompt.

**Exit condition:** `PHASE_{N}_DEFINITION_OF_DONE_REPORT.md` records an
overall determination of LEVEL 11 ACHIEVED. Step 23 (GO / NO-GO Decision)
does not begin until this report reads ACHIEVED.

---

### Step 23: GO / NO-GO Decision

**Purpose:** The formal, recorded decision to close the phase.

**Process:**
1. Produce `PHASE_{N}_GO_NO_GO_REPORT.md`, following the structure
   already established in `PHASE_1_FOUNDATION_IMPLEMENTATION_PLAN.md`'s
   "Phase 1 GO/NO-GO Decision" section: enumerate every GO criterion
   (milestone completion, defining tests, quality gates, architecture,
   operational readiness, documentation) and every NO-GO trigger.
2. **Sole authority: the developer.** The Principal Architect may
   recommend a verdict; only the developer's explicit confirmation
   constitutes a recorded GO.
3. **NO-GO handling:** per ADR-010's phase-gate rule, a NO-GO means
   development stops on the failing item, the defect is corrected, and
   ALL checklists are re-run from the beginning — partial re-validation
   is not permitted.

**Exit condition:** A recorded, developer-confirmed GO decision.

---

### Step 24: Rollback Procedure

**Purpose:** Define how to recover if a phase is later found to be
fundamentally flawed, even after a GO decision.

**Process:** Ties directly to ADR-010 Section 5 (Rollback Requirements)
and Section 6 (Recovery Requirements).
1. Identify the pre-phase tag (the last tag before `phase/{N}` began).
2. Restore from the most recent verified backup taken before the phase
   began, following the SQLite / Qdrant / Redis rollback procedures in
   ADR-010 Section 5.2.
3. Document the rollback in `docs/architecture/operations-log.md`,
   including what triggered it.
4. This procedure exists but is invoked only if genuinely necessary —
   Steps 7 through 14 exist specifically to prevent ever needing it.

**Exit condition:** Rollback capability confirmed available; invoked only
if actually required.

---

### Step 25: Phase Closure

**Purpose:** Formally merge and finalize the phase in the repository.

**Process:**
1. Merge `phase/{N}` into `develop`, then `develop` into `main`, per the
   branch protection rules in ADR-010 Section 7.2.
2. Create the phase completion tag (Step 18).
3. Update `README.md` to mark the phase complete.
4. Update `CHANGELOG.md` with the final phase-completion entry.

**Exit condition:** `main` reflects the fully completed phase; phase
completion tag is pushed.

---

### Step 26: Phase Archive

**Purpose:** Preserve the phase's working documents as permanent
historical reference without cluttering active project documentation.

**Process:**
1. Move phase-specific working documents into
   `docs/phases/phase-{N}/archive/`, retaining the five canonical
   artifacts at the top level: the Technical Specification (if one was
   produced), the Implementation Plan, the Review Report, the Lessons
   Learned document, and the GO/NO-GO Report.
2. Update `docs/architecture/context-log.md` with a phase-closure
   snapshot, per ADR-010 Section 18.2.

**Exit condition:** Phase documents archived; context log updated.

---

### Step 27: Next Phase Initialization

**Purpose:** Explicitly close the loop.

**Process:** This step does not itself perform work. It states, formally,
that the cycle now returns to Step 1 for Phase {N+1} — and that this does
not happen automatically.

**Exit condition — and the governing rule of this entire document:**

**STOP. Wait for explicit human approval before allowing the next phase to
begin.**

---

## PART THREE: NESTED WORKFLOW STRUCTURE

---

## 5. THE MILESTONE CYCLE WITHIN THE PHASE CYCLE

The twenty-seven steps above are not one straight line executed once per
phase. Steps 4 through 14 form an inner cycle that repeats once for every
milestone the phase contains. This is the exact pattern Phase 1 has
followed across all fourteen of its prompts to date.

```
PHASE {N} BEGINS
│
├─ Step 1  Phase Entry Criteria                    (once)
├─ Step 2  Phase Initialization                    (once)
├─ Step 3  Repository Preparation                  (once)
│
│  ┌─────────────────────────────────────────────────────────┐
│  │  MILESTONE CYCLE — repeats once per milestone            │
│  │  (Bootstrap, M0, M1.0, M1.1 ... for as many as the       │
│  │   phase's Implementation Plan defines)                   │
│  │                                                          │
│  │  Step 4   AI Skill Loading Workflow                     │
│  │  Step 5   Antigravity Prompt Generation Workflow        │
│  │  Step 6   Antigravity Implementation Workflow           │
│  │  Step 7   Human Review Workflow                         │
│  │  Step 8   Claude Review Workflow                        │
│  │  Step 9   Architecture Compliance Review                │
│  │  Step 10  Security Review                               │
│  │  Step 11  Performance Review (spot-check)                │
│  │  Step 12  Testing Workflow                               │
│  │  Step 13  Bug Fix Workflow        ──┐ (loop back to 7    │
│  │  Step 14  Regression Testing      ◄─┘  if defects found) │
│  │                                                          │
│  │  MILESTONE GATE: developer approves → next milestone     │
│  │  begins its own cycle at Step 4. Developer does not      │
│  │  approve → Bug Fix Workflow repeats until it does.       │
│  └─────────────────────────────────────────────────────────┘
│
│  (Milestone cycle repeats until every milestone in the
│   phase's Implementation Plan has passed its own gate)
│
├─ Step 15  Documentation Updates                  (once, at phase close)
├─ Step 16  ADR Update Rules                       (once, at phase close)
├─ Step 17  Git Commit Strategy                    (continuous + closing)
├─ Step 18  Git Tag Strategy                       (once, phase tag)
├─ Step 19  Release Candidate Workflow             (once)
├─ Step 20  Phase Review                           (once)
├─ Step 21  Lessons Learned                        (once)
├─ Step 22  Definition of Done Verification        (once)
├─ Step 23  GO / NO-GO Decision                    (once)
├─ Step 24  Rollback Procedure                     (available, invoked only if needed)
├─ Step 25  Phase Closure                          (once)
├─ Step 26  Phase Archive                          (once)
└─ Step 27  Next Phase Initialization → STOP
```

Every one of the fourteen Phase 1 prompts generated so far — Repository
Bootstrap through M1.11 — is a completed pass through the inner milestone
cycle (Steps 4–14). What remains for Phase 1 is the outer close: Steps 15
through 27, beginning the moment M1.11's own milestone cycle reaches its
gate and the developer confirms it.

---

## PART FOUR: MANDATORY ARTIFACTS

---

## 6. THE MANDATORY PHASE DOCUMENT SET

Every phase produces the following documents. None are optional except
where explicitly marked conditional. No phase may reach Step 23 (GO/NO-GO)
without all mandatory documents in this set existing and being current.

| Document | Mandatory? | Produced At | Template |
|---|---|---|---|
| `PHASE_{N}_TECHNICAL_SPECIFICATION.md` | Conditional — only if the phase introduces architecture beyond V1_TECHNICAL_SPECIFICATION.md | Step 2 | (Phase 1 used V1_TECHNICAL_SPECIFICATION.md directly) |
| `PHASE_{N}_IMPLEMENTATION_PLAN.md` | Mandatory | Step 2 | `PHASE_1_FOUNDATION_IMPLEMENTATION_PLAN.md` |
| `PHASE_{N}_REVIEW_REPORT.md` | Mandatory | Step 20 | AETHER_DEFINITION_OF_DONE.md Template 1 |
| `PHASE_{N}_TECHNICAL_DEBT_REPORT.md` | Mandatory | Step 20 | AETHER_DEFINITION_OF_DONE.md Template 2 |
| `PHASE_{N}_RISK_REVIEW_REPORT.md` | Mandatory | Step 20 | AETHER_DEFINITION_OF_DONE.md Template 3 |
| `PHASE_{N}_LESSONS_LEARNED.md` | Mandatory | Step 21 | AETHER_DEFINITION_OF_DONE.md Template 4 |
| `PHASE_{N}_DEFINITION_OF_DONE_REPORT.md` | Mandatory | Step 22 | AETHER_DEFINITION_OF_DONE.md Template 5 |
| `PHASE_{N}_GO_NO_GO_REPORT.md` | Mandatory | Step 23 | AETHER_DEFINITION_OF_DONE.md Template 6 |
| `PHASE_{N}_COMPLETE_REPORT.md` | Mandatory | Step 25 | AETHER_DEFINITION_OF_DONE.md Template 7 |

**Directory structure:**
```
docs/phases/phase-{N}/
  PHASE_{N}_TECHNICAL_SPECIFICATION.md    (if applicable)
  PHASE_{N}_IMPLEMENTATION_PLAN.md
  PHASE_{N}_REVIEW_REPORT.md
  PHASE_{N}_TECHNICAL_DEBT_REPORT.md
  PHASE_{N}_RISK_REVIEW_REPORT.md
  PHASE_{N}_LESSONS_LEARNED.md
  PHASE_{N}_DEFINITION_OF_DONE_REPORT.md
  PHASE_{N}_GO_NO_GO_REPORT.md
  PHASE_{N}_COMPLETE_REPORT.md
  archive/
    (working documents moved here at Step 26)
```

### 6.1 Historical Exception: Phase 1 Closure

Phase 1 is exempted from producing the seven phase-closure documents above
as formal, standalone artifacts. This exemption was explicitly authorized
by the developer, recorded at the same time as this document's amendment
that introduced Template 5 (`PHASE_{N}_DEFINITION_OF_DONE_REPORT.md`), on
the basis of the developer's direct statement: **"Phase 1 has been
successfully completed."** That statement is treated as satisfying
Non-Bypassable Rule NB-6 of AETHER_DEFINITION_OF_DONE.md (a GO decision
requires the developer's own explicit confirmation) for Phase 1
specifically, in lieu of the full `PHASE_1_GO_NO_GO_REPORT.md`.

This exception is granted for Phase 1 only, because Phase 1's actual
engineering quality was already governed in full by every substantive gate
in this workflow — Architecture Compliance (Step 9), Security Review (Step
10), and Testing (Step 12) were applied at every one of its fourteen
milestones. What Phase 1 lacks is the retrospective paperwork, not the
underlying rigor.

**This exception does not extend to any future phase.** From Phase 2
onward, every document in the table above is mandatory without exception,
per the Non-Negotiable Rules in Section 8.

---

## PART FIVE: ENFORCEMENT

---

## 7. THE STOP PROTOCOL

The word STOP, followed by an explicit statement that the next unit of work
awaits human approval, is required at two levels:

**At the end of every milestone**, exactly as every Phase 1 implementation
prompt has already done:
> STOP. Wait for developer approval before proceeding to the next milestone.

**At the end of every phase**, per Step 27 of this document:
> STOP. Wait for explicit human approval before allowing the next phase to
> begin.

The Principal Architect never generates the next milestone's prompt, and
never initializes the next phase, without this explicit approval having
been given. Silence is not approval. Enthusiasm expressed about a future
phase is not approval. Only an explicit, affirmative confirmation from the
developer constitutes approval.

---

## 8. NON-NEGOTIABLE RULES

These rules, several already given as explicit Implementation Rules for
Phase 1, are made permanent here for every phase without exception:

1. No phase may begin before the prior phase records GO at Step 23.
2. No milestone may be combined with another milestone in a single
   implementation prompt.
3. No milestone may be skipped.
4. No future phase or future milestone may be anticipated or partially
   implemented ahead of its turn.
5. No approved architecture may be violated in the name of expedience.
6. No frozen Constitutional document is informally edited; amendment
   follows ADR-010 Section 16.4 exactly.
7. No destructive or Level 5 operation (ADR-010 Section 3) occurs without
   the developer personally executing it after the full override process.
8. Every milestone ends with STOP; every phase ends with STOP. Neither
   cycle self-continues.

---

*Document Version: 1.1*
*Status: ACCEPTED — ENFORCED*
*Constitutional Tier: Tier 2*
*Applies From: Immediately, governing the remainder of Phase 1 (from
Milestone M1.11's Claude Review Workflow onward) and every phase thereafter*
*Amendment History: v1.1 — Step 22 now names PHASE_{N}_DEFINITION_OF_DONE_
REPORT.md as its produced artifact; Section 6's document table completed to
list all seven templates from AETHER_DEFINITION_OF_DONE.md (previously
listed four); added Section 6.1 recording the Phase 1 Closure Exception*
*Review Trigger: Any phase-transition incident, or at the completion of
each phase*
*Owner: Principal Systems Engineer*
*Last Updated: 2025-11-15*
