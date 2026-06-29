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
