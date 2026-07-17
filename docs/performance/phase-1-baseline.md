# Phase 1 Performance Baseline

**Date**: 2026-07-03

## Overview
This document records the baseline performance metrics of the Aether OS at the conclusion of Phase 1. These metrics serve as the regression baseline for Phase 2 optimizations.

## Metrics

### 1. Startup Latency
- **Aether Core (FastAPI)**: `[ ] ms`
- **Aether Voice (FastAPI + Models)**: `[ ] ms`
- **Docker Infrastructure (Qdrant + Redis)**: `[ ] ms`

### 2. Memory Latency (Qdrant)
- **Vector Upsert (per point)**: `[ ] ms`
- **Vector Query (Top-K=5)**: `[ ] ms`
- **SQLite Write Latency (per transaction)**: `[ ] ms`

### 3. Voice Pipeline Latency
- **VAD Inference (per 30ms chunk)**: `[ ] ms`
- **Wake Word Detection (per frame)**: `[ ] ms`
- **TTS Generation (Kokoro - 1 sentence)**: `[ ] ms`
- **STT Transcription (FasterWhisper - 5s audio)**: `[ ] ms`

### 4. LLM Router Latency
- **Local Model Token Generation Rate**: `[ ] tokens/sec`
- **Tool Call Parsing Overhead**: `[ ] ms`

## Hardware Context
- **OS**: Windows 11
- **CPU**: (Fill in)
- **GPU**: (Fill in)
- **RAM**: (Fill in)
- **Storage**: (Fill in)

## Conclusion
(Fill in notes on current performance bottlenecks and Phase 2 targets)
