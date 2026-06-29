# AETHER AI OS — MASTER BLUEPRINT v1.0

> *"The measure of intelligence is the ability to change."*
> — Albert Einstein

---

**Document Status:** Living Document — Foundation Release  
**Version:** 1.0.0  
**Classification:** Project Cornerstone  
**Owner:** Chief Architect (Claude) + Product Owner  
**Purpose:** Authoritative architectural reference for all Aether AI OS development decisions

---

## TABLE OF CONTENTS

1. [Executive Vision Analysis](#1-executive-vision-analysis)
2. [Guiding Principles](#2-guiding-principles)
3. [System Architecture](#3-system-architecture)
4. [Agent Ecosystem Design](#4-agent-ecosystem-design)
5. [Memory Architecture](#5-memory-architecture)
6. [Technology Stack](#6-technology-stack)
7. [Development Roadmap](#7-development-roadmap)
8. [Repository Structure](#8-repository-structure)
9. [Risk Register](#9-risk-register)
10. [Architecture Decision Records](#10-architecture-decision-records)
11. [Future Expansion Strategy](#11-future-expansion-strategy)
12. [Development Workflow](#12-development-workflow)
13. [Glossary](#13-glossary)

---

## 1. EXECUTIVE VISION ANALYSIS

### 1.1 Project Interpretation

Aether AI OS is not a product. It is an **infrastructure**. The distinction matters enormously for every architectural decision that follows.

A product solves a problem. Infrastructure enables a universe of future solutions. JARVIS was not a product Tony Stark used — it was the cognitive nervous system of his entire operation. That is the correct mental model for Aether.

The fundamental proposition is this: **every digital interaction a human performs today is mediated by dumb software that requires precise human input.** Aether replaces that mediation layer with an intelligent agent that understands goals, maintains context, takes initiative, and executes across the entire digital surface.

This means Aether must eventually:
- Know what the user is working on *without being told*
- Anticipate needs before they are expressed
- Execute multi-step workflows from high-level intent alone
- Maintain a coherent model of the user's world that persists and grows
- Operate across all digital surfaces (desktop, browser, mobile, code, data)
- Eventually extend into physical interfaces (AR, mobile, wearables)

### 1.2 What Aether Is — and Is Not

| Aether IS | Aether is NOT |
|-----------|---------------|
| A personal AI Operating System | A chatbot |
| A long-term intelligent companion | A single-session assistant |
| An autonomous agent platform | A query-response tool |
| A local-first, privacy-preserving system | A cloud-dependent SaaS |
| A platform that grows through modular upgrades | A feature-complete application |
| An OS-level intelligence layer | A productivity app |

### 1.3 Long-Term Objectives

**Year 1:** Foundation — Establish the core intelligence loop: perceive → reason → act → remember. Build the architectural skeleton that all future phases attach to.

**Year 2:** Competency — Aether becomes genuinely useful across multiple domains (PC control, web research, development assistance, multi-agent tasks).

**Year 3:** Integration — Aether extends into business workflows, mobile, and begins visual intelligence. The floating UI becomes the primary interaction surface.

**Year 4+:** Transcendence — Holographic interfaces, AR integration, deeper autonomy, robotics-readiness. Aether becomes the user's primary interface to the digital world.

### 1.4 Core Differentiators

**Persistent Identity:** Unlike every AI assistant on the market, Aether will remember everything — conversations, decisions, patterns, preferences — indefinitely. It will know you better over time, not reset with every session.

**True Agency:** Aether does not just respond. It plans, executes, monitors, and corrects — with multi-step autonomous workflows that require minimal human intervention.

**Privacy-First Architecture:** Local-first by design. Your memory, your data, your patterns live on your infrastructure. Cloud LLMs are tools Aether calls, not custodians of your information.

**Multi-Modal Presence:** Voice, text, vision, screen understanding — Aether perceives the world the same way a human assistant would.

**Modular Evolution:** Every subsystem is designed to be replaced, upgraded, or extended without touching others. Aether in Year 5 will be unrecognizable from Aether in Year 1, but the architectural skeleton will be identical.

### 1.5 Technical Challenges — Honestly Assessed

| Challenge | Severity | Why It's Hard |
|-----------|----------|---------------|
| Voice response latency | HIGH | Must feel conversational; >800ms feels broken |
| Memory recall quality | HIGH | Retrieving *the right* memory, not just a related one, at scale |
| Agent reliability | HIGH | Agents hallucinate, loop, and fail; production robustness is hard |
| LLM context limits | MEDIUM | Managing what goes into a 200k context window across 2 years of memory |
| Security surface | HIGH | An OS-level AI that can execute code and control the PC is an enormous attack target |
| Multi-agent coordination | MEDIUM | Deadlocks, conflicts, and race conditions in distributed agent execution |
| LLM cost at scale | MEDIUM | 10,000 calls/day to a premium model is expensive; requires smart routing |
| Long-term maintainability | MEDIUM | LLM providers change; frameworks evolve; must design for replacement |
| Cross-device state sync | MEDIUM | Keeping identical context across desktop, mobile, and web |

---

## 2. GUIDING PRINCIPLES

These principles are immutable. Every architectural debate should be resolved by returning to them.

### P1: Intelligence Should Be Ambient, Not On-Demand
Aether is always present, always aware, always ready. Design every interface for *continuous presence*, not session-based activation.

### P2: Local-First, Cloud-Enhanced
All memory, all critical data, all core logic runs locally. Cloud LLMs are *tools Aether uses*, not places where Aether lives. This protects privacy, enables offline capability, and removes vendor lock-in.

### P3: Every Boundary is a Contract
Services communicate only through defined API contracts. No shared databases between services. No direct function calls across service boundaries. This is what makes the system replaceable and evolvable.

### P4: Agents Are Citizens, Not Functions
An agent is not a function you call. It is an autonomous entity with a role, responsibilities, state, and lifecycle. Design agents as you would design team members — clear responsibilities, defined interfaces, explicit handoffs.

### P5: Memory Is the Core Product
The intelligence of Aether scales directly with the quality of its memory. A system with brilliant agents but poor memory is worthless. Memory architecture receives the same engineering investment as the agent framework itself.

### P6: Confirm Before Destroy
Any action that is irreversible, destructive, or high-stakes requires explicit human confirmation. This is a non-negotiable safety principle that spans every phase.

### P7: Build for Replacement, Not Permanence
Every component will eventually be replaced with something better. Design for this explicitly: LLM provider abstraction, database abstraction, UI framework abstraction. The system should be able to swap its LLM backbone in a config change.

### P8: Complexity Must Be Earned
Do not add complexity in anticipation of future needs that may never arrive. Add it when a real requirement demands it. But when you add it, add it at the architectural level — not as a hack.

---

## 3. SYSTEM ARCHITECTURE

### 3.1 Architectural Pattern

**Pattern:** Distributed Event-Driven Microservices with a Central Orchestration Kernel

Aether's architecture is modeled directly on an operating system:

| OS Concept | Aether Equivalent |
|------------|-------------------|
| Kernel | `aether-core` — the orchestration engine |
| Processes | Agents — autonomous, isolated execution units |
| Memory System | `memory-nexus` — multi-tier memory management |
| I/O System | `perception-service` (input) + `action-engine` (output) |
| File System | `knowledge-graph` — structured persistent knowledge |
| Shell | `aether-desktop` / `aether-mobile` / `aether-cli` |
| Drivers | `integration-hub` — external service connectors |
| Scheduler | `agent-runtime` — task scheduling and agent lifecycle |
| Bus | Redis Streams — event bus connecting all services |

### 3.2 High-Level System Topology

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACES                               │
│  ┌──────────────┐   ┌─────────────────┐   ┌────────────────────────┐   │
│  │ aether-cli   │   │ aether-desktop  │   │  aether-mobile         │   │
│  │ (Phase 1)    │   │ (Phase 9)       │   │  (Phase 7)             │   │
│  └──────┬───────┘   └────────┬────────┘   └───────────┬────────────┘   │
│         └─────────────────────┼──────────────────────┘                 │
└─────────────────────────────┬─┼────────────────────────────────────────┘
                               │ │  WebSocket / REST
┌──────────────────────────────▼─▼────────────────────────────────────────┐
│                           API GATEWAY                                    │
│                  Authentication · Rate Limiting · Routing               │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                           AETHER CORE                                    │
│         Session Manager · Intent Router · Response Assembler            │
│         Conversation Manager · LLM Router (LiteLLM)                    │
└──┬───────────────┬─────────────────────┬────────────────────────────────┘
   │               │                     │
   ▼               ▼                     ▼
┌──────────┐  ┌──────────────┐  ┌───────────────────────────────┐
│ VOICE    │  │ AGENT        │  │ MEMORY NEXUS                  │
│ ENGINE   │  │ RUNTIME      │  │                               │
│          │  │              │  │  L0: Working Memory           │
│ STT      │  │ Orchestrator │  │  L1: Session Memory (Redis)   │
│ TTS      │  │ Planner      │  │  L2: Episodic Memory (Qdrant) │
│ VAD      │  │ Executor     │  │  L3: Semantic Memory (Qdrant) │
│ Audio    │  │ Researcher   │  │  L4: Procedural (PostgreSQL)  │
└──────────┘  │ Coder        │  │  L5: World Model (Neo4j)      │
              │ Memory Mgr   │  └───────────────────────────────┘
              │ Guardian     │
              └──────┬───────┘
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
┌──────────┐  ┌──────────┐   ┌────────────────┐
│ PERCEPTION│  │  ACTION  │   │  INTEGRATION   │
│ SERVICE   │  │  ENGINE  │   │  HUB           │
│           │  │          │   │                │
│ Vision    │  │ PC Ctrl  │   │ Google         │
│ Screen    │  │ FileSystem│  │ GitHub         │
│ Text NLP  │  │ Browser  │   │ Notion         │
└──────────┘  │ AppCtrl  │   │ CRM            │
              └──────────┘   │ Custom...      │
                             └────────────────┘
                                     │
        ┌────────────────────────────┘
        ▼
┌──────────────────┐
│ KNOWLEDGE GRAPH  │
│ Neo4j + Qdrant   │
│ Entity Relations │
│ Semantic Index   │
└──────────────────┘

═══ EVENT BUS (Redis Streams) connects all services ═══
═══ METRICS (OpenTelemetry → Prometheus → Grafana) observes all ═══
```

### 3.3 Service Boundaries and Responsibilities

#### `aether-core` — The Kernel
- **Owns:** Session state, conversation history (current session), intent classification, LLM routing
- **Responsibilities:** Receive user input, determine intent, route to appropriate agents or services, assemble final response, manage conversation flow
- **Does NOT own:** Long-term memory (Memory Nexus owns this), agent execution (Agent Runtime owns this)
- **Exposes:** REST API consumed by API Gateway, WebSocket for streaming responses

#### `memory-nexus` — The Memory System
- **Owns:** All memory tiers (episodic, semantic, procedural, world model), retrieval logic, memory maintenance
- **Responsibilities:** Store memories, retrieve relevant context given a query, consolidate and maintain memory over time
- **Does NOT own:** What to remember (Aether Core decides relevance), agent state (Agent Runtime owns this)
- **Exposes:** REST API with `remember()`, `recall()`, `forget()`, `consolidate()` operations

#### `agent-runtime` — The Process Manager
- **Owns:** Agent registry, agent lifecycle, task scheduling, inter-agent communication
- **Responsibilities:** Launch, monitor, and terminate agents; route tasks to capable agents; manage task queues; handle agent failures
- **Does NOT own:** Agent-specific logic (each agent owns its own reasoning), memory (Memory Nexus owns this)
- **Exposes:** REST API for task submission, WebSocket for task progress streaming

#### `perception-service` — The Sensory System
- **Owns:** Voice input pipeline (STT, VAD), screen capture, image preprocessing, text normalization
- **Responsibilities:** Transform raw input (audio, screen, text) into structured data that Aether Core can process
- **Does NOT own:** Understanding of input (Aether Core and agents handle understanding)
- **Exposes:** WebSocket (streaming voice), REST (on-demand screen capture, image analysis)

#### `voice-engine` — The Voice Output
- **Owns:** TTS synthesis, audio streaming, voice personality configuration
- **Responsibilities:** Convert text responses to natural speech, stream audio in real-time
- **Exposes:** WebSocket (streaming audio), REST (generate audio file)

#### `action-engine` — The Hands
- **Owns:** PC control primitives (keyboard, mouse, clipboard), file system operations, application control, system monitoring
- **Responsibilities:** Execute physical actions on the operating system, report action results
- **Safety:** All destructive actions require confirmation token from guardian
- **Exposes:** REST API with action primitives; all actions are logged

#### `browser-agent` — The Web Navigator
- **Owns:** Browser instance pool, page navigation, element interaction, data extraction
- **Responsibilities:** Navigate web pages, extract structured data, fill forms, take screenshots
- **Exposes:** REST API for browser tasks; runs as isolated service with sandboxed browser instances

#### `knowledge-graph` — The World Model
- **Owns:** Entity graph (Neo4j), semantic embeddings (Qdrant), knowledge indexing
- **Responsibilities:** Maintain a graph of entities and their relationships, provide semantic search over knowledge
- **Exposes:** GraphQL API for complex queries, REST for simple entity operations

#### `integration-hub` — The Connectors
- **Owns:** OAuth token management, external API clients, webhook receivers, connector registry
- **Responsibilities:** Manage all third-party service integrations, abstract external APIs behind consistent interfaces
- **Exposes:** Unified REST API that translates Aether requests into third-party API calls

#### `api-gateway` — The Front Door
- **Owns:** Authentication/authorization, rate limiting, request routing, SSL termination
- **Responsibilities:** Single entry point for all client requests; security perimeter
- **Exposes:** Public REST and WebSocket API consumed by all UIs

### 3.4 Inter-Service Communication

| Pattern | Technology | Use Case |
|---------|-----------|----------|
| Synchronous Request/Response | REST over HTTP | Direct service queries |
| Asynchronous Events | Redis Streams | Service notifications, state changes |
| Real-time Streaming | WebSocket | Voice, agent progress, live updates |
| Background Tasks | Redis Queues | Non-urgent processing, consolidation |
| Service Discovery | Docker DNS / Consul (Phase 5+) | Dynamic service location |

**Event Naming Convention:** `{service}.{entity}.{action}`  
Examples: `memory.episodic.stored`, `agent.task.completed`, `action.file.deleted`

### 3.5 The Standard Event Envelope

Every event on the bus follows this envelope:

```json
{
  "event_id": "uuid-v4",
  "event_type": "memory.episodic.stored",
  "source_service": "aether-core",
  "session_id": "uuid-v4",
  "conversation_id": "uuid-v4",
  "timestamp_utc": "ISO-8601",
  "schema_version": "1.0",
  "payload": { ... },
  "correlation_id": "uuid-v4",
  "causation_id": "uuid-v4"
}
```

---

## 4. AGENT ECOSYSTEM DESIGN

### 4.1 Agent Philosophy

An agent in Aether is not a function or a tool. It is an autonomous reasoning unit with:
- A defined **role** and area of expertise
- **State** that persists across a task lifecycle
- A **capability declaration** that tells the runtime what it can do
- **Input/output contracts** that other agents can depend on
- **Safety guardrails** specific to its domain
- **Error recovery** mechanisms built in

### 4.2 Agent Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│                 ORCHESTRATOR AGENT                      │
│   Master coordinator. Understands goals. Delegates.     │
│   Never executes directly. Only plans and coordinates.  │
└────────────────────────┬────────────────────────────────┘
         ┌───────────────┼───────────────────┐
         ▼               ▼                   ▼
┌─────────────┐  ┌────────────────┐  ┌──────────────────┐
│  PLANNER    │  │   EXECUTOR     │  │   GUARDIAN       │
│  AGENT      │  │   AGENT        │  │   AGENT          │
│             │  │                │  │                  │
│ Decomposes  │  │ Sequences and  │  │ Safety checker.  │
│ goals into  │  │ monitors task  │  │ Reviews actions  │
│ task trees  │  │ execution      │  │ before execution │
└──────┬──────┘  └───────┬────────┘  └──────────────────┘
       │                 │
       ▼                 ▼
┌──────────────────────────────────────────────────────────┐
│                  SPECIALIST AGENTS                       │
├─────────────┬──────────────┬──────────────┬─────────────┤
│  RESEARCH   │   CODING     │   BROWSER    │   MEMORY    │
│  AGENT      │   AGENT      │   AGENT      │   AGENT     │
│             │              │              │             │
│ Information │ Code writing │ Web         │ Memory ops  │
│ gathering   │ review       │ automation  │ maintenance │
│ synthesis   │ debugging    │ extraction  │ retrieval   │
├─────────────┼──────────────┼──────────────┼─────────────┤
│  FILE       │  SYSTEM      │  VISION     │  COMMS      │
│  AGENT      │  AGENT       │  AGENT      │  AGENT      │
│ (Phase 2)   │ (Phase 2)    │ (Phase 6)   │ (Phase 8)   │
└─────────────┴──────────────┴──────────────┴─────────────┘
```

### 4.3 Agent Profiles

#### ORCHESTRATOR AGENT
- **Model:** Claude Opus (most capable — plans must be correct)
- **Role:** Interpret user goals, determine whether single-agent or multi-agent handling is needed, delegate appropriately, synthesize final response
- **Key Behaviors:**
  - Always retrieves relevant memory context before planning
  - Maintains a task graph for complex multi-step requests
  - Monitors delegated tasks for completion or failure
  - Handles clarification requests when intent is ambiguous
- **Does NOT:** Execute any actions directly. It only delegates.
- **Safety:** Guardian agent reviews any plan involving system-level actions before execution begins

#### PLANNER AGENT
- **Model:** Claude Opus / Gemini Flash (balance of quality and speed)
- **Role:** Given a goal, produce a concrete, executable task plan with dependencies
- **Key Behaviors:**
  - Produces task trees (not flat lists) to capture dependencies
  - Estimates resource requirements per task
  - Identifies which specialist agents are needed
  - Produces rollback plans for reversible operations
- **Output Format:** Structured `TaskGraph` JSON that Agent Runtime can execute

#### EXECUTOR AGENT
- **Model:** Gemini Flash (needs to be fast; execution is not reasoning)
- **Role:** Execute task sequences produced by Planner, monitor progress, report results
- **Key Behaviors:**
  - Confirms task completion before moving to dependents
  - Detects and reports failures to Orchestrator
  - Implements retry logic with exponential backoff
  - Records execution logs to memory

#### MEMORY AGENT
- **Model:** Gemini Flash (housekeeping work, not complex reasoning)
- **Role:** All memory operations — store, retrieve, consolidate, maintain
- **Key Behaviors:**
  - Runs consolidation jobs on a schedule
  - Extracts entities and relationships from conversations for knowledge graph
  - Manages memory decay (importance scoring over time)
  - Provides context packages to other agents on request
- **Critical:** This agent's quality determines Aether's long-term intelligence

#### RESEARCH AGENT
- **Model:** Claude Sonnet (balance of quality and speed for research synthesis)
- **Role:** Deep information gathering and synthesis
- **Key Behaviors:**
  - Uses Browser Agent as a tool for web access
  - Evaluates source credibility
  - Synthesizes multiple sources into structured reports
  - Stores new knowledge to Knowledge Graph via Memory Agent

#### CODING AGENT
- **Model:** Claude Sonnet (code quality demands good reasoning)
- **Role:** Code generation, review, refactoring, and debugging
- **Key Behaviors:**
  - Reads codebase context before writing new code
  - Generates tests alongside implementation
  - Uses isolated execution sandbox for testing
  - Tracks file changes in working memory
- **Tools:** Git operations, code execution sandbox, file read/write

#### BROWSER AGENT
- **Model:** Claude Sonnet + Vision (needs to understand page structure)
- **Role:** Web navigation, interaction, and data extraction
- **Key Behaviors:**
  - Maintains browser session state
  - Handles dynamic pages (waits for load, handles SPAs)
  - Extracts structured data from unstructured HTML
  - Screenshots for visual confirmation
- **Security:** Runs in isolated container; no access to local file system

#### GUARDIAN AGENT
- **Model:** Claude Sonnet (must reason carefully about safety)
- **Role:** Safety enforcer. Reviews all potentially dangerous actions before execution.
- **Key Behaviors:**
  - Maintains a risk policy (configurable by user)
  - Blocks: irreversible deletions, external data sends, financial operations — without explicit confirmation
  - Logs all reviewed actions
  - Can be configured for different risk tolerance levels
- **Override:** User can grant blanket permissions per session or per operation type

### 4.4 Inter-Agent Communication Protocol (CATP)

The **Communication and Task Protocol (CATP)** is the standard language all agents speak.

#### Task Request
```json
{
  "catp_version": "1.0",
  "task_id": "uuid-v4",
  "task_type": "research | code | action | memory | browse | ...",
  "priority": 1,
  "requester_agent": "orchestrator",
  "target_agent": "researcher",
  "objective": "Find the top 5 competitors of X and their pricing",
  "context": {
    "session_id": "...",
    "relevant_memories": [...],
    "constraints": ["only use publicly available information"]
  },
  "success_criteria": ["Returns structured list with name, URL, pricing"],
  "timeout_ms": 60000,
  "allow_sub_delegation": true,
  "callback_channel": "redis:task-results:uuid-v4"
}
```

#### Task Result
```json
{
  "catp_version": "1.0",
  "task_id": "uuid-v4",
  "status": "completed | failed | partial | timeout",
  "result": { ... },
  "confidence": 0.92,
  "sources": [...],
  "execution_time_ms": 4500,
  "errors": [],
  "memory_stored": ["uuid-v4"]
}
```

### 4.5 Agent Lifecycle States

```
REGISTERED → IDLE → ACTIVATED → PLANNING → EXECUTING → MONITORING
                                                              │
                         ┌────────────────────────────────────┤
                         ▼                                    ▼
                     COMPLETED ←───── REPORTING ←────── FAILED
                         │
                         ▼
                       IDLE
```

### 4.6 Agent Runtime Requirements
- Maximum concurrent agents per type: configurable (default: 3)
- Task timeout: configurable per agent type (default: 120 seconds)
- Max retry attempts: 3 with exponential backoff
- Agent heartbeat interval: 5 seconds
- Dead agent detection: after 2 missed heartbeats → task reassigned

---

## 5. MEMORY ARCHITECTURE

### 5.1 Memory Philosophy

Human intelligence is fundamentally memory. Without memory, every conversation is with a stranger. Aether's long-term value to the user is directly proportional to the quality of its memory system.

The memory architecture is inspired by cognitive science models of human memory:
- **Working memory** → In-process context window
- **Short-term/episodic memory** → Recent conversations and events
- **Long-term/semantic memory** → Consolidated facts and knowledge
- **Procedural memory** → Learned skills and workflows
- **World model** → Mental model of entities, relationships, and the environment

### 5.2 Memory Tier Architecture

| Layer | Name | Storage | Scope | Capacity | TTL | Access Speed |
|-------|------|---------|-------|----------|-----|--------------|
| L0 | Working Memory | In-process (Python dict) | Current LLM call | ~200k tokens | Seconds | Microseconds |
| L1 | Session Memory | Redis | Current session | Unlimited (summarized) | 24 hours | <1ms |
| L2 | Episodic Memory | Qdrant + PostgreSQL | All conversations | Unlimited | Permanent | <50ms |
| L3 | Semantic Memory | Qdrant + PostgreSQL | Knowledge facts | Unlimited | Permanent | <50ms |
| L4 | Procedural Memory | PostgreSQL | Skills & workflows | Unlimited | Permanent | <10ms |
| L5 | World Model | Neo4j | Entity graph | Unlimited | Permanent | <100ms |

### 5.3 Memory Data Models

#### Episodic Memory Record
```
{
  id: uuid,
  session_id: uuid,
  conversation_id: uuid,
  timestamp: datetime,
  type: "conversation | action | observation | decision",
  summary: string,                    # Human-readable summary
  raw_content: text,                  # Full original content
  embedding: vector[1536],            # Semantic embedding for retrieval
  entities: [entity_id, ...],         # Links to World Model entities
  importance_score: float,            # 0.0-1.0, decays over time
  access_count: int,                  # Increased on retrieval
  last_accessed: datetime,
  tags: [string, ...]
}
```

#### Semantic Memory Record (Knowledge)
```
{
  id: uuid,
  fact: string,                       # The knowledge statement
  source: "conversation | web | file | inference",
  confidence: float,                  # 0.0-1.0
  embedding: vector[1536],
  entities: [entity_id, ...],
  related_facts: [fact_id, ...],
  created_at: datetime,
  verified_at: datetime,
  contradicts: [fact_id, ...]         # Conflict detection
}
```

#### World Model Entity (Neo4j Node)
```
{
  id: uuid,
  type: "person | organization | project | concept | place | ...",
  name: string,
  aliases: [string, ...],
  properties: {key: value, ...},
  embedding: vector[1536],
  confidence: float,
  created_at: datetime,
  last_updated: datetime
}
```

World Model edges represent relationships:
- WORKS_AT, OWNS, CREATED, RELATED_TO, PART_OF, KNOWS, etc.

### 5.4 The Retrieval Pipeline

When Aether needs context for a response, the Memory Agent executes:

```
Step 1: Query Analysis
   → Extract key entities, topics, and temporal signals from current query

Step 2: Multi-Tier Retrieval (parallel)
   → L1: Fetch session context from Redis (always included)
   → L2: Vector search episodic memory (top-20 candidates)
   → L3: Vector search semantic memory (top-20 candidates)
   → L5: Traverse entity relationships from identified entities (depth-2)

Step 3: Relevance Scoring
   → Recency score (exponential decay from timestamp)
   → Semantic similarity score (cosine distance)
   → Access frequency score
   → Entity overlap score
   → Combined weighted score

Step 4: Token Budget Management
   → Sort by combined score
   → Include until token budget is exhausted (~8,000 tokens for context)
   → Prefer recency over semantic similarity when tie-breaking

Step 5: Context Package Assembly
   → Format as structured context block
   → Include source metadata for transparency
   → Return to requesting agent/service
```

### 5.5 Memory Operations API

```python
# Core operations exposed by Memory Nexus
remember(content, type, session_id, metadata) → memory_id
recall(query, filters, max_tokens) → ContextPackage
forget(memory_id, reason) → bool
update(memory_id, changes) → memory_id
consolidate(session_id) → ConsolidationReport
reflect(time_range) → InsightReport
search(query, memory_type, limit) → [MemoryRecord]
entity_graph(entity_id, depth) → SubGraph
```

### 5.6 Memory Maintenance Routines

**Session Consolidation** (triggered: session end)
- Summarize conversation into single episodic record
- Extract entities → update World Model
- Extract facts → add to Semantic Memory
- Update relationship graph in Neo4j

**Nightly Consolidation** (scheduled: 3 AM local)
- Merge near-duplicate episodic memories
- Recalculate importance scores (decay inactive memories)
- Identify and resolve knowledge contradictions
- Rebuild stale embeddings

**Importance Decay Function:**
```
new_score = base_score × e^(-λ × days_since_access)
where λ = 0.01 (slow decay for important memories)
boost = log(1 + access_count) × 0.1
final_score = min(1.0, new_score + boost)
```

---

## 6. TECHNOLOGY STACK

### 6.1 Stack Selection Philosophy

Every technology choice follows three criteria:
1. **Production-grade:** Used by large-scale systems in production
2. **Replaceable:** Can be swapped without rewriting the service
3. **Local-capable:** Can run on developer hardware without cloud dependency

### 6.2 Core Technology Decisions

#### Programming Languages

| Language | Version | Rationale | Used For |
|----------|---------|-----------|---------|
| Python | 3.12+ | AI/ML ecosystem. Async with FastAPI. Rich agent libraries. | All backend services |
| TypeScript | 5.x | Type safety for frontend. Great tooling. | All UI apps, shared SDK |

#### Backend Framework

**FastAPI** (Python)
- Reason: Native async, automatic OpenAPI documentation, Pydantic validation, fastest Python web framework for I/O-bound workloads
- Alternative considered: Django (too heavy), Flask (no async-native)

#### Agent Orchestration

**LangGraph** (primary) + **Custom CATP layer** (protocol)
- Reason: LangGraph provides battle-tested state machine infrastructure for agents. The custom CATP layer sits on top to enforce Aether-specific protocols.
- Alternative considered: CrewAI (less flexible graph control), AutoGen (Microsoft-centric, less Python-native), custom-only (too much infrastructure work)
- LangGraph handles: State persistence, cyclic agent graphs, parallel execution branches, conditional routing
- CATP handles: Inter-service agent calls, task queue integration, cross-session continuity

#### LLM Routing

**LiteLLM**
- Reason: Single interface to Claude, GPT-4, Gemini, and local models. Vendor lock-in prevention. Automatic fallback. Cost tracking.
- Configuration: Primary = Claude; Fallback = Gemini Flash; Local = Ollama (for simple tasks)

#### Vector Database

**Qdrant**
- Reason: Self-hosted, Rust-based (fast), production-grade, supports filtering on metadata alongside vector search, multi-vector per record, HNSW indexing
- Alternative considered: Chroma (simpler but not as production-ready), Weaviate (more complex), PostgreSQL + pgvector (less performant at scale)
- Deployment: Local Docker container; no cloud dependency

#### Relational Database

**PostgreSQL 16**
- Reason: The gold standard. JSONB for flexible schema. Extensions ecosystem. Excellent Python support via SQLAlchemy async.
- Used for: Structured records, agent task logs, procedural memory, user config, audit logs

#### Graph Database

**Neo4j** (Phase 3+)
- Reason: World-class graph database. Cypher query language. Excellent Python driver. Perfect for entity relationship modeling.
- Alternative considered: PostgreSQL recursive queries (works but limited), ArangoDB (less mature ecosystem)
- Deployment: Docker container, no cloud required

#### Cache & Message Bus

**Redis 7** (Redis Stack)
- Reason: One technology solves three problems: caching, pub/sub messaging, and task queues. Redis Streams for event bus. RedisJSON for complex objects. Extremely fast.
- Session Memory, Event Bus, Task Queue, Distributed Locks all run on Redis

#### Embeddings

**sentence-transformers** (`all-MiniLM-L6-v2` for speed, `all-mpnet-base-v2` for quality)
- Reason: Local embedding generation. No API cost. High quality. GPU acceleration supported.
- Alternative: OpenAI text-embedding-3-small (higher quality but API cost + latency)

#### Voice Input (STT)

**OpenAI Whisper** via `faster-whisper` (CTranslate2-optimized)
- Reason: Best accuracy among available models. Local deployment. `faster-whisper` is 4x faster than original with same accuracy.
- Voice Activity Detection: **Silero VAD** (lightweight, accurate, local)
- Real-time streaming: **RealtimeSTT** library for <300ms latency

#### Voice Output (TTS)

**Kokoro TTS** (primary, local, high quality, Apache 2.0)
- Fallback: **ElevenLabs** API (for highest quality when needed)
- Reason: Kokoro provides near-ElevenLabs quality fully locally. No cost per character.

#### Browser Automation

**Playwright** (Python)
- Reason: Modern, reliable, multi-browser, handles SPAs, async-native, excellent selector engine
- Alternative considered: Selenium (legacy, slower, less reliable)
- Deployment: Isolated Docker container per browser agent instance

#### PC Control

**pyautogui** + **pynput** (cross-platform)
- Windows-specific enhanced control: **pywinauto** (native Windows accessibility API)
- Screen capture: **mss** (fastest cross-platform screenshot library)

#### Desktop UI

**Electron** + **React** + **Tailwind CSS**
- Reason: Cross-platform, web technologies, large ecosystem, production-ready overlay window support
- UI Framework: React 18 with Zustand (state management)

#### Web Dashboard

**Next.js 15** (App Router) + **Tailwind CSS** + **Radix UI**
- Reason: React-based, excellent TypeScript support, production-grade

#### Mobile App (Phase 7)

**React Native** + **Expo**
- Reason: Code sharing with web dashboard, TypeScript, mature ecosystem, voice/notification APIs

#### Containerization

**Docker** + **Docker Compose** (development/personal deployment)
- **Kubernetes** (Phase 5+ for production scaling)
- Reason: Every service runs in its own container from Phase 1. No "works on my machine" issues.

#### Observability

| Tool | Purpose |
|------|---------|
| OpenTelemetry | Distributed tracing instrumentation (language-agnostic) |
| Prometheus | Metrics collection and storage |
| Grafana | Metrics dashboards and alerting |
| Loki | Log aggregation |
| Python `structlog` | Structured JSON logging in all services |

### 6.3 Package Management

- Python services: **Poetry** (deterministic dependency resolution)
- JavaScript apps/packages: **pnpm** (fast, disk-efficient, workspace support)

### 6.4 Technology Versioning Strategy

All dependency versions are **pinned** in production configuration. A quarterly review updates dependencies in a dedicated branch with full test coverage required before merging.

---

## 7. DEVELOPMENT ROADMAP

### Phase Overview

| Phase | Name | Weeks | Core Deliverable |
|-------|------|-------|-----------------|
| 1 | Foundation | 1–6 | Conversational AI with persistent memory |
| 2 | PC Intelligence | 7–12 | Computer control via voice |
| 3 | Web Intelligence | 13–20 | Autonomous web research and automation |
| 4 | Development Partnership | 21–28 | AI coding companion |
| 5 | Multi-Agent Intelligence | 29–42 | Complex autonomous task execution |
| 6 | Vision Intelligence | 43–50 | Screen understanding and vision-guided action |
| 7 | Mobile Integration | 51–62 | Cross-device Aether presence |
| 8 | Business Automation | 63–76 | End-to-end business workflow automation |
| 9 | Floating Assistant UI | 77–84 | Always-present AI interface |
| 10 | Holographic Interface | 85+ | Future-forward visual experience |

---

### PHASE 1: Foundation
**Duration:** Weeks 1–6  
**Theme:** "Establish the Core Intelligence Loop"

#### Objective
Build the architectural skeleton and a working conversational AI that persists context across sessions. The goal is not feature richness — it is architectural correctness that all future phases will build on.

#### Services to Build
| Service | Priority | Description |
|---------|----------|-------------|
| `aether-core` | Critical | Session management, conversation loop, LiteLLM integration |
| `memory-nexus` | Critical | L0–L2 memory (working, session, basic episodic) |
| `voice-engine` | High | Whisper STT + Kokoro TTS + Silero VAD |
| `api-gateway` | Critical | FastAPI gateway with basic auth |

#### Applications to Build
| App | Priority | Description |
|-----|----------|-------------|
| `aether-cli` | High | Command-line interface (Textual-based TUI) |

#### Key Milestones
- [ ] All services containerized and running via `docker compose up`
- [ ] Aether can have a multi-turn voice conversation
- [ ] Episodic memories survive a service restart
- [ ] Aether references past conversations accurately
- [ ] End-to-end latency: voice in → voice out < 2 seconds

#### Entry Criteria
- Development environment established (Docker, Python, Node)
- Repository structure created

#### Exit Criteria
- Can discuss a topic across multiple sessions with accurate recall
- Memory persists across process restarts
- Voice pipeline working at <2s round-trip

#### Dependencies for Next Phase
- None (Phase 1 is the foundation)

---

### PHASE 2: PC Intelligence
**Duration:** Weeks 7–12  
**Theme:** "Give Aether Hands"

#### Objective
Aether can control the operating system on behalf of the user. This phase makes Aether a genuine OS-level assistant, not just a chat window.

#### New Services
| Service | Description |
|---------|-------------|
| `action-engine` | PC control (keyboard, mouse, clipboard, app launch, system monitoring) |

#### Key Features
- Open, close, switch between applications
- File system navigation, search, create, move, delete (with Guardian confirmation)
- Clipboard read/write
- System status reporting (CPU, RAM, disk, network, processes)
- Volume/brightness/display control
- Screenshot capture and analysis

#### Safety Measures (Critical)
- Destructive operations (delete, overwrite) require explicit voice or text confirmation
- Action log maintains a record of every PC action taken
- Rate limiting on rapid successive actions (anti-runaway protection)
- Configurable allowlist/blocklist of applications Aether can control

#### Exit Criteria
- "Open Chrome and go to gmail.com" works end-to-end via voice
- "Create a folder called Projects on my Desktop" works
- "What processes are using the most CPU?" returns accurate answer

---

### PHASE 3: Web Intelligence
**Duration:** Weeks 13–20  
**Theme:** "Give Aether Eyes on the Web"

#### Objective
Aether can research any topic autonomously, navigate websites, extract data, and synthesize multi-source information.

#### New Services
| Service | Description |
|---------|-------------|
| `browser-agent` | Playwright-based autonomous browser |
| `knowledge-graph` | Initial Neo4j + Qdrant setup for storing extracted knowledge |

#### Key Features
- Multi-source web research with synthesis
- Structured data extraction from web pages
- Form filling on websites
- News aggregation and summarization
- Price/product research
- Knowledge graph population from web research

#### Architecture Note
The `browser-agent` runs in an isolated Docker container. It has no access to the host file system. Results are passed back through the API only.

#### Exit Criteria
- "Research the top 5 AI frameworks and give me a comparison" produces accurate, multi-source report
- "Go to [website] and fill in the contact form with my details" works
- Extracted knowledge is stored and retrievable in future sessions

---

### PHASE 4: Development Partnership
**Duration:** Weeks 21–28  
**Theme:** "Aether as Co-Developer"

#### Objective
Aether becomes a genuine development partner — reading code, writing code, reviewing PRs, and debugging.

#### New Services
| Service | Description |
|---------|-------------|
| `coding-agent` | Code generation, review, refactoring, debugging |
| `code-sandbox` | Isolated Docker execution environment for running generated code |

#### New Integrations
- GitHub API (via `integration-hub`)
- Local Git operations

#### Key Features
- Codebase semantic search (understand code by intent, not just keyword)
- Context-aware code generation (reads existing code before writing)
- Automated PR creation with description
- Code review with structured feedback
- Test generation alongside implementation
- Debugging workflow (reproduce → hypothesize → fix → verify)

#### Architecture Note
**Code is never executed outside the sandbox.** The `code-sandbox` is a Docker container with no network access and no volume mounts to sensitive directories. Results are returned as stdout/stderr.

#### Exit Criteria
- "Add a function to this file that does X" produces working code
- "Review the last commit for potential bugs" produces meaningful feedback
- Generated code passes basic tests

---

### PHASE 5: Multi-Agent Intelligence
**Duration:** Weeks 29–42  
**Theme:** "Aether Thinks in Parallel"

#### Objective
This is the pivotal phase. Individual agents become a coordinated team capable of handling complex, multi-step autonomous workflows. This is where Aether becomes genuinely JARVIS-like.

#### New Services / Major Expansions
| Service | Description |
|---------|-------------|
| `agent-runtime` | Full implementation: registry, scheduler, task graph executor |
| Planner Agent | Goal decomposition, task graph generation |
| Guardian Agent | Safety reviewer for all planned actions |

#### Key Features
- Complex task decomposition ("Research X, write a report, send it to my email")
- Parallel agent execution where tasks are independent
- Task graph visualization in dashboard
- Agent monitoring and management UI
- Long-running task support (hours, not just seconds)
- Human-in-the-loop checkpoints for high-risk steps

#### Critical Architecture Work
- Formal CATP protocol implementation
- Agent state persistence (survive service restarts mid-task)
- Task priority queue
- Agent failure recovery

#### Exit Criteria
- "Research our top 3 competitors, analyze their pricing, and create a slide deck summary" completes autonomously
- Task graph visible in dashboard
- Agent failures handled gracefully (retry or escalate to user)

---

### PHASE 6: Vision Intelligence
**Duration:** Weeks 43–50  
**Theme:** "Aether Sees What You See"

#### Objective
Aether gains visual understanding of the screen, enabling context-aware assistance without explicit descriptions.

#### New Capabilities in Perception Service
- Continuous screen capture pipeline (configurable fps)
- UI element detection (accessibility tree + vision model)
- Screen state understanding ("User is in VS Code, editing a Python file")
- Vision-guided action execution ("Click the Save button in the top-left")
- Change detection ("The email I was waiting for has arrived")

#### Architecture Note
Screen capture happens locally. Images are processed locally where possible (OCR, element detection). Vision LLM calls (for understanding) are only made when necessary. User controls exactly when screen monitoring is active.

#### Exit Criteria
- "What is the error message on my screen?" answered accurately without screenshot request
- "Click the Accept button in that dialog" executes correctly by finding the button visually
- Screen-aware context improves response quality measurably

---

### PHASE 7: Mobile Integration
**Duration:** Weeks 51–62  
**Theme:** "Aether In Your Pocket"

#### Objective
Aether available on mobile, with full context sync across devices.

#### New Applications
| App | Description |
|-----|-------------|
| `aether-mobile` | React Native + Expo iOS/Android app |

#### New Services
| Service | Description |
|---------|-------------|
| `sync-service` | Cross-device state synchronization |
| `notification-service` | Push notification management |

#### Key Features
- Voice assistant on mobile
- Full memory sync (desktop context available on mobile)
- Task status monitoring from mobile
- Push notifications for completed tasks
- Quick capture (notes, reminders → fed into desktop workflow)
- Offline basic mode (simple queries without network)

#### Exit Criteria
- Conversation started on desktop continues on mobile with full context
- Task initiated on desktop sends push notification on completion
- Mobile voice query answered using full desktop memory context

---

### PHASE 8: Business Automation
**Duration:** Weeks 63–76  
**Theme:** "Aether Handles the Busywork"

#### Objective
Aether integrates deeply into business workflows, managing CRM, email, calendar, and marketing operations autonomously.

#### New Integrations (Integration Hub)
- Email (Gmail/Outlook via OAuth)
- Calendar (Google Calendar/Outlook)
- CRM (HubSpot, Salesforce — connector pattern)
- Marketing platforms (configurable)
- Analytics (Google Analytics, custom)

#### Key Features
- Email triage and drafting
- Meeting scheduling and follow-up
- CRM data entry and lead management
- Marketing campaign monitoring
- Business performance dashboards
- Workflow automation builder (visual, no-code)

#### Exit Criteria
- "Summarize my emails from today and draft replies to the urgent ones" works end-to-end
- "Create a CRM record for the lead I just spoke with" works via voice
- "Schedule a follow-up meeting with [contact] for next week" books the meeting

---

### PHASE 9: Floating Assistant UI
**Duration:** Weeks 77–84  
**Theme:** "Aether Is Always There"

#### Objective
Replace the CLI and dashboard with a beautiful, always-present floating overlay that makes Aether feel like a genuine ambient intelligence.

#### App: `aether-desktop` (Electron)

#### Key Features
- Frameless, always-on-top, semi-transparent overlay
- Voice-activated (wake word: "Aether")
- Context-aware panels that appear when relevant
- Minimal form factor when idle (thin bar or corner indicator)
- Expanding interface when active
- Animated AI presence (visual pulse, thinking animations)
- System tray integration
- Dark/light theme, fully customizable

#### Design Principles
- **Non-intrusive:** Should feel like part of the OS, not a foreign app
- **Responsive:** Interface should respond faster than the user expects
- **Character:** Aether should have a visual personality, not just text output

#### Exit Criteria
- Floating UI working on Windows and macOS
- Voice activation (wake word) working without button press
- All Phase 1–8 functionality accessible through floating UI

---

### PHASE 10: Holographic Interface
**Duration:** Week 85+  
**Theme:** "The Vision Realized"

This phase is deliberately open-ended. It represents the long-term evolution of Aether's interface layer.

#### Near-Term (Year 3)
- 3D data visualization in overlay (Recharts → Three.js)
- Spatial task management UI
- Advanced animation system

#### Mid-Term (Year 4)
- WebXR integration (browser-based AR)
- Early compatibility with AR glasses APIs
- 3D agent visualization

#### Long-Term (Year 5+)
- Meta Ray-Ban / Apple Vision Pro integration
- Spatial computing interface
- Environmental awareness

---

## 8. REPOSITORY STRUCTURE

### 8.1 Top-Level Architecture

```
aether-os/                          # Root monorepo
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  # Run tests on PR
│   │   ├── build.yml               # Build Docker images
│   │   └── release.yml             # Semantic versioning
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
│
├── docs/
│   ├── architecture/
│   │   ├── MASTER_BLUEPRINT.md     # ← This document
│   │   ├── decisions/              # Architecture Decision Records (ADRs)
│   │   │   ├── ADR-001-monorepo.md
│   │   │   ├── ADR-002-python-primary.md
│   │   │   └── ...
│   │   ├── diagrams/               # Draw.io / Mermaid diagrams
│   │   └── runbooks/               # Operational procedures
│   ├── api/                        # OpenAPI specifications
│   │   ├── aether-core.yaml
│   │   ├── memory-nexus.yaml
│   │   └── ...
│   ├── guides/
│   │   ├── GETTING_STARTED.md
│   │   ├── DEVELOPMENT.md
│   │   ├── DEPLOYMENT.md
│   │   └── CONTRIBUTING.md
│   └── phases/                     # Per-phase implementation guides
│       ├── PHASE_1.md
│       └── ...
│
├── services/                       # Backend microservices (Python/FastAPI)
│   ├── aether-core/
│   │   ├── src/
│   │   │   └── aether_core/
│   │   │       ├── __init__.py
│   │   │       ├── main.py         # FastAPI app entry point
│   │   │       ├── orchestrator/   # Core orchestration logic
│   │   │       ├── router/         # Intent routing
│   │   │       ├── session/        # Session management
│   │   │       ├── conversation/   # Conversation management
│   │   │       ├── llm/            # LiteLLM wrapper + config
│   │   │       ├── models/         # Pydantic data models
│   │   │       └── api/            # FastAPI route handlers
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   └── integration/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── memory-nexus/
│   │   ├── src/
│   │   │   └── memory_nexus/
│   │   │       ├── working/        # L0: In-process working memory
│   │   │       ├── session/        # L1: Redis session memory
│   │   │       ├── episodic/       # L2: Qdrant + PostgreSQL episodic
│   │   │       ├── semantic/       # L3: Qdrant + PostgreSQL semantic
│   │   │       ├── procedural/     # L4: PostgreSQL procedural
│   │   │       ├── world_model/    # L5: Neo4j entity graph
│   │   │       ├── retrieval/      # Multi-tier retrieval pipeline
│   │   │       ├── maintenance/    # Consolidation, decay jobs
│   │   │       ├── embedding/      # Sentence transformer service
│   │   │       └── api/
│   │   └── ...
│   │
│   ├── agent-runtime/
│   │   ├── src/
│   │   │   └── agent_runtime/
│   │   │       ├── registry/       # Agent capability registry
│   │   │       ├── scheduler/      # Task queue and priority scheduling
│   │   │       ├── executor/       # Task graph executor
│   │   │       ├── monitor/        # Agent health monitoring
│   │   │       ├── protocols/      # CATP implementation
│   │   │       └── agents/
│   │   │           ├── base.py     # Base agent class
│   │   │           ├── orchestrator/
│   │   │           ├── planner/
│   │   │           ├── executor/
│   │   │           ├── researcher/
│   │   │           ├── coder/
│   │   │           ├── browser/
│   │   │           ├── memory/
│   │   │           └── guardian/
│   │   └── ...
│   │
│   ├── perception-service/
│   │   ├── src/
│   │   │   └── perception/
│   │   │       ├── voice/
│   │   │       │   ├── stt/        # Whisper + faster-whisper
│   │   │       │   ├── vad/        # Silero VAD
│   │   │       │   └── streaming/  # RealtimeSTT pipeline
│   │   │       ├── vision/
│   │   │       │   ├── capture/    # mss screen capture
│   │   │       │   ├── ocr/        # Text extraction
│   │   │       │   └── understanding/ # Vision LLM calls
│   │   │       └── text/           # Text preprocessing/NLP
│   │   └── ...
│   │
│   ├── voice-engine/
│   │   ├── src/
│   │   │   └── voice_engine/
│   │   │       ├── synthesis/      # Kokoro TTS
│   │   │       ├── streaming/      # Audio streaming
│   │   │       ├── providers/      # ElevenLabs fallback
│   │   │       └── audio/          # Audio processing utils
│   │   └── ...
│   │
│   ├── action-engine/
│   │   ├── src/
│   │   │   └── action_engine/
│   │   │       ├── pc_control/     # pyautogui + pynput
│   │   │       ├── file_system/    # File operations
│   │   │       ├── applications/   # App launch/control
│   │   │       ├── system/         # System monitoring
│   │   │       ├── safety/         # Action safety checks
│   │   │       └── audit/          # Action logging
│   │   └── ...
│   │
│   ├── browser-agent/
│   │   ├── src/
│   │   │   └── browser_agent/
│   │   │       ├── navigator/      # Playwright navigation
│   │   │       ├── extractor/      # Data extraction
│   │   │       ├── forms/          # Form handling
│   │   │       ├── research/       # Multi-page research
│   │   │       └── pool/           # Browser instance pool
│   │   └── ...
│   │
│   ├── knowledge-graph/
│   │   ├── src/
│   │   │   └── knowledge_graph/
│   │   │       ├── schema/         # Neo4j node/edge definitions
│   │   │       ├── indexer/        # Knowledge ingestion pipeline
│   │   │       ├── query/          # Cypher query builders
│   │   │       └── api/
│   │   └── ...
│   │
│   ├── integration-hub/
│   │   ├── src/
│   │   │   └── integration_hub/
│   │   │       ├── registry/       # Connector registry
│   │   │       ├── oauth/          # OAuth token management
│   │   │       └── connectors/
│   │   │           ├── base.py     # Base connector class
│   │   │           ├── google/     # Gmail, Calendar, Drive
│   │   │           ├── github/     # Repository operations
│   │   │           ├── notion/     # Notion workspace
│   │   │           └── ...
│   │   └── ...
│   │
│   └── api-gateway/
│       ├── src/
│       │   └── api_gateway/
│       │       ├── routes/         # Route definitions
│       │       ├── middleware/     # Auth, rate limit, logging
│       │       ├── auth/           # JWT + API key management
│       │       └── proxy/          # Service proxying
│       └── ...
│
├── apps/                           # Frontend applications
│   ├── aether-cli/                 # Textual TUI (Phase 1)
│   │   ├── src/
│   │   │   └── aether_cli/
│   │   │       ├── app.py          # Textual application
│   │   │       ├── widgets/        # Custom UI widgets
│   │   │       └── client/         # API client
│   │   └── pyproject.toml
│   │
│   ├── aether-desktop/             # Electron overlay (Phase 9)
│   │   ├── src/
│   │   │   ├── main/               # Electron main process
│   │   │   │   ├── index.ts
│   │   │   │   ├── window/         # Overlay window management
│   │   │   │   └── tray/           # System tray
│   │   │   ├── renderer/           # React UI
│   │   │   │   ├── app.tsx
│   │   │   │   ├── components/
│   │   │   │   ├── overlays/       # Context overlays
│   │   │   │   ├── panels/         # Information panels
│   │   │   │   └── presence/       # AI presence animation
│   │   │   └── preload/            # Electron preload scripts
│   │   └── package.json
│   │
│   ├── aether-dashboard/           # Next.js web UI
│   │   ├── src/
│   │   │   └── app/
│   │   │       ├── layout.tsx
│   │   │       ├── page.tsx
│   │   │       ├── conversations/
│   │   │       ├── agents/
│   │   │       ├── memory/
│   │   │       ├── settings/
│   │   │       └── automations/
│   │   └── package.json
│   │
│   └── aether-mobile/              # React Native (Phase 7)
│       ├── src/
│       │   ├── screens/
│       │   ├── components/
│       │   └── services/
│       └── package.json
│
├── packages/                       # Shared libraries
│   ├── aether-types/               # Shared TypeScript types
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── memory.types.ts
│   │   │   ├── agent.types.ts
│   │   │   └── api.types.ts
│   │   └── package.json
│   │
│   ├── aether-protocols/           # CATP protocol definitions
│   │   ├── src/
│   │   │   ├── catp/
│   │   │   └── events/
│   │   └── package.json
│   │
│   ├── aether-ui/                  # Shared React component library
│   │   ├── src/
│   │   │   ├── components/
│   │   │   └── theme/
│   │   └── package.json
│   │
│   └── aether-sdk/                 # Public SDK for extensions
│       ├── src/
│       │   ├── client.ts
│       │   └── types.ts
│       └── package.json
│
├── infrastructure/
│   ├── docker/
│   │   ├── compose/
│   │   │   ├── docker-compose.base.yml     # All services defined
│   │   │   ├── docker-compose.dev.yml      # Dev overrides (hot reload)
│   │   │   ├── docker-compose.prod.yml     # Production overrides
│   │   │   └── docker-compose.phase1.yml   # Phase 1 only (minimal)
│   │   └── configs/                        # Service-specific Docker configs
│   ├── kubernetes/                         # Phase 5+
│   │   ├── base/
│   │   └── overlays/
│   │       ├── development/
│   │       └── production/
│   └── scripts/
│       ├── setup.sh                        # First-time setup
│       ├── start.sh                        # Start all services
│       ├── health-check.sh                 # Verify all services healthy
│       └── reset.sh                        # Reset to clean state
│
├── tests/
│   ├── integration/                # Cross-service integration tests
│   ├── e2e/                        # End-to-end workflow tests
│   └── load/                       # Load and performance tests
│
├── .aether/                        # Aether system configuration
│   ├── config.yaml                 # Primary configuration
│   ├── permissions.yaml            # What Aether is allowed to do
│   └── personas/                   # Aether personality configurations
│
├── .env.example                    # Environment variable template
├── pyproject.toml                  # Root Python workspace config
├── package.json                    # Root Node workspace config
├── Makefile                        # Common developer commands
└── README.md
```

### 8.2 Service Internal Structure (Standard Pattern)

Every Python service follows this internal structure:

```
service-name/
├── src/
│   └── service_module/
│       ├── __init__.py
│       ├── main.py                 # FastAPI app + lifespan hooks
│       ├── config.py               # Pydantic settings from env vars
│       ├── models/                 # Pydantic data models
│       │   ├── __init__.py
│       │   ├── requests.py         # API request models
│       │   └── responses.py        # API response models
│       ├── api/                    # FastAPI route handlers (thin)
│       │   ├── __init__.py
│       │   ├── router.py           # Route registration
│       │   └── handlers/           # One file per endpoint group
│       ├── core/                   # Business logic (thick)
│       │   └── ...
│       ├── adapters/               # External service adapters
│       │   └── ...
│       └── utils/                  # Shared utilities
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── Dockerfile
├── pyproject.toml
├── alembic/                        # Database migrations (if needed)
└── README.md
```

---

## 9. RISK REGISTER

### 9.1 Risk Matrix

| Risk ID | Risk | Probability | Impact | Priority |
|---------|------|-------------|--------|----------|
| R-01 | Voice response latency exceeds acceptable threshold | Medium | High | P1 |
| R-02 | Agent infinite loops or deadlocks | Medium | High | P1 |
| R-03 | Memory system recall quality degrades at scale | High | High | P1 |
| R-04 | LLM provider API changes break core functionality | High | High | P1 |
| R-05 | Security breach via agentic action execution | Low | Critical | P1 |
| R-06 | LLM context window insufficient for memory retrieval | Medium | Medium | P2 |
| R-07 | Runaway LLM API costs | Medium | High | P2 |
| R-08 | Agent produces confidently wrong actions | Medium | High | P2 |
| R-09 | Cross-service dependency failure cascades | Low | High | P2 |
| R-10 | Long-term dependency rot / unmaintained packages | High | Medium | P2 |
| R-11 | Memory data corruption | Low | Critical | P3 |
| R-12 | Multi-agent coordination complexity explosion | Medium | Medium | P3 |
| R-13 | Cross-device sync conflicts | Low | Medium | P3 |

### 9.2 Mitigations

#### R-01: Voice Latency
- **Primary:** Streaming TTS (start speaking before full response generated)
- **Secondary:** Use Gemini Flash for simple/quick queries (faster than Claude)
- **Tertiary:** Local Kokoro TTS (eliminates API round-trip for speech)
- **Monitoring:** P95 latency alert at 1.5 seconds

#### R-02: Agent Infinite Loops
- **Primary:** Hard timeout on every agent task (configurable, default 120s)
- **Secondary:** Loop detection (same action attempted 3 times → abort)
- **Tertiary:** Circuit breaker pattern in Agent Runtime
- **Recovery:** Failed tasks escalate to user with context

#### R-03: Memory Recall Quality
- **Primary:** Hybrid retrieval (vector + keyword + graph — not just vector)
- **Secondary:** Regular memory consolidation to remove duplicates/noise
- **Tertiary:** Human feedback loop (user can mark memories as wrong/irrelevant)
- **Monitoring:** Sample recall quality on schedule; alert on degradation

#### R-04: LLM Provider Changes
- **Primary:** LiteLLM abstraction — all LLM calls go through one interface
- **Secondary:** Never hard-code model names in business logic; always config
- **Tertiary:** Maintain tested backup models for each tier

#### R-05: Security Breach
- **Primary:** Guardian Agent reviews all system-level actions before execution
- **Secondary:** Action sandbox — browser-agent has no local filesystem access
- **Tertiary:** Allowlists for what applications/paths Aether can access
- **Tertiary:** Audit log of every action Aether takes (immutable, append-only)
- **Emergency:** Kill switch that immediately disables all action-engine capabilities

#### R-07: Runaway LLM Costs
- **Primary:** Daily/monthly cost budgets with hard cutoffs in LiteLLM
- **Secondary:** Route simple tasks to smaller/cheaper models (Gemini Flash)
- **Tertiary:** Response caching for identical or near-identical queries
- **Tertiary:** Local models (Ollama) for classification, simple extraction tasks

#### R-08: Confidently Wrong Actions
- **Primary:** Confidence thresholds — agents below threshold escalate to user
- **Secondary:** Plan preview before execution for multi-step tasks
- **Tertiary:** Easy rollback — action engine logs all actions with reversal info

#### R-10: Dependency Rot
- **Primary:** Dependabot automated PRs + quarterly manual review
- **Secondary:** Abstraction layers over all major dependencies (LLM, vector DB, etc.)
- **Tertiary:** Keep a changelog of any dependency that is security-critical

---

## 10. ARCHITECTURE DECISION RECORDS

ADRs document every significant architectural choice, the alternatives considered, and the rationale. This section contains the foundational ADRs.

---

### ADR-001: Monorepo Architecture

**Status:** Accepted  
**Date:** Foundation Phase

**Decision:** Use a single monorepo for all Aether services, apps, and packages.

**Rationale:**
- During active development, cross-service changes are frequent. Monorepo eliminates version coordination overhead.
- Shared packages (`aether-types`, `aether-protocols`) are trivially consumed.
- Single CI/CD pipeline for consistent builds.
- Easier to enforce architectural standards across the codebase.

**Trade-offs:**
- Slower CI as the repo grows (mitigated by incremental builds)
- All developers have access to all code (acceptable for personal project)

**Alternatives considered:** Polyrepo — rejected due to overhead during early development.

---

### ADR-002: Python as Primary Backend Language

**Status:** Accepted

**Decision:** All backend services use Python 3.12+.

**Rationale:**
- AI/ML ecosystem is Python-native (LangGraph, sentence-transformers, Whisper, all Python-first)
- FastAPI provides production-grade async performance
- Richest selection of AI tooling
- Single language reduces context switching

**Trade-offs:**
- Python is slower than Go/Rust for CPU-bound work (mitigated by async I/O and offloading CPU work to specialized tools)

**Alternatives considered:** Go (missing AI ecosystem), Node.js (weaker AI ecosystem), Rust (too low-level for rapid development)

---

### ADR-003: LangGraph as Agent Foundation

**Status:** Accepted

**Decision:** Use LangGraph as the state machine infrastructure for agents, with a custom CATP layer on top for inter-service communication.

**Rationale:**
- LangGraph solves the hardest part of agentic systems: managing complex state across multi-step, potentially cyclic workflows
- Maintained by the LangChain team; production-proven
- Supports parallel execution branches natively
- State persistence built-in (essential for long-running tasks)

**Trade-offs:**
- Adds dependency on LangChain ecosystem
- Must abstract behind CATP to allow future replacement

**Alternatives considered:** CrewAI (less flexible), AutoGen (Microsoft ecosystem), Custom-only (enormous infrastructure investment)

---

### ADR-004: Qdrant for Vector Storage

**Status:** Accepted

**Decision:** Qdrant as the primary vector database for both episodic and semantic memory.

**Rationale:**
- Self-hosted with no cloud requirement (privacy-first)
- Written in Rust — fastest vector search performance available
- Production-grade: filtering alongside vector search, multiple distance metrics, quantization
- Multi-vector per record (store different embedding models' outputs for same record)
- Excellent Python SDK

**Trade-offs:**
- Separate service to manage (Chroma would be simpler — but less capable)
- More infrastructure than PostgreSQL+pgvector

**Alternatives considered:** Chroma (simpler, less production-ready), pgvector (simpler stack, lower performance), Weaviate (too complex for our needs)

---

### ADR-005: Local-First Architecture

**Status:** Accepted  
**This is a founding principle, not a debatable decision.**

**Decision:** All data storage, memory, and core processing runs locally. Cloud LLMs are called as needed but own no data.

**Rationale:**
- Privacy: years of personal context should never leave your machine
- Reliability: offline operation possible for core features
- Cost: no per-query storage costs
- Independence: not hostage to cloud provider decisions

**Trade-offs:**
- Requires adequate local hardware
- More complex deployment than cloud-first
- User responsible for backup

---

### ADR-006: FastAPI over Django/Flask

**Status:** Accepted

**Decision:** FastAPI for all Python web services.

**Rationale:**
- Native async — critical for I/O-heavy AI workloads (LLM calls, database queries)
- Automatic OpenAPI/Swagger documentation
- Pydantic validation built-in
- Highest performance Python web framework for I/O workloads
- Modern Python (type hints, async/await) throughout

**Alternatives considered:** Django (synchronous core, too opinionated), Flask (no async native, manual OpenAPI)

---

### ADR-007: Redis as Event Bus (Phase 1–4)

**Status:** Accepted (with Phase 5 review trigger)

**Decision:** Redis Streams as the event bus for inter-service communication.

**Rationale:**
- One technology for three needs: caching, pub/sub, task queues
- Extremely low latency
- Simple operations model
- Already required for session memory (L1)
- Consumer groups support (multiple agents can consume from same stream)

**Trigger for Replacement:** If sustained event throughput exceeds 50,000 events/second or if complex routing rules exceed Redis Streams capability → evaluate Apache Kafka.

**Alternatives considered:** RabbitMQ (heavier, more features than needed early), Kafka (excellent but complex for Phase 1 needs)

---

### ADR-008: Playwright for Browser Automation

**Status:** Accepted

**Decision:** Playwright (Python API) for all browser automation.

**Rationale:**
- Modern architecture — supports Chromium, Firefox, WebKit
- Native async Python API
- Better handling of SPAs than Selenium
- Auto-wait mechanisms reduce flaky tests
- Screenshot and video recording built-in
- Active development with excellent documentation

**Alternatives considered:** Selenium (legacy, slower, less reliable), Puppeteer (Node.js only)

---

### ADR-009: LiteLLM for LLM Abstraction

**Status:** Accepted

**Decision:** All LLM calls go through LiteLLM, never directly to provider APIs.

**Rationale:**
- Provider independence — switch Claude for Gemini in one config line
- Cost tracking per call
- Automatic fallback configuration
- Rate limiting and retry logic
- Consistent interface across 100+ providers

**Trade-offs:**
- Additional dependency
- Slight latency overhead (negligible vs LLM response time)

---

### ADR-010: Docker Compose for Phase 1–4 Deployment

**Status:** Accepted (with Phase 5 review trigger)

**Decision:** Docker Compose orchestrates all services for Phase 1 through Phase 4.

**Rationale:**
- Simple, well-understood, widely documented
- Single `docker compose up` to start entire system
- Easy port mapping and networking between services
- Service health checks built-in
- Adequate for personal deployment

**Trigger for Replacement:** Phase 5 multi-agent architecture may require advanced orchestration → evaluate Kubernetes or Nomad.

---

## 11. FUTURE EXPANSION STRATEGY

### 11.1 Near-Term Expansion (Year 2–3)

**Plugin System (Phase 5+)**  
Aether should support community-built agents and integrations without modifying core code. The plugin system:
- Defines a standard `BasePlugin` interface in `aether-sdk`
- Plugins declare capabilities, required permissions, and configuration
- Plugin registry manages discovery, installation, and sandboxed execution
- Plugins run in isolated containers — no access to core services except through defined APIs

**Custom Automation Workflows (Phase 8)**  
A workflow builder allows defining trigger→condition→action automation chains without code. Backend: stored as YAML in PostgreSQL; executed by a dedicated workflow engine (or n8n-compatible format).

**Multi-User Support (Phase 6+)**  
Architecture is designed to be multi-user from day one (all memory and sessions are namespaced by `user_id`). Activating multi-user support requires only authentication expansion, not database restructuring.

### 11.2 Mid-Term Expansion (Year 3–5)

**AR and Wearable Integration**  
Phase 9's floating UI is explicitly designed as a stepping stone to AR. The overlay window architecture maps directly to AR head-mounted displays:
- `aether-desktop` renders to a 2D overlay window today
- The same React components will render to an AR plane tomorrow
- WebXR API in modern browsers makes this transition incremental
- Target: Meta Ray-Ban API, Apple Vision Pro visionOS, Microsoft HoloLens

**Voice Persona System**  
Aether's voice and personality should be configurable per use case:
- Work persona: formal, efficient, concise
- Creative persona: exploratory, generative, playful
- Focus persona: minimal responses, only critical interruptions
- Each persona has: system prompt profile, voice settings, memory weighting, response style

**Advanced Memory: Emotional Context**  
Store not just what happened but the emotional context of interactions. Understand when the user is stressed, excited, or focused. Adapt responses accordingly. This requires both a sentiment analysis pipeline and memory schema extensions.

### 11.3 Long-Term Vision (Year 5+)

**Robotics Integration**  
The Action Engine's clean interface (`execute_action(type, params) → result`) is designed to abstract over action targets. Today those targets are a desktop OS. Future targets: ROS 2 robot actuators. The agent layer is already robotics-ready — only the action adapters need new implementations.

**Distributed Aether**  
A version of Aether where multiple agents run on specialized hardware:
- Memory-intensive agents on high-RAM server
- Vision agents on GPU node
- PC control agents on each workstation
- Unified memory that all nodes share via a distributed Qdrant cluster

**External Tool Ecosystem**  
Open the Integration Hub to third-party developers with:
- Connector SDK documentation
- Sandboxed connector execution
- Community connector registry
- Revenue sharing for commercial connectors

---

## 12. DEVELOPMENT WORKFLOW

### 12.1 Roles

| Role | Responsibility | Primary Tool |
|------|---------------|-------------|
| Chief Architect | Architecture, system design, documentation, design reviews, phase planning | This document + Claude Web |
| Implementer | Code generation, refactoring, implementation of designed components | Antigravity IDE (Claude Opus / Gemini Flash) |
| Product Owner | Vision, testing, decisions, final acceptance | Direct interaction + testing |

### 12.2 Development Cycle

**Before Each Phase:**
1. Chief Architect reviews and confirms architecture for the phase
2. Detailed component specifications written in `docs/phases/PHASE_N.md`
3. Antigravity receives specific implementation prompts (not vague requests)

**Implementation Pattern:**
1. Architect specifies: purpose, inputs, outputs, data models, error cases
2. Antigravity generates service skeleton + tests
3. Antigravity implements feature by feature, using existing patterns
4. Product Owner tests and provides feedback
5. Chief Architect reviews any architectural deviation before merging

**Prompt Engineering for Antigravity:**
When instructing Antigravity to build a component, always include:
- The relevant section of this blueprint
- The specific service's README
- The existing code patterns from that service
- The CATP protocol spec if agents are involved
- The exact inputs, outputs, and error conditions

**Anti-Patterns to Avoid:**
- Do NOT ask Antigravity to "build the memory system" — too vague
- DO ask Antigravity to "implement the `EpisodicMemoryStore.store()` method as specified in memory-nexus/README.md, storing a record to Qdrant and PostgreSQL with the schema defined in memory-nexus/src/memory_nexus/models/memory.py"

### 12.3 Documentation Requirements

Every service must maintain:
- `README.md` — Purpose, API summary, configuration, local development steps
- `docs/api/service-name.yaml` — OpenAPI specification
- Inline docstrings on all public functions and classes
- `CHANGELOG.md` — Following Keep a Changelog format

### 12.4 Testing Standards

| Level | Coverage Target | Tool |
|-------|----------------|------|
| Unit | 80% line coverage | Pytest |
| Integration | Key workflows covered | Pytest + TestContainers |
| Contract | All API contracts | Schemathesis (OpenAPI fuzzing) |
| E2E | Per-phase exit criteria scenarios | Custom test harness |

---

## 13. GLOSSARY

**Agent:** An autonomous reasoning unit with a defined role, capability declaration, and lifecycle. Not a function.

**CATP:** Communication and Task Protocol — the standard message format used for all inter-agent communication.

**Episodic Memory:** Memory of specific events and conversations, indexed by time and semantics.

**Knowledge Graph:** A graph structure of entities and their relationships, representing Aether's model of the world.

**LiteLLM:** An abstraction layer that provides a unified interface to multiple LLM providers.

**Memory Nexus:** The central service responsible for all memory tiers in Aether.

**Orchestrator Agent:** The top-level agent responsible for coordinating all other agents. Never executes directly.

**Perception Service:** The service responsible for transforming raw input (voice, screen, text) into structured data.

**Procedural Memory:** Memory of skills, workflows, and how-to knowledge.

**Semantic Memory:** Memory of facts and knowledge, independent of when they were learned.

**World Model:** Aether's persistent graph of entities (people, projects, places) and the relationships between them.

---

## APPENDIX A: QUICK REFERENCE — TECHNOLOGY CHOICES

| Category | Choice | Alternative Considered |
|----------|--------|----------------------|
| Backend Language | Python 3.12+ | Go, Node.js |
| Web Framework | FastAPI | Django, Flask |
| Agent Framework | LangGraph + CATP | CrewAI, AutoGen |
| LLM Router | LiteLLM | Direct API calls |
| Vector DB | Qdrant | Chroma, pgvector |
| Relational DB | PostgreSQL 16 | MySQL, SQLite |
| Graph DB | Neo4j | ArangoDB, TigerGraph |
| Cache/Bus | Redis 7 (Streams) | RabbitMQ, Kafka |
| STT | Whisper (faster-whisper) | Deepgram, AssemblyAI |
| TTS | Kokoro (local) + ElevenLabs | Coqui, Azure TTS |
| VAD | Silero VAD | WebRTC VAD |
| Browser Automation | Playwright | Selenium |
| PC Control | pyautogui + pynput | AutoHotkey |
| Screen Capture | mss | pygetwindow |
| Containerization | Docker + Compose | Podman |
| Desktop App | Electron + React | Tauri, Qt |
| Web App | Next.js 15 | Remix, SvelteKit |
| Mobile | React Native + Expo | Flutter |
| Observability | OpenTelemetry + Grafana | Datadog |
| Package Manager (Py) | Poetry | pip, conda |
| Package Manager (JS) | pnpm | npm, yarn |

---

## APPENDIX B: PHASE 1 IMPLEMENTATION CHECKLIST

Use this as the first implementation briefing for Antigravity IDE.

- [ ] Initialize monorepo structure (`aether-os/`)
- [ ] Configure root `pyproject.toml` (workspace) and `package.json`
- [ ] Create `infrastructure/docker/compose/docker-compose.phase1.yml`
- [ ] Define base Docker images for Python services
- [ ] Scaffold `api-gateway` service with health check endpoint
- [ ] Scaffold `aether-core` service with session management
- [ ] Scaffold `memory-nexus` service with L0 (working) and L1 (Redis session)
- [ ] Scaffold `voice-engine` service with Whisper STT
- [ ] Implement basic conversation loop in `aether-core`
- [ ] Implement L2 episodic memory (Qdrant + PostgreSQL) in `memory-nexus`
- [ ] Implement TTS (Kokoro) in `voice-engine`
- [ ] Build `aether-cli` with Textual TUI
- [ ] End-to-end test: voice input → response → stored in episodic memory
- [ ] Verify cross-session memory recall
- [ ] Document: Phase 1 complete

---

*This document is the authoritative reference for Aether AI OS development decisions.*  
*All architectural changes must be reflected here before implementation begins.*  
*Version this document alongside the codebase. It is not documentation — it is architecture.*

---

**AETHER AI OS — MASTER BLUEPRINT v1.0**  
*"Not a chatbot. An operating system for intelligence."*
