# AETHER AI OS — MASTER ARCHITECTURE BLUEPRINT
### Version 1.0 | Chief Architect Edition
### Classification: Project Foundation Document

---

> *"The goal is not to build a chatbot. The goal is to build an intelligent ecosystem that thinks, plans, executes, remembers, and grows alongside its owner — a second mind."*

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Vision Analysis](#2-vision-analysis)
3. [System Architecture](#3-system-architecture)
4. [Development Roadmap](#4-development-roadmap)
5. [Agent Ecosystem Design](#5-agent-ecosystem-design)
6. [Memory Architecture](#6-memory-architecture)
7. [Technology Stack](#7-technology-stack)
8. [Repository Structure](#8-repository-structure)
9. [Risk Analysis](#9-risk-analysis)
10. [Future Expansion Strategy](#10-future-expansion-strategy)
11. [Master Blueprint Summary](#11-master-blueprint-summary)

---

## 1. EXECUTIVE SUMMARY

Aether AI OS is a long-term personal AI operating system. It is not a product in the conventional sense — it is a *platform* that will grow in capability, intelligence, and integration depth over several years. Every architectural decision made today must accommodate features that do not yet exist.

The system must function as a **personal AI companion, task executor, knowledge repository, and digital environment controller** — unified under a single, coherent intelligence layer.

The architecture is designed around five non-negotiable principles:

| Principle | Implementation |
|---|---|
| **Modularity** | Every subsystem is independently deployable and replaceable |
| **Scalability** | Architecture handles personal use today, team use tomorrow |
| **Agent-first** | All intelligent behavior is implemented as autonomous agents |
| **Memory-driven** | All context, history, and knowledge persists and is retrievable |
| **Event-driven** | All subsystems communicate via an internal event bus |

---

## 2. VISION ANALYSIS

### 2.1 Project Interpretation

Aether is architecturally distinct from existing AI assistants in four critical ways:

**1. Persistent Identity**
Unlike ChatGPT or standalone Claude, Aether maintains continuous memory across every session, across every device, across every modality. It knows who you are, what you have done, what you are building, and what you care about.

**2. Agentic Authority**
Aether does not just suggest — it executes. It can control software, automate browsers, write and run code, manage files, and coordinate multi-step plans without continuous human supervision.

**3. Modular Intelligence**
Aether is not a single model call. It is an orchestrated ecosystem of specialized agents, each responsible for a domain, coordinated by a supervisor that understands intent, context, and priority.

**4. Environmental Awareness**
Through vision, PC control, and browser automation, Aether understands and interacts with the digital environment — not just language.

### 2.2 Long-Term Objectives

| Objective | Description |
|---|---|
| **Natural Interaction** | Seamless voice-first conversation with sub-500ms response loop |
| **Persistent Memory** | Recall any fact, task, or conversation from any point in history |
| **Autonomous Execution** | Complete multi-step tasks without step-by-step user guidance |
| **System Control** | Control any software on the host machine |
| **Continuous Learning** | Improve from experience through memory consolidation |
| **Cross-Device Presence** | Consistent identity across PC, phone, and future devices |
| **Developer Augmentation** | Accelerate development workflows through deep integration |
| **Business Automation** | Automate routine business operations end-to-end |

### 2.3 Core Technical Challenges

**Challenge 1: Context Window vs. Long-Term Memory**
LLM context windows have hard limits. Aether must implement a sophisticated memory retrieval system that surfaces only the most relevant memories per task, making infinite history feel present without overloading the context.

**Challenge 2: Agent Reliability**
Agents can hallucinate, loop, or fail silently. Every agent must have structured output validation, timeout handling, fallback strategies, and human-in-the-loop escalation paths.

**Challenge 3: PC/System Control Security**
Granting an AI system control over a personal computer introduces significant attack surface. A sandboxed permission model with user-defined capability boundaries is mandatory.

**Challenge 4: Voice Latency**
A voice-first system must complete the STT → LLM → TTS pipeline in under 800ms to feel natural. This requires careful model selection, streaming architecture, and local processing where possible.

**Challenge 5: Agent Coordination**
Multiple agents operating concurrently can deadlock, duplicate work, or produce conflicting outputs. Agent orchestration must include task locking, shared state management, and conflict resolution.

**Challenge 6: Upgrade Path Without Breakage**
A 10-phase system that evolves over years must maintain backward compatibility. Every API boundary, data schema, and event contract must be versioned from day one.

---

## 3. SYSTEM ARCHITECTURE

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AETHER AI OS                              │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  INTERFACES  │  │    AGENTS    │  │     MEMORY       │  │
│  │              │  │              │  │                  │  │
│  │  Voice I/O   │  │ Orchestrator │  │  Working Memory  │  │
│  │  Web Dashboard│  │   Planner    │  │  Episodic Store  │  │
│  │  Desktop HUD │  │   Executor   │  │  Semantic Store  │  │
│  │  Mobile App  │  │   Researcher │  │ Knowledge Graph  │  │
│  │  CLI / API   │  │    Coder     │  │                  │  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬──────────┘  │
│         │                 │                  │              │
│  ═══════╪═════════════════╪══════════════════╪═══════════   │
│                   CORE EVENT BUS                            │
│  ═══════╪═════════════════╪══════════════════╪═══════════   │
│         │                 │                  │              │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌───────┴──────────┐  │
│  │   SERVICES   │  │ INTEGRATIONS │  │ INFRASTRUCTURE   │  │
│  │              │  │              │  │                  │  │
│  │  PC Control  │  │  LLM Router  │  │  Config Manager  │  │
│  │  Browser Svc │  │  Tool System │  │  Logging/Tracing │  │
│  │  Vision Svc  │  │  External APIs│  │  Secret Manager  │  │
│  │  Task Manager│  │  Webhooks    │  │  Health Monitor  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Core Subsystems

#### 3.2.1 The Kernel
The kernel is the heartbeat of Aether. It is responsible for:
- Booting and initializing all subsystems in dependency order
- Maintaining the service registry
- Exposing the plugin/extension API
- Managing global configuration and secrets
- Health monitoring and self-healing of crashed services

The kernel does NOT contain business logic. It is pure infrastructure.

#### 3.2.2 The Event Bus
Every subsystem communicates exclusively through the event bus. No direct service-to-service calls at the architectural level. This ensures:
- Complete decoupling between subsystems
- Easy addition of new subscribers without modifying producers
- Full audit trail of all system events
- Replay capability for debugging and testing

**Event Schema (versioned from day one):**
```
{
  "event_id": "uuid-v4",
  "event_type": "agent.task.completed",
  "event_version": "1.0",
  "source": "executor_agent",
  "timestamp": "ISO-8601",
  "correlation_id": "uuid-v4",
  "payload": { ... },
  "metadata": { "user_id": "...", "session_id": "..." }
}
```

#### 3.2.3 The Agent Orchestrator
The single entry point for all intelligent behavior. Receives goals/intents from the interface layer, decomposes them, routes them to the correct agents, monitors execution, and returns unified responses. Detailed in Section 5.

#### 3.2.4 The Memory System
A multi-tier system that stores, retrieves, and consolidates information across all time horizons. Detailed in Section 6.

#### 3.2.5 The Service Layer
Encapsulates all external capabilities: PC control, browser automation, vision processing, voice I/O, and task management. Services expose clean interfaces to the agent layer and emit events to the bus.

#### 3.2.6 The Interface Layer
Translates user input/output across modalities: voice, web UI, desktop overlay, mobile, and CLI/API. All interfaces translate to a unified internal intent format before passing to the orchestrator.

### 3.3 Service Boundaries

```
BOUNDARY: Interface Layer → Agent Layer
  Protocol: Intent Objects (structured JSON)
  No raw text crosses this boundary.

BOUNDARY: Agent Layer → Service Layer
  Protocol: Typed Tool Calls
  Agents call services through a typed tool interface only.

BOUNDARY: Service Layer → External World
  Protocol: HTTP / WebSocket / System API
  All external I/O is isolated to service adapters.

BOUNDARY: Any Layer → Memory System
  Protocol: Memory Operations API (read/write/search)
  No service accesses the database directly.

BOUNDARY: Any Layer ↔ Event Bus
  Protocol: Typed, versioned events
  All inter-subsystem communication flows through the bus.
```

### 3.4 Concurrency and Process Model

```
Process 1: aether-core
  - Kernel, event bus, service registry
  - Always running, restarts automatically

Process 2: aether-agents
  - Agent orchestrator and all agents
  - Spawns worker threads per task

Process 3: aether-memory
  - Memory consolidation daemon
  - Background embedding generation
  - Knowledge graph maintenance

Process 4: aether-voice  (Phase 1)
  - Voice activity detection loop
  - STT/TTS pipeline
  - Always running when voice enabled

Process 5: aether-browser  (Phase 3)
  - Persistent browser context
  - Playwright session management

Process 6: aether-vision  (Phase 6)
  - Screen capture loop
  - Vision analysis workers
```

---

## 4. DEVELOPMENT ROADMAP

### Roadmap Overview

```
Phase 1  ──► Phase 2  ──► Phase 3  ──► Phase 4  ──► Phase 5
Foundation    PC Control   Browser      Coding        Multi-Agent
(Core OS)     (System)     (Web)        (Dev)         (Orchestration)
    │             │             │             │              │
    └─────────────┴─────────────┴─────────────┴──────────────┘
                                                              │
                                                         Phase 6
                                                          Vision
                                                              │
                                                         Phase 7
                                                          Mobile
                                                              │
                                                         Phase 8
                                                          Business
                                                              │
                                                         Phase 9
                                                          Float UI
                                                              │
                                                         Phase 10
                                                          Holographic
```

---

### PHASE 1 — FOUNDATION
**Codename:** Genesis
**Duration:** 8–12 weeks
**Goal:** Build the core OS infrastructure that every future phase depends on.

#### Deliverables
- [ ] Aether Kernel (process manager, service registry, config system)
- [ ] Core Event Bus (Redis Pub/Sub backed, typed event schemas)
- [ ] Plugin/Service framework (register, discover, invoke services)
- [ ] LLM Router Service (abstract over Claude/GPT/local, model selection logic)
- [ ] Basic Agent Framework (base agent class, tool use interface, structured output)
- [ ] Memory System v1 (short-term conversation memory, basic persistence)
- [ ] Conversational Agent v1 (single-turn and multi-turn chat)
- [ ] Task Manager Service (create, track, update, complete tasks)
- [ ] Knowledge Store v1 (ingest documents, retrieve by semantic search)
- [ ] CLI Interface (text-based interaction, dev tooling)
- [ ] Voice Pipeline v1 (STT + TTS, wake word detection)
- [ ] Web Dashboard v1 (chat UI, task view, basic settings)
- [ ] Logging & Tracing infrastructure
- [ ] Configuration management system
- [ ] Secret/credential manager

#### Architecture Foundation Rules (Phase 1)
- Every service must register with the service registry before accepting traffic
- Every LLM call goes through the LLM Router (never direct API calls from agents)
- Every memory read/write goes through the Memory API (never direct DB access)
- All events are logged to an event store from day one
- Config is environment-based (dev/prod) from day one

#### Key Milestones
- M1.1: Kernel boots, event bus live, services register
- M1.2: Single LLM-powered conversation with memory persistence
- M1.3: Voice I/O fully operational, sub-800ms response loop
- M1.4: Task creation and tracking working end-to-end
- M1.5: Document ingestion and semantic retrieval functional

#### Phase 1 Dependencies
- None. This is the foundation all other phases depend on.

---

### PHASE 2 — PC CONTROL
**Codename:** Operator
**Duration:** 6–8 weeks
**Depends on:** Phase 1 complete, Event Bus stable

#### Deliverables
- [ ] PC Control Service (OS abstraction layer for Windows/macOS/Linux)
- [ ] Application Launcher (open, close, focus apps by name or intent)
- [ ] File System Service (browse, read, write, search, organize files)
- [ ] System Monitor Service (CPU, memory, disk, network, process list)
- [ ] Clipboard Service (read/write clipboard)
- [ ] Notification Service (send desktop notifications)
- [ ] Executor Agent v1 (executes PC control commands safely)
- [ ] Capability Permission System (user-approved capability boundaries)
- [ ] Audit Log (every system action is logged with user attribution)

#### Security Requirements (Phase 2)
- All PC control actions require a capability token granted by the user
- Destructive operations (file deletion, process kill) require explicit confirmation
- A capability boundary file defines what Aether is allowed to do
- All executed actions are reversible where possible (soft deletes, undo stack)
- The permission system must be expandable — never hardcoded rules

#### Key Milestones
- M2.1: Open/close/focus applications on command
- M2.2: File operations working (search, read, move, organize)
- M2.3: System monitoring dashboard live
- M2.4: Permission system fully functional with user configuration

---

### PHASE 3 — BROWSER AUTOMATION
**Codename:** Navigator
**Duration:** 6–8 weeks
**Depends on:** Phase 1 + Phase 2 stable

#### Deliverables
- [ ] Browser Service (Playwright-backed, persistent session management)
- [ ] Web Navigation Agent (navigate, click, type, extract data)
- [ ] Form Filling Service (identify and fill web forms intelligently)
- [ ] Web Research Agent (search, read, synthesize web content)
- [ ] Data Extraction Pipeline (structured extraction from web pages)
- [ ] Screenshot and DOM inspection capability
- [ ] Session Manager (save/restore browser sessions)
- [ ] Anti-detection layer (ethical use only, no bypass of legitimate auth)

#### Key Milestones
- M3.1: Navigate to URLs, click elements, fill forms on command
- M3.2: Research task: given a topic, return synthesized findings
- M3.3: Data extraction: given a URL and schema, return structured data
- M3.4: Multi-step web workflow completed autonomously

---

### PHASE 4 — CODING ASSISTANT
**Codename:** Forge
**Duration:** 6–8 weeks
**Depends on:** Phase 1 + Phase 2 stable

#### Deliverables
- [ ] Coding Agent v1 (generate, explain, review, debug code)
- [ ] Repository Service (git operations: clone, commit, branch, push)
- [ ] Code Execution Service (sandboxed code runner, output capture)
- [ ] File Editor Service (read, write, patch files with diff awareness)
- [ ] Development Workflow Service (build, test, lint automation)
- [ ] IDE Integration Bridge (communicate with Antigravity IDE)
- [ ] Code Search Service (semantic and structural code search)

#### Key Milestones
- M4.1: Generate code for a described task, write it to file
- M4.2: Debug a failing test by reading logs and patching code
- M4.3: Full git workflow: branch, commit, push on command
- M4.4: Integrated with Antigravity IDE (bidirectional communication)

---

### PHASE 5 — MULTI-AGENT ARCHITECTURE
**Codename:** Constellation
**Duration:** 10–14 weeks
**Depends on:** Phases 1–4 all stable; this phase refactors existing agents

#### Deliverables
- [ ] LangGraph-based Agent Orchestration Framework
- [ ] Planner Agent v1 (goal decomposition, task graph generation)
- [ ] Executor Agent v2 (upgraded with tool selection and rollback)
- [ ] Memory Agent v1 (dedicated agent for all memory operations)
- [ ] Research Agent v1 (upgraded web research with synthesis)
- [ ] Coding Agent v2 (multi-file, multi-step coding tasks)
- [ ] Agent Communication Protocol (how agents delegate to each other)
- [ ] Task Queue and Priority System
- [ ] Human-in-the-loop escalation framework
- [ ] Agent monitoring dashboard

#### Key Milestones
- M5.1: Planner decomposes a complex goal into a task graph
- M5.2: Executor completes a 5-step task using multiple tools
- M5.3: Memory Agent handles all memory ops transparently
- M5.4: Full multi-agent workflow: "Research X, summarize findings, write code to process them, commit to repo"

---

### PHASE 6 — VISION CAPABILITIES
**Codename:** Iris
**Duration:** 6–8 weeks
**Depends on:** Phase 5 (agents must be mature before adding vision)

#### Deliverables
- [ ] Screen Capture Service (real-time, region-selective, efficient)
- [ ] Vision Agent (analyze screenshots, describe UI state, extract text)
- [ ] UI Interaction via Vision (click coordinates derived from vision analysis)
- [ ] OCR Pipeline (extract text from images and screen regions)
- [ ] Visual Memory (store and retrieve screenshots as memories)
- [ ] Screen Change Detection (alert on meaningful screen changes)

---

### PHASE 7 — MOBILE INTEGRATION
**Codename:** Reach
**Duration:** 10–14 weeks
**Depends on:** Phase 1 core must be API-stable

#### Deliverables
- [ ] Aether Mobile App (React Native, iOS + Android)
- [ ] Aether Sync Service (cross-device state synchronization)
- [ ] Push Notification System (intelligent, context-aware alerts)
- [ ] Mobile Voice Interface (on-device STT with cloud fallback)
- [ ] Background Sync Agent (keeps mobile up-to-date passively)
- [ ] Secure Mobile Auth (biometric + token)

---

### PHASE 8 — BUSINESS AUTOMATION
**Codename:** Hermes
**Duration:** 8–10 weeks
**Depends on:** Phases 3, 4, 5 stable

#### Deliverables
- [ ] Business Workflow Engine (define, trigger, execute workflows)
- [ ] CRM Integration Service (HubSpot, Salesforce adapters)
- [ ] Email Automation Agent (compose, send, manage email campaigns)
- [ ] Lead Management Agent (track, qualify, follow up)
- [ ] Marketing Automation Workflows (content, scheduling, analytics)
- [ ] Calendar and Scheduling Agent
- [ ] Business Intelligence Dashboard

---

### PHASE 9 — FLOATING ASSISTANT INTERFACE
**Codename:** Specter
**Duration:** 8–12 weeks
**Depends on:** Phase 7 + mature voice pipeline

#### Deliverables
- [ ] Always-on Desktop Overlay (Tauri-based, minimal footprint)
- [ ] Floating Widget System (draggable, collapsible, always-on-top)
- [ ] Ambient Listening Mode (passive, context-aware)
- [ ] Real-time Overlay Rendering (display info on screen regions)
- [ ] Meta-glass Inspired Visual Language (design system)
- [ ] Gesture and Hotkey Control
- [ ] Context-aware Sidebar (shows relevant info for current task)

---

### PHASE 10 — HOLOGRAPHIC INTERFACE
**Codename:** Prism
**Duration:** 12–18 months from Phase 9
**Depends on:** Phase 9 + emerging XR hardware

#### Deliverables
- [ ] AR/XR Runtime Adapter (Apple Vision Pro, Meta Quest)
- [ ] 3D Information Space (spatial memory visualization)
- [ ] Holographic Data Display (charts, feeds, notifications in 3D space)
- [ ] Spatial Agent Interface (interact with Aether in 3D space)
- [ ] Environmental Awareness (understand physical context via cameras)

---

## 5. AGENT ECOSYSTEM DESIGN

### 5.1 Agent Hierarchy

```
                    ┌─────────────────────┐
                    │   USER / INTERFACE  │
                    └──────────┬──────────┘
                               │ Intent
                    ┌──────────▼──────────┐
                    │    ORCHESTRATOR     │
                    │  (Supervisor Agent) │
                    └──┬───┬───┬───┬──┬──┘
                       │   │   │   │  │
              ┌────────┘   │   │   │  └────────┐
              │        ┌───┘   └───┐           │
         ┌────▼────┐ ┌─▼──────┐ ┌─▼──────┐ ┌──▼─────┐
         │PLANNER  │ │EXECUTOR│ │MEMORY  │ │RESEARCH│
         │ Agent   │ │ Agent  │ │ Agent  │ │ Agent  │
         └────┬────┘ └───┬────┘ └───┬────┘ └──┬─────┘
              │          │          │          │
         ┌────▼────┐ ┌───▼────┐     │     ┌────▼────┐
         │  Task   │ │  Tool  │     │     │  Web    │
         │  Graph  │ │  Pool  │     │     │  Tools  │
         └─────────┘ └────────┘     │     └─────────┘
                              ┌─────▼─────┐
                              │  Memory   │
                              │  System   │
                              └───────────┘

              ┌────────────┐    ┌─────────────┐
              │  CODER     │    │  VOICE      │
              │  Agent     │    │  Agent      │
              └────────────┘    └─────────────┘
```

### 5.2 The Orchestrator (Supervisor Agent)

**Role:** The single routing intelligence for all incoming requests.

**Responsibilities:**
- Parse and classify user intent
- Determine which agent(s) are needed
- Create an execution plan
- Delegate tasks to agents
- Monitor agent progress and handle failures
- Synthesize outputs from multiple agents into a coherent response
- Decide when human confirmation is needed

**Design Pattern:** ReAct + Supervisor (LangGraph StateGraph)

**State it maintains:**
```python
class OrchestratorState:
    user_intent: Intent
    active_tasks: List[Task]
    agent_outputs: Dict[str, AgentOutput]
    conversation_context: ConversationContext
    execution_plan: ExecutionPlan
    requires_confirmation: bool
    escalation_reason: Optional[str]
```

---

### 5.3 The Planner Agent

**Role:** Decomposes complex goals into executable task graphs.

**Responsibilities:**
- Receive a high-level goal
- Break it into ordered, parallel, or conditional steps
- Identify required tools and agents per step
- Estimate resource requirements
- Produce a structured task graph
- Revise plan if execution fails or conditions change

**Output Format:**
```json
{
  "plan_id": "uuid",
  "goal": "Research quantum computing startups and prepare an investment brief",
  "steps": [
    {
      "step_id": "s1",
      "action": "research",
      "agent": "research_agent",
      "input": "quantum computing startups 2024–2025",
      "depends_on": [],
      "parallel_ok": false
    },
    {
      "step_id": "s2",
      "action": "structure_data",
      "agent": "executor_agent",
      "input": "extract company names, funding, founders from s1 output",
      "depends_on": ["s1"],
      "parallel_ok": false
    },
    {
      "step_id": "s3",
      "action": "write_document",
      "agent": "coder_agent",
      "input": "generate markdown investment brief from s2 output",
      "depends_on": ["s2"],
      "parallel_ok": false
    }
  ]
}
```

---

### 5.4 The Executor Agent

**Role:** Takes individual, well-defined tasks and executes them using the tool pool.

**Responsibilities:**
- Select the correct tool(s) for the task
- Execute tools with structured inputs
- Validate tool outputs
- Retry on failure with modified approach
- Log every action for the audit trail
- Roll back incomplete actions when possible

**Tool Pool (Phase 1–5):**
```
file_read         file_write        file_search
app_open          app_close         app_focus
browser_navigate  browser_click     browser_extract
code_run          code_write        git_commit
memory_search     memory_write      web_search
notify_user       ask_user          calendar_read
```

Each tool is implemented as an independent, typed module with:
- Input schema (Pydantic model)
- Output schema (Pydantic model)
- Error schema
- Retry policy
- Audit log entry

---

### 5.5 The Memory Agent

**Role:** Handles ALL memory operations for all agents. No other agent touches the database directly.

**Responsibilities:**
- Write new memories (facts, events, summaries)
- Retrieve relevant memories for a given query
- Consolidate short-term into long-term memory
- Prune stale or redundant memories
- Maintain the knowledge graph
- Generate embeddings for semantic search
- Respond to "what do I know about X" queries

---

### 5.6 The Research Agent

**Role:** Autonomous web research and knowledge synthesis.

**Responsibilities:**
- Formulate search strategies for a research goal
- Execute multiple searches across multiple sources
- Read and comprehend web pages at depth
- Cross-reference and validate information
- Synthesize findings into structured summaries
- Identify conflicting information and flag it
- Store research outputs to memory automatically

---

### 5.7 The Coding Agent

**Role:** Write, understand, debug, and manage code.

**Responsibilities:**
- Generate code from natural language descriptions
- Understand and explain existing codebases
- Debug errors from logs and stack traces
- Refactor code to match patterns and standards
- Write and run tests
- Manage git operations
- Integrate with Antigravity IDE as a peer

---

### 5.8 The Voice Agent

**Role:** Manages all voice input/output processing.

**Responsibilities:**
- Continuously monitor audio input (wake word detection)
- Transcribe speech to text (STT pipeline)
- Convert text responses to speech (TTS pipeline)
- Manage voice activity detection and silence detection
- Handle interruptions and barge-in
- Adapt voice persona based on context

**Voice Pipeline:**
```
Microphone → VAD → Wake Word → STT → Intent → Orchestrator
Orchestrator → Response Text → TTS → Audio Output → Speaker
```

---

### 5.9 Future Agents (Phases 6–10)

| Agent | Phase | Responsibility |
|---|---|---|
| Vision Agent | 6 | Screen understanding, UI analysis |
| Notification Agent | 7 | Smart alert management |
| Scheduler Agent | 8 | Calendar and time management |
| CRM Agent | 8 | Lead and contact management |
| Automation Agent | 8 | Business workflow execution |
| Security Agent | Cross-cut | Monitor for anomalies, enforce permissions |
| Self-Improvement Agent | Long-term | Analyze usage patterns, suggest optimizations |

---

## 6. MEMORY ARCHITECTURE

### 6.1 Multi-Tier Memory Model

Aether's memory system is modeled on how human memory actually works — multiple tiers with different access speeds, capacities, and lifetimes.

```
TIER 0 — Working Memory (In-process, microseconds)
  ├── Current conversation context (last N turns)
  ├── Active task state
  ├── Agent intermediate outputs
  └── Holds while processing; discarded after

TIER 1 — Short-Term Memory (Redis, seconds to hours)
  ├── Recent conversation summaries
  ├── Session context
  ├── Active goals and tasks
  └── TTL: configurable, default 24 hours

TIER 2 — Long-Term Memory (PostgreSQL + Vector DB, permanent)
  ├── User facts ("User is building a startup called Aether")
  ├── Historical conversation summaries
  ├── Learned preferences and patterns
  ├── Task history and outcomes
  └── Stored indefinitely; retrieved by relevance

TIER 3 — Knowledge Store (Qdrant vector DB, permanent)
  ├── Ingested documents
  ├── Research outputs
  ├── Domain knowledge
  └── Retrieved by semantic similarity

TIER 4 — Knowledge Graph (Neo4j, future Phase 3+)
  ├── Entity relationships
  ├── Concept connections
  ├── Causal chains
  └── Retrieved by graph traversal
```

### 6.2 Memory Operations

All memory operations go through a single Memory API surface:

```python
class MemoryAPI:

    # Write operations
    def remember(fact: str, context: dict, importance: float) -> MemoryID
    def log_event(event: Event, extract_facts: bool = True) -> MemoryID
    def ingest_document(doc: Document, namespace: str) -> List[MemoryID]

    # Read operations
    def recall(query: str, k: int = 10, filters: dict = {}) -> List[Memory]
    def get_recent(hours: int = 24) -> List[Memory]
    def search_knowledge(query: str, namespace: str = "*") -> List[Knowledge]

    # Maintenance operations
    def consolidate() -> ConsolidationReport  # Background job
    def reflect() -> Insight                  # Generate insights from patterns
    def forget(memory_id: MemoryID, reason: str) -> bool
```

### 6.3 Memory Consolidation Pipeline

This background process runs on a schedule (e.g., every 6 hours):

```
1. GATHER: Collect all Tier 1 memories approaching TTL expiry
2. SUMMARIZE: Use LLM to extract key facts and events
3. DEDUPLICATE: Check against existing long-term memories
4. EMBED: Generate vector embeddings for new facts
5. STORE: Write to Tier 2 and Tier 3
6. PRUNE: Remove consolidated items from Tier 1
7. REFLECT: Generate higher-level insights from patterns
8. REPORT: Log consolidation stats to system monitor
```

### 6.4 Memory Retrieval Strategy

When an agent needs context for a task, the Memory Agent runs a **hybrid retrieval** pipeline:

```
Query: "What does the user want me to build for them?"

Step 1: Semantic Search (Qdrant)
  → Find semantically similar memories via embedding comparison
  → Top-K candidates returned

Step 2: Keyword Search (PostgreSQL full-text)
  → Find exact-match or near-match memories
  → Boosted by recency

Step 3: Graph Lookup (Neo4j, Phase 3+)
  → Traverse relationships from known entities

Step 4: Reranking
  → Score candidates by: relevance score × recency weight × importance score

Step 5: Context Assembly
  → Format top memories into a concise context block
  → Respect token budget for LLM context window
```

### 6.5 Memory Schema (Core)

```python
@dataclass
class Memory:
    id: UUID
    content: str                        # The actual fact or summary
    embedding: List[float]              # Vector representation
    source: MemorySource                # conversation | document | event | agent
    importance: float                   # 0.0 to 1.0
    created_at: datetime
    last_accessed_at: datetime
    access_count: int
    tags: List[str]
    entities: List[str]                 # Named entities for graph linking
    session_id: Optional[UUID]
    expiry: Optional[datetime]          # None = permanent
    meta: dict                          # Extensible metadata
```

---

## 7. TECHNOLOGY STACK

### 7.1 Language Decisions

| Language | Role | Rationale |
|---|---|---|
| **Python 3.12+** | Core backend, all agents, all services | Ecosystem dominance in AI/ML, LangGraph, LangChain, every AI library is Python-first |
| **TypeScript** | Web dashboard, API gateway, Electron overlay | Type safety for UI and API contracts |
| **Rust** | Performance-critical services (audio, screen capture) | Memory safety, zero-cost abstractions, no GC pauses in real-time pipelines |
| **Kotlin/Swift** | Mobile app (Phase 7) | Native performance for mobile voice and push notifications |

### 7.2 AI / Agent Orchestration

| Tool | Role |
|---|---|
| **LangGraph** | Primary agent orchestration — state machine for multi-agent graphs, native checkpointing, human-in-the-loop, streaming |
| **LangChain** | Tool integration, document loaders, text splitters |
| **Anthropic SDK** | Claude API (primary LLM for reasoning and planning) |
| **OpenAI SDK** | GPT-4o fallback, embeddings (text-embedding-3-large) |
| **Pydantic** | All data models, tool input/output schemas, validation |
| **instructor** | Structured output extraction from LLM responses |

### 7.3 Memory / Database

| Technology | Role |
|---|---|
| **Redis 7** | Event bus (Pub/Sub + Streams), Tier 1 memory, session cache, rate limiting |
| **PostgreSQL 16** | Tier 2 long-term memory, task data, user config, audit logs |
| **Qdrant** | Vector store for semantic memory, knowledge base search. Self-hosted, open source |
| **pgvector** | Fallback vector search in PostgreSQL (Phase 1, simpler infra) |
| **Neo4j** | Knowledge graph (Phase 3+, add when entity relationships become complex) |
| **SQLite** | Local-first fallback, embedded device usage, testing |

> **Phase 1 simplification:** Start with PostgreSQL + pgvector. Migrate to Qdrant when vector search query volume grows or performance demands it. Neo4j deferred until Phase 3.

### 7.4 Voice Stack

| Component | Technology | Rationale |
|---|---|---|
| **Wake Word** | Porcupine (Picovoice) | On-device, low CPU, high accuracy, no cloud call needed |
| **VAD** | Silero VAD | Fast, accurate, runs locally |
| **STT** | Deepgram (cloud) / Whisper.cpp (local fallback) | Deepgram: <300ms latency streaming. Whisper: full privacy |
| **TTS** | ElevenLabs (primary) / Edge TTS (fallback) | ElevenLabs: most natural. Edge: free, fast fallback |
| **Audio I/O** | sounddevice (Python) / PortAudio | Cross-platform, reliable |

### 7.5 Browser Automation

| Component | Technology |
|---|---|
| **Browser Engine** | Playwright (primary) |
| **Language** | Python (sync + async) |
| **Anti-detection** | playwright-stealth |
| **Session Storage** | Persistent Chromium profiles in local config |
| **DOM Parsing** | BeautifulSoup4 + html5lib |
| **Data Extraction** | Jina AI Reader API / trafilatura for content extraction |

### 7.6 Vision Stack

| Component | Technology |
|---|---|
| **Screen Capture** | mss (Python, cross-platform, fast) |
| **Vision Analysis** | Claude claude-opus-4-20250514 (Vision) / GPT-4o Vision |
| **OCR** | Tesseract 5 (local) / Azure Computer Vision (cloud) |
| **UI Element Detection** | YOLO-based UI detector (future) / Claude Vision (present) |
| **Change Detection** | OpenCV image diffing |

### 7.7 PC Control

| Platform | Technology |
|---|---|
| **Windows** | pywin32 + pyautogui + comtypes (COM automation for Office) |
| **macOS** | PyObjC + AppKit + Quartz + Atomacos (accessibility API) |
| **Linux** | AT-SPI + xdotool + wnck |
| **Cross-platform** | pyautogui for basic mouse/keyboard; OS-specific for deep control |

### 7.8 API and Services

| Technology | Role |
|---|---|
| **FastAPI** | All internal HTTP APIs, REST gateway |
| **WebSockets** | Real-time streaming from agents to UI |
| **gRPC** | High-performance inter-service communication (Phase 3+) |
| **uvicorn** | ASGI server |
| **Pydantic v2** | Request/response validation |

### 7.9 Observability

| Technology | Role |
|---|---|
| **structlog** | Structured logging (JSON, searchable) |
| **OpenTelemetry** | Distributed tracing across agents and services |
| **Prometheus** | Metrics collection |
| **Grafana** | Metrics visualization |
| **LangSmith** | LLM call tracing, agent observability (Langchain ecosystem) |

### 7.10 Frontend

| Technology | Role |
|---|---|
| **React 19 + TypeScript** | Web dashboard |
| **Tailwind CSS** | Styling |
| **shadcn/ui** | Component library base |
| **Tauri 2** | Desktop overlay app (lighter than Electron, Rust backend) |
| **React Native + Expo** | Mobile app (Phase 7) |
| **Zustand** | Frontend state management |
| **TanStack Query** | Server state management, API caching |

### 7.11 Infrastructure

| Technology | Role |
|---|---|
| **Docker + Compose** | Development environment, service containerization |
| **uv** | Python package management (faster than pip) |
| **pnpm** | Node package management |
| **GitHub Actions** | CI/CD pipeline |
| **Doppler** | Secrets management |
| **Ruff** | Python linting + formatting |

---

## 8. REPOSITORY STRUCTURE

### 8.1 Top-Level Layout

```
aether-ai-os/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── release.yml
│   │   └── docs.yml
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
│
├── docs/
│   ├── architecture/
│   │   ├── decisions/              # Architecture Decision Records (ADRs)
│   │   │   ├── 0001-event-bus-technology.md
│   │   │   ├── 0002-vector-database-selection.md
│   │   │   └── 0003-agent-framework-choice.md
│   │   ├── diagrams/               # System diagrams (draw.io / Mermaid)
│   │   └── specs/                  # Detailed technical specs per subsystem
│   ├── guides/
│   │   ├── development/
│   │   │   ├── getting-started.md
│   │   │   ├── adding-a-new-agent.md
│   │   │   ├── adding-a-new-tool.md
│   │   │   └── adding-a-new-service.md
│   │   └── deployment/
│   ├── api/                        # Auto-generated API docs
│   └── MASTER_BLUEPRINT.md         # This document
│
├── aether/                         # Main Python package
│   ├── __init__.py
│   │
│   ├── core/                       # Kernel: the heartbeat of Aether
│   │   ├── __init__.py
│   │   ├── kernel.py               # Process manager, boot sequence
│   │   ├── event_bus/
│   │   │   ├── __init__.py
│   │   │   ├── bus.py              # Event emission and subscription
│   │   │   ├── events.py           # All typed event definitions
│   │   │   └── middleware.py       # Logging, validation middleware
│   │   ├── service_registry/
│   │   │   ├── __init__.py
│   │   │   ├── registry.py         # Service registration and discovery
│   │   │   └── health.py           # Health check manager
│   │   └── plugin_system/
│   │       ├── __init__.py
│   │       ├── loader.py           # Plugin discovery and loading
│   │       └── base.py             # Base plugin interface
│   │
│   ├── agents/                     # Agent ecosystem
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── agent.py            # BaseAgent abstract class
│   │   │   ├── state.py            # AgentState base models
│   │   │   ├── tools.py            # Tool registry and invocation
│   │   │   └── output.py           # Structured output models
│   │   ├── orchestrator/
│   │   │   ├── agent.py
│   │   │   ├── intent.py           # Intent classification
│   │   │   ├── router.py           # Task routing logic
│   │   │   └── graph.py            # LangGraph orchestration graph
│   │   ├── planner/
│   │   │   ├── agent.py
│   │   │   ├── decomposer.py       # Goal → task graph
│   │   │   └── models.py           # Plan, Step, TaskGraph models
│   │   ├── executor/
│   │   │   ├── agent.py
│   │   │   ├── tool_selector.py    # Choose tools for a task
│   │   │   └── rollback.py         # Undo executed actions
│   │   ├── memory_agent/
│   │   │   ├── agent.py
│   │   │   └── consolidation.py    # Memory consolidation logic
│   │   ├── researcher/
│   │   │   ├── agent.py
│   │   │   └── synthesizer.py      # Multi-source synthesis
│   │   ├── coder/
│   │   │   ├── agent.py
│   │   │   └── code_tools.py       # Code-specific tool implementations
│   │   └── voice/
│   │       ├── agent.py
│   │       └── pipeline.py         # STT/TTS pipeline
│   │
│   ├── memory/                     # Memory subsystem
│   │   ├── __init__.py
│   │   ├── api.py                  # MemoryAPI — the only public interface
│   │   ├── models.py               # Memory, Knowledge, Entity models
│   │   ├── working/
│   │   │   └── context.py          # In-process working memory
│   │   ├── short_term/
│   │   │   └── redis_store.py      # Redis-backed Tier 1
│   │   ├── long_term/
│   │   │   ├── postgres_store.py   # Structured facts
│   │   │   └── vector_store.py     # Qdrant-backed semantic search
│   │   ├── knowledge_graph/
│   │   │   └── graph.py            # Neo4j adapter (Phase 3+)
│   │   ├── consolidation/
│   │   │   ├── pipeline.py         # Consolidation orchestration
│   │   │   └── extractor.py        # Fact extraction from text
│   │   └── retrieval/
│   │       ├── hybrid.py           # Hybrid retrieval (semantic + keyword)
│   │       └── reranker.py         # Result reranking
│   │
│   ├── services/                   # Core capability services
│   │   ├── __init__.py
│   │   ├── base.py                 # BaseService abstract class
│   │   ├── voice/
│   │   │   ├── service.py
│   │   │   ├── stt.py              # Speech-to-text
│   │   │   ├── tts.py              # Text-to-speech
│   │   │   ├── vad.py              # Voice activity detection
│   │   │   └── wake_word.py        # Wake word detection
│   │   ├── vision/
│   │   │   ├── service.py
│   │   │   ├── capture.py          # Screen capture
│   │   │   ├── analyzer.py         # Vision model calls
│   │   │   └── ocr.py              # Text extraction
│   │   ├── pc_control/
│   │   │   ├── service.py
│   │   │   ├── permissions.py      # Capability permission system
│   │   │   ├── app_control.py      # Application control
│   │   │   ├── file_system.py      # File operations
│   │   │   ├── system_monitor.py   # System stats
│   │   │   └── adapters/
│   │   │       ├── windows.py
│   │   │       ├── macos.py
│   │   │       └── linux.py
│   │   ├── browser/
│   │   │   ├── service.py
│   │   │   ├── session.py          # Browser session management
│   │   │   ├── navigator.py        # Navigation and interaction
│   │   │   ├── extractor.py        # Data extraction
│   │   │   └── researcher.py       # Research pipeline
│   │   └── task_manager/
│   │       ├── service.py
│   │       ├── models.py           # Task, Goal, Priority models
│   │       └── scheduler.py        # Task scheduling
│   │
│   ├── integrations/               # External integrations
│   │   ├── __init__.py
│   │   ├── llm/
│   │   │   ├── router.py           # LLM Router — all model calls go here
│   │   │   ├── providers/
│   │   │   │   ├── anthropic.py
│   │   │   │   ├── openai.py
│   │   │   │   └── local.py        # Ollama / local model adapter
│   │   │   └── models.py           # ModelConfig, TokenBudget
│   │   ├── tools/
│   │   │   ├── registry.py         # Tool registration and discovery
│   │   │   ├── base.py             # BaseTool interface
│   │   │   └── implementations/    # All tool implementations
│   │   │       ├── web_search.py
│   │   │       ├── file_tools.py
│   │   │       ├── code_tools.py
│   │   │       └── calendar_tools.py
│   │   └── apis/                   # External API adapters
│   │       ├── hubspot.py
│   │       ├── github.py
│   │       └── calendar.py
│   │
│   └── interfaces/                 # Interface adapters
│       ├── __init__.py
│       ├── api/
│       │   ├── main.py             # FastAPI application
│       │   ├── routers/            # API route modules
│       │   └── middleware/         # Auth, rate limiting, logging
│       ├── websocket/
│       │   └── handler.py          # Real-time streaming
│       └── cli/
│           └── main.py             # CLI entry point
│
├── apps/                           # Frontend applications
│   ├── dashboard/                  # React web dashboard
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── stores/             # Zustand state stores
│   │   │   ├── api/                # API client hooks
│   │   │   └── types/
│   │   ├── package.json
│   │   └── vite.config.ts
│   ├── overlay/                    # Tauri desktop overlay (Phase 9)
│   │   ├── src/
│   │   ├── src-tauri/
│   │   └── package.json
│   └── mobile/                     # React Native app (Phase 7)
│       ├── src/
│       └── package.json
│
├── infrastructure/
│   ├── docker/
│   │   ├── Dockerfile.core
│   │   ├── Dockerfile.agents
│   │   └── Dockerfile.memory
│   ├── docker-compose.yml          # Full development environment
│   ├── docker-compose.prod.yml
│   └── scripts/
│       ├── bootstrap.sh            # One-command dev setup
│       ├── migrate.py              # Database migrations
│       └── seed.py                 # Seed test data
│
├── tests/
│   ├── unit/                       # Fast, isolated unit tests
│   ├── integration/                # Tests with real services
│   ├── e2e/                        # Full end-to-end scenarios
│   └── fixtures/
│
├── config/
│   ├── default.yaml                # Base configuration
│   ├── development.yaml
│   └── production.yaml
│
├── pyproject.toml                  # Python project config (uv/ruff)
├── docker-compose.yml
└── README.md
```

### 8.2 Architecture Decision Records (ADRs)

Every significant technology choice must be documented as an ADR in `docs/architecture/decisions/`. Format:

```markdown
# ADR-XXXX: [Title]
Date: YYYY-MM-DD
Status: [Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]

## Context
Why does this decision need to be made?

## Decision
What was decided?

## Rationale
Why this option over alternatives?

## Consequences
What are the trade-offs?

## Alternatives Considered
What else was evaluated?
```

---

## 9. RISK ANALYSIS

### 9.1 Technical Risks

| Risk | Severity | Probability | Mitigation |
|---|---|---|---|
| **LLM context window overflow** for long tasks | High | High | Memory summarization, sliding context windows, RAG over memory |
| **Agent hallucination** causing incorrect tool execution | High | Medium | Structured output validation, confirmation gates for destructive actions |
| **Agent infinite loops** (planner/executor deadlock) | High | Medium | Max iteration limits, loop detection, circuit breakers per agent |
| **Voice latency too high** for natural conversation | Medium | Medium | Local STT fallback, response streaming, interrupt-on-input support |
| **LLM API rate limits** breaking workflows | Medium | High | Request queuing, exponential backoff, multi-provider routing |
| **LangGraph state corruption** in long multi-agent runs | Medium | Low | Checkpointing, state validation after each step |
| **Embedding drift** as models change | Medium | Medium | Store model version with each embedding, reindex on model upgrade |

### 9.2 Security Risks

| Risk | Severity | Mitigation |
|---|---|---|
| **Prompt injection** via web content into agents | Critical | Input sanitization boundary between web content and agent context; never directly embed unvalidated web text into system prompts |
| **Unauthorized PC/system control** | Critical | Capability permission manifest; user approval flow; no action without token |
| **API key exfiltration** | Critical | Doppler secrets management; keys never stored in code or .env files in repo |
| **Memory poisoning** (malicious content in long-term memory) | High | Memory provenance tracking; user review mode for important memories |
| **Agent impersonation** between agents | Medium | Signed internal messages; agent identity tokens |
| **Browser session credential theft** | High | Encrypted session storage; sessions never serialized to plain files |
| **Logging sensitive data** | Medium | Structured logging with PII field redaction; log levels for sensitive operations |

### 9.3 Scalability Risks

| Risk | Mitigation |
|---|---|
| **Vector DB growing unbounded** | Importance-based pruning, TTL on non-critical embeddings |
| **Event bus becoming a bottleneck** | Redis Streams with consumer groups; upgrade path to Kafka documented |
| **Memory consolidation lagging** | Background workers, incremental consolidation, priority queuing |
| **LLM costs growing as usage scales** | Model routing (use cheap models for simple tasks), local model for low-stakes ops |
| **Browser session resource leaks** | Session pool with max size, timeout-based cleanup |

### 9.4 Maintenance Risks

| Risk | Mitigation |
|---|---|
| **LLM API breaking changes** | LLM Router abstraction layer isolates all model calls; swap providers without touching agents |
| **Dependency conflicts as project grows** | uv for Python dependency management; lockfiles committed; monthly dependency audit |
| **Schema migration breaking existing memories** | All DB schemas versioned with Alembic; migration scripts required for all schema changes |
| **Feature coupling making Phase N difficult** | Strict service boundary contracts; event-driven decoupling from day one |
| **Documentation falling behind implementation** | ADR process for every significant decision; code must not be merged without docs update |

### 9.5 Human Risks

| Risk | Mitigation |
|---|---|
| **Scope creep delaying Phase 1** | Strict phase gates; no Phase N+1 work until Phase N milestones are met |
| **Over-engineering early phases** | Resist adding Phase 5 patterns in Phase 1; use "good enough for now, designed for later" |
| **Architectural drift as AI assists with code** | AI-generated code must be reviewed against this blueprint before merge |

---

## 10. FUTURE EXPANSION STRATEGY

### 10.1 Phase 9: Floating Assistant Interface

**Architecture Approach: Layered Overlay System**

The overlay is a separate process (Tauri app) that communicates with the Aether core via a local WebSocket connection. It has zero business logic — it is purely a rendering surface.

```
Tauri Overlay Process
  ├── Transparent frameless window (always-on-top)
  ├── React frontend (minimal, fast)
  ├── WebSocket client → aether-core
  ├── Hotkey listener (global shortcuts)
  └── Tray icon with quick commands

Design Language: "Crystalline HUD"
  ├── Dark, translucent panels
  ├── Glowing accent lines (configurable color)
  ├── Monospace + geometric font pairing
  ├── Information density: high on command, minimal at rest
  └── Animated transitions that feel physical, not just decorative
```

The overlay can display:
- Chat input/output
- Active task status
- System notifications
- Research results
- Code diffs
- Any structured data from any agent

**Expandability:** New "panels" are just React components registered with the overlay's component registry. Adding a new display surface requires zero changes to the overlay core.

### 10.2 Phase 10: Holographic Interface

**Architecture Approach: Spatial Rendering Adapter**

The holographic interface is NOT a rebuild. It is a new rendering adapter that consumes the same WebSocket stream from aether-core that the overlay uses.

```
Spatial Interface (Apple Vision Pro / Meta Quest)
  ├── XR Runtime Adapter (connects to aether-core WebSocket)
  ├── 3D Panel System (information in spatial layers)
  ├── Hand gesture input → translated to Aether intents
  ├── Voice input (native, same pipeline)
  └── Environmental anchors (panels attached to physical locations)

Key Design Principle: Aether's intelligence doesn't move.
Only the rendering surface changes.
```

**3D Information Architecture:**
- Tier 1 Space (arm's reach): Active tasks, current conversation
- Tier 2 Space (room scale): Research panels, code editor, notifications
- Tier 3 Space (ambient): Background monitoring, system stats, news feeds

### 10.3 Robotics Integration

**Long-term possibility. Architecture must not prevent it.**

Aether's agent architecture maps naturally to robotics:
- The Executor Agent gains physical tool calls (move_arm, pick_object, navigate_to)
- The Vision Agent already handles real-world scene understanding
- The Planner Agent already handles multi-step physical task decomposition
- Memory already tracks physical environment state

The bridge is a **Robotics Integration Service** (future):
```
aether-core ←→ Robot Bridge Service ←→ ROS2 / LeRobot ←→ Hardware
```

No architectural changes to the core are needed. The robot is just another set of tools in the tool pool.

### 10.4 External Tool Ecosystem

Aether should eventually support a **Tool Plugin Marketplace** pattern:

```
Third-party tool developer:
  1. Creates a tool package conforming to the BaseTool interface
  2. Publishes to a tool registry
  3. User installs: aether tools install github.com/user/aether-tool-salesforce
  4. Tool is auto-discovered and available to all agents
```

This requires:
- A stable BaseTool interface (design from Phase 1)
- A tool manifest format (name, description, input/output schema, permissions)
- A sandbox for running untrusted tools (subprocess isolation)
- A capability permission check before any tool is invoked

### 10.5 Multi-User / Team Expansion

Aether is personal-first, but the architecture must not prevent team use.

Design considerations from day one:
- All data models have a `user_id` field
- Memory is namespaced by user
- The permission system is user-scoped
- The API gateway has authentication from day one (even if only single-user)
- Events carry user attribution

When team features are added, it's a new **Identity and Access Management** service added to the existing architecture — not a refactor.

### 10.6 Local AI Model Strategy

As local models (Llama, Mistral, Phi) improve, Aether should shift appropriate workloads off cloud APIs.

**LLM Router evolution:**
```
Phase 1:    Cloud-only (Claude + GPT-4o)
Phase 2–4:  Cloud primary, local for simple tasks (Ollama)
Phase 5+:   Smart routing based on task complexity
Phase 7+:   Local-first for privacy-sensitive operations
Future:     Fully local for mobile/edge deployment
```

The LLM Router abstraction means this transition requires no changes to agents.

---

## 11. MASTER BLUEPRINT SUMMARY

### The Golden Rules of Aether Development

These rules are above any individual phase requirement. They must never be violated.

```
RULE 1: The Event Bus Is Sacred
  All inter-subsystem communication flows through the event bus.
  Direct service-to-service calls are architectural violations.

RULE 2: The Memory API Is the Only Door
  No code outside the memory subsystem touches the database.
  All memory operations go through MemoryAPI.

RULE 3: The LLM Router Is the Only Gateway
  No code calls an LLM API directly.
  All model calls go through the LLM Router.

RULE 4: Tools Are First-Class Citizens
  Every action an agent takes is a tool call.
  Tools have typed inputs, typed outputs, and audit entries.

RULE 5: Version Everything
  All event schemas are versioned.
  All API contracts are versioned.
  All database schemas have migration scripts.

RULE 6: Security Is Not a Phase
  Capability permissions exist from Phase 2.
  Secrets management exists from Phase 1.
  Audit logging exists from Phase 1.

RULE 7: Observability Is Not Optional
  Every agent run is traced.
  Every LLM call is logged.
  Every error is structured and searchable.

RULE 8: Phases Are Gates, Not Suggestions
  Phase N+1 development does not begin until Phase N milestones are complete.

RULE 9: AI-Generated Code Must Match the Blueprint
  Code generated by Antigravity IDE must be reviewed against this document.
  Architecture drift is caught at review, not at refactor.

RULE 10: Document Before You Build
  For any new subsystem or feature, write the spec first.
  Code is implementation detail. Architecture is truth.
```

---

### System Capability Matrix

| Capability | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Voice conversation | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Persistent memory | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Task management | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| PC control | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Browser automation | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Coding assistant | — | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Multi-agent reasoning | — | — | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Vision / screen understanding | — | — | — | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Mobile integration | — | — | — | — | — | — | ✓ | ✓ | ✓ | ✓ |
| Business automation | — | — | — | — | — | — | — | ✓ | ✓ | ✓ |
| Floating overlay UI | — | — | — | — | — | — | — | — | ✓ | ✓ |
| Holographic / XR interface | — | — | — | — | — | — | — | — | — | ✓ |

---

### Technology Stack Summary

```
Language:         Python 3.12+ (backend) | TypeScript (UI) | Rust (perf)
Agent Framework:  LangGraph + LangChain
Primary LLM:      Claude claude-opus-4-20250514 (reasoning) | GPT-4o (fallback)
Embeddings:       text-embedding-3-large (OpenAI)
Vector DB:        Qdrant (self-hosted)
Relational DB:    PostgreSQL 16
Cache / Bus:      Redis 7 (Pub/Sub + Streams)
Knowledge Graph:  Neo4j (Phase 3+)
Voice STT:        Deepgram streaming / Whisper.cpp (local)
Voice TTS:        ElevenLabs / Edge TTS (fallback)
Wake Word:        Porcupine (on-device)
Browser:          Playwright
PC Control:       pywin32 / PyObjC / AT-SPI
Screen Capture:   mss
Vision:           Claude Vision / GPT-4o Vision
Frontend:         React 19 + TypeScript + Tailwind
Desktop App:      Tauri 2
Mobile:           React Native + Expo
API:              FastAPI + WebSockets
Observability:    OpenTelemetry + LangSmith + Grafana
Secrets:          Doppler
Packaging:        uv (Python) + pnpm (Node)
```

---

### The First 30 Days

When Phase 1 begins, the first 30 days should focus on exactly three things:

**Days 1–10: Infrastructure**
- Repository created with the full folder structure above
- Docker Compose with Redis + PostgreSQL running
- Kernel boots, event bus live, service registry functional
- Logging and configuration working
- One ADR written documenting a key decision

**Days 11–20: Intelligence Layer**
- LLM Router live, calling Claude
- BaseAgent class implemented
- Basic Conversational Agent responding to text input
- Memory write and read working (short-term only)

**Days 21–30: First Human Interaction**
- Voice pipeline working end-to-end (wake → speak → response → voice)
- Simple task creation via voice
- Dashboard showing conversation history
- Aether introduces itself and remembers your name across restarts

When these three milestones are hit, the foundation is real. Everything else is iteration.

---

### Final Architectural Statement

Aether is not built in a day. It is not built in a year. It is grown — one phase at a time, each one making the previous ones more powerful.

The architecture described in this document is designed to be true for all ten phases. Not because the future is predictable, but because the core abstractions — event bus, memory API, agent framework, LLM router, tool system — are stable enough to absorb any technology change on top of them.

Every future LLM breakthrough, every new hardware platform, every new capability can be added as:
- A new tool in the tool pool
- A new agent in the agent graph
- A new service behind the service interface
- A new rendering surface on the interface layer

The core never changes. The capabilities grow forever.

**This is how you build JARVIS.**

---

*Document Version: 1.0*
*Maintained by: Chief Architect (Claude) + Product Owner*
*Review Cycle: At each phase completion*
*Next Review: End of Phase 1*
