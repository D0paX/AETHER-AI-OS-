# Aether AI OS: The Learning Journal

Welcome to your personal learning journal! Building an AI Operating System from scratch is an incredible journey. Since this is your first time, this document will serve as your **plain-English guide**.

Whenever we finish a milestone, I will update this file to explain exactly **what** we just did, **why** we did it, and **how** it works in simple terms.

---

## Milestone 0 (M0): Infrastructure & Environment Setup

_Status: Complete_

Before building a house, you need a solid foundation and the right tools. M0 was all about setting up your computer so it's powerful enough to run an AI OS locally.

### What we did:

1. **Installed Python & `uv`**: Python is the main programming language we are using. `uv` is an ultra-fast tool that manages our Python packages (the pre-written code libraries we borrow from others).
2. **Installed C++ Build Tools & CUDA**: AI models run on your Graphics Card (GPU) because GPUs are basically supercomputers for math. CUDA is the software that lets Python talk directly to your NVIDIA GPU to run AI models fast.
3. **Set up Windows Subsystem for Linux (WSL) & Docker**: Windows is great, but a lot of developer tools run best on Linux. WSL is a hidden Linux computer inside your Windows PC. Docker uses WSL to run software in isolated "containers" so we don't clutter up your main computer.
4. **Installed Ollama & Llama 3.2**: Ollama is a program that runs AI brains (models) locally on your machine. We downloaded Llama 3.2, which is the actual AI model that will power Aether's thinking.
5. **Configured API Keys (`.env`)**: We securely saved your private passwords/keys in a `.env` file so the OS can talk to the outside world when it needs to.

---

## Milestone 1.0 (M1.0): Repository Foundation

_Status: Complete_

Now that your computer has the right tools, we needed to lay down the rules for the code we are about to write. Imagine this as hiring a team of strict automated inspectors who watch us code and yell at us if we make a mistake.

### What we did:

1. **Created `pyproject.toml`**: This is the master blueprint for our project. It lists exactly what external packages Aether needs (like databases, web servers, and AI routers).
2. **Set up `Ruff` (The Grammar Police)**: Ruff is an automated tool that instantly reads our code and fixes formatting (like extra spaces) so everything looks neat and standard.
3. **Set up `MyPy` (The Type Checker)**: In Python, you can accidentally put a word where a number should go, causing a crash later. MyPy checks our code _before_ we run it to ensure all our data types match perfectly.
4. **Set up `Import-Linter` (The Security Guard)**: We defined strict "Architectural Boundaries." For example, the Voice system is strictly forbidden from directly reading the Database. The Import Linter enforces these rules so our OS doesn't become a tangled mess.
5. **Set up `pre-commit` (The Bouncer)**: We hooked all these tools into `git`. Now, whenever we try to save (commit) our code, `pre-commit` forces Ruff, MyPy, and the Linter to check the code first. If the code is bad, it rejects the save!
6. **Set up `pytest` and `conftest.py`**: This is our automated testing laboratory. We built the empty stubs for it so we can easily test individual parts of the OS later.

---

## Milestone 1.1 (M1.1): Docker Infrastructure

_Status: Complete_

Now that our rules are set, we need places to store our data. Aether needs a **Vector Database** (Qdrant) to remember things long-term, and a **Cache** (Redis) to remember things short-term. We put these inside Docker containers.

### What we did:

1. **Created `docker-compose.yml`**: This is a recipe that tells Docker exactly how to build and connect Redis and Qdrant.
2. **Configured Security and Storage**: We locked down the ports so nobody else on your Wi-Fi can access your AI's memory. We also created "named volumes," which are safe, permanent folders inside Docker where the databases save their files.
3. **Created PowerShell Scripts (`start.ps1`, `stop.ps1`, `health_check.ps1`)**: Instead of typing long Docker commands every day, we created simple scripts you can run to turn your databases on and off. The `stop.ps1` script is specially designed to never accidentally delete your data.

### 🐛 Problem Encountered & Fixed

- **The Problem:** We originally tried to check if Qdrant was healthy by having Docker run a program called `curl` to hit the `/health` web address.
- **Why it failed:** The creators of Qdrant recently updated their software (v1.18.2). They removed `curl` entirely to make the program smaller, and they changed the web address from `/health` to `/readyz`. This caused our health check script to crash.
- **Future Risk:** If we left it broken, the OS would constantly think Qdrant was dead and might refuse to save any AI memories.
- **The Fix:** Instead of trying to force `curl` inside the container (which would require us to build a custom Docker image), we changed our PowerShell scripts to check the new `/readyz` address from _outside_ the container using Windows commands. This keeps the setup simple and perfectly healthy.

### 🐛 Problem Encountered & Fixed: `start.ps1` Syntax Error

- **The Problem:** The `start.ps1` script (which starts our database containers) failed to run and threw an error: *"The Try statement is missing its Catch or Finally block."*
- **Why it failed:** The script file got accidentally corrupted (likely from a copy-paste error). A "try" block was left open without telling the computer what to do if it failed (the "catch" block), and some code was duplicated at the bottom of the file.
- **The Fix:** We completely rebuilt the script file. We properly organized the code into clean functions and correctly paired every `try` command with its matching `catch` command so errors are handled gracefully.

---

## Milestone 1.2 (M1.2): Configuration, Logging, and Events
*Status: Complete*

To give our AI a solid brain, it needs three things: a way to read settings (Config), a way to write down what it is doing (Logging), and a way for its different parts to talk to each other (Events).

### What we did:
1. **Configuration System**: We used a tool called Pydantic to strictly check all of Aether's settings. If a setting is missing, the OS safely stops instead of crashing unpredictably later. We put all this in `aether/core/config.py`.
2. **Structured Logging**: Instead of simple print statements, we used `structlog`. This forces every log message to be saved as structured JSON, making it incredibly easy to search through logs when things break.
3. **Event Bus (The Nervous System)**: Aether's parts (like Memory and LLM) shouldn't be directly tangled together. Instead, they send "Events" to a central bus using Redis Streams. For example, when a new memory is created, it throws an event into the stream, and anyone who cares can read it asynchronously. 
4. **Exception Hierarchy**: We mapped out 19 specific types of errors (like `LLMTimeoutError` or `MemoryStorageError`) so that when a failure occurs, the code knows *exactly* what went wrong.

### 💡 Why we chose this approach:
By locking down these three systems right now, we ensure that every future module we build will speak the same language, use the same logging format, and communicate through the same safe event bus.

---

*This document will be updated after we complete the next milestone: M1.3 (LLM Router).*

## Milestone 1.3 (M1.3): LLM Router & Budget Manager

*Status: Complete*

We want Aether to be smart, but we also don't want it to accidentally spend hundreds of dollars if it gets confused and talks to itself all night! We built the LLM Router and Budget Manager to solve this.

### What we did:
1. **The LLM Router (The Switchboard)**: We created a smart router that takes a request from the AI and automatically sends it to the best AI model. It has four "Tiers":
   - **Local Tier**: Free, runs on your PC (Ollama).
   - **Cheap Tier**: Extremely fast and low-cost (Gemini Flash).
   - **Standard Tier**: Smart but reasonably priced (Claude Sonnet).
   - **Premium Tier**: The smartest, most expensive model (Claude Opus).
2. **The Budget Manager (The Accountant)**: Before the Router sends a request, it asks the Accountant if we have enough money left in our daily or monthly budget. 
3. **The Fail-Safe (Fallback Chain)**: If we hit our budget limit, or if the internet goes down, the Router will silently downgrade the request to the Local Tier. This ensures the OS keeps working (for free!) even when things break.
4. **Local Embeddings (The Translator)**: We added a fast, free local system that translates text into numbers (vectors) so the AI can store them in Qdrant later.

### 💡 Why we chose this approach:
By putting all AI models behind a single Router, the rest of the OS never needs to worry about which model to use or how much it costs. The Router handles all the complexity, retries, and budgeting automatically.

---

## Milestone 1.4 (M1.4): Memory Database & Search

*Status: Complete*

Aether needs a long-term, organized filing cabinet to remember conversations, tasks, and system settings. We built this filing cabinet using SQLite, an ultra-fast database that runs completely locally.

### What we did:
1. **The Tables (The Filing System):** We created 8 specific "tables" (like spreadsheets) to store data: Configurations, Conversations, Messages, Memories, Tasks, Tool Executions, Agent Runs, and Cost tracking.
2. **UUIDv7 Identifiers:** Instead of standard numbers (1, 2, 3), we use a special ID system (UUIDv7) that allows the computer to perfectly sort everything by exactly *when* it happened down to the millisecond.
3. **Full-Text Search (FTS5):** We created "Virtual Tables" for Memories and Tasks. Think of this as a super-powered search engine built right into the filing cabinet. It allows Aether to instantly search through millions of words to find specific memories without slowing down.
4. **Automated Triggers (The Invisible Helpers):** We wrote invisible database rules (Triggers) so that whenever Aether creates or deletes a memory, the Full-Text Search index is updated completely automatically in the background.

### 💡 Why we chose this approach:
By using SQLite locally instead of an external cloud database, we guarantee that all your private conversations and memories never leave your machine. The automated triggers mean the OS can run lightning-fast searches without any extra code slowing down the main program.

*This document will be updated after we complete the next milestone: M1.5 (Memory System).*

---

## Milestone 1.5 (M1.5): Memory System

*Status: Complete*

Aether now has a fully functioning brain! While the previous milestone gave us the empty filing cabinets (SQLite), this milestone gave Aether the ability to automatically read, write, and search those cabinets using both exact keywords and "vibes" (semantic search).

### What we did:
1. **The Public Interface (`MemoryAPI`):** We built a single, clean doorway into the memory system. The rest of the OS only ever talks to this doorway to `remember`, `recall`, or `forget` things, keeping everything organized.
2. **Hybrid Search (The Best of Both Worlds):** When Aether tries to remember something, it searches two ways at the same time:
   - **Vector Search (Qdrant):** It searches for things that *mean* the same thing, even if the exact words are different (e.g. searching for "dog" might find "puppy").
   - **Keyword Search (SQLite FTS5):** It searches for the exact words you typed.
   We merged both of these results together so Aether never misses a memory.
3. **The Reranker (The Judge):** Not all memories are equal. We wrote a mathematical formula that looks at all the memories Aether found and scores them based on three things:
   - **Similarity:** How closely does it match what we are looking for? (60% weight)
   - **Recency:** How new is the memory? Older memories slowly lose score over 30 days. (30% weight)
   - **Importance:** How critical is this information? (10% weight)
4. **Automated Consolidation (Sleep Cycles):** At the end of a conversation, Aether runs a "consolidation pipeline." It uses a fast, free local LLM to read the entire chat, summarize what happened, extract key facts (like "User likes coffee"), and store them permanently for the future.

### 💡 Why we chose this approach:
Human memory isn't perfect, but AI memory can be. By forcing the OS to mathematically decay old memories and rank things by importance, we ensure that Aether's brain doesn't get cluttered with useless information over time. The hybrid search guarantees that whether you ask a vague question or a specific one, Aether will find the right answer.

---

## Milestone 1.6 (M1.6): Tool System & Task Manager

*Status: Complete*

Aether can now actually *do* things! Instead of just talking and remembering, Aether now has "hands" (Tools) and a "to-do list" (Task Manager) to interact with the world and manage its own long-running jobs.

### What we did:
1. **The Tool Box (`ToolRegistry`):** We created a standardized way for Aether to use tools. Every tool requires a very specific set of instructions (schemas) so the AI knows exactly how to use it without making mistakes.
2. **First Tools:** We built a clock (`GetCurrentDatetimeTool`) so Aether knows what time it is, and a web browser (`WebSearchTool`) so Aether can look up real-time information on the internet.
3. **The To-Do List (`TaskManager`):** When Aether has a big job (like "Write a report"), it can't just do it all at once. We built a Task Manager that tracks these jobs. It forces tasks to follow a strict order: they start as `PENDING`, move to `ACTIVE`, and finish as `COMPLETED`, `FAILED`, or `CANCELLED`.
4. **The Pager System (Events):** Every time a task changes state (e.g., from active to completed), the Task Manager shouts it out on the central Event Bus. This means the rest of the OS instantly knows when a job is done without having to constantly check.

### 💡 Why we chose this approach:
By strictly enforcing how tools are built and how tasks transition from one state to another, we prevent the AI from "hallucinating" tool usage or getting stuck in infinite loops. If a task fails or the AI tries to use a tool incorrectly, the system cleanly catches the error instead of crashing.

---

## Milestone 1.7 (M1.7): Agent Runtime & Conversation Agent

*Status: Complete*

Aether now has a cohesive "Supervisor" and its first true Agent! While previous milestones gave Aether a brain, memory, and hands, this milestone gives it a **Personality and a Workflow Loop**. It can now think, act, and remember in a continuous cycle.

### What we did:
1. **The Base Agent Rules:** We created strict rules (`BaseAgent`) that every future agent must follow. They must declare their name, their role, how smart they need to be (LLM Tier), and exactly which tools they are allowed to use.
2. **The Conversation Agent:** This is Aether's primary persona. When you talk to Aether, this agent takes your message, pulls relevant memories from the Memory System, and decides how to answer. If you ask a question that requires a tool (like "what's the time?"), it knows how to use it!
3. **The Agent Runtime (The Supervisor):** We built a "Runtime Loop". Think of it as a supervisor that watches the agent. The loop goes like this: 
   - The agent thinks.
   - If the agent wants to use a tool, the Supervisor stops the agent, runs the tool for it, and feeds the result back to the agent.
   - The agent thinks again until it's finally ready to give you the answer.
4. **Resilient Testing:** We ensured that the agents can recall your past conversations from previous sessions (Cross-Session Memory) and proved that they can parse complex tasks flawlessly.

### 💡 Why we chose this approach:
By putting a Supervisor (`AgentRuntime`) in charge of the agents, we prevent the AI from running out of control. The AI never actually executes code or tools itself—it merely *requests* that the Supervisor do it. This keeps the OS incredibly secure and ensures that every action is logged, audited, and strictly controlled.

---

## Milestone 1.8 (M1.8): Session Manager & Morning Briefing

*Status: Complete*

Aether now has a sense of time and boundaries! Just like humans wake up, go about their day, and go to sleep, Aether now starts and ends "Sessions". This milestone tied everything together so the AI can gracefully manage its own context.

### What we did:
1. **The Morning Briefing:** Whenever you start a new conversation, the Session Manager gathers all your active tasks and any highly relevant past memories. It sends them to the LLM to generate an ultra-short (under 50 words) "Morning Briefing". This ensures Aether is instantly caught up on what it was doing previously.
2. **Context Packaging (`SessionContext`):** We built a strict package that holds the active task queue, the message transcript, and memory results. This package gets injected into the agent's brain before it answers you.
3. **Graceful Sleep (Background Consolidation):** When you say goodbye and end the session, Aether doesn't make you wait. It instantly says goodbye, but secretly spins up a background task to read the whole chat, extract the important facts, and save them to long-term memory. 
4. **Redis State Caching:** We hooked up Redis (our fast, short-term memory) so that if the OS crashes unexpectedly, it can instantly recover exactly where you left off.

### 💡 Why we chose this approach:
We want Aether to feel snappy and responsive. By putting the heavy lifting (memory consolidation) into a non-blocking background task, you never have to wait for the AI to "think" about what happened before closing the program. The Morning Briefing makes sure the AI never forgets what you were working on yesterday.

---

## Milestone 1.9 (M1.9): CLI Interface [TEXT MILESTONE]

*Status: Complete*

We did it! Aether is no longer just a bunch of hidden background processes; it now has a face you can talk to. This milestone represents our first usable, fully conversational version of the OS, known as the "TEXT MILESTONE".

### What we did:
1. **The Terminal Interface (CLI):** We built a beautiful terminal application (using a tool called `rich`). When you start it up, Aether welcomes you, gives you your morning briefing, and presents a glowing cyan prompt (`Aether >`) waiting for your input.
2. **Slash Commands:** We gave you direct control over the OS with simple commands like `/tasks` to see your to-do list, `/memory` to search through past thoughts, and `/status` to check the budget.
3. **The Internal API:** We built a local web server (FastAPI) that acts as a secure bridge. Even though we are typing in the terminal right now, this API means that in the future, we can easily connect a Voice service or a web dashboard without rewriting the brain of the AI. 
4. **The Entry Point:** We created the main `python -m aether` start command, which cleanly boots up the entire Aether Kernel, connects all the databases, and launches the chat interface in one go.

### 💡 Why we chose this approach:
We intentionally kept the CLI simple and strictly separated the terminal screen from the actual "brain" (the Kernel). The CLI contains zero business logic—it simply takes your text and passes it to the OS. This means if we ever want to build a completely new interface (like a mobile app), the core OS doesn't have to change at all.

---

*This document will be updated after we complete the next milestone: M1.10 (Voice Service).*
