# AI SKILLS INTEGRATION — AETHER AI OS
### docs/architecture/AI_SKILLS_INTEGRATION.md
### Formal Skill-Loading Architecture and Evaluation Framework

---

**Date:** 2025-11-15  
**Status:** ACCEPTED — ENFORCED  
**Classification:** Project Governance — Operational  
**Authority:** Principal Systems Engineer  
**Applies To:** Claude, Gemini, Antigravity IDE, and all future AI coding assistants  
**Governs:** All skill loading, evaluation, classification, and compliance verification

---

## THE SKILL LOADING MANDATE

**Every AI system operating within Aether AI OS must load and comply with all applicable
skill packs before generating architecture, code, tests, documentation, or UI components.
Skill loading is not optional. Skill compliance is not optional. Skill quality standards
are not negotiable.**

This mandate applies without exception. A session that begins without loading applicable
skills is a non-compliant session. Output from a non-compliant session is treated as
ungoverned output and subject to the full review standards defined in ADR-011.

---

## TABLE OF CONTENTS

**Part One — Foundations**
1. [Purpose and Authority](#1-purpose-and-authority)
2. [What a Skill Is](#2-what-a-skill-is)
3. [What a Skill Is Not](#3-what-a-skill-is-not)
4. [Skill Quality Philosophy](#4-skill-quality-philosophy)

**Part Two — Skill Architecture**
5. [Skill File Format Standard](#5-skill-file-format-standard)
6. [Skill Directory Architecture](#6-skill-directory-architecture)
7. [Skill Loading Protocol](#7-skill-loading-protocol)
8. [Skill Dependency and Conflict Resolution](#8-skill-dependency-and-conflict-resolution)

**Part Three — Skill Categories**
9. [Category Registry and Extension Points](#9-category-registry-and-extension-points)

**Part Four — Evaluation Framework**
10. [The Aether Skill Evaluation Framework](#10-the-aether-skill-evaluation-framework)
11. [Scoring Dimensions and Rubrics](#11-scoring-dimensions-and-rubrics)
12. [Disqualifying Conditions](#12-disqualifying-conditions)
13. [Evaluation Process](#13-evaluation-process)

**Part Five — Classification System**
14. [Classification Definitions](#14-classification-definitions)
15. [Mandatory Skills Registry (Placeholder)](#15-mandatory-skills-registry)
16. [Recommended Skills Registry (Placeholder)](#16-recommended-skills-registry)
17. [Optional Skills Registry (Placeholder)](#17-optional-skills-registry)
18. [Rejected Patterns Registry](#18-rejected-patterns-registry)

**Part Six — Reference Repository Analysis**
19. [Source Repository Evaluation](#19-source-repository-evaluation)

**Part Seven — Governance**
20. [Skill Registration Process](#20-skill-registration-process)
21. [Skill Lifecycle Management](#21-skill-lifecycle-management)
22. [Compliance Verification](#22-compliance-verification)

---

## PART ONE: FOUNDATIONS

---

## 1. PURPOSE AND AUTHORITY

### 1.1 Why Skill Architecture Exists

AI coding assistants have no inherent domain expertise. They have training data. Training data is a mixture of every quality level ever published on the internet — brilliant architecture papers, entry-level tutorials, deprecated patterns, outright wrong implementations, and security vulnerabilities presented as solutions.

When an AI generates code without domain-specific guidance, it synthesizes from this mixture. The result is probabilistically average code. For a five-year AI Operating System project built to production standards, probabilistically average code is unacceptable.

Skills solve this by pre-loading the domain knowledge, standards, and constraints that a principal engineer or staff architect would bring to a session. They shift the AI's generation baseline from "average of the internet" to "principal-engineer-level standards for this specific domain."

### 1.2 Target Expertise Level

Skills loaded into Aether sessions encode the knowledge and standards expected of:

- **Senior Software Engineers** — production-tested implementation patterns
- **Staff Engineers** — cross-system design and long-term maintainability standards
- **Principal Engineers** — architectural integrity, system-level tradeoffs
- **Systems Architects** — service boundaries, communication patterns, data modeling
- **AI Researchers** — agent design, memory systems, reasoning patterns
- **Browser Engineers** — Playwright automation, CDP protocols, isolation boundaries
- **Security Engineers** — threat modeling, input validation, secure defaults
- **Infrastructure Engineers** — containerization, process management, operational reliability
- **Product Engineers** — user-facing quality, accessibility, experience coherence

Skills written at tutorial or hobby-project level are rejected. Skills that encode rapid-prototyping shortcuts are rejected. Skills that introduce architecture violations are rejected. The quality bar is the standards held by engineers who have shipped systems that run at scale, not systems that run in demos.

### 1.3 This Document's Authority

This document is part of the Aether Project Constitution (defined in ADR-010 Section 16). It governs:
- The format every skill must follow
- The directory structure that organizes skills
- The protocol for loading skills into AI sessions
- The 8-dimension evaluation framework every candidate skill must pass
- The classification system that determines a skill's loading behavior
- The analysis and classification of skills from reference repositories
- The governance process for adding, updating, and retiring skills

---

## 2. WHAT A SKILL IS

### 2.1 Formal Definition

A **skill** is a structured, versioned instruction package that provides an AI system with domain-specific expertise, production standards, constraint sets, and workflow patterns for a defined area of engineering work.

A skill has three layers:

**Layer 1 — Identity (always loaded, ~50 tokens)**  
The skill's name and description, used by the AI to determine relevance to the current task. This layer loads at session start for all registered skills.

**Layer 2 — Core Instructions (loaded when relevant, 500–5,000 tokens)**  
The `SKILL.md` body: patterns, standards, constraints, anti-patterns, examples, and decision guidance for the domain.

**Layer 3 — Reference Materials (loaded on demand, variable)**  
Supporting files in `references/` and `scripts/` that provide depth when a task requires it.

### 2.2 The SKILL.md Standard

The SKILL.md format is an open standard introduced by Anthropic in October 2025 and released publicly in December 2025. It is now supported by Claude Code, Antigravity, Gemini CLI, Cursor, Codex, and Windsurf. Aether uses this standard natively, with extensions defined in Section 5.

### 2.3 What a Skill Provides

A well-constructed skill provides:

- **Domain constraints** — what is forbidden in this domain and why
- **Production patterns** — how senior engineers solve the core problems of this domain
- **Decision frameworks** — how to choose between competing approaches
- **Anti-patterns** — what to avoid and the specific failure modes each anti-pattern causes
- **Quality gates** — what constitutes done in this domain
- **Interaction rules** — how this skill's domain interacts with adjacent domains

---

## 3. WHAT A SKILL IS NOT

Skills are not:

**Not tutorials.** A skill is not a learning resource for engineers who are unfamiliar with the domain. It is a constraint and standards document for engineers (and AI) who are operating in the domain.

**Not examples.** A skill does not primarily consist of code examples. Examples may support the constraints but are never the substance of the skill.

**Not opinionated preferences.** A skill is not a record of one engineer's stylistic preferences. Every rule in a skill must have a production-validated reason.

**Not tool advertisements.** A skill does not promote a specific library, framework, or service above alternatives without evaluated justification. Tool recommendations in skills are based on production evidence, not hype.

**Not prototyping shortcuts.** A skill that teaches how to do something quickly at the expense of correctness, maintainability, or security is categorically rejected.

**Not MCP servers.** MCP servers provide tool access. Skills define how those tools are used. They operate at different layers and are not substitutes for each other.

---

## 4. SKILL QUALITY PHILOSOPHY

### 4.1 The Production Standard

Every skill approved for Aether must encode practices that a principal engineer would defend in a production system review. The test for any guidance in a skill is:

*"Would a staff or principal engineer at a company with 99.9% uptime requirements approve code generated following this guidance?"*

If the answer is no, the guidance does not belong in an approved skill.

### 4.2 What "Industry-Grade" Means in This Context

Industry-grade means the patterns encoded in the skill are:

- **Battle-tested** — used in systems that have run in production under real load, not just demonstrated in talks or tutorials
- **Failure-aware** — the skill addresses what happens when things go wrong, not just the happy path
- **Maintainability-proven** — teams have been able to maintain systems built with these patterns over months and years, not just shipped them
- **Security-validated** — the patterns have been evaluated from a security perspective by engineers with security expertise
- **Scalability-considered** — the patterns do not create hard ceilings that would require a rewrite to scale

### 4.3 The Rejection Threshold

The following patterns in any skill are grounds for immediate rejection of that skill, regardless of its other quality:

- Advice to use `except: pass` or equivalent
- Advice to hardcode configuration values
- Advice to skip type annotations for "speed"
- Advice to write tests "later"
- Advice that security validation can be "simplified" in early phases
- Advice using the words "vibe," "just," "quick," or "hack" as implementation strategies
- Advice that architecture rules are optional when under time pressure

---

## PART TWO: SKILL ARCHITECTURE

---

## 5. SKILL FILE FORMAT STANDARD

### 5.1 SKILL.md Structure

Every Aether skill follows this exact structure:

```
skills/{classification}/{category}/{skill-name}/
  SKILL.md              # Required — core skill definition
  references/           # Optional — supporting reference documents
    *.md
  scripts/              # Optional — supporting scripts or templates
    *.py / *.ps1 / *.sh
  EVALUATION.md         # Required — completed evaluation scorecard
  CHANGELOG.md          # Required — version history
```

### 5.2 SKILL.md YAML Frontmatter (Required Fields)

```yaml
---
name: {unique-skill-identifier}
version: {semver: MAJOR.MINOR.PATCH}
description: >
  One to three sentences. Loaded at session start for every session.
  Must clearly describe what domain this skill governs and the target
  expertise level. This text determines whether the skill loads.
category: {category-identifier from Section 9}
classification: mandatory | recommended | optional
aether_score: {numeric score from evaluation framework, e.g., 87}
evaluated_date: {YYYY-MM-DD}
evaluated_by: {role, e.g., "Principal Systems Engineer"}
load_conditions:
  - {keyword or condition that triggers loading this skill}
  - {additional conditions}
incompatible_with:
  - {skill-name of any skills that conflict with this one}
depends_on:
  - {skill-name of skills that must load before this one}
source:
  origin: {aether-internal | external-evaluated}
  external_url: {if external — original source URL}
  external_version: {if external — version of the source evaluated}
applies_to:
  - claude
  - gemini
  - antigravity
  - codex
  - {other compatible AI systems}
target_expertise:
  minimum: {senior | staff | principal}
  optimal: {staff | principal | architect}
rejects_patterns:
  - {pattern name that this skill explicitly prohibits}
---
```

### 5.3 SKILL.md Body Sections (Required Structure)

Every SKILL.md body must contain these sections in this order:

```markdown
## DOMAIN AUTHORITY

[One paragraph establishing what this skill governs, what its boundaries are, and
what adjacent domains it interacts with but does not govern.]

## CORE CONSTRAINTS

[A numbered list of constraints. Each constraint is a rule with a specific reason.
No constraint appears without a stated consequence of violating it.]

## PRODUCTION PATTERNS

[The patterns that principal engineers use in this domain. Each pattern is named,
described, and explained with its production rationale.]

## ANTI-PATTERNS

[Named anti-patterns with the specific failure modes each one causes. Anti-patterns
are named patterns, not vague warnings.]

## QUALITY GATES

[The specific criteria that determine when work in this domain is complete.
Measurable. Checkable. Not subjective.]

## DECISION FRAMEWORK

[When the skill requires choosing between approaches, a framework for making
the correct choice. Not "it depends" — a structured decision process.]

## INTERACTION WITH OTHER SKILLS

[How this skill's domain interacts with adjacent domains and which skills govern
those adjacent domains.]
```

### 5.4 EVALUATION.md Structure

Every approved skill must have a completed EVALUATION.md:

```markdown
# Skill Evaluation: {skill-name}

**Evaluation Date:** YYYY-MM-DD  
**Evaluated By:** {role}  
**Final Score:** {n}/100  
**Classification:** Mandatory | Recommended | Optional | Rejected  

## Dimension Scores

| Dimension | Raw Score (1-10) | Weight | Weighted Score |
|---|---|---|---|
| Production Readiness | n | 1.5x | n |
| Maintainability | n | 1.0x | n |
| Security | n | 2.0x | n |
| Scalability | n | 1.0x | n |
| Performance | n | 1.0x | n |
| Documentation Quality | n | 1.0x | n |
| Industry Adoption | n | 1.0x | n |
| Long-Term Viability | n | 1.5x | n |
| **TOTAL** | | | **n/100** |

## Dimension Justifications

[For each dimension: specific evidence for the score.]

## Disqualifying Conditions Checked

[ ] No reject-on-sight anti-patterns present
[ ] Security score >= 12/20
[ ] Production Readiness score >= 11/15
[ ] No "vibe coding" or prototyping language
[ ] No architecture bypass patterns

## Classification Justification

[Why this score maps to this classification.]

## Conditions and Restrictions (if Conditional)

[Any usage restrictions that apply.]
```

---

## 6. SKILL DIRECTORY ARCHITECTURE

### 6.1 Complete Directory Structure

```
skills/
│
├── REGISTRY.md                     # Master registry: all approved skills with scores
├── EVALUATION_TEMPLATE.md          # Template for new skill evaluations
├── SKILL_TEMPLATE.md               # Template for new SKILL.md files
│
├── mandatory/                      # Always loaded when task matches load_conditions
│   ├── core/
│   │   ├── architecture/           # EXTENSION POINT — see Section 9.1
│   │   ├── security/               # EXTENSION POINT — see Section 9.2
│   │   ├── python/                 # EXTENSION POINT — see Section 9.16
│   │   ├── testing/                # EXTENSION POINT — see Section 9.19
│   │   └── documentation/          # EXTENSION POINT — see Section 9.22
│   └── ai-systems/
│       ├── agent-engineering/      # EXTENSION POINT — see Section 9.4
│       └── memory-systems/         # EXTENSION POINT — see Section 9.5
│
├── recommended/                    # Loaded when task type matches load_conditions
│   ├── architecture/
│   │   ├── system-design/          # EXTENSION POINT — see Section 9.3
│   │   ├── event-driven/           # EXTENSION POINT — see Section 9.8
│   │   └── distributed-systems/    # EXTENSION POINT — see Section 9.7
│   ├── ai/
│   │   ├── rag/                    # EXTENSION POINT — see Section 9.6
│   │   └── ai-engineering/         # EXTENSION POINT — see Section 9.3 (AI)
│   ├── backend/
│   │   └── backend-engineering/    # EXTENSION POINT — see Section 9.9
│   ├── frontend/
│   │   ├── react/                  # EXTENSION POINT — see Section 9.11
│   │   └── typescript/             # EXTENSION POINT — see Section 9.12
│   ├── security/
│   │   └── security-engineering/   # EXTENSION POINT — see Section 9.13
│   ├── performance/
│   │   └── performance-engineering/# EXTENSION POINT — see Section 9.18
│   └── observability/
│       └── observability/          # EXTENSION POINT — see Section 9.21
│
├── optional/                       # Loaded on demand or by explicit request
│   ├── voice/
│   │   └── voice-systems/          # EXTENSION POINT — see Section 9.17
│   ├── browser/
│   │   └── browser-engineering/    # EXTENSION POINT — see Section 9.14
│   ├── automation/
│   │   └── automation-engineering/ # EXTENSION POINT — see Section 9.15
│   ├── devops/
│   │   └── devops/                 # EXTENSION POINT — see Section 9.20
│   ├── design/
│   │   ├── ui-ux/                  # EXTENSION POINT — see Section 9.23
│   │   └── accessibility/          # EXTENSION POINT — see Section 9.24
│   └── product/
│       └── product-engineering/    # EXTENSION POINT — see Section 9.25
│
└── rejected/
    ├── REJECTED_REGISTRY.md        # All rejected skills with rejection reasons
    └── patterns/                   # Documented anti-patterns to recognize
        ├── vibe-coding-patterns.md
        ├── prototyping-shortcuts.md
        ├── security-bypasses.md
        └── architecture-violations.md
```

### 6.2 The Registry Files

**`skills/REGISTRY.md`** — Master registry. Every approved skill has one entry:

```markdown
| Skill Name | Category | Classification | Score | Version | Last Reviewed |
|---|---|---|---|---|---|
| aether-python-production | python | mandatory | —/— | — | PLACEHOLDER |
```

**`skills/rejected/REJECTED_REGISTRY.md`** — Every evaluated-and-rejected skill:

```markdown
| Source | Pattern/Skill | Rejection Score | Primary Rejection Reason | Date |
|---|---|---|---|---|
| PatrickJS/awesome-cursorrules | vibe-coding patterns | — | Vibe coding conflicts with production standards | PLACEHOLDER |
```

---

## 7. SKILL LOADING PROTOCOL

### 7.1 Session Initialization

When an AI session begins for Aether development, the following loading sequence executes before any code generation, documentation, or architectural work:

```
SKILL LOADING SEQUENCE:

STEP 1: TASK CLASSIFICATION
  Identify: What category of work does this session involve?
  Result: List of applicable skill categories

STEP 2: MANDATORY SKILL LOADING
  Load ALL mandatory skills whose load_conditions match the task categories.
  These load in full. There are no exceptions.
  Mandatory skills are always loaded before recommended or optional skills.

STEP 3: RECOMMENDED SKILL LOADING
  Evaluate each recommended skill's load_conditions against the task.
  Load all recommended skills where conditions match.

STEP 4: OPTIONAL SKILL LOADING
  Load optional skills only when:
    a. Explicitly requested by the developer, OR
    b. The task is clearly within the optional skill's domain

STEP 5: DEPENDENCY RESOLUTION
  For each loaded skill, check depends_on.
  Load any unloaded dependencies.
  Repeat until no unresolved dependencies remain.

STEP 6: CONFLICT DETECTION
  For each loaded skill, check incompatible_with.
  If conflicts exist: report to developer, request resolution.
  Do not proceed with conflicting skills both loaded.

STEP 7: COMPLIANCE DECLARATION
  State: "Skills loaded: [list of loaded skills]. Generating output in
  compliance with all loaded skill constraints."

STEP 8: GENERATE
  All output must comply with constraints from all loaded skills.
  Where skills conflict on a specific constraint, the Mandatory skill wins,
  then Recommended, then Optional. Report the conflict.
```

### 7.2 Loading Declaration Format

Every session that generates code, documentation, or architecture must begin with a loading declaration:

```
SKILLS LOADED FOR THIS SESSION:

Mandatory:
  [skill-name v.X.X] — [brief description]

Recommended:
  [skill-name v.X.X] — [brief description]

Optional:
  [none | list]

Skills not applicable to this task:
  [skills that were evaluated and not loaded]

Generating output in compliance with all loaded skill constraints.
```

### 7.3 Skill Loading for Specific Task Types

| Task Type | Mandatory Loads | Recommended Loads |
|---|---|---|
| Architecture design | architecture, security | system-design, distributed-systems |
| Python module implementation | python, security, testing | backend-engineering, performance |
| Agent implementation | agent-engineering, python, security | memory-systems, testing |
| Memory system work | memory-systems, python, security | rag, performance |
| Frontend component | typescript, react, security | ui-ux, accessibility, testing |
| Database migration | python, security | backend-engineering |
| Voice pipeline | voice-systems, python, security | performance |
| Infrastructure | security, devops | observability, performance |
| Documentation | documentation | — |
| Test suite | testing, python | performance |
| Security review | security, security-engineering | — |

---

## 8. SKILL DEPENDENCY AND CONFLICT RESOLUTION

### 8.1 Dependency Rules

- A skill may declare dependencies on other skills via `depends_on`
- Dependent skills are always loaded before the declaring skill
- Circular dependencies are a registration error and must be resolved before the skill is approved
- A skill may not depend on an Optional skill (would force Optional loading)
- Recommended skills may depend on Mandatory skills only
- Optional skills may depend on Mandatory or Recommended skills

### 8.2 Conflict Resolution

When two loaded skills specify conflicting guidance on the same topic:

1. **Mandatory wins over Recommended wins over Optional** — the higher classification takes precedence
2. **More specific wins over more general** — a Python-specific constraint overrides a general programming constraint on Python topics
3. **Security wins over all** — a security constraint from any classification overrides non-security guidance from any other classification
4. **When conflict remains unresolved** — the AI reports the conflict and asks the developer to resolve it before generating output

### 8.3 Aether Project Constitution Supremacy

All skills are subordinate to the Aether Project Constitution (ADR-010 Section 16). No skill, regardless of source or score, may override or contradict:
- ADR-010 (AI Safety and Code Generation)
- ADR-011 (Production Engineering Standards)
- AI_GENERATION_RULES_V2.md
- V1 Foundation Architecture Decision
- V1 Technical Specification

Where a skill conflicts with a Constitutional document, the Constitutional document governs and the skill constraint is treated as void for that specific conflict.

---

## PART THREE: SKILL CATEGORIES

---

## 9. CATEGORY REGISTRY AND EXTENSION POINTS

Each category is defined here as a formal extension point. Skills are registered in each category as they are evaluated and approved. Current state: all categories are PLACEHOLDER — awaiting skill population following the evaluation process in Part Four.

The placeholder structure for each category shows exactly where approved skills will be placed and what the loading trigger is.

---

### 9.1 Architecture Skills

**Category ID:** `architecture`  
**Target Expertise:** Staff Engineer / Principal Engineer / Systems Architect  
**Classification Target:** Mandatory  
**Load Conditions:** architecture design, system design, module design, service boundary, ADR creation, pattern selection  

**What this category governs:**
- Modular monolith patterns and enforcement
- Service boundary decision frameworks
- API contract design
- Event-driven architecture patterns
- Long-term architectural evolution
- Architectural decision recording

**Placeholder registry:**
```
skills/mandatory/core/architecture/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md  # describes what skills belong here
```

**Anti-patterns this category must reject:**
- Premature microservice extraction
- God modules (no boundary enforcement)
- Shared mutable state across module boundaries
- Implicit coupling via direct database access

---

### 9.2 Security Engineering Skills

**Category ID:** `security`  
**Target Expertise:** Security Engineer / Senior Engineer  
**Classification Target:** Mandatory  
**Load Conditions:** ALL sessions — security loads in every Aether development session without exception  

**What this category governs:**
- Input validation patterns
- Secrets management
- Permission validation frameworks
- SQL injection prevention
- Prompt injection defense
- Authentication patterns
- Secure defaults
- Threat modeling for AI systems

**Placeholder registry:**
```
skills/mandatory/core/security/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

**Non-negotiable constraints for skills in this category:**
- No skill in this category may permit stub security validation
- No skill in this category may suggest deferring security implementation
- No skill in this category may introduce patterns that bypass the SafetyValidator

---

### 9.3 AI Engineering Skills

**Category ID:** `ai-engineering`  
**Target Expertise:** AI Researcher / Staff Engineer  
**Classification Target:** Recommended  
**Load Conditions:** LLM integration, model routing, AI system design, foundation model interaction  

**What this category governs:**
- Model-agnostic architecture patterns
- LLM prompt construction standards
- Structured output validation
- Token budget management
- LLM cost optimization
- AI system reliability patterns

**Placeholder registry:**
```
skills/recommended/ai/ai-engineering/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.4 Agent Engineering Skills

**Category ID:** `agent-engineering`  
**Target Expertise:** AI Researcher / Staff Engineer  
**Classification Target:** Mandatory  
**Load Conditions:** agent implementation, agent runtime, agent orchestration, tool use, agent lifecycle  

**What this category governs:**
- ReAct pattern implementation
- LangGraph state graph design
- Tool use architecture
- Agent iteration limits and circuit breakers
- Human-in-the-loop patterns
- Agent failure recovery
- Multi-agent coordination
- Agent observability

**Placeholder registry:**
```
skills/mandatory/ai-systems/agent-engineering/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.5 Memory System Skills

**Category ID:** `memory-systems`  
**Target Expertise:** AI Researcher / Staff Engineer  
**Classification Target:** Mandatory  
**Load Conditions:** memory implementation, memory retrieval, memory consolidation, vector store operations  

**What this category governs:**
- Multi-tier memory architecture
- Hybrid retrieval implementation (vector + keyword)
- Embedding generation and management
- Memory consolidation pipelines
- Memory quality and decay
- Context window budget management
- Memory privacy and security

**Placeholder registry:**
```
skills/mandatory/ai-systems/memory-systems/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.6 RAG Skills

**Category ID:** `rag`  
**Target Expertise:** AI Researcher / Senior Engineer  
**Classification Target:** Recommended  
**Load Conditions:** document ingestion, knowledge retrieval, semantic search, embedding pipeline  

**What this category governs:**
- Document chunking strategies
- Embedding model selection and evaluation
- Vector similarity search optimization
- Hybrid search implementation
- Reranking algorithms
- Context assembly for LLM consumption
- RAG evaluation metrics

**Placeholder registry:**
```
skills/recommended/ai/rag/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.7 Distributed Systems Skills

**Category ID:** `distributed-systems`  
**Target Expertise:** Staff Engineer / Principal Engineer  
**Classification Target:** Recommended  
**Load Conditions:** distributed state, consensus, eventual consistency, service communication, fault tolerance  

**What this category governs:**
- Consistency models and their trade-offs
- Distributed state management
- Failure detection and recovery
- Idempotency patterns
- Distributed tracing
- Service mesh patterns
- Backpressure and circuit breakers

**Placeholder registry:**
```
skills/recommended/architecture/distributed-systems/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.8 Event-Driven Architecture Skills

**Category ID:** `event-driven`  
**Target Expertise:** Staff Engineer / Systems Architect  
**Classification Target:** Recommended  
**Load Conditions:** event bus, Redis Streams, event schema, event sourcing, pub/sub, consumer groups  

**What this category governs:**
- Event schema design and versioning
- Producer/consumer patterns
- Consumer group management
- Event replay and backfill
- Dead-letter queue patterns
- Event store design
- Ordering and idempotency guarantees

**Placeholder registry:**
```
skills/recommended/architecture/event-driven/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.9 Backend Engineering Skills

**Category ID:** `backend-engineering`  
**Target Expertise:** Senior Engineer / Staff Engineer  
**Classification Target:** Recommended  
**Load Conditions:** FastAPI, REST API, database integration, service implementation  

**What this category governs:**
- FastAPI production patterns
- Database transaction management
- Connection pooling
- API versioning
- Rate limiting
- Graceful degradation
- Service health and readiness

**Placeholder registry:**
```
skills/recommended/backend/backend-engineering/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.10 System Design Skills

**Category ID:** `system-design`  
**Target Expertise:** Staff Engineer / Principal Engineer / Systems Architect  
**Classification Target:** Recommended  
**Load Conditions:** system design, capacity planning, scalability analysis, architectural tradeoffs  

**What this category governs:**
- Capacity estimation patterns
- Bottleneck identification
- Horizontal vs vertical scaling decisions
- Data modeling for scale
- Caching strategy design
- Load distribution patterns

**Placeholder registry:**
```
skills/recommended/architecture/system-design/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.11 React Skills

**Category ID:** `react`  
**Target Expertise:** Senior Engineer / Staff Engineer  
**Classification Target:** Recommended  
**Load Conditions:** React, JSX, component, hook, state management, frontend  

**What this category governs:**
- React 19+ production patterns
- Component composition patterns
- State management with Zustand
- React Server Components architecture
- Performance optimization (memo, useMemo, useCallback when justified)
- Testing React components
- Accessibility in React

**Placeholder registry:**
```
skills/recommended/frontend/react/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.12 TypeScript Skills

**Category ID:** `typescript`  
**Target Expertise:** Senior Engineer / Staff Engineer  
**Classification Target:** Recommended  
**Load Conditions:** TypeScript, .ts, .tsx, type system, generics, utility types  

**What this category governs:**
- TypeScript strict mode as default
- Type-safe API contracts
- Generic patterns for production systems
- Utility type composition
- Branded types for domain safety
- Module resolution patterns
- Build configuration standards

**Placeholder registry:**
```
skills/recommended/frontend/typescript/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.13 Security Engineering Skills (Specialist)

**Category ID:** `security-engineering`  
**Target Expertise:** Security Engineer / Principal Engineer  
**Classification Target:** Recommended  
**Load Conditions:** threat modeling, security review, penetration testing patterns, secure coding review  

**What this category governs:**
- OWASP Top 10 for AI systems
- Prompt injection defense patterns
- Privilege escalation prevention
- Data exfiltration detection
- Secure inter-service communication
- Cryptography application patterns
- Security audit frameworks

**Note:** This is distinct from the mandatory `security` category. `security` loads for all sessions and enforces baseline security. `security-engineering` loads when security is the primary domain of the work.

**Placeholder registry:**
```
skills/recommended/security/security-engineering/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.14 Browser Engineering Skills

**Category ID:** `browser-engineering`  
**Target Expertise:** Browser Engineer / Senior Engineer  
**Classification Target:** Optional  
**Load Conditions:** Playwright, browser automation, web scraping, CDP, browser agent  

**What this category governs:**
- Playwright production patterns
- Browser isolation and sandboxing
- CDP (Chrome DevTools Protocol) usage
- Prompt injection defense for browser agents
- Anti-detection for legitimate automation
- Browser session management
- Web content extraction without violating sites' terms

**Placeholder registry:**
```
skills/optional/browser/browser-engineering/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.15 Automation Engineering Skills

**Category ID:** `automation-engineering`  
**Target Expertise:** Senior Engineer / Staff Engineer  
**Classification Target:** Optional  
**Load Conditions:** PC control, pyautogui, pywinauto, automation workflow, system automation  

**What this category governs:**
- Windows automation APIs
- Accessibility API (UI Automation) patterns
- Safe automation boundaries
- Permission validation for automated actions
- Idempotent automation design
- Audit logging for automated actions
- Rollback patterns for automation

**Placeholder registry:**
```
skills/optional/automation/automation-engineering/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.16 Python Skills

**Category ID:** `python`  
**Target Expertise:** Senior Engineer / Staff Engineer  
**Classification Target:** Mandatory  
**Load Conditions:** Python, .py file, asyncio, Pydantic, SQLAlchemy, module implementation  

**What this category governs:**
- Python 3.12+ production patterns
- Async/await correctness
- Pydantic v2 production usage
- Type annotation completeness
- Error handling hierarchy design
- Module structure and public API design
- Performance considerations for CPython

**Placeholder registry:**
```
skills/mandatory/core/python/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.17 Voice System Skills

**Category ID:** `voice-systems`  
**Target Expertise:** Senior Engineer / Audio Engineer  
**Classification Target:** Optional  
**Load Conditions:** voice pipeline, STT, TTS, VAD, wake word, audio processing  

**What this category governs:**
- Real-time audio pipeline design
- STT model selection and configuration
- TTS quality and latency optimization
- Voice activity detection tuning
- Wake word reliability patterns
- Audio device handling on Windows
- End-to-end latency measurement and optimization

**Placeholder registry:**
```
skills/optional/voice/voice-systems/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.18 Performance Engineering Skills

**Category ID:** `performance-engineering`  
**Target Expertise:** Staff Engineer / Principal Engineer  
**Classification Target:** Recommended  
**Load Conditions:** performance optimization, profiling, latency reduction, throughput, benchmarking  

**What this category governs:**
- Profiling methodology (measure before optimizing)
- Async I/O performance patterns
- CPU-bound vs I/O-bound task classification
- Memory allocation patterns
- Caching strategy hierarchy
- Database query optimization
- Vector search performance tuning

**Placeholder registry:**
```
skills/recommended/performance/performance-engineering/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.19 Testing Skills

**Category ID:** `testing`  
**Target Expertise:** Senior Engineer / Staff Engineer  
**Classification Target:** Mandatory  
**Load Conditions:** test implementation, pytest, unit test, integration test, contract test, test design  

**What this category governs:**
- Test pyramid implementation
- Unit test isolation patterns
- Integration test boundaries
- Contract test design
- Fixture and mock patterns
- Test coverage strategy (what to cover, not just what percentage)
- Performance test design
- AI system testing patterns

**Placeholder registry:**
```
skills/mandatory/core/testing/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.20 DevOps Skills

**Category ID:** `devops`  
**Target Expertise:** Infrastructure Engineer / Senior Engineer  
**Classification Target:** Optional  
**Load Conditions:** Docker, CI/CD, deployment, infrastructure, GitHub Actions, operational scripts  

**What this category governs:**
- Docker production patterns (multi-stage builds, minimal images)
- Docker Compose for local development
- GitHub Actions workflow design
- Secrets management in CI/CD
- Health check implementation
- Graceful shutdown patterns
- Log aggregation design

**Placeholder registry:**
```
skills/optional/devops/devops/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.21 Observability Skills

**Category ID:** `observability`  
**Target Expertise:** Staff Engineer / Infrastructure Engineer  
**Classification Target:** Recommended  
**Load Conditions:** logging, tracing, metrics, monitoring, structlog, OpenTelemetry  

**What this category governs:**
- Structured logging standards (structlog)
- Distributed tracing implementation
- Metrics design (what to measure and why)
- Alerting thresholds and runbooks
- Log correlation across services
- Observability-driven development
- Debugging production systems from logs

**Placeholder registry:**
```
skills/recommended/observability/observability/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.22 Documentation Skills

**Category ID:** `documentation`  
**Target Expertise:** Senior Engineer  
**Classification Target:** Mandatory  
**Load Conditions:** ALL sessions — documentation standards load for every session  

**What this category governs:**
- Docstring standards (Google style)
- ADR writing methodology
- Technical specification writing
- API documentation standards
- Architecture diagram conventions
- README standards for production systems
- Change log maintenance

**Placeholder registry:**
```
skills/mandatory/core/documentation/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.23 UI/UX Design Skills

**Category ID:** `ui-ux`  
**Target Expertise:** Product Engineer / Senior Engineer  
**Classification Target:** Optional  
**Load Conditions:** UI design, dashboard, overlay, design system, user experience  

**What this category governs:**
- Information hierarchy and density
- Component design system patterns
- Motion and animation principles
- Dark interface design (for Aether HUD aesthetic)
- User feedback and loading state patterns
- Error state design
- Desktop overlay-specific UI patterns

**Placeholder registry:**
```
skills/optional/design/ui-ux/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.24 Accessibility Skills

**Category ID:** `accessibility`  
**Target Expertise:** Product Engineer / Senior Engineer  
**Classification Target:** Optional  
**Load Conditions:** UI, accessibility, WCAG, screen reader, keyboard navigation  

**What this category governs:**
- WCAG 2.2 AA compliance patterns
- Keyboard navigation implementation
- Screen reader compatibility
- Color contrast requirements
- Focus management in dynamic interfaces
- ARIA attribute usage
- Testing accessibility automatically

**Placeholder registry:**
```
skills/optional/design/accessibility/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

### 9.25 Product Engineering Skills

**Category ID:** `product-engineering`  
**Target Expertise:** Product Engineer / Senior Engineer  
**Classification Target:** Optional  
**Load Conditions:** product design, user story, feature design, experience architecture  

**What this category governs:**
- Feature flag implementation patterns
- Gradual rollout design
- User-facing error message standards
- Telemetry design (privacy-preserving)
- Feedback loop implementation
- Feature completeness criteria
- Product quality gates

**Placeholder registry:**
```
skills/optional/product/product-engineering/
  [EMPTY — awaiting evaluated skills]
  EXTENSION_POINT.md
```

---

## PART FOUR: EVALUATION FRAMEWORK

---

## 10. THE AETHER SKILL EVALUATION FRAMEWORK

### 10.1 Overview

Every skill considered for Aether classification is evaluated against an eight-dimension framework producing a score out of 100 points. The framework is designed so that skills encoding production-antipatterns cannot achieve high scores even if they appear comprehensive.

**Scoring formula:**

```
Total Score = 
  (Production Readiness × 1.5)  + [max 15 points]
  (Maintainability × 1.0)       + [max 10 points]
  (Security × 2.0)              + [max 20 points]
  (Scalability × 1.0)           + [max 10 points]
  (Performance × 1.0)           + [max 10 points]
  (Documentation Quality × 1.0) + [max 10 points]
  (Industry Adoption × 1.0)     + [max 10 points]
  (Long-Term Viability × 1.5)     [max 15 points]

Maximum total: 100 points
Each raw dimension: scored 1–10
```

**Classification thresholds:**

| Classification | Score Range | Additional Requirements |
|---|---|---|
| **Mandatory** | 90–100 | Security >= 18/20 AND Production Readiness >= 13/15 AND no disqualifying conditions |
| **Recommended** | 75–89 | Security >= 14/20 AND no disqualifying conditions |
| **Optional** | 60–74 | Security >= 10/20 AND no disqualifying conditions |
| **Rejected** | < 60 | OR Security < 10/20 OR any disqualifying condition present |

---

## 11. SCORING DIMENSIONS AND RUBRICS

### Dimension 1: Production Readiness (weight 1.5x, max 15 points)

**What it measures:** Whether the skill encodes patterns that function correctly under real production conditions: load, failure, recovery, and long-term operation.

| Score | Criterion |
|---|---|
| **10** | Skill explicitly addresses production failure modes, graceful degradation, monitoring hooks, operational runbooks, and has documented production usage at scale |
| **8–9** | Skill addresses most production concerns; addresses failure modes and recovery; may lack detailed monitoring guidance |
| **6–7** | Skill is production-capable with additions; covers the primary success path and most common failure modes |
| **4–5** | Skill requires significant augmentation for production; focuses primarily on development usage |
| **2–3** | Skill is primarily development or staging oriented; production use would require near-complete rewrite |
| **1** | Tutorial or example quality; no production applicability without complete replacement |

### Dimension 2: Maintainability (weight 1.0x, max 10 points)

**What it measures:** Whether following the skill produces code that teams can maintain, understand, and evolve over years.

| Score | Criterion |
|---|---|
| **10** | Skill enforces separation of concerns, named abstractions, testability, clear interfaces, and explicit over implicit patterns; systems built with it remain comprehensible after 2+ years |
| **8–9** | Strongly promotes maintainability; minor patterns that could create maintenance burden |
| **6–7** | Generally maintainable guidance; some patterns that could become problematic at scale |
| **4–5** | Neutral; some concerning patterns but compensated by good practices |
| **2–3** | Patterns that actively create maintenance burden over time |
| **1** | Guidance that systematically degrades maintainability |

### Dimension 3: Security (weight 2.0x, max 20 points)

**What it measures:** Whether the skill treats security as a first-class concern, not an afterthought.

| Score | Criterion |
|---|---|
| **10** | Comprehensive security coverage: input validation, secrets management, least-privilege, injection prevention, threat modeling, secure defaults; any security guidance is correct |
| **8–9** | Strong security stance; covers critical security concerns; may have minor gaps in edge cases |
| **6–7** | Security-aware; addresses obvious threats; some gaps in defense-in-depth |
| **4–5** | Mentions security but does not enforce it; some security-relevant guidance correct but incomplete |
| **2–3** | Security largely absent or treated as optional; no validation patterns |
| **1** | Security anti-patterns present; guidance that would introduce vulnerabilities if followed |

**Note:** A raw security score below 5 (weighted below 10/20) automatically classifies the skill as Rejected regardless of total score.

### Dimension 4: Scalability (weight 1.0x, max 10 points)

**What it measures:** Whether the skill avoids patterns that create hard scaling ceilings.

| Score | Criterion |
|---|---|
| **10** | Explicitly addresses horizontal scaling, statelessness where appropriate, distributed concerns, and avoids patterns that cannot scale |
| **8–9** | Scalability-aware; avoids common bottlenecks; may not explicitly address distributed concerns |
| **6–7** | Neutral to scaling; neither helps nor hurts; works at Aether's target scale |
| **4–5** | Some patterns that limit scalability; addressable without full rewrite |
| **2–3** | Patterns that create scalability ceilings that would require significant rework |
| **1** | Patterns that fundamentally cannot scale beyond a single process |

### Dimension 5: Performance (weight 1.0x, max 10 points)

**What it measures:** Whether the skill avoids common performance anti-patterns and provides performance-aware guidance.

| Score | Criterion |
|---|---|
| **10** | Explicit performance guidance; async-first for I/O; avoids N+1 queries; caching strategy; profiling methodology; benchmark targets |
| **8–9** | Performance-aware; avoids obvious bottlenecks; guidance on measurement |
| **6–7** | Neutral; no major performance anti-patterns; some consideration for efficiency |
| **4–5** | Some performance anti-patterns; tolerable at Aether's current scale |
| **2–3** | Performance anti-patterns that would require significant refactoring under load |
| **1** | Guidance that systematically produces slow code |

### Dimension 6: Documentation Quality (weight 1.0x, max 10 points)

**What it measures:** The quality of the skill document itself as a reference artifact.

| Score | Criterion |
|---|---|
| **10** | Complete, structured, examples for every constraint, clear rationale for every rule, when-to-use and when-not-to-use, decision frameworks, interaction with adjacent domains |
| **8–9** | Well-documented; clear structure; rationale present; most examples included |
| **6–7** | Adequately documented; main constraints clear; some gaps in rationale or examples |
| **4–5** | Sparse; key information present but without sufficient context or rationale |
| **2–3** | Difficult to follow; missing critical context; would require interpretation |
| **1** | Insufficient, misleading, or contradictory documentation |

### Dimension 7: Industry Adoption (weight 1.0x, max 10 points)

**What it measures:** Whether the patterns in the skill have been validated by meaningful production adoption.

| Score | Criterion |
|---|---|
| **10** | Patterns are used by companies at scale (FAANG, major cloud providers, or equivalent); recognized as industry standard; validated by published post-mortems or engineering blogs |
| **8–9** | Widely adopted by leading engineering teams; strong community validation; multiple production case studies |
| **6–7** | Adopted by reputable organizations; emerging standard with growing evidence base |
| **4–5** | Limited production evidence; theoretically sound but not widely validated |
| **2–3** | Mostly experimental; community-originated without production validation |
| **1** | No meaningful production validation; purely theoretical or tutorial-level |

### Dimension 8: Long-Term Viability (weight 1.5x, max 15 points)

**What it measures:** Whether the skill's guidance will remain correct and relevant as technology evolves.

| Score | Criterion |
|---|---|
| **10** | Based on stable engineering principles not tied to specific library versions; aligns with clear industry direction; backed by major organizations with long-term commitment |
| **8–9** | Stable patterns; technology-aware but not technology-dependent; low obsolescence risk |
| **6–7** | Moderate stability; some technology-specific guidance but core principles stable |
| **4–5** | Partially technology-specific; some obsolescence risk if underlying technology changes |
| **2–3** | Strongly tied to a specific library version or current trend; high obsolescence risk |
| **1** | Trendy or experimental; likely to become obsolete as technology evolves |

---

## 12. DISQUALIFYING CONDITIONS

The following conditions automatically classify a skill as Rejected regardless of total score. Each condition has a specific reason.

**DQ-1: Contains prototyping-first language**  
Words or phrases such as "for now," "later," "quick," "just," "skip for MVP," "we can add this later" in the context of quality requirements. Reason: These phrases train AI to defer quality, which is incompatible with Aether's standards.

**DQ-2: Contains security bypasses**  
Any guidance suggesting security validation can be skipped, stubbed, simplified "for speed," or deferred. Reason: Security bypasses in skill instructions will propagate to generated code.

**DQ-3: Contains architecture violation patterns**  
Any guidance suggesting direct database access outside module boundaries, direct LLM provider calls outside the router, or any violation of the Aether Project Constitution. Reason: Skills that encode architecture violations corrupt the codebase systematically.

**DQ-4: Promotes "vibe coding" methodology**  
Any skill whose philosophy or guidelines originate from or promote rapid iterative generation without standards enforcement. Reason: Vibe coding is explicitly incompatible with production engineering. See Section 18.

**DQ-5: Promotes "move fast" over correctness**  
Any skill that frames engineering speed as more valuable than correctness, testability, or security. Reason: Aether is a five-year project. Speed decisions made in Phase 1 become debt compounding through Phase 10.

**DQ-6: Missing evaluation scorecard**  
Any skill without a completed EVALUATION.md cannot be classified. Reason: All classification decisions must be traceable to evidence.

**DQ-7: Source repository archived or abandoned**  
A skill sourced from a repository with no activity in 18+ months, or that has been officially archived. Reason: Abandoned skills receive no security updates or corrections. See Section 19.3.

**Note on steipete/agent-rules:** This repository was archived on December 31, 2025. Skills from this source must be re-evaluated from their content alone, not from the source's reputation. The archival status means they receive DQ-7 consideration unless content is independently validated.

---

## 13. EVALUATION PROCESS

### 13.1 How to Evaluate a Candidate Skill

**Phase 1 — Disqualification Screening (5 minutes)**  
Read the skill for DQ-1 through DQ-5. If any disqualifying condition is present, the skill is Rejected immediately. No further evaluation is required. Document the specific condition in REJECTED_REGISTRY.md.

**Phase 2 — Dimension Scoring (30 minutes)**  
Score each of the eight dimensions using the rubrics in Section 11. For each dimension, identify the specific evidence in the skill text that supports the score. A score without evidence is invalid.

**Phase 3 — Score Calculation**  
Apply weights. Sum to total. Check against classification thresholds in Section 10.1.

**Phase 4 — Additional Requirements Check**  
Verify the classification-specific additional requirements are met (Security threshold, Production Readiness threshold for Mandatory).

**Phase 5 — Documentation**  
Complete the EVALUATION.md template. Commit the evaluation alongside the skill file. The skill is not registered until the evaluation is committed.

### 13.2 Who Evaluates Skills

For this project: the developer. Every skill evaluation is a documented architectural decision. The evaluation is not delegated to an AI tool without human verification of the scores.

AI tools may assist with research and initial analysis of a candidate skill. The developer reviews the analysis and assigns final scores.

---

## PART FIVE: CLASSIFICATION SYSTEM

---

## 14. CLASSIFICATION DEFINITIONS

### 14.1 Mandatory

**Definition:** Skills that encode non-negotiable standards for the Aether project. These skills load in every applicable session. Their constraints are not optional — generated output must comply.

**Requirements for Mandatory classification:**
- Score 90+ on the evaluation framework
- Security dimension: minimum 18/20
- Production Readiness dimension: minimum 13/15
- No disqualifying conditions
- Content directly governs a core Aether capability
- Failure to apply the skill's guidance would compromise the project

**Current Mandatory categories:** architecture, security, python, testing, documentation, agent-engineering, memory-systems

### 14.2 Recommended

**Definition:** Skills that represent best practices for specific task types. These skills load when the session involves the skill's domain. Their guidance is expected to be followed; deviation requires explicit justification.

**Requirements for Recommended classification:**
- Score 75–89 on the evaluation framework
- Security dimension: minimum 14/20
- No disqualifying conditions
- Content governs a domain that appears regularly in Aether development

**Current Recommended categories:** ai-engineering, rag, distributed-systems, event-driven, backend-engineering, system-design, react, typescript, security-engineering, performance-engineering, observability

### 14.3 Optional

**Definition:** Skills that apply to specific, less frequent development tasks. These skills load on demand or when a task clearly falls within their domain. Their guidance is expected when loaded.

**Requirements for Optional classification:**
- Score 60–74 on the evaluation framework
- Security dimension: minimum 10/20
- No disqualifying conditions
- Content governs a domain that appears occasionally in Aether development

**Current Optional categories:** voice-systems, browser-engineering, automation-engineering, devops, ui-ux, accessibility, product-engineering

### 14.4 Rejected

**Definition:** Skills that do not meet Aether's quality standards, contain disqualifying patterns, or encode practices incompatible with the project's standards.

**Grounds for Rejected classification:**
- Score below 60 on the evaluation framework
- Security dimension below 10/20
- Any disqualifying condition (DQ-1 through DQ-7)
- Content conflicts with the Aether Project Constitution

Rejected skills are documented in REJECTED_REGISTRY.md with specific rejection reasons. This documentation serves as guidance for prompt engineering (what to avoid) and as a record for future re-evaluation if the skill is significantly updated.

---

## 15. MANDATORY SKILLS REGISTRY

**Status: PLACEHOLDER — Awaiting evaluation and population**

```
skills/mandatory/core/architecture/
  [ No skills registered yet ]
  Waiting for: Evaluation of architecture skills from reference sources

skills/mandatory/core/security/
  [ No skills registered yet ]
  Waiting for: Evaluation of security skills; matank001/cursor-security-rules is
  priority source for initial security skill

skills/mandatory/core/python/
  [ No skills registered yet ]
  Waiting for: Evaluation of Python production patterns from reference sources

skills/mandatory/core/testing/
  [ No skills registered yet ]
  Waiting for: Evaluation of testing skills

skills/mandatory/core/documentation/
  [ No skills registered yet ]
  Waiting for: Aether-internal documentation skill (authored internally, not sourced)

skills/mandatory/ai-systems/agent-engineering/
  [ No skills registered yet ]
  Waiting for: Evaluation of agent engineering patterns from VoltAgent and Anthropic sources

skills/mandatory/ai-systems/memory-systems/
  [ No skills registered yet ]
  Waiting for: Aether-internal memory system skill (authored internally to reflect
  the specific memory architecture defined in V1_TECHNICAL_SPECIFICATION.md)
```

---

## 16. RECOMMENDED SKILLS REGISTRY

**Status: PLACEHOLDER — Awaiting evaluation and population**

```
skills/recommended/ai/ai-engineering/
  [ No skills registered yet ]

skills/recommended/ai/rag/
  [ No skills registered yet ]
  Source candidate: Evaluate skills from VoltAgent/awesome-agent-skills that address RAG

skills/recommended/architecture/distributed-systems/
  [ No skills registered yet ]

skills/recommended/architecture/event-driven/
  [ No skills registered yet ]
  Note: Aether-internal skill covering Redis Streams specifics likely needed alongside any
  external event-driven skill

skills/recommended/architecture/system-design/
  [ No skills registered yet ]

skills/recommended/backend/backend-engineering/
  [ No skills registered yet ]
  Source candidate: PatrickJS FastAPI skill (evaluate against framework)

skills/recommended/frontend/react/
  [ No skills registered yet ]
  Source candidate: Evaluate React skills from PatrickJS collection, priority on
  React Server Components and strict TypeScript integration

skills/recommended/frontend/typescript/
  [ No skills registered yet ]
  Source candidate: Evaluate TypeScript strict mode skills; reject any that suggest
  disabling strict mode

skills/recommended/security/security-engineering/
  [ No skills registered yet ]
  Source candidate: matank001/cursor-security-rules

skills/recommended/performance/performance-engineering/
  [ No skills registered yet ]

skills/recommended/observability/observability/
  [ No skills registered yet ]
```

---

## 17. OPTIONAL SKILLS REGISTRY

**Status: PLACEHOLDER — Awaiting evaluation and population**

```
skills/optional/voice/voice-systems/
  [ No skills registered yet ]
  Note: No external source identified for voice system skills. Likely requires
  Aether-internal authorship based on Windows audio stack specifics.

skills/optional/browser/browser-engineering/
  [ No skills registered yet ]
  Source candidate: Playwright-specific skills from VoltAgent collection

skills/optional/automation/automation-engineering/
  [ No skills registered yet ]
  Note: Windows-specific automation at this level likely requires internal authorship

skills/optional/devops/devops/
  [ No skills registered yet ]
  Source candidate: Docker and GitHub Actions skills from VoltAgent or PatrickJS

skills/optional/design/ui-ux/
  [ No skills registered yet ]

skills/optional/design/accessibility/
  [ No skills registered yet ]

skills/optional/product/product-engineering/
  [ No skills registered yet ]
```

---

## 18. REJECTED PATTERNS REGISTRY

The following patterns and skill sources are classified as Rejected. Skills encoding these patterns are not evaluated further — they are rejected on the pattern alone.

### 18.1 Vibe Coding Patterns

**Source:** github.com/obviousworks/vibe-coding-ai-rules and similar  
**Rejection Reason:** DQ-4 — Promotes vibe coding methodology  
**Classification Decision:** REPOSITORY REJECTED IN FULL

Vibe coding is defined as: a development methodology where AI generates code iteratively based on natural language descriptions without enforcing structural, quality, or architectural standards. The developer accepts whatever the AI generates as long as it "feels right."

This methodology is explicitly incompatible with Aether's production engineering standards for the following specific reasons:

- Vibe coding produces code that cannot be understood without running it
- Vibe coding accumulates technical debt faster than any other methodology
- Vibe coding does not enforce architectural boundaries
- Vibe coding produces untestable implementations
- Vibe coding treats correctness as a nice-to-have

No skill from this source, or from any source that describes its philosophy as "vibe coding," will be evaluated. The rejection is final.

**Documentation file:** `skills/rejected/patterns/vibe-coding-patterns.md` — to be authored describing the specific patterns to recognize and avoid.

### 18.2 Rapid Prototyping Shortcuts

Patterns rejected across all sources:

```
"Skip tests for now, add them later"
→ REJECTED: "Later" does not exist in production software.

"Use Any type to save time"
→ REJECTED: Type safety is not optional in Aether.

"Hardcode this value, we'll config it when needed"
→ REJECTED: Configuration from day one is a constitutional rule.

"Just use a bare except for now"
→ REJECTED: Silent exception handling is a Zero-Tolerance violation.

"Quick hack: import the database directly from the agent"
→ REJECTED: Architecture boundary violation, constitutional level.

"For MVP: disable security validation"
→ REJECTED: Security is never disabled.

"Add types later when the API stabilizes"
→ REJECTED: Types are written when the function is written.
```

### 18.3 Architecture Violation Patterns

Patterns that appear in some cursor rule collections but are incompatible with Aether:

```
"Access the database wherever it's most convenient"
→ REJECTED: The memory module owns all database access.

"Call the Anthropic API directly for quick tasks"
→ REJECTED: All LLM calls go through the router.

"Use globals for shared state between functions"
→ REJECTED: No global mutable state.

"Put configuration in constants in the source file"
→ REJECTED: All configuration from config system.

"Create a utility file for everything that doesn't fit elsewhere"
→ REJECTED: Every piece of code belongs to a specific module with a specific owner.
```

---

## PART SIX: REFERENCE REPOSITORY ANALYSIS

---

## 19. SOURCE REPOSITORY EVALUATION

The following repositories were evaluated as sources for Aether skill content. For each repository, the evaluation covers: what it contains, quality assessment, and classification recommendation for Aether use.

### 19.1 github.com/VoltAgent/awesome-agent-skills

**Status:** ACTIVE (1,424+ skills as of evaluation date)  
**Assessment:** PRIMARY REFERENCE SOURCE  

**What it contains:** Official skills from Anthropic, Google Labs, NVIDIA, Vercel, Stripe, Cloudflare, DuckDB, and hundreds of community contributors. The repository explicitly curates for quality: "Unlike many bulk-generated skill repositories, this collection focuses on real-world Agent Skills created and used by actual engineering teams, not mass AI-generated stuff."

**Quality level:** HIGH for official skills from named engineering organizations. Variable for community contributions.

**Aether classification guidance:**

| Skills from | Aether Recommendation |
|---|---|
| Anthropic official skills | EVALUATE — high prior probability of meeting standards |
| Google Labs (google-labs-code) | EVALUATE — official engineering team output |
| NVIDIA/TensorRT-LLM skills | EVALUATE for AI engineering domain |
| Vercel official skills | EVALUATE for deployment and frontend domains |
| DuckDB official skills | EVALUATE for data engineering domain |
| VoltAgent official skills | EVALUATE — strong engineering pedigree |
| Community skills (no org affiliation) | EVALUATE CAREFULLY — must pass full framework |

**Specific skills of interest for Aether (require individual evaluation):**
- `voltagent/voltagent-best-practices` — agent architecture patterns
- Any Anthropic-sourced skill covering Claude Code behavior
- NVIDIA TensorRT-LLM skills if they encode production AI system patterns

### 19.2 github.com/ComposioHQ/awesome-claude-skills

**Status:** ACTIVE (1,000+ skills)  
**Assessment:** SELECTIVE REFERENCE SOURCE  

**What it contains:** Curated collection of SKILL.md format skills across document processing (docx, pdf, pptx, xlsx), development workflows, and integrations. Quality is mixed — some official, some community.

**Notable items of interest for Aether (require individual evaluation):**
- `docx`, `pdf`, `pptx`, `xlsx` skills — document processing capabilities
- `prompt-engineering` skill — evaluate for AI engineering category
- Skills from named engineering organizations

**Aether classification guidance:** Evaluate official and organization-sourced skills. Reject anonymous community skills without evidence of production use.

### 19.3 github.com/steipete/agent-rules

**Status:** ARCHIVED — December 31, 2025  
**Assessment:** HISTORICAL REFERENCE ONLY — DQ-7 applies  

**What it contained:** Global and project-level agent rules for Claude Code and Cursor, authored by a senior iOS engineer. Well-regarded before archival.

**Aether classification guidance:** This repository is archived. Per DQ-7 (archived/abandoned sources), skills from this repository receive the disqualifying condition automatically. Skills of interest must be:
1. Identified by content (not by reputation of the source)
2. Re-validated against current Aether standards
3. Re-evaluated through the full framework before registration

Peter Steinberger has moved to OpenAI and is now involved with OpenClaw (openclaw/agent-skills). That repository supersedes this one as a potential source.

### 19.4 github.com/PatrickJS/awesome-cursorrules

**Status:** ACTIVE (40,000+ stars, large community)  
**Assessment:** SELECTIVE REFERENCE — High volume, mixed quality  

**What it contains:** A very large collection of `.mdc` cursor rule files covering many technology stacks. The repository is community-contributed and does not enforce quality standards at the source level.

**Quality assessment:** Highly variable. Some rules (FastAPI patterns, TypeScript strict mode configurations) encode production-grade guidance. Many rules are beginner-level or encode personal preferences rather than production standards. A subset contains patterns inconsistent with Aether's architecture.

**Aether classification guidance:**

| Category | Recommendation |
|---|---|
| Framework-specific patterns (FastAPI, Pydantic, SQLAlchemy) | EVALUATE INDIVIDUALLY |
| TypeScript strict configuration rules | EVALUATE — likely high scores |
| React + TypeScript patterns | EVALUATE INDIVIDUALLY |
| Generic "code quality" rules | EVALUATE — likely variable scores |
| "Rapid development" or "vibe" rules | REJECT — DQ-4/5 |
| Game development rules (Unity, GameMaker) | NOT APPLICABLE to Aether |
| Landing page or marketing site rules | NOT APPLICABLE to Aether |

**Specific rule files of potential interest (require individual evaluation):**
- `clean-code.mdc` — evaluate for production standards
- `typescript.mdc` — evaluate for TypeScript category
- `python.mdc` — evaluate for Python mandatory category
- `react.mdc` — evaluate for React recommended category
- `fastapi.mdc` — evaluate for backend-engineering category
- `database.mdc` — evaluate for backend-engineering category

### 19.5 github.com/matank001/cursor-security-rules

**Status:** EVALUATE STATUS — Requires direct assessment  
**Assessment:** PRIORITY EVALUATION FOR SECURITY CATEGORY  

**What it contains:** Security-focused cursor rules. Priority source for the Mandatory security skill category.

**Aether classification guidance:** This repository's primary domain (security) is critical for Aether. Priority evaluation target. Specific concerns to check during evaluation:
- Does it address AI-specific security concerns (prompt injection)?
- Does it cover Windows-specific security contexts?
- Does it address Python async security patterns?
- Does it address secrets management in development workflows?

### 19.6 github.com/continuedev/awesome-rules

**Status:** ACTIVE  
**Assessment:** SELECTIVE REFERENCE — IDE-specific, partially applicable  

**What it contains:** Rules for the Continue IDE extension. Some rules are IDE-specific and not applicable to Aether's session-based skill loading. Others encode language and framework patterns that are applicable.

**Aether classification guidance:** Evaluate language-specific and framework-specific rules that do not depend on Continue-specific features. Reject IDE-specific rules that assume Continue's tool integrations.

### 19.7 github.com/obviousworks/vibe-coding-ai-rules

**Status:** ACTIVE  
**Assessment:** REPOSITORY REJECTED IN FULL — DQ-4  

**What it contains:** Rules for "vibe coding" methodology.

**Aether classification guidance:** This repository is rejected in its entirety per Disqualifying Condition DQ-4 (promotes vibe coding methodology). No skills from this source are evaluated or registered. See Section 18.1 for the detailed rejection rationale.

**This rejection is final and not subject to re-evaluation unless the repository's stated methodology changes.**

### 19.8 github.com/tonynguyennvt/cursor-rules-awesome

**Status:** EVALUATE STATUS  
**Assessment:** SUPPLEMENTARY REFERENCE — Similar to PatrickJS collection  

**What it contains:** Another curated cursorrules collection. Similar scope and quality distribution to the PatrickJS collection.

**Aether classification guidance:** Check for rules not present in PatrickJS collection. Apply the same selective evaluation criteria. Avoid registering duplicate rules from multiple sources.

### 19.9 github.com/ciembor/agent-rules-books

**Status:** EVALUATE STATUS  
**Assessment:** EVALUATE — "Books" framing suggests structured knowledge  

**What it contains:** Requires direct evaluation. The "books" framing suggests more structured, comprehensive content than typical cursor rule collections.

**Aether classification guidance:** Evaluate individually. If content encodes structured domain knowledge at the level of an engineering reference book, likely candidate for Recommended or Optional classification.

---

## PART SEVEN: GOVERNANCE

---

## 20. SKILL REGISTRATION PROCESS

### 20.1 Proposing a New Skill

A skill is proposed by creating a branch in the Aether repository and submitting a PR with:
1. The skill directory structure (SKILL.md + EVALUATION.md + CHANGELOG.md)
2. Completed EVALUATION.md with all scores and evidence
3. An entry in REGISTRY.md
4. A commit message following the format: `skill(register): add {skill-name} [{classification}] score={n}/100`

### 20.2 The Registration Checklist

```
SKILL REGISTRATION CHECKLIST:

Pre-Registration:
  [ ] DQ-1 through DQ-7 screening complete — no disqualifying conditions
  [ ] All 8 dimensions scored with documented evidence
  [ ] Score calculated using the weighted formula
  [ ] Classification threshold verified
  [ ] Additional requirements for classification verified (Security, PR thresholds)

File Completeness:
  [ ] SKILL.md present with all required sections
  [ ] SKILL.md YAML frontmatter complete with all required fields
  [ ] EVALUATION.md complete with scores and justifications
  [ ] CHANGELOG.md created with initial version entry
  [ ] Extension point placeholder removed from target directory

Registry Updates:
  [ ] REGISTRY.md entry added
  [ ] Skill load_conditions are specific and testable
  [ ] Any dependencies verified as already registered or registered simultaneously
  [ ] Any incompatibilities declared in both skills

Compliance Verification:
  [ ] Skill content does not contradict any Constitutional document
  [ ] Skill content is consistent with V1_TECHNICAL_SPECIFICATION.md
  [ ] Skill content is consistent with ARCHITECTURE_RULES.md
```

### 20.3 Internal vs. External Skills

**Internal skills** are authored specifically for Aether by the developer. They encode Aether-specific patterns, configurations, and constraints that no external source would provide. They must still be evaluated against the framework.

Required internal skills (authored by developer, not sourced externally):
- `aether-memory-system` — the specific memory architecture defined in the spec
- `aether-event-contracts` — the specific Redis Streams event schema standards
- `aether-llm-router` — the model-agnostic routing patterns specific to Aether
- `aether-documentation-standards` — documentation standards from ADR-011

**External skills** are sourced from reference repositories. They must cite their source in the YAML frontmatter and their EVALUATION.md must note any modifications made to adapt them for Aether.

---

## 21. SKILL LIFECYCLE MANAGEMENT

### 21.1 Versioning

Skills follow semantic versioning:
- **MAJOR:** Breaking change to constraints (existing generated code would violate new rules)
- **MINOR:** New constraints added (existing code unaffected; new code must comply)
- **PATCH:** Clarifications, examples, documentation improvements; no constraint changes

When a skill's source repository releases an update, the Aether evaluation of the update is required before upgrading. A source update does not automatically trigger an Aether version increment.

### 21.2 Mandatory Review Events

A registered skill must be re-evaluated when:
- Its source repository releases a major version
- A disqualifying condition is discovered in existing content (downgrade to Rejected)
- An ADR changes the standards the skill encodes (alignment check required)
- The technology the skill covers releases a major version
- 12 months have elapsed since the last evaluation

### 21.3 Skill Retirement

A skill is retired when:
- Its source has been abandoned for 18+ months (DQ-7 applies at renewal)
- The technology it covers has been officially deprecated
- An Aether-internal skill supersedes it
- A higher-quality alternative is registered that addresses the same domain

Retired skills move to an `archived/` directory within the classification tier. They are not deleted — they serve as historical reference.

### 21.4 The Skill Debt Register

Similar to the technical debt register in ADR-010 Section 13, skills have a skill debt register at `skills/SKILL_DEBT_REGISTER.md`. A skill debt entry is created when:
- A skill category has no registered skills (placeholder only) — debt priority P2
- A registered skill scores between 60–74 (optional) but is needed for a Recommended domain — debt P3
- A skill is identified as needing an update but the update hasn't been evaluated — debt P2

---

## 22. COMPLIANCE VERIFICATION

### 22.1 Session Compliance

At the start of every AI code generation session, compliance with the skill loading mandate is verified by:
1. The developer confirming the session begins with the skill loading declaration
2. The AI system declaring which skills are loaded
3. The AI system confirming output will comply with all loaded skill constraints

A session that does not include the loading declaration is non-compliant. Output from non-compliant sessions receives the full ADR-011 review treatment.

### 22.2 Output Compliance

Generated output is verified against loaded skill constraints as part of the self-verification checklist in AI_GENERATION_RULES_V2.md Section 21. Skills may add items to the self-verification checklist — this is one of their functions.

When generated output violates a loaded skill's constraints:
1. The violation is noted by type and location
2. The output is corrected before presentation
3. If correction requires architectural guidance from the developer, a stop condition is raised

### 22.3 The Skill Loading Mandate — Restated

**Every AI system operating within Aether AI OS must load and comply with all applicable skill packs before generating architecture, code, tests, documentation, or UI components.**

This mandate is enforceable. Compliance is verified through:
- Session opening declarations
- Self-verification checklists
- Code review process (ADR-011 Section 5.2)
- Automated CI checks (where skill constraints can be expressed as linting rules)

Non-compliance is treated as a process failure, not a minor oversight. The appropriate response to non-compliance is:
1. Identify which skills were not loaded
2. Reload the session with correct skills
3. Re-generate the output
4. Review the output against the loaded skills before committing

The skill loading mandate exists because the difference between AI-assisted output with production-grade skills loaded and AI-assisted output without any domain guidance is the difference between principal-engineer-level code and probabilistically average internet code. Aether requires the former.

---

*Document Version: 1.0*  
*Status: ACCEPTED — ENFORCED*  
*Classification: Project Governance — Operational*  
*Skill Registry Status: All categories PLACEHOLDER — population begins after evaluation process*  
*Review Trigger: Skill registration events, quarterly lifecycle reviews, Constitutional amendments*  
*Owner: Principal Systems Engineer*  
*Last Updated: 2025-11-15*
