# AETHER INTELLIGENCE ARCHITECTURE
### docs/architecture/AETHER_INTELLIGENCE_ARCHITECTURE.md
### The Complete Cognitive Architecture of Aether AI OS

---

**Date:** 2025-11-15
**Status:** ACCEPTED — FOUNDATIONAL ARCHITECTURE
**Classification:** Project Architecture — Cognitive / Intelligence Layer
**Constitutional Tier:** Tier 1 (per ADR-010 Section 16.1) — joining the Master
Blueprint, V1 Foundation Architecture Decision, and V1 Technical Specification
**Authority:** Chief AI Architect / Principal Systems Engineer
**Horizon:** This document is written to remain correct for 5–10 years of
Aether's development. It is not an implementation document and contains no
code.

---

## THE UNIFIED INTELLIGENCE MANDATE

**Aether is one continuous intelligence, built from many specialized
engines. No engine speaks to the user directly. No engine is irreplaceable.
The architecture defined here — the Personality Engine, the Executive
Intelligence Layer, the Capability Registry, the Runtime Scheduler, the
full agent hierarchy — is permanent. The models occupying each capability
slot are not. This document governs how intelligence operates inside
Aether for the life of the project, independent of which specific models
fill which role on any given day.**

**A note on scope.** This document defines the mature, full-vision
cognitive architecture of Aether across its entire ten-phase roadmap. It is
deliberately larger than what Phase 1 has built so far. Phase 1's
`ModelTier` enum (`LOCAL`/`CHEAP`/`STANDARD`/`PREMIUM`, defined in
V1_TECHNICAL_SPECIFICATION.md Section 2.4) is the earliest, simplest
working instance of the Capability-Based Engine Assignment principle
formalized in Section 9 below — a single conversational agent needed only
four generic quality tiers. As Aether's agent roster diversifies through
later phases, those four tiers are expected to evolve into the named
capability engines this document describes. Nothing here requires
reopening Phase 1's already-approved milestones; it describes where the
architecture is headed, built on the same principles Phase 1 already
established: a locked, model-agnostic router at the center, and no
component anywhere permitted to hardcode a model name.

---

## TABLE OF CONTENTS

1. [The Philosophy of Intelligence](#1-the-philosophy-of-intelligence)
2. [Unified Personality Architecture](#2-unified-personality-architecture)
3. [Unified Memory Architecture](#3-unified-memory-architecture)
4. [Concurrent Intelligence Runtime](#4-concurrent-intelligence-runtime)
5. [Runtime Scheduler](#5-runtime-scheduler)
6. [Executive Intelligence Layer](#6-executive-intelligence-layer)
7. [Agent Architecture](#7-agent-architecture)
8. [Sub-Agent Architecture](#8-sub-agent-architecture)
9. [Capability-Based Engine Assignment](#9-capability-based-engine-assignment)
10. [Current Approved Runtime Mapping](#10-current-approved-runtime-mapping)
11. [Context Synchronization](#11-context-synchronization)
12. [Collective Intelligence](#12-collective-intelligence)
13. [Resource Management](#13-resource-management)
14. [Future Evolution](#14-future-evolution)
15. [Future Intelligence Roadmap](#15-future-intelligence-roadmap)
16. [Guiding Principles](#16-guiding-principles)
17. [Collective Intelligence Network](#17-collective-intelligence-network)
18. [Engine Collaboration Protocol](#18-engine-collaboration-protocol)
19. [Capability Registry](#19-capability-registry)
20. [Engine Lifecycle](#20-engine-lifecycle)
21. [Agent Health Monitoring](#21-agent-health-monitoring)
22. [Runtime Telemetry Framework](#22-runtime-telemetry-framework)
23. [Graceful Degradation](#23-graceful-degradation)
24. [Long-Term Intelligence Evolution](#24-long-term-intelligence-evolution)

---

## 1. THE PHILOSOPHY OF INTELLIGENCE

### 1.1 Why Aether Is an Operating System, Not a Chatbot

A chatbot is a function: text goes in, text comes out, and nothing persists
between calls except what the caller chooses to resend. Its entire
existence is the duration of a single request.

An operating system is not a function. It is a persistent environment. It
boots once and keeps running. It holds state that outlives any individual
process. It manages resources — memory, CPU, GPU — across many concurrent
consumers. It enforces boundaries between what different processes are
permitted to do. It presents one coherent interface to whoever is using it,
regardless of how many separate subsystems are working underneath at any
given moment.

Aether is built as the second kind of thing. Every architectural document
already produced for this project — the modular monolith with locked
module boundaries, the persistent memory system that survives process
restarts, the event bus that lets subsystems communicate without knowing
about each other, the permission system that governs what any given action
is allowed to do — is already, in miniature, operating-system engineering,
not chatbot engineering. This document extends that same discipline to the
part of Aether that thinks.

### 1.2 Why Intelligence Is Distributed Internally But Unified Externally

No single model is the best tool for every cognitive task. A model tuned
for fluent, natural dialogue is not the model you want reasoning through a
fifteen-step refactor. A model that reasons well through multi-step logic
is not the model you want doing millisecond-latency tool-call
classification. This is not a limitation to route around — it is the same
reason an operating system does not run every process on a single,
undifferentiated execution unit. It assigns work to the component built
for that work: disk I/O to a disk controller, rendering to a GPU,
scheduling to a scheduler. Aether's intelligence is organized the same
way: many engines, each assigned to the capability it is genuinely suited
for.

But an operating system does not expose this internal division to the
person using it. A user does not open five different programs because five
different subsystems handled their file save. They experience one
computer. Aether's user experience follows the identical principle for a
different reason: trust. A person building a long-term relationship with a
persistent AI companion cannot be asked to track which of several
sub-personalities they are currently addressing, or to notice a jarring
shift in tone between one reply and the next because a different engine
happened to generate it. Continuity of identity is not a cosmetic
preference — it is the precondition for the kind of trust a five-to-ten
year companion relationship requires. Internally distributed. Externally,
always, only, Aether.

### 1.3 Why Intelligence Is an Operating System Capability, Not a Model Call

Treating "thinking" as a single LLM call means treating intelligence as
stateless computation — the same category of thing as a hash function.
Treating intelligence as an operating system capability means treating it
the way an OS treats computing generally: as a resource that is scheduled,
allocated, bounded, monitored, and shared across many simultaneous
consumers, with a persistent identity that exists independently of any
single request being served right now.

This reframing is what makes every other section of this document
possible. A scheduler only makes sense if there is more than one thing
that might need to run. A memory architecture only makes sense if state is
expected to outlive a single call. A Personality Engine only makes sense
if there is more than one internal voice that needs unifying. None of
these are add-ons to a chatbot. They are the definition of an operating
system, applied to cognition.

---

## 2. UNIFIED PERSONALITY ARCHITECTURE

### 2.1 The Core Rule

**No internal engine is permitted to produce the final text, voice, or
visual response the user receives.** Every output — regardless of which
engine or combination of engines produced the underlying content — passes
through exactly one component before reaching the user: the **Personality
Engine**. This is not a stylistic preference. It is the architectural
mechanism that makes Section 1.2's promise ("externally unified") true
rather than aspirational.

### 2.2 The Personality Engine's Responsibilities

- **Tone** — the register Aether speaks in (warm, direct, occasionally
  dry) and how that register flexes appropriately by context without ever
  becoming unrecognizable.
- **Humor** — calibrated, consistent comedic timing and style, distinct
  from whatever incidental humor an underlying engine's raw output might
  contain.
- **Empathy** — how Aether acknowledges difficulty, uncertainty, or
  emotional weight in what the user is going through, independent of which
  engine handled the underlying task.
- **Vocabulary** — a consistent word-choice profile; Aether does not
  suddenly speak in the vocabulary of a code-completion model because a
  coding task was involved.
- **Conversation style** — sentence length, structure, and rhythm held
  consistent across every interaction.
- **Greeting style** — how Aether opens a session, consistent with the
  morning-briefing pattern already established in Phase 1.
- **Emotional consistency** — Aether's emotional register does not swing
  unpredictably between replies that happen to originate from different
  engines.
- **Relationship continuity** — Aether remembers, and speaks as though it
  remembers, the ongoing relationship with this specific user.
- **Long-term behavioral consistency** — the Aether a user talks to in
  year three behaves recognizably like the Aether from year one, even as
  every engine underneath has been replaced multiple times.
- **Trust** — never overstating confidence, never hiding a limitation,
  never producing a response that reads as coming from someone other than
  the entity the user has built a relationship with.
- **Communication consistency** — formatting habits, response length
  calibration, and structural conventions held stable across every domain
  Aether operates in.

### 2.3 The Two-Stage Pipeline

```
   Any Engine(s)                Personality Engine              User
┌──────────────────┐         ┌──────────────────────┐      ┌────────┐
│  Content          │         │  Personality          │      │        │
│  Generation       │────────▶│  Rendering            │─────▶│  Aether│
│                   │  draft  │                        │final │        │
│  (Coding Engine,  │ content │  - applies tone        │ text │        │
│   Reasoning       │  or     │  - applies style        │      │        │
│   Engine,         │structured│  - applies relationship │      │        │
│   Conversation    │  intent │    continuity            │      │        │
│   Engine, etc.)   │         │  - never exposes source  │      │        │
└──────────────────┘         └──────────────────────┘      └────────┘
```

No engine's output reaches the user as-is. What crosses the boundary
between Content Generation and the Personality Engine is **structured
content or intent**, not finished prose — a fact, a code diff, a research
summary, a proposed plan — never a fully-formed reply pretending to be
Aether's voice. The Personality Engine is the only component with
authority to produce the literal words, tone, and phrasing the user
receives.

### 2.4 What the Personality Engine Maintains

- **Personality Profile** — the stable parameters of Aether's voice (tone
  register, humor calibration, formality level, response-length defaults),
  bounded within a range the user may adjust but never removed entirely.
- **Relationship State** — how long Aether and this user have known each
  other, recurring themes, and continuity markers that make long-term
  familiarity legible in how Aether talks, without requiring every past
  conversation to be re-read.
- **Style Consistency Rules** — banned phrasings, preferred phrasing
  patterns, and length calibration, enforced identically regardless of
  which engine produced the underlying content.

### 2.5 Implementation Independence

The Personality Engine is itself a capability (Section 9) — its specific
implementation (a lightweight dedicated pass, a strict-system-prompt final
pass through the Conversation Engine, or a future dedicated Aether
Foundation Model) is replaceable exactly like every other engine. What is
never replaceable is the **contract**: structured content in, Aether's
voice out, and no engine bypasses this gate.

---

## 3. UNIFIED MEMORY ARCHITECTURE

### 3.1 One Memory, No Exceptions

Every agent and every engine reads and writes memory through exactly one
interface: the Memory API already established in Phase 1
(`aether/memory/api.py`, V1_TECHNICAL_SPECIFICATION.md Section 2.5). There
is no engine-local cache, no agent-private memory, and no scenario in which
two parts of Aether hold divergent beliefs about the same fact because they
consulted different stores. This is not a new rule this document
introduces — it is the same rule Phase 1 already enforces via the
`MemoryAPI` boundary, extended without modification to every future agent
and engine.

### 3.2 The Seven Memory Types

The following are **functional, logical categories** of memory, not seven
separate storage systems. They are all implemented through the same
underlying `MemoryAPI`, the same `MemoryType` enum (extended conceptually
below), and the same tagging mechanism already present in the
`MemoryRecord` schema.

| Memory Type | Definition | Physical Implementation |
|---|---|---|
| **Working Memory** | The immediate, in-flight context for a task currently executing | Tier 0 — the in-process, immutable `AgentContext` object; never persisted |
| **Conversation Memory** | The raw transcript of the active session | The `messages` table, scoped to a `session_id`; short-lived unless consolidated |
| **Episodic Memory** | Summarized events and interactions ("on this date, the user did X") | `MemoryType.EPISODE` |
| **Semantic Memory** | Durable facts and learned procedural knowledge | `MemoryType.FACT` (declarative facts) and `MemoryType.SKILL` (procedural knowledge, a specialized subtype of semantic memory) |
| **Preference Memory** | How the user likes things done | `MemoryType.PREFERENCE` |
| **Project Memory** | Memories scoped to a specific ongoing context (a project, a goal, a recurring theme) | Any `MemoryType`, scoped via the existing `tags` field — a cross-cutting dimension, not a separate store |
| **Long-Term Memory** | The umbrella term for everything that survives beyond the active session | The union of Episodic + Semantic + Preference memory, durable in SQLite and Qdrant |

### 3.3 Synchronization Between Engines

Because every engine reads and writes through the same `MemoryAPI`, there
is no synchronization problem to solve in the traditional distributed-
systems sense — there is only one copy of the truth. What must still be
designed is **concurrent access discipline**, addressed fully in Section
11: writes are serialized through the Memory API, state changes are
broadcast on the existing event bus so concurrently-running engines learn
of relevant updates without polling, and every engine operates against an
immutable context snapshot rather than a live, mutable view that could
change underneath it mid-task.

---

## 4. CONCURRENT INTELLIGENCE RUNTIME

### 4.1 The Requirement

Aether must be able to run many cognitive processes at once: writing code,
planning a multi-step goal, automating a browser workflow, conducting
research, consolidating yesterday's memories, indexing newly ingested
documents, organizing files, processing email, managing a calendar,
executing a scheduled reminder, and generating documentation — potentially
all in the same window of time. Two rules govern this without exception:

**Conversation with the user is never blocked by background work.**
**Background work is never interrupted by conversation.**

A user should never experience Aether going quiet because it is busy
indexing a document in the background. A background consolidation job
should never be aborted mid-write because the user started talking. These
are resolved through priority, not through mutual exclusion — the
mechanism is defined fully in Section 5.

### 4.2 The Concurrency Model

Every active cognitive process — whether foreground (the live conversation)
or background (everything else) — is represented as an independent **job**
submitted to the Runtime Scheduler. Jobs do not share mutable state with
each other directly; they communicate exclusively through the Memory API
and the event bus, exactly as Section 3.1 requires. This means the actual
mechanism of "running two things at once" is ordinary concurrent task
execution (async tasks within a process, or separate processes where
technical isolation is required, exactly as Phase 1 already separates the
voice pipeline into its own process for GIL-related reasons) — the
architectural novelty is not in the concurrency primitive itself, but in
the **scheduling discipline layered on top of it**, described next.

### 4.3 Relationship to Phase 1

Phase 1's `AgentRuntime` is explicitly documented in
V1_TECHNICAL_SPECIFICATION.md Section 2.7 as "a simple sequential runner
(no LangGraph)... Phase 5 upgrade: replace runner internals with a
LangGraph state graph. Agent interface unchanged." This section describes
exactly that mature, Phase 5 form. Nothing here contradicts Phase 1's
deliberately simple starting point — it describes what that starting point
is already designed to grow into.

---

## 5. RUNTIME SCHEDULER

### 5.1 Purpose

The Runtime Scheduler is Aether's answer to the question every operating
system scheduler answers: given more work than can run simultaneously on
the available hardware, what runs now, what waits, and what gets
preempted? It governs every engine, every agent job, and every background
process in the system.

### 5.2 Job Classes

| Class | Examples | Default Priority |
|---|---|---|
| **Foreground Jobs** | The live conversation turn currently in progress | INTERACTIVE (highest) |
| **Background Jobs** | Memory consolidation, indexing, research, file organization, scheduled automations | HIGH / NORMAL / LOW / IDLE |

### 5.3 Priority Scale

```
INTERACTIVE   — the active conversation turn; never queued, never preempted
HIGH          — user-requested background work the user is actively waiting on
                (e.g., "research this while I do something else")
NORMAL        — routine background work (indexing, file organization)
LOW           — deferrable maintenance (memory consolidation, non-urgent
                learning passes)
IDLE          — runs only when no other class has pending work (deep
                background analysis, speculative pre-computation)
```

### 5.4 Scheduling Queues

Each priority level has its own queue, and each engine (Section 9) has its
own per-engine queue beneath that — a job waits both for its priority
class to be served and for its assigned engine to be available. This
two-dimensional queuing is what allows, for example, a LOW-priority memory
consolidation job to proceed on the Memory Consolidation Engine at the same
moment an INTERACTIVE conversation job is being served by the Conversation
Engine — different engines, no contention.

### 5.5 Interrupt Handling and Cancellation

- **Interruption:** A background job occupying an engine that a
  higher-priority job now needs is paused (not killed) at the next safe
  checkpoint, its partial state preserved, and resumed once the engine is
  free again.
- **Cancellation:** Any job, foreground or background, can be cancelled
  cleanly. A cancelled job's partial results are either discarded or
  checkpointed to memory, depending on whether partial progress has
  standalone value — this determination is made by the Executive
  Intelligence Layer (Section 6) at cancellation time, not hardcoded per
  job type.

### 5.6 Resource Allocation

- **CPU Scheduling** — lightweight, high-frequency engines (tool calling,
  embedding, reranking, OCR) are CPU-eligible by default, freeing GPU
  headroom for heavier engines, consistent with the CPU-embedding decision
  already made in Phase 1 (V1_TECHNICAL_SPECIFICATION.md Section 2.4).
- **GPU Scheduling** — heavy engines (reasoning, coding, vision) compete
  for VRAM through the GPU Resource Manager (Section 7, Group C), which
  the scheduler consults before dispatching any GPU-bound job.
- **Memory Allocation** — both system RAM and VRAM are tracked per-engine;
  the scheduler will not dispatch a job whose engine cannot currently fit
  within budget without first freeing space (Section 13).
- **Future Distributed Scheduling** — nothing in this design assumes a
  single machine. Jobs are already addressed by capability, not by
  physical location; a future multi-machine Aether deployment extends the
  same queue-and-priority model across a network boundary without changing
  the scheduling contract any job or engine relies on.

### 5.7 Engine Warm Pools and Lifecycle Management

Loading a large local model from disk into VRAM is expensive in latency.
The Scheduler maintains a **warm pool**: a small number of engines kept
resident and ready, chosen by recent-use frequency and priority-weighted
demand, with least-recently-used eviction when a higher-priority engine
needs the space. Every engine moves through a defined lifecycle:

```
UNLOADED → LOADING → WARM (idle, resident) → ACTIVE (serving a job)
                          ▲                        │
                          └────────────────────────┘
                                (job completes,
                                 returns to WARM)
                          │
                          ▼ (evicted under memory pressure)
                       UNLOADED
```

### 5.8 Graceful Degradation

When hardware cannot support the ideal configuration, the Scheduler — in
this order — queues the job if nothing is waiting on it, substitutes a
registered lighter-weight engine for that capability if one exists, or
delays non-urgent background work. It never silently fails and never
blocks the foreground conversation indefinitely. The full resource
strategy for the current hardware target is detailed in Section 13.

---

## 6. EXECUTIVE INTELLIGENCE LAYER

### 6.1 Role

The Executive Intelligence Layer is Aether's cognitive brain — the single
central controller that receives goals, understands intent, decomposes
work, assigns it to the right agents and engines, monitors execution,
merges results, recovers from failure, and hands every final result to the
Personality Engine before it reaches the user. It is the mature,
formalized descendant of the Orchestrator (Supervisor Agent) concept
already introduced in the original Master Blueprint Section 5.2.

### 6.2 Internal Structure

```
                    ┌─────────────────────────────┐
                    │   EXECUTIVE INTELLIGENCE      │
                    │          LAYER                │
                    │                               │
  User / Trigger ──▶│  1. Intent Parser             │
                    │       ↓                       │
                    │  2. Task Decomposer           │
                    │       ↓                       │
                    │  3. Engine/Agent Selector      │
                    │       ↓                       │
                    │  4. Execution Monitor          │
                    │       ↓                       │
                    │  5. Result Merger              │
                    │       ↓                       │
                    │  6. Personality Handoff        │
                    └───────────┬───────────────────┘
                                ▼
                       Personality Engine (Section 2)
```

1. **Intent Parser** — turns raw input (a user utterance, a scheduled
   trigger, a system event) plus current context into a structured Goal
   object.
2. **Task Decomposer** — breaks a Goal into an ordered or parallel Task
   Graph, reusing the Planner Agent's task-graph concept already defined in
   the original Master Blueprint Section 5.3.
3. **Engine/Agent Selector** — consults the Capability Registry (Section
   9) to determine which agent, and which engine behind that agent, handles
   each node of the task graph.
4. **Execution Monitor** — tracks progress against the Runtime Scheduler
   (Section 5), handles timeouts, and escalates failures rather than
   letting them silently propagate.
5. **Result Merger** — combines outputs, potentially from multiple engines
   working on the same goal (Section 12), into one coherent structured
   result.
6. **Personality Handoff** — packages the final result as structured
   content, never raw model text, and passes it to the Personality Engine.
   The Executive Layer never allows any engine's raw output to reach the
   user directly.

### 6.3 Authority Boundaries

The Executive Intelligence Layer has authority to assign work, reprioritize
jobs, and merge results. It does not have authority to bypass the
permission system already established in ADR-010 and
`.aether/permissions.yaml`, to perform a Level 4 or Level 5 operation
without the governed override process, or to speak to the user without
passing through the Personality Engine. Its authority is coordination, not
override of the Constitution.

---

## 7. AGENT ARCHITECTURE

Every agent below is defined by Purpose, Responsibilities, Authority,
Inputs, Outputs, Communication Contract, and Dependencies. Agents are
organized into five groups for clarity; the grouping is descriptive, not
architectural — every agent communicates with the Executive Intelligence
Layer through the same contract regardless of group.

---

### GROUP A — CORE COGNITIVE AGENTS

**Conversation Agent**
Purpose: the primary interactive agent handling live dialogue with the
user; already implemented in Phase 1.
Responsibilities: interpret user intent within a turn; invoke tools when
needed; produce structured draft content for the Personality Engine.
Authority: may invoke any tool in its allowed-tools list and recall/store
memory directly; may not perform PC control or destructive actions without
Executive Layer coordination and permission validation.
Inputs: user utterance, `AgentContext` (conversation history, memory
context, active tasks).
Outputs: structured response content (never final user-facing text).
Communication Contract: `agent.run.started` / `agent.run.completed`
events, per V1_TECHNICAL_SPECIFICATION.md Section 7.
Dependencies: Memory API, Tool Registry, Conversation Engine capability,
Personality Engine.

**Reasoning Agent**
Purpose: handles complex, multi-step analytical tasks that do not belong
to a narrower domain agent.
Responsibilities: work through open-ended problems requiring extended
chain-of-thought; validate the logical soundness of plans or arguments
produced elsewhere in the system.
Authority: may request additional context from the Memory API and consult
other agents' outputs; may not take real-world action directly.
Inputs: a defined problem statement plus relevant context.
Outputs: structured reasoning traces and conclusions.
Communication Contract: reports results to the Executive Intelligence
Layer's Result Merger.
Dependencies: Reasoning Engine capability, Memory API.

**Planning Agent**
Purpose: decomposes high-level goals into ordered, dependency-aware task
graphs.
Responsibilities: identify subtasks, sequence dependencies, flag parallel-
izable work, revise plans when execution conditions change.
Authority: may create and modify task graphs; may not execute tasks
directly (execution belongs to the Task Agent and domain agents).
Inputs: a Goal object from the Executive Layer's Intent Parser.
Outputs: a Task Graph.
Communication Contract: hands the Task Graph to the Executive Layer's
Engine/Agent Selector.
Dependencies: Planning Engine capability, Memory API (for prior-plan
precedent).

**Memory Agent**
Purpose: the active cognitive process responsible for memory quality,
distinct from the passive `MemoryAPI` storage interface every agent uses
directly.
Responsibilities: run consolidation passes; audit for contradictory or
stale memories; synthesize answers to "what do you know about X" queries
spanning many individual memories; execute the importance-decay and
pruning strategy.
Authority: may write consolidated summaries and flag memories for review;
may not delete a memory without the audit trail required by ADR-010
Section 3.
Inputs: session transcripts, existing memory records.
Outputs: consolidated memories, quality audit reports.
Communication Contract: `memory.consolidation.completed` events.
Dependencies: Memory Consolidation Engine capability, Memory API.

**Learning Agent**
Purpose: observes usage patterns over time and proposes adjustments,
without ever acting on an inferred pattern unilaterally.
Responsibilities: identify recurring behaviors worth surfacing (a
consistently rejected suggestion, a repeated manual workaround); propose —
never silently apply — adjustments to preferences or workflows.
Authority: may propose; may never change a Preference Memory or workflow
without explicit user confirmation, given the trust implications of a
system that acts on inferred rather than stated intent.
Inputs: long-term interaction history via the Memory Agent.
Outputs: proposed adjustments, surfaced to the user through the Executive
Layer and Personality Engine.
Communication Contract: `learning.proposal.created` events, never a direct
state change.
Dependencies: Memory Agent, Memory API.

**Decision Agent**
Purpose: resolves low-stakes, clear-cut choices autonomously so the system
does not interrupt the user with trivial questions.
Responsibilities: choose between near-equivalent valid options (a file
name convention, a minor formatting choice) using established preference
memory and precedent.
Authority: bounded to decisions with no meaningful downside; any decision
with a real cost of being wrong escalates to the user via the Executive
Layer instead.
Inputs: a bounded decision request with its candidate options.
Outputs: the selected option plus a brief rationale, logged for audit.
Communication Contract: reports the decision and rationale to whichever
agent requested it.
Dependencies: Preference Memory, Memory API.

---

### GROUP B — DOMAIN EXECUTION AGENTS

**Coding Agent**
Purpose: generates, reviews, refactors, and debugs code.
Responsibilities: implement described tasks; explain generated code;
delegate to language/domain specialists (Section 8) as needed.
Authority: may read/write files within the active project workspace; may
not push to a remote repository or perform destructive git operations
without the ADR-010 Level 5 override process.
Inputs: task description, relevant code context from the Context Manager.
Outputs: code diffs, patches, and explanations.
Communication Contract: hands output to the Code Review Agent (Group D)
before it is considered complete.
Dependencies: Coding Engine capability, sub-agent specialists (Section 8),
File System Agent, Code Review Agent.

**Research Agent**
Purpose: conducts higher-level, multi-source research and synthesizes
findings.
Responsibilities: formulate a research strategy; delegate actual page
navigation to the Browser Agent; cross-reference and validate information;
flag conflicts between sources.
Authority: may direct the Browser Agent's navigation; may not act on
research findings (e.g., submit a form) without explicit escalation.
Inputs: a research goal or question.
Outputs: a structured, synthesized summary with sourcing.
Communication Contract: stores findings to memory automatically via the
Memory API.
Dependencies: Browser Agent, Reasoning Engine capability, Memory API.

**Browser Agent**
Purpose: executes the mechanics of web automation — navigation, clicking,
typing, extraction.
Responsibilities: carry out browser actions requested by the Research
Agent, Automation Agent, or Executive Layer; run inside the sandboxed
browser process defined in V1_FOUNDATION_ARCHITECTURE.md Section 3.6.
Authority: confined entirely to its sandboxed container; no access to
memory databases or conversation history, per the security isolation
already specified in that document.
Inputs: navigation and interaction instructions.
Outputs: page content, screenshots, extracted structured data.
Communication Contract: a REST API boundary to the rest of Aether, exactly
as specified in V1_TECHNICAL_SPECIFICATION.md Section 6.3.
Dependencies: Browser Automation Engine capability.

**Vision Agent**
Purpose: interprets screen content and images.
Responsibilities: analyze screenshots; describe UI state; identify
actionable elements for PC Control Agent to interact with.
Authority: read-only with respect to what it observes; does not itself
take action on what it sees.
Inputs: captured screen regions or images.
Outputs: structured descriptions of visual content and detected elements.
Communication Contract: reports to the Executive Layer or the requesting
agent (commonly PC Control Agent).
Dependencies: Vision Engine capability, OCR Engine capability (via OCR
delegation for pure text extraction).

**Voice Agent**
Purpose: the logical interface to Aether's speech pipeline.
Responsibilities: coordinate speech recognition and speech synthesis
requests with the underlying voice pipeline.
Authority: manages voice I/O only; carries no conversational reasoning of
its own.
Inputs: audio for transcription; text for synthesis.
Outputs: transcripts; synthesized audio.
Communication Contract: identical to the process-separated voice service
already defined in V1_TECHNICAL_SPECIFICATION.md Section 9 — this agent is
the logical face of that physically separate process, which remains
separate for the same GIL-related technical reasons already documented
there.
Dependencies: Speech Recognition Engine capability, Speech Synthesis Engine
capability.

**Automation Agent**
Purpose: executes pre-defined, repeatable automation sequences —
scheduled or triggered, as opposed to ad hoc reasoning.
Responsibilities: run automations such as a recurring morning briefing
assembly, a scheduled file cleanup, or a triggered notification sequence.
Authority: confined to the specific automation definition it is executing;
any automation touching a destructive or Level 4/5 operation requires the
ADR-010 override process regardless of how routine the automation appears.
Inputs: an automation definition and its trigger condition.
Outputs: the automation's defined side effects, logged in full.
Communication Contract: emits a completion event per automation run.
Dependencies: Runtime Scheduler, relevant domain agents (File System, PC
Control, Notification Manager) depending on the automation's content.

**Email Agent**
Purpose: reads, drafts, and sends email (future capability, architecture
reserved now).
Responsibilities: triage inbox content; draft responses for review;
send only with explicit confirmation.
Authority: drafting is unrestricted; sending is always a confirmed action,
never autonomous, given the irreversibility of sent email.
Inputs: inbox content, drafting requests.
Outputs: drafts, sent confirmations.
Communication Contract: routes all outbound sends through a confirmation
gate before the action executes.
Dependencies: Conversation Engine capability (for drafting), external
email integration (future).

**File System Agent**
Purpose: file operations specifically — reading, writing, searching,
organizing.
Responsibilities: execute file operations validated against
`.aether/permissions.yaml`; maintain an audit trail of every operation.
Authority: bound entirely by the permission system in ADR-010; destructive
operations (delete, overwrite) always require the confirmation gate.
Inputs: file operation requests.
Outputs: operation results, audit log entries.
Communication Contract: every operation logged to the `tool_executions`
table, per V1_TECHNICAL_SPECIFICATION.md Section 3.2.
Dependencies: `SafetyValidator` (permission system), PC Control Agent for
broader OS context.

**PC Control Agent**
Purpose: lower-level system interaction — launching applications, managing
windows, adjusting system settings. Distinct from File System Agent's
narrower file-operation scope.
Responsibilities: application lifecycle control; system-level actions
within the allowlist defined in `.aether/permissions.yaml`.
Authority: bound entirely by the permission system; forbidden applications
and operations (per the permissions schema) are never executed regardless
of instruction framing.
Inputs: application and system control requests.
Outputs: operation results.
Communication Contract: every action logged to the audit trail; destructive
or ambiguous actions escalate through the confirmation gate.
Dependencies: `SafetyValidator`, Vision Agent (for locating on-screen
targets when needed).

**Calendar Agent**
Purpose: calendar read, write, and scheduling.
Responsibilities: check availability, create and modify events, surface
upcoming commitments to the Session Manager's morning briefing.
Authority: may create tentative events; confirmed, user-facing calendar
commitments require confirmation before finalizing.
Inputs: scheduling requests, calendar queries.
Outputs: event confirmations, availability summaries.
Communication Contract: feeds the Context Manager's active-tasks context.
Dependencies: external calendar integration (future), Memory API.

**Reminder Agent**
Purpose: time-based reminder creation and triggering.
Responsibilities: schedule reminders; trigger notifications at the
appropriate time via the Notification Manager.
Authority: may create and fire reminders autonomously once set by the
user; cannot invent new reminders unprompted.
Inputs: reminder creation requests, the system clock.
Outputs: triggered notifications at the scheduled time.
Communication Contract: hands off to the Notification Manager at trigger
time.
Dependencies: Runtime Scheduler, Notification Manager.

**Knowledge Agent**
Purpose: manages ingested external reference material — documents,
articles, manuals — distinct from the Memory Agent's focus on personal and
episodic memory.
Responsibilities: ingest, chunk, and index external documents; answer
queries against the knowledge base.
Authority: read/write to the Knowledge Store tier of memory (Phase 3+ per
the original Master Blueprint Section 6.1); does not modify personal
memory.
Inputs: documents to ingest, knowledge queries.
Outputs: indexed content, retrieval results.
Communication Contract: uses the same `MemoryAPI` boundary, with a distinct
namespace for ingested knowledge versus personal memory.
Dependencies: Embedding Engine capability, Reranking Engine capability,
Memory API.

**Workflow Agent**
Purpose: orchestrates multi-step, multi-agent workflows — chaining several
agents together to fulfill a compound request (e.g., "research this, then
summarize it, then email the summary").
Responsibilities: sequence agent hand-offs for a defined workflow pattern;
track workflow-level progress distinct from any single agent's task.
Authority: coordinates agents already authorized individually; does not
grant any agent authority it would not otherwise have.
Inputs: a workflow definition or an Executive Layer decomposition spanning
multiple agents.
Outputs: the workflow's end-to-end result.
Communication Contract: reports intermediate and final workflow state to
the Executive Layer's Execution Monitor.
Dependencies: every agent participating in a given workflow; Runtime
Scheduler.

**Task Agent**
Purpose: manages the discrete to-do item domain — creating, tracking, and
updating individual tasks; the direct evolution of Phase 1's `TaskManager`.
Responsibilities: task CRUD, status transitions, active-task summaries for
the morning briefing.
Authority: full authority over task records themselves; no authority over
the work a task represents.
Inputs: task creation, update, and query requests.
Outputs: task records, active-task summaries.
Communication Contract: `task.lifecycle.*` events, exactly as already
defined in V1_TECHNICAL_SPECIFICATION.md Section 7.3.
Dependencies: Memory API, `TaskManager` (already implemented in Phase 1).

---

### GROUP C — SYSTEM & INFRASTRUCTURE AGENTS

**Security Agent**
Purpose: cross-cutting enforcement of the permission system and detection
of anomalous behavior.
Responsibilities: validate every privileged action against
`.aether/permissions.yaml`; monitor for patterns consistent with prompt
injection or permission-boundary probing.
Authority: may block any action that fails validation; cannot itself be
overridden by any other agent, including the Executive Layer, without the
full ADR-010 Level 5 process.
Inputs: every privileged action request system-wide.
Outputs: allow/deny decisions, audit log entries, anomaly flags.
Communication Contract: a mandatory pre-execution check, not an optional
consultation.
Dependencies: `SafetyValidator`, the full permission schema.

**Health Monitor Agent**
Purpose: monitors the operational health of Aether's own infrastructure.
Responsibilities: track Redis/Qdrant/service availability, resource usage,
and error rates.
Authority: read-only observation; escalates but does not itself remediate.
Inputs: service health endpoints, system metrics.
Outputs: health status reports, escalation events on degradation.
Communication Contract: `system.health.degraded` events, per
V1_TECHNICAL_SPECIFICATION.md Section 7.3.
Dependencies: Observability Agent, Infrastructure Agent.

**GPU Resource Manager**
Purpose: tracks VRAM allocation across all resident engines and advises
the Runtime Scheduler on warm-pool decisions.
Responsibilities: maintain a live account of VRAM committed versus
available; flag when a requested engine cannot fit without eviction.
Authority: advisory to the Scheduler; the Scheduler makes the final
dispatch decision using this agent's data.
Inputs: engine load/unload requests, current VRAM usage.
Outputs: fit/no-fit determinations, eviction candidates.
Communication Contract: consulted synchronously by the Runtime Scheduler
before any GPU-bound dispatch.
Dependencies: Runtime Scheduler.

**Runtime Scheduler** *(agent-facing interface to Section 5)*
Purpose: the agent-facing entry point through which every other agent
submits jobs to the scheduling system described in full in Section 5.
Responsibilities: queue management, priority enforcement, interrupt
handling, cancellation, resource-aware dispatch.
Authority: full authority over job ordering and engine dispatch; no
authority over what work exists to be scheduled.
Inputs: job submissions from every other agent.
Outputs: dispatch decisions, pause/resume/cancel signals.
Communication Contract: every agent submits work through the same
submission contract regardless of job type.
Dependencies: GPU Resource Manager, Capability Registry (Section 9).

**Context Manager**
Purpose: assembles and maintains the `AgentContext` for any given task —
the generalized form of Phase 1's `SessionStartupBuilder`.
Responsibilities: pull together conversation history, active tasks,
memory context, and system state into the immutable context snapshot each
engine operates against (Section 11.5).
Authority: read access across memory, tasks, and session state; produces
context, does not modify underlying state.
Inputs: a request for context assembly, scoped to a task or session.
Outputs: an `AgentContext` object.
Communication Contract: called by the Executive Layer before dispatching
any job.
Dependencies: Memory API, Session Manager, Task Agent.

**Tool Manager** *(agent-facing interface to the `ToolRegistry`)*
Purpose: manages tool registration, discovery, and permission checks — the
agent-facing framing of Phase 1's `ToolRegistry`.
Responsibilities: register new tools; produce function-calling schemas for
requesting agents; enforce per-tool permission requirements.
Authority: gatekeeps all tool invocation; no agent calls a tool
implementation directly, per the boundary already locked in
ARCHITECTURE_RULES.md.
Inputs: tool registration and invocation requests.
Outputs: tool results, function schemas.
Communication Contract: identical to the existing `ToolRegistry` public
API.
Dependencies: `SafetyValidator`.

**Session Manager**
Purpose: session lifecycle management — directly Phase 1's already-
implemented `SessionManager`, unchanged in role.
Responsibilities: session start/end, context caching, morning briefing
assembly, consolidation triggering.
Authority: as already defined in V1_TECHNICAL_SPECIFICATION.md Section 2.8.
Inputs: session start/end requests.
Outputs: `Session` and `SessionContext` objects.
Communication Contract: `session.lifecycle.*` events.
Dependencies: Context Manager, Memory Agent (for consolidation).

**Notification Manager**
Purpose: manages outbound notifications and alerts to the user.
Responsibilities: desktop notifications now; mobile push in later phases,
per the original Master Blueprint Phase 7.
Authority: may surface a notification; may not interrupt an active
conversation to do so (per Section 4.1's non-interruption rule) — non-
urgent notifications queue until the conversation is idle.
Inputs: notification requests from any agent.
Outputs: delivered notifications.
Communication Contract: respects the Runtime Scheduler's priority rules
for interruption.
Dependencies: Runtime Scheduler.

**Plugin Manager**
Purpose: manages the future third-party tool and skill plugin ecosystem,
per the Tool Plugin Marketplace concept in the original Master Blueprint
Section 10.4.
Responsibilities: discover, validate, and sandbox third-party tool
packages before registering them with the Tool Manager.
Authority: may register a validated plugin; may never register a plugin
that fails the `BaseTool` interface contract or requests permissions
outside the sandbox.
Inputs: plugin packages.
Outputs: registered tools, validation reports.
Communication Contract: hands validated tools to the Tool Manager for
registration.
Dependencies: Tool Manager, Security Agent.

**Infrastructure Agent**
Purpose: manages Docker infrastructure services and the operational
scripts already established in Phase 1 (`start.ps1`, `stop.ps1`,
`health_check.ps1`).
Responsibilities: service lifecycle management, health verification before
declaring readiness.
Authority: may start and stop infrastructure services; destructive
operations (volume removal) are permanently forbidden per ADR-010 Section
3.4.
Inputs: start/stop/health-check requests.
Outputs: service status.
Communication Contract: reports to Health Monitor Agent.
Dependencies: Docker Compose infrastructure.

**Deployment Agent**
Purpose: manages release and deployment processes (currently manual, per
ADR-010's git tag strategy; formalized here for future automation).
Responsibilities: coordinate the Release Candidate and Phase Closure
workflows already defined in AETHER_PHASE_EXECUTION_WORKFLOW.md Steps
19–26.
Authority: prepares releases; the GO/NO-GO decision itself remains the
developer's sole authority, per that document's Section 4.3.
Inputs: release readiness signals.
Outputs: tagged releases.
Communication Contract: integrates with the Phase Execution Workflow
directly.
Dependencies: Git repository, Phase Execution Workflow.

**Observability Agent**
Purpose: aggregates logs, metrics, and traces, surfacing system health
insight.
Responsibilities: structured log aggregation (structlog-based, per
ADR-011 Section 3.5), performance baseline tracking (ADR-011 Section 10).
Authority: read-only aggregation and reporting.
Inputs: logs and metrics from every subsystem.
Outputs: dashboards, alerts, baseline reports.
Communication Contract: feeds the Health Monitor Agent and the phase-level
Performance Review (AETHER_PHASE_EXECUTION_WORKFLOW.md Step 11).
Dependencies: structlog infrastructure, Health Monitor Agent.

---

### GROUP D — DEVELOPMENT & QUALITY AGENTS

*These agents participate in Aether building and reviewing itself — the
AI-assisted development loop already governed by AI_GENERATION_RULES_V2.md
and ADR-011.*

**Quality Assurance Agent**
Purpose: reviews user-facing outputs across the system for quality issues
before they reach the Personality Engine — distinct from Code Review
Agent's coding-specific scope.
Responsibilities: cross-cutting output review for coherence, accuracy, and
tone consistency.
Authority: may flag or hold an output for revision; cannot itself rewrite
the underlying content.
Inputs: draft outputs from any content-generating agent.
Outputs: pass/flag determinations.
Communication Contract: sits between Content Generation and the
Personality Engine (Section 2.3) as an optional quality gate for
high-stakes outputs.
Dependencies: Reasoning Engine capability.

**Testing Agent**
Purpose: writes and runs tests for Aether's own codebase — part of the
AI-assisted development pipeline, not a user-facing capability.
Responsibilities: generate unit, integration, and contract tests per
ADR-011 Section 3.4's requirements.
Authority: writes tests; cannot mark a milestone's Testing Done level
(AETHER_DEFINITION_OF_DONE.md Level 4) complete — that remains a human/
Claude-reviewed determination.
Inputs: implementation code requiring test coverage.
Outputs: test files.
Communication Contract: integrates with the Testing Workflow defined in
AETHER_PHASE_EXECUTION_WORKFLOW.md Step 12.
Dependencies: Coding Engine capability.

**Documentation Agent**
Purpose: writes and maintains Aether's own documentation — again, about
the development process, not user-facing content.
Responsibilities: docstrings, ADRs, specification synchronization per
ADR-011 Section 3.6.
Authority: drafts documentation; documentation changes affecting
Constitutional documents still follow the amendment process in ADR-010
Section 16.4.
Inputs: implementation changes requiring documentation.
Outputs: documentation drafts.
Communication Contract: integrates with the Documentation Updates workflow
step (AETHER_PHASE_EXECUTION_WORKFLOW.md Step 15).
Dependencies: Conversation Engine or Reasoning Engine capability.

**Architecture Compliance Agent**
Purpose: enforces `ARCHITECTURE_RULES.md` boundaries — an agent-formalized
counterpart to the automated `lint-imports` check.
Responsibilities: continuous boundary verification across the codebase.
Authority: may flag a violation; cannot itself resolve one.
Inputs: the current state of the codebase.
Outputs: violation reports.
Communication Contract: feeds the Architecture Compliance Review
(AETHER_PHASE_EXECUTION_WORKFLOW.md Step 9; AETHER_DEFINITION_OF_DONE.md
Level 3).
Dependencies: `lint-imports`, `mypy --strict`.

**Code Review Agent**
Purpose: reviews Aether's own generated code, working alongside the
Human Review and Claude Review workflows already established.
Responsibilities: a first-pass automated review against ADR-011's Zero-
Tolerance Violations and forbidden patterns before human/Claude review
begins.
Authority: may flag issues; final review authority remains with the
Human Review Workflow and Claude Review Workflow (AETHER_PHASE_EXECUTION_
WORKFLOW.md Steps 7–8).
Inputs: generated code changes.
Outputs: a pre-review flag report.
Communication Contract: precedes, never replaces, Steps 7–8 of the Phase
Execution Workflow.
Dependencies: Coding Engine capability, Architecture Compliance Agent.

---

### GROUP E — FUTURE EXPANSION AGENTS

*Stub definitions, following the extensibility pattern already established
in the original Master Blueprint's Future Expansion Strategy (Section 10).
Each becomes fully specified when its corresponding phase begins.*

**Future Robotics Agent** — Purpose: bridges Aether's Executor-level
capabilities to physical actuators via a Robotics Integration Service, per
the original Master Blueprint Section 10.3. Authority, inputs, outputs,
and dependencies are defined at the time this phase is initiated,
following AETHER_PHASE_EXECUTION_WORKFLOW.md Step 2.

**Future Mobile Agent** — Purpose: cross-device synchronization and
mobile-native interaction, corresponding to the original Master Blueprint
Phase 7.

**Future AR Agent** — Purpose: spatial rendering adapter for augmented-
reality interfaces, corresponding to the original Master Blueprint Phase
10's spatial rendering concept.

**Future VR Agent** — Purpose: fully immersive spatial interaction,
sharing the same rendering-adapter pattern as the AR Agent — "the same
WebSocket stream from aether-core that the overlay uses," per the original
Master Blueprint Section 10.2.

**Future IoT Agent** — Purpose: extends Aether's environmental awareness
and control to networked physical devices, an extension of the tool pool
described in the original Master Blueprint Section 10.4, requiring no
architectural change to accommodate.

---

## 8. SUB-AGENT ARCHITECTURE

Sub-agent specialization is warranted where a domain has genuinely
distinct internal skill areas that benefit from separate context, tuning,
or engine assignment. Not every agent needs this — most system and
infrastructure agents (Group C) have no natural sub-specialization. The
following major agents do.

### 8.1 Coding Agent

```
Coding Agent
  ├── Python Specialist
  ├── TypeScript Specialist
  ├── Rust Specialist
  ├── Go Specialist
  ├── SQL Specialist
  ├── Frontend Specialist
  ├── Backend Specialist
  ├── API Specialist
  ├── Testing Specialist
  ├── Refactoring Specialist
  ├── Architecture Review Specialist
  ├── Security Review Specialist
  ├── Performance Specialist
  └── Documentation Specialist
```

Each specialist receives the same Coding Engine capability assignment
(Section 9) but with a narrower, domain-tuned context and prompt profile —
the specialization is in framing and context assembly, not necessarily in
a different underlying model, though the architecture permits assigning a
distinct engine per specialist where warranted.

### 8.2 Research Agent

```
Research Agent
  ├── Academic Research Specialist
  ├── Market Research Specialist
  ├── Technical Documentation Specialist
  ├── Fact-Verification Specialist
  └── Source-Credibility Specialist
```

### 8.3 Browser / Automation Agent

```
Browser Agent
  ├── Form-Filling Specialist
  ├── Data-Extraction Specialist
  ├── Multi-Step Workflow Specialist
  └── Authentication-Flow Specialist
        (legitimate authentication only — never credential bypass,
         per ADR-010's forbidden operations catalog)
```

### 8.4 Security Agent

```
Security Agent
  ├── Permission-Validation Specialist
  ├── Threat-Detection Specialist
  ├── Prompt-Injection-Defense Specialist
  └── Audit-Trail Specialist
```

### 8.5 Vision Agent

```
Vision Agent
  ├── UI-Element-Detection Specialist
  ├── OCR-Text-Extraction Specialist
      (delegates to the OCR Engine capability directly)
  ├── Screen-Change-Detection Specialist
  └── Document-Layout Specialist
```

### 8.6 The General Rule

A parent agent spawns a sub-agent specialist when, and only when, the
domain's internal variety is large enough that a single undifferentiated
prompt profile would meaningfully underperform a specialized one. The
Executive Intelligence Layer's Engine/Agent Selector (Section 6.2) is
responsible for routing to the correct specialist based on task
classification; the parent agent remains the single point of authority
and accountability for its domain.

---

## 9. CAPABILITY-BASED ENGINE ASSIGNMENT

### 9.1 The Principle

No agent, no architectural component, and no piece of this Constitution
references a model name directly — the same rule already codified as
ADR-011 Zero-Tolerance Violation ZT-10, generalized here from Phase 1's
four generic quality tiers to a full set of named capabilities. Every
engine is accessed exclusively through its **Capability Interface**: a
defined input contract, a defined output contract, and a registry entry
mapping the capability to its current implementing engine.

### 9.2 The Capability Registry

```
Capability                    →  Currently Assigned Engine (Section 10)
────────────────────────────────────────────────────────────
Conversation Engine           →  (see Section 10)
Reasoning Engine              →  (see Section 10)
Coding Engine                 →  (see Section 10)
Planning Engine                →  (see Section 10)
Vision Engine                  →  (see Section 10)
Embedding Engine                →  (see Section 10)
Reranking Engine                 →  (see Section 10)
OCR Engine                        →  (see Section 10)
Speech Recognition Engine          →  (see Section 10)
Speech Synthesis Engine             →  (see Section 10)
Translation Engine                   →  (reserved — no current assignment)
Summarization Engine                  →  (reserved — no current assignment)
Future Aether Foundation Models        →  (Section 14)
```

This registry is the direct architectural descendant of `LLMRouter.
get_available_models()`, already implemented in Phase 1
(V1_TECHNICAL_SPECIFICATION.md Section 2.4). Resolving a `ModelTier` to a
model string via config is the same operation, at smaller scale, as
resolving a named Capability to an engine via this registry.

### 9.3 Replaceability Is Structural, Not a Promise

Because every consumer of a capability interacts only with the interface —
never the underlying engine — replacing an engine is a registry change,
not an architecture change. This is not a design goal to be maintained by
discipline; it is enforced the same way Phase 1 enforces the LLM Router
boundary: by import-linter contracts and code review, per ADR-011 Section
2, ZT-10, and ADR-010 Section 10.

### 9.4 Governance of Registry Changes

Any change to the Section 10 mapping — including the eventual introduction
of an Aether Foundation Model per Section 14 — follows the Dependency
Governance process in ADR-010 Section 11, and where it constitutes a
genuine architectural decision per ADR-010 Section 10.2, requires an
approved ADR before implementation. This document's Section 10 is
authoritative for the *current* mapping; it is not itself the mechanism by
which that mapping changes.

---

## 10. CURRENT APPROVED RUNTIME MAPPING

This section maps the runtime stack already selected by the project owner
to the capability interfaces defined in Section 9. **This mapping is not
open for redesign here.** What follows is the architectural rationale for
why each assignment fits its capability, not a recommendation exercise.

| Capability | Assigned Engine | Why This Assignment Fits |
|---|---|---|
| **Coding Engine** | NVIDIA Nemotron Ultra 3 | A model class oriented toward code generation and structural reasoning about codebases — the right profile for the Coding Agent's sustained, multi-file work. |
| **Conversation Engine** | Kimi K2 Instruct | Strong, fluent instruction-following dialogue — the appropriate "raw material" layer for content the Personality Engine subsequently renders into Aether's voice. |
| **Reasoning Engine** | DeepSeek R1 | A reasoning-specialized model well suited to the extended, multi-step chain-of-thought work the Reasoning Agent performs. |
| **Planning Engine** | DeepSeek R1 | Planning and reasoning draw on the same underlying cognitive skill — multi-step logical decomposition — so sharing one engine across both capabilities is both architecturally coherent and resource-efficient under the VRAM constraints in Section 13. |
| **Memory Consolidation Engine** | Qwen3 14B Instruct | Consolidation needs reliable summarization and fact-extraction, not frontier-scale reasoning depth — a capable mid-sized instruction model is the right weight class for this high-frequency, moderate-complexity task. |
| **Tool Calling Engine** | Qwen3 8B Instruct | Tool-call interpretation is high-frequency and latency-sensitive; a smaller, fast model is the correct trade-off, prioritizing speed over depth for this narrow task. |
| **Browser Automation Engine** | Qwen3 Coder | Interpreting DOM structure and generating action sequences benefits from the same structured, code-like reasoning a coder-tuned model provides. |
| **Vision Engine** | Qwen2.5-VL | A vision-language model appropriate for screen and image understanding tasks the Vision Agent performs. |
| **OCR Engine** | PaddleOCR | A dedicated, lightweight, purpose-built OCR engine outperforms a general vision-language model on pure text-extraction speed and accuracy — the right tool for a narrow, well-solved problem. |
| **Embedding Engine** | BGE-M3 | A strong general-purpose multilingual embedding model, consistent with the embedding role already established in Phase 1's memory system. |
| **Reranking Engine** | BGE Reranker v2 | Pairs naturally with BGE-M3 in the two-stage retrieve-then-rerank pattern already specified in V1_TECHNICAL_SPECIFICATION.md Section 2.5 (`HybridRetrieval`). |
| **Speech Recognition Engine** | Architecture Only | The capability slot is reserved and model-agnostic at this architectural layer; Phase 1's concrete implementation (`faster-whisper`, per V1_TECHNICAL_SPECIFICATION.md Section 9.3) already fills it operationally without being locked in here. |
| **Speech Synthesis Engine** | Architecture Only | Reserved identically; Phase 1's concrete implementation (Kokoro TTS) already fills it operationally without being locked in here. |

### 10.1 How Engines Communicate

Engines never communicate directly with one another. All coordination
flows through the Executive Intelligence Layer's task assignment (Section
6); where one engine's output becomes another's input, that hand-off is a
structured artifact passed through the Executive Layer or written to
shared memory — never a direct engine-to-engine call. This avoids tight
coupling between engine implementations and keeps every engine
independently replaceable.

### 10.2 How Engines Synchronize Memory

Every engine's agent reads and writes through the single `MemoryAPI`
(Section 3.1). There is no engine-local memory to synchronize because
there is only one memory system.

### 10.3 How Engines Execute Concurrently

Through the Runtime Scheduler (Section 5), which allocates CPU, GPU, and
queue priority across every simultaneously active engine.

### 10.4 How Capability Interfaces Isolate Implementation Details

The registry table above is itself the isolation boundary. Nothing above
this layer — no agent, no Executive Layer logic, no Personality Engine
rule — knows or depends on the fact that Coding Engine is currently
Nemotron Ultra 3 rather than some future Aether Foundation Model. That
knowledge exists only here, in Section 10, and in the configuration that
implements it.

---

## 11. CONTEXT SYNCHRONIZATION

### 11.1 The Problem

Multiple engines may be active simultaneously — on entirely different
goals (Section 4) or on parts of the same goal (Section 12). Without
discipline, this creates the classic distributed-systems hazards: race
conditions on shared state, conflicting outputs reaching the user, and
divergent views of what is currently true.

### 11.2 Single Source of Truth

The `MemoryAPI` and the `SessionManager`'s `SessionContext` are the only
authoritative stores in the system. No engine, and no agent, maintains
private state that is permitted to diverge from these. This is not new —
it is Phase 1's existing memory boundary, held without exception as
concurrency increases.

### 11.3 Event-Driven Propagation

Any state change — a new memory, a task status change, a plan revision —
is emitted on the existing Redis Streams event bus
(V1_TECHNICAL_SPECIFICATION.md Section 5). Concurrently active engines
that care about a given state change subscribe to the relevant event type
rather than polling for changes, reusing infrastructure Phase 1 already
built rather than introducing a second synchronization mechanism.

### 11.4 The Executive Layer as Sole Arbiter

When two engines produce potentially conflicting outputs for the same
goal — two different proposed plans, two different code approaches — the
Executive Intelligence Layer's Result Merger (Section 6.2) is the single
arbitration point. Engines never negotiate or resolve conflicts among
themselves; this keeps engines simple, stateless with respect to each
other, and fully replaceable without needing to understand any other
engine's behavior.

### 11.5 Immutable Context Snapshots

The `AgentContext` object passed to any engine is an immutable snapshot —
already `frozen=True` in Phase 1's implementation — taken at task-
assignment time. If the world changes while an engine is working, it does
not see a torn or partial update. It either completes against the
snapshot it was given, or the Executive Layer explicitly re-issues the
task with a freshly assembled context. This eliminates an entire class of
concurrency bugs by construction rather than by careful locking.

### 11.6 Conversation Write Exclusivity

The live conversation transcript has a single writer at a time — the
Conversation Agent, mediated by the Executive Layer. Background agents may
read conversation context freely but never append directly to the live
transcript. If a background agent has something to surface mid-
conversation, it does so as a proposed interjection or a queued
notification (Section 7, Notification Manager), and the Executive Layer
decides whether and when to surface it — preserving both of Section 4.1's
non-interruption rules simultaneously.

---

## 12. COLLECTIVE INTELLIGENCE

### 12.1 The Principle

Aether is not powered by one model answering every question alone. It is
powered by a coordinated intelligence network in which the Executive
Intelligence Layer may assign a single task to multiple engines
simultaneously, and combine their outputs into one result — entirely
invisible to the user, who experiences only Aether.

```
        Coding Engine
              │
        Reasoning Engine  ──┐
              │              │
        Memory Engine        ├──▶  Result Merger  ──▶  Collaborative
              │              │      (Section 6.2)         Result
        Planning Engine  ────┘
```

### 12.2 Collaboration Patterns

**Parallel Consultation** — the Executive Layer sends the same or a
related sub-problem to multiple engines, collects their outputs, and
either has one engine (commonly the Reasoning Engine) synthesize between
them, or merges directly if the outputs are complementary rather than
competing.

**Sequential Pipeline** — one engine's output becomes another's input: the
Planning Engine produces a task graph, the Coding Engine implements each
node, the Reasoning Engine reviews the implementation against the original
plan.

**Critique-and-Refine Loop** — one engine produces a draft; a second,
different engine critiques it, deliberately avoiding the "grading its own
homework" failure mode; the first engine or the Executive Layer
incorporates the critique. This is the same pattern already at work in
Group D's Code Review Agent reviewing the Coding Agent's output, and in
the Quality Assurance Agent reviewing draft content before it reaches the
Personality Engine.

### 12.3 Invisibility Is Mandatory

The user never sees "the Coding Engine proposed X, the Reasoning Engine
flagged a problem, here is the resolution." They see one coherent Aether
response. This is not merely good UX — it is the direct, load-bearing
consequence of Section 2's rule that no engine speaks to the user
directly. Collective Intelligence is precisely why that rule cannot be
relaxed: as the number of engines contributing to any single answer grows,
the Personality Engine's role as the sole rendering gate is what keeps the
result experienced as one entity rather than a committee.

---

## 13. RESOURCE MANAGEMENT

### 13.1 Current Hardware

```
CPU:      Intel Core i7-13700HX
GPU:      NVIDIA RTX 4050 Laptop GPU — 6GB VRAM
RAM:      16GB DDR5
OS:       Windows 11
```

### 13.2 The Real Constraint

The approved runtime stack (Section 10) includes several genuinely large
local models — Nemotron Ultra 3, DeepSeek R1, Kimi K2 Instruct, and the
Qwen3 family — that cannot all be resident in 6GB of VRAM simultaneously.
This is not a hypothetical concern; it is the defining resource constraint
this section is designed around.

### 13.3 Engine Weight Classes

| Weight Class | Engines | Typical Residency Strategy |
|---|---|---|
| **Heavy** | Coding Engine (Nemotron Ultra 3), Reasoning/Planning Engine (DeepSeek R1), Conversation Engine (Kimi K2 Instruct) | One resident at a time in the warm pool (Section 5.7); swapped on demand |
| **Medium** | Memory Consolidation Engine (Qwen3 14B), Browser Automation Engine (Qwen3 Coder), Vision Engine (Qwen2.5-VL) | Loaded on demand, evicted aggressively when idle |
| **Light** | Tool Calling Engine (Qwen3 8B) | CPU-eligible or kept warm cheaply given frequent, low-latency use |
| **CPU-Native** | Embedding Engine (BGE-M3), Reranking Engine (BGE Reranker v2), OCR Engine (PaddleOCR) | Run on CPU by default, freeing VRAM entirely — consistent with the existing Phase 1 decision to run embeddings on CPU (V1_TECHNICAL_SPECIFICATION.md Section 2.4) |

### 13.4 The Degradation Ladder

When the ideal configuration cannot fit:
1. **Queue** the job if nothing is actively waiting on it.
2. **Substitute** a registered lighter-weight fallback for that capability,
   if one exists in the registry.
3. **Delay** non-urgent background work until resource pressure eases.
4. **Communicate honestly** — if none of the above resolves the situation
   quickly, the Personality Engine surfaces a brief, honest status message
   ("still working on that — give me a moment") rather than failing
   silently or blocking indefinitely.

This ladder never fails silently and never blocks the foreground
conversation without explanation.

### 13.5 Quantization as an Implementation Detail

Engines may run at whatever quantization level (Q4, Q8, full precision)
fits the current VRAM budget. This is an engine implementation detail
governed entirely within the engine's own deployment configuration — it
never surfaces as an architectural concern, consistent with the model-
agnostic principle running through this entire document.

---

## 14. FUTURE EVOLUTION

### 14.1 The Migration Guarantee

Because every engine sits behind a Capability Interface (Section 9) with a
fixed input/output contract, replacing "Coding Engine: Nemotron Ultra 3"
with "Coding Engine: Aether Foundation Model — Code" is a registry change,
not an architecture change — precisely analogous to how Phase 1's
`LLMRouter` can swap the `STANDARD` tier's underlying model via
configuration alone, with zero changes to any agent that consumes it.

### 14.2 The Shadow-Mode Migration Pattern

```
Step 1: REGISTER
  A candidate engine is registered as an alternate implementation
  for a capability, alongside the current production engine.

Step 2: SHADOW
  The candidate engine receives the same inputs as the production
  engine and produces outputs that are logged and compared — never
  surfaced to the user — until quality is validated.

Step 3: CUTOVER
  Once validated, the registry's primary mapping for that capability
  is switched to the candidate engine.

Step 4: RETIRE OR RETAIN
  The previous engine is either fully retired or kept registered as
  a fallback, per the Dependency Governance process in ADR-010
  Section 11.
```

This pattern is the actual operational mechanism by which model
replacement happens safely over the 5–10 year horizon this document is
written for — not a promise, but a defined procedure.

### 14.3 What Never Changes

The Personality Engine's contract. The Memory API boundary. The Executive
Intelligence Layer's coordination role. The Capability Registry pattern
itself. The Runtime Scheduler's priority discipline. These are the
permanent skeleton. Every engine behind them is temporary by design.

---

## 15. FUTURE INTELLIGENCE ROADMAP

```
Stage 1 — CURRENT LOCAL MULTI-MODEL RUNTIME  (Present)
  The approved runtime stack (Section 10) operates as discrete,
  capability-assigned engines under a maturing Executive Intelligence
  Layer. Corresponds to the original Master Blueprint Phases 1–4.
              │
              ▼
Stage 2 — ADVANCED MULTI-AGENT RUNTIME
  The full Runtime Scheduler (Section 5) and true concurrent execution
  (Section 4) come online; agents genuinely run in parallel with
  resource-aware scheduling. Corresponds to the original Master
  Blueprint Phase 5 (Multi-Agent Architecture).
              │
              ▼
Stage 3 — HYBRID COGNITIVE RUNTIME
  Local engines are supplemented, where explicitly opted into, by
  higher-capacity engines for capabilities that benefit from
  reasoning depth beyond what local hardware supports — always
  through the same Capability Interface (Section 9), never as a
  special case. Collective Intelligence patterns (Section 12) become
  routine rather than exceptional.
              │
              ▼
Stage 4 — INTERNALLY DEVELOPED SPECIALIST MODELS
  Aether begins training and fine-tuning its own specialist models,
  starting with the highest-value, highest-volume capability —
  likely Tool Calling or Conversation, given frequency of use —
  trained in part on Aether's own accumulated interaction history,
  with explicit user consent and privacy safeguards throughout.
              │
              ▼
Stage 5 — COMPLETE AETHER FOUNDATION MODEL ECOSYSTEM
  Every capability slot in the Section 9 registry is filled by an
  internally developed Aether Foundation Model. The external model
  stack from Section 10 becomes legacy, retained only as fallback
  per the shadow-mode migration pattern (Section 14.2).
              │
              ▼
Stage 6 — UNIFIED AETHER INTELLIGENCE
  The distinction between "capabilities" begins to blur as Aether
  Foundation Models are trained as a coordinated family rather than
  independently-sourced components. The architecture defined in this
  document — capability interfaces, Executive Layer, Personality
  Engine, Runtime Scheduler — remains the permanent skeleton. The
  engines behind it become a single coherent lineage rather than a
  coalition of external models.
```

---

## 16. GUIDING PRINCIPLES

> *"The user never speaks to a model.*
> *The user always speaks to Aether.*
>
> *Models are replaceable.*
> *Aether is permanent.*
>
> *One identity.*
> *One memory.*
> *One personality.*
> *Many specialized intelligences.*
> *One consciousness."*

---

## 17. COLLECTIVE INTELLIGENCE NETWORK

### 17.1 Relationship to Section 12

Section 12 already established the principle — Aether is a coordinated
network, not one model — and the three collaboration patterns (Parallel
Consultation, Sequential Pipeline, Critique-and-Refine Loop) by which
multiple engines contribute to a single result. This section does not
restate those patterns. It adds the layer Section 12 did not cover: the
**network topology** those patterns run on top of — how many engines can
participate in one operation, how that network is structured, and why its
shape is what guarantees Section 12.3's invisibility mandate rather than
merely asserting it as policy.

### 17.2 Topology: A Star, Not a Mesh

Every engine currently in a servable state (Section 20) is a potential
node. But nodes never connect to each other directly — Section 10.1
already established this ("Engines never communicate directly with one
another") and Section 11.4 already established the Executive Intelligence
Layer as the sole arbitration point for conflicting outputs. Read
together, these two existing rules describe a specific network shape: a
**star topology**, with the Executive Intelligence Layer as the single
hub every edge passes through.

```
   Conversation Engine ──┐
   Reasoning Engine ─────┤
   Memory Engine ────────┼──▶  Executive Intelligence Layer  ──▶  Personality Engine  ──▶  Unified Response
   Planning Engine ──────┘         (Section 6 — hub node)          (Section 2 — sole
                                                                      rendering gate)
```

### 17.3 Why This Topology Is What Makes One Personality Structural, Not Just Policy

Because every edge in this network routes through the hub, and the hub's
only path to the user is through the Personality Engine, there is no
network path by which any individual engine's raw output could reach the
user directly — not a missing safeguard that happens to be enforced by
discipline, but a topology in which the shortcut simply does not exist.
This is the concrete, structural argument for Section 2's rule and Section
12.3's invisibility mandate: they hold because of the shape of the graph,
not only because of a policy written down.

### 17.4 Scale Properties

A single collective operation is bounded by two independent constraints:
how many *distinct* capabilities the Task Decomposer (Section 6.2)
determines a goal genuinely requires, and how many of those capabilities'
engines can be simultaneously resident given the hardware constraints in
Section 13. When a goal wants to span more nodes than current hardware
supports, that is a Graceful Degradation scenario, addressed fully in
Section 23.

---

## 18. ENGINE COLLABORATION PROTOCOL

The Result Merger (Section 6.2) follows this exact eight-step sequence
whenever a goal is dispatched to more than one engine — that is, whenever
Section 17's network spans more than one node for a single operation. The
user never observes any of these eight steps; they observe only the
Unified Response Section 17.2 already diagrams. This protocol is the
mechanical implementation of Section 12.3's invisibility mandate, not an
addition to it.

**1. Task Delegation** — the Task Decomposer assigns each subtask to
exactly one engine, resolved through the Capability Registry (Section 19).
No engine is delegated work outside a capability it is registered against.

**2. Result Sharing** — each engine returns its structured output to the
Executive Intelligence Layer only, per Section 10.1's no-direct-
communication rule. Every result is tagged with the capability and engine
that produced it, for audit purposes only — this tag is never forwarded
to the user.

**3. Internal Validation** — before any result is merged, it is checked
against its own capability's declared output contract (Section 19's
schema). A result that does not match its declared shape is treated as a
failed delegation, not silently passed through to merging.

**4. Consensus** — when multiple engines were asked the same question
(Parallel Consultation, Section 12.2) rather than complementary pieces of
one answer, their results are compared. Substantive agreement reaches
consensus automatically and proceeds directly to merging.

**5. Conflict Resolution** — when engines disagree, Section 11.4's
existing rule applies concretely here: the Executive Layer is the sole
arbiter. It resolves the conflict via Result Ranking, not arbitrary
selection.

**6. Result Ranking** — candidate results are ranked by: internal
validation pass/fail (step 3) as a hard filter; the originating
capability's Priority Class (Section 19's schema field) as a base signal;
and, for genuinely ambiguous cases, referral to a designated tie-breaking
capability — Reasoning — consistent with Section 10's existing rationale
for why Reasoning and Planning already share one engine (DeepSeek R1):
multi-step arbitration is the same underlying skill as multi-step
decomposition.

**7. Retry** — a result failing Internal Validation, or an engine not
responding within its task's timeout, is retried according to
exception-type-based eligibility. This reuses, rather than reinvents, the
retry-eligibility table already established at the task level in
PHASE_2_TECHNICAL_SPECIFICATION.md Section 10.4, applied here to
individual engine contributions within a collective operation.

**8. Escalation** — if Consensus is not reached and Result Ranking cannot
produce a clear winner after retry, the Executive Layer does not guess.
For genuinely subjective or high-stakes cases, the ambiguity is surfaced
to the user honestly through the Personality Engine ("I see two ways to
approach this — which do you prefer?"). For low-stakes cases, resolution
is delegated to the Decision Agent (Section 7, Group A), whose authority
is already explicitly bounded to "decisions with no meaningful downside,"
with the decision logged for audit.

---

## 19. CAPABILITY REGISTRY

### 19.1 Relationship to Section 9

Section 9.2 introduced the Capability Registry as a simple two-column
mapping — capability name to currently assigned engine. This section
provides the full operational schema that mapping was always intended to
grow into, and in doing so, reconciles a gap between Section 9.2's
introductory list and Section 10's actual runtime mapping: Section 10
already assigns real engines to Memory Consolidation, Tool Calling, and
Browser Automation, none of which Section 9.2's abstract list separately
named. This registry is the single, complete, authoritative list —
including the Memory and Browser capabilities this appendix was asked to
add — consolidating what Sections 9 and 10 already established rather
than introducing a second, competing list.

### 19.2 The Schema

| Field | Purpose |
|---|---|
| Capability Name | Unique identifier, e.g. `"reasoning"` |
| Capability Description | Human-readable statement of what this capability does |
| Required Engine Type | The category of engine needed (e.g., "extended chain-of-thought reasoning") |
| Preferred Engine | The currently assigned engine, per Section 10 |
| Minimum Supported Engine | The lowest-capability engine that still fulfills this capability adequately |
| Fallback Engine | What serves this capability if the Preferred Engine is in a Failed or Unloading state (Section 20) |
| Parallel Execution Support | Boolean — whether multiple simultaneous requests can be served concurrently |
| Estimated Resource Cost | Low / Medium / High |
| Priority Class | INTERACTIVE / HIGH / NORMAL / LOW / IDLE — the exact scale already defined in Section 5.3 |
| Scheduling Requirements | Free-form notes on special scheduling constraints |

### 19.3 The Complete Registry

| Capability | Preferred Engine | Fallback Engine | Parallel | Cost | Priority | Scheduling Notes |
|---|---|---|---|---|---|---|
| Conversation | Kimi K2 Instruct | Reasoning capability (degraded fluency, retained coherence) | No (pre-Phase 5) | Medium | INTERACTIVE | Preempts every background capability request |
| Reasoning | DeepSeek R1 | Conversation capability (reduced depth) | Yes (Phase 5+) | High | NORMAL/HIGH | Also serves as Section 18's tie-breaking capability |
| Planning | DeepSeek R1 | Reasoning capability (same engine; degrades only if DeepSeek R1 itself is unavailable, then Conversation) | Yes (Phase 5+) | High | HIGH | Shares an engine with Reasoning by design (Section 10) |
| Coding | Nemotron Ultra 3 | Reasoning capability (functional but not code-specialized) | Yes (Phase 5+) | High | NORMAL | — |
| Memory Consolidation | Qwen3 14B Instruct | Queue rather than substitute — consolidation is not time-critical | Yes | Low | LOW/IDLE | Never preempts conversation; see Section 23 |
| Tool Calling | Qwen3 8B Instruct | Memory Consolidation capability (larger, higher-cost, still correct) | Yes | Low | HIGH | Latency-critical within an active conversation turn |
| Browser Automation | Qwen3 Coder | Coding capability (same structured-reasoning family) | Yes | Medium | NORMAL | Runs inside the sandboxed browser process (V1 Foundation Architecture, Section 3.6) |
| Vision | Qwen2.5-VL | None — queue rather than substitute; no text-only engine can meaningfully replace vision understanding | Yes | Medium | NORMAL | See Section 23's Engine Failure scenario |
| Embedding | BGE-M3 | None registered — recovery (Section 20), not substitution | Yes | Low | NORMAL | CPU-native, per Section 13.3 |
| Reranking | BGE Reranker v2 | None registered — recovery, not substitution | Yes | Low | NORMAL | CPU-native; pairs with Embedding |
| OCR | PaddleOCR | Vision capability (slower, less precise for pure text) | Yes | Low | LOW | CPU-native |
| Speech Recognition | Architecture Only (Phase 1: `faster-whisper`) | — | No | Medium | INTERACTIVE | Runs in the separate voice process (V1 Technical Specification, Section 9) |
| Speech Synthesis | Architecture Only (Phase 1: Kokoro) | — | No | Low | INTERACTIVE | Same as above |

### 19.4 Dynamic Assignment

When an agent declares a capability (per PHASE_2_TECHNICAL_SPECIFICATION.md
Section 10.3's `capability` attribute, now generalized as the standard
pattern for every future agent), resolution at dispatch time follows: (1)
is the Preferred Engine currently Warm or Idle (Section 20) — if so,
assign it; (2) if Busy, queue per Section 5.4's priority discipline; (3)
if Failed, resolve through the Fallback Engine column above, or queue if
no fallback is registered; (4) if no engine for this capability is
currently Loaded at all, trigger lazy loading (Section 20.4) before
dispatch. This is the concrete mechanism behind Section 9.3's promise that
replacing an engine is "a registry change, not an architecture change" —
the dispatch logic above never changes; only this table's contents do.

---

## 20. ENGINE LIFECYCLE

### 20.1 Relationship to Section 5.7

Section 5.7 introduced a simplified four-state model — `UNLOADED →
LOADING → WARM → ACTIVE` — sufficient for describing warm-pool eviction
at a conceptual level. This section provides the full nine-state lifecycle
that formalizes those four states for implementation. Nothing below
contradicts Section 5.7; the table in 20.2 shows exactly how the two
relate.

### 20.2 The Nine States and Their Relationship to Section 5.7

| New State | Meaning | Relationship to Section 5.7 |
|---|---|---|
| *(implicit)* Unloaded | No engine instance exists; no resources allocated | Identical to Section 5.7's `UNLOADED` — the state before and after this lifecycle |
| Loaded | Weights resident in memory, not yet initialized | Corresponds to the moment Section 5.7's `LOADING` transition completes |
| Warm | Initialized and ready to accept work | Corresponds to Section 5.7's `WARM` |
| Idle | Warm, with zero active requests | A refinement of `WARM` — specifically, warm and currently unused |
| Busy | Warm, currently serving one or more requests | Corresponds to Section 5.7's `ACTIVE` |
| Paused | Warm, but not being scheduled any new work; in-flight work suspended (job-level `PAUSED`, PHASE_2_TECHNICAL_SPECIFICATION.md Section 10.4) | New — not present in Section 5.7 |
| Swapping | Being evicted specifically to make room for a replacement engine, coordinated with that engine's simultaneous Loading | A refinement of Section 5.7's eviction concept, made explicit |
| Unloading | Being removed without a specific replacement in mind (graceful shutdown, administrative unload) | A refinement of Section 5.7's eviction concept, made explicit |
| Failed | Crashed or errored during load or while serving; cannot currently serve requests | New — not present in Section 5.7 |
| Recovering | Attempting to restart after Failed, before returning to Loaded | New — not present in Section 5.7 |

### 20.3 State Transitions

```
Unloaded ──(lazy load triggered)────────▶ Loaded
Loaded   ──(initialization completes)───▶ Warm
Warm     ──(request assigned)───────────▶ Busy
Busy     ──(request completes, none queued)─▶ Idle
Idle     ──(request assigned)───────────▶ Busy
Idle     ──(idle timeout, or VRAM pressure)─▶ Unloading
Warm/Idle/Busy ──(higher-priority engine needs the slot)─▶ Swapping
Swapping ──(eviction completes)─────────▶ Unloaded
Warm/Idle ──(explicit pause: thermal event, user request)─▶ Paused
Paused   ──(resume)─────────────────────▶ Warm
Loaded/Warm/Busy ──(crash or error)─────▶ Failed
Failed   ──(restart attempted)──────────▶ Recovering
Recovering ──(restart succeeds)─────────▶ Loaded
Recovering ──(restart fails, retries exhausted)─▶ Unloaded
Unloading ──(removal completes)─────────▶ Unloaded
```

### 20.4 Lazy Loading

No engine is loaded preemptively at system startup, with one deliberate
exception: capabilities with `Priority Class: INTERACTIVE` (Section 19.3
— Conversation, Speech Recognition, Speech Synthesis, Tool Calling) may be
configured to load at startup specifically because their latency
sensitivity makes cold-start loading during a live conversation
unacceptable. Every other engine transitions `Unloaded → Loaded` only when
the Capability Registry (Section 19.4) resolves a request to it and no
already-Warm instance can serve it.

### 20.5 Automatic Unloading

An engine in `Idle` transitions to `Unloading` when either a configurable
idle timeout elapses, or the GPU Resource Manager (Section 7, Group C)
signals VRAM pressure requiring space — the same LRU-plus-priority
eviction logic already described in Section 5.7, now given a named state
to occupy while it happens. A `Failed` engine is evicted from the warm
pool immediately, distinct from a graceful `Unloading` — its slot becomes
available at once rather than waiting for an idle timeout. A `Recovering`
engine does not occupy a warm-pool slot until it successfully returns to
`Loaded`.

### 20.6 Warm Pools

Unchanged in concept from Section 5.7: a small number of engines are kept
`Warm` (idle or busy) at once, chosen by recent-use frequency and
priority-weighted demand. This section's contribution is the vocabulary
for describing what happens at the pool's edges — `Swapping` when a pool
member is displaced for another, `Failed` when a pool member stops
responding, `Recovering` while it attempts to rejoin.

---

## 21. AGENT HEALTH MONITORING

### 21.1 Relationship to PHASE_2_TECHNICAL_SPECIFICATION.md Section 10.5

Phase 2 already introduced an initial Agent Health Interface as a
phase-scoped, additive extension to `BaseAgent`: `is_alive()`,
`health_status()`, `current_load()`, `estimated_completion()`,
`last_error()`, `active_tasks()`, `queued_tasks()`. This section formalizes
that interface at the constitutional level and adds the one dimension
Phase 2's version did not yet need: **Recovery State**, since Phase 2 has
no automated recovery mechanism to report on. Nothing below removes or
narrows what Phase 2 already specified.

### 21.2 The Complete Contract

Every agent exposes:

- **Health** — `health_status()`: `HEALTHY | DEGRADED | UNHEALTHY`, with
  optional detail. `DEGRADED` includes, but is not limited to, an agent
  whose declared capability (Section 19) is currently resolving through
  its Fallback Engine rather than its Preferred Engine.
- **Load** — `current_load()`: 0.0–1.0.
- **Queue Length** — `len(queued_tasks())`.
- **Failure State** — `last_error()`: the most recent `AetherError`-family
  exception (ADR-011 Section 9.4), if any.
- **Recovery State** — new in this section: `NONE | ATTEMPTING |
  ESCALATED`. `NONE` when healthy. `ATTEMPTING` when the agent has
  detected sustained failure and is running a lightweight self-check
  before accepting new work. `ESCALATED` when self-recovery has not
  resolved the issue within a bounded window, at which point the agent
  stops accepting new work and surfaces the failure state for external
  intervention.

### 21.3 How the Executive Intelligence Layer Monitors All Agents

Section 6.2 already names an Execution Monitor as one of the Executive
Intelligence Layer's six internal components, without previously
specifying its mechanism. That mechanism is this interface: the Execution
Monitor polls, or subscribes via the event bus to, every registered
agent's health contract. An agent reporting `UNHEALTHY` with `Recovery
State: ESCALATED` is not retried by the Execution Monitor directly —
escalation here follows the same pattern Section 18's protocol already
establishes: low-stakes recovery decisions may be delegated to the
Decision Agent, while anything with genuine downside is surfaced to the
user through the Personality Engine rather than resolved silently.

---

## 22. RUNTIME TELEMETRY FRAMEWORK

### 22.1 Relationship to PHASE_2_TECHNICAL_SPECIFICATION.md Section 10.6

Phase 2 already extended Aether's event bus with `runtime.resource.
snapshot` and additive `retry_count` fields on `llm.call.completed` and
`agent.run.completed`. This section formalizes the complete telemetry
framework those additions were the first instance of. Token Usage is not
new — `LLMResponse.prompt_tokens` / `completion_tokens` / `total_tokens`
already exist (V1_TECHNICAL_SPECIFICATION.md Section 2.4) and are already
carried on `llm.call.completed`; this framework recognizes them formally
as a telemetry dimension rather than introducing a new field for them.

### 22.2 What Is Genuinely New at This Level

**Throughput** — the one dimension with no per-task equivalent. Unlike
Execution Time, Queue Time, or Latency (all measured per task), Throughput
is a system-level aggregate: completed operations per unit time, per
capability. It is computed from the existing `agent.run.completed` and
`llm.call.completed` event stream rather than requiring a new event type
— a query over telemetry already being collected, not new collection.

### 22.3 The Complete Dimension Set

| Dimension | Source |
|---|---|
| Execution Time | `AgentResult.duration_ms` |
| Token Usage | `LLMResponse.prompt_tokens/completion_tokens/total_tokens` |
| CPU / GPU / RAM | `runtime.resource.snapshot` (PHASE_2_TECHNICAL_SPECIFICATION.md Section 10.6) |
| Queue Time | Section 20's state timestamps — duration in `Loaded`/`Idle` awaiting `Busy` |
| Failures | `agent.run.failed`, `last_error()` (Section 21.2) |
| Retries | `retry_count` field on `llm.call.completed` and `agent.run.completed` |
| Latency | Time from request to first response byte — a refinement of Execution Time for streaming contexts |
| Throughput | Computed aggregate, per Section 22.2 |

### 22.4 What Telemetry Supports

*Optimization* — this telemetry is the raw data source for the Performance
Review already mandatory at every phase close (ADR-011 Section 10;
AETHER_PHASE_EXECUTION_WORKFLOW.md Step 11). Nothing about optimization
work here requires inventing a separate measurement pass.

*Diagnostics* — every event carries the existing `correlation_id`
(V1_TECHNICAL_SPECIFICATION.md Section 2.3), so any failure traces across
every event it touched via Redis Streams' persistence.

*Future learning* — the Learning Agent (Section 7, Group A) requires
long-term interaction history to propose adjustments. This telemetry is
the system-behavior analog of that: a sustained rise in `retry_count`, or
a capability spending a growing share of its time `DEGRADED`, is precisely
the signal a future self-improvement process needs — recorded from now
onward, well before any component exists sophisticated enough to act on
it.

---

## 23. GRACEFUL DEGRADATION

### 23.1 Relationship to Sections 5.8 and 13.4

Both sections already establish the general degradation ladder: queue,
substitute, delay, communicate honestly. This section does not re-derive
that ladder — it applies it concretely to five named scenarios, which is
the genuinely new content this appendix contributes here.

### 23.2 Scenario: Low VRAM

Triggered when the GPU Resource Manager reports insufficient free VRAM for
a Preferred Engine's residency. Response, in order: substitute via Section
19.3's Fallback Engine column, if one is registered for the requesting
capability; queue, if the capability's Priority Class is not INTERACTIVE;
as a last resort, force an `Idle` engine into `Unloading` (Section 20.5),
chosen by the existing LRU-plus-priority eviction logic.

### 23.3 Scenario: Low RAM

System-level RAM pressure, distinct from VRAM. `aether-core` and
`aether-voice` are never evicted to relieve RAM pressure; background,
non-interactive work (a long-running consolidation batch, an indexing job)
is paused first, per the job-level `PAUSED` state.

### 23.4 Scenario: High CPU

CPU-native capabilities (Embedding, Reranking, OCR — Section 13.3) queue
behind one another rather than contending for cycles. INTERACTIVE-priority
work is never CPU-starved by background capability requests — enforced by
the same priority queue discipline already defined in Section 5.4.

### 23.5 Scenario: Engine Failure

An engine transitions to `Failed` (Section 20.3). Response: immediate
substitution via that capability's registered Fallback Engine (Section
19.3), if one exists. If none exists — Vision is the clearest example, per
Section 19.3's note that no text-only engine can meaningfully substitute
for it — the affected task transitions to `BLOCKED`
(PHASE_2_TECHNICAL_SPECIFICATION.md Section 10.4's state model, exercised
here for the first genuinely load-bearing case) while the failed engine
attempts `Recovering` in the background.

### 23.6 Scenario: GPU Failure

A hardware-level failure (driver crash, thermal shutdown) affects every
currently resident GPU engine at once. All affected engines transition to
`Failed` simultaneously. CPU-native capabilities are unaffected, since
they never depended on the GPU. GPU-dependent capabilities queue or
degrade to their fallback until the GPU Resource Manager confirms
recovery.

### 23.7 The Invariant Every Scenario Respects

In every scenario above, Conversation's `INTERACTIVE` priority class means
it is the last capability degraded and the first restored. This is not
scenario-specific — it is the same non-negotiable rule Section 4.1 already
states ("Conversation with the user is never blocked by background work"),
now shown to hold under every named failure mode this section addresses,
not merely in the general case.

---

## 24. LONG-TERM INTELLIGENCE EVOLUTION

### 24.1 This Section Does Not Introduce a New Roadmap

The six-stage progression this section's title evokes — Current Runtime →
Multi-Agent Runtime → Collaborative Intelligence → Specialist Models →
Foundation Models → Unified Native Intelligence — is the same roadmap
Section 15 already specifies in full (Current Local Multi-Model Runtime →
Advanced Multi-Agent Runtime → Hybrid Cognitive Runtime → Internally
Developed Specialist Models → Complete Aether Foundation Model Ecosystem →
Unified Aether Intelligence). The principle that architecture stays fixed
while implementations evolve is the same principle Section 14 already
establishes. Restating either in different words here would create two
descriptions of the same thing, free to drift apart over time. Section 15
and Section 14 remain the single source of truth for both; this section
does not duplicate them.

### 24.2 What This Section Adds Instead

Section 14.3 named what never changes as of the original document:
the Personality Engine's contract, the Memory API boundary, the
Executive Intelligence Layer's coordination role, the Capability Registry
pattern itself, the Runtime Scheduler's priority discipline. Sections 17
through 23 have since introduced genuinely new permanent architecture that
Section 14.3's original list — written before those sections existed —
could not have named. This section extends that list, without rewriting
Section 14.3 itself:

Also now permanent:

- The star-topology network structure (Section 17.2) — engines never
  connect to each other directly, only through the Executive Intelligence
  Layer.
- The eight-step Engine Collaboration Protocol and its ordering (Section
  18).
- The Capability Registry's ten-field schema (Section 19.2) — the values
  in any row change freely; the schema does not.
- The nine-state Engine Lifecycle (Section 20.2) — which specific engines
  exist changes freely; the states and their transitions do not.
- The Agent Health Interface's contract, now including Recovery State
  (Section 21.2).
- The Runtime Telemetry dimension set and its extension-not-replacement
  relationship to the existing event bus (Section 22.3).
- The five Graceful Degradation scenario responses and the invariant that
  conversation responsiveness degrades last and restores first (Section
  23.7).

### 24.3 What This Means in Practice

What Nemotron Ultra 3 does today, an Aether Foundation Model does
tomorrow — but it does it through the same star topology, the same
eight-step protocol, the same ten-field registry, the same nine-state
lifecycle, the same seven-method health contract, the same telemetry
dimensions, and the same degradation invariants. This is Section 16's
closing principle, made concrete in exactly the detail that did not yet
exist before this appendix: models are replaceable, and now, specifically,
so is every named engine in Section 19.3's table — but the shape of how
they cooperate is permanent.

---

*Document Version: 2.0 (Sections 1-16: v1.0, Sections 17-24: appended v2.0)*
*Status: ACCEPTED — FOUNDATIONAL ARCHITECTURE*
*Constitutional Tier: Tier 1*
*Model Stack Status: Current mapping per Sections 10 and 19.3; changes
governed by ADR-010 Section 11 (Dependency Governance) and, where
architecturally significant, Section 10 (Architectural Authority Rules)*
*Amendment History: v2.0 — appended Sections 17-24 (Collective
Intelligence Network, Engine Collaboration Protocol, Capability Registry,
Engine Lifecycle, Agent Health Monitoring, Runtime Telemetry Framework,
Graceful Degradation, Long-Term Intelligence Evolution). No prior section
modified. Sections 17, 19, 21, 22, 23, and 24 explicitly extend and
cross-reference existing Sections 5, 6, 9, 12, 13, 14, and 15 rather than
restate them; Sections 18 and 20 introduce genuinely new architecture not
previously specified. Section 19 additionally reconciles a pre-existing
gap between Section 9.2's introductory capability list and Section 10's
fuller runtime mapping.*
*Review Trigger: Any capability registry change, any new phase's agent
roster expansion, or annually as part of the phase review cycle*
*Owner: Chief AI Architect / Principal Systems Engineer*
*Last Updated: 2025-11-15*
