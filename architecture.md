# AI Influencer Platform MVP Architecture

## 1. Goals

Build a production-ready MVP platform for creating and operating AI influencers with:

- durable persona consistency across text and visual content
- structured, versioned memory with automatic retrieval during generation
- provider-agnostic model interfaces for text, image, and embedding workloads
- asynchronous pipelines for content generation, indexing, validation, and asset processing
- an admin UI for managing influencers, memory, assets, and generations

This MVP prioritizes correctness of persona behavior, extensibility of the memory model, and operational simplicity for a small production team.

## 2. High-Level Architecture

The system is a modular monolith for the MVP, split into internal bounded services. This keeps deployment simple while preserving clean interfaces for later extraction into separate services.

### Runtime components

1. API Service
   - FastAPI application
   - serves REST endpoints and internal orchestration endpoints
   - owns authentication, request validation, and domain workflows

2. Worker Service
   - Celery worker backed by Redis
   - executes long-running jobs:
     - generation
     - embedding creation
     - retrieval indexing
     - asset post-processing
     - validation/review jobs

3. Scheduler Service
   - Celery Beat
   - triggers maintenance tasks:
     - stale cache cleanup
     - memory compaction
     - embedding backfills
     - asset similarity refresh

4. PostgreSQL
   - system of record
   - stores influencer configuration, memory records, generations, assets, jobs, evaluations, and version history
   - uses `pgvector` for vector search

5. Redis
   - Celery broker/result backend
   - hot cache for prompt fragments, retrieval results, rate-limit tokens, and short-lived generation state

6. Frontend Admin Panel
   - React + Vite
   - manages influencers, memory editing, content generation requests, assets, and generation history

## 3. Core Modules

### 3.1 Influencer Service

Responsibilities:

- CRUD for influencer entities
- lifecycle management
- persona status controls (`draft`, `active`, `paused`, `archived`)
- provider profile selection
- top-level consistency policy assignment

### 3.2 Memory Service

Responsibilities:

- manage six memory classes:
  - identity
  - canon
  - style
  - working
  - asset
  - knowledge
- versioning and immutable history
- publish/draft workflow for memory changes
- retrieval APIs by content type and intent
- contradiction-safe updates

Key rule:

Memory is never overwritten destructively. All updates create a new version and optionally a new published pointer.

### 3.3 Content Generation Service

Responsibilities:

- orchestrate end-to-end generation pipeline
- build generation context packs
- call provider abstraction
- run consistency validation
- persist outputs, traces, and embeddings

Supported content types:

- social post
- caption
- script
- image prompt

### 3.4 Prompt Template Engine

Responsibilities:

- render strongly structured templates
- compose sections by memory type
- enforce template contracts per content type
- attach machine-readable constraints for downstream validation

### 3.5 Asset Management Service

Responsibilities:

- store generated and uploaded assets
- attach provenance:
  - prompt
  - model/provider
  - seed
  - generation settings
  - linked influencer
- generate embeddings for similarity search
- maintain asset-to-memory associations

### 3.6 Embedding & Retrieval Service

Responsibilities:

- chunk and embed knowledge documents
- embed memory summaries and assets
- perform hybrid retrieval:
  - structured filters first
  - vector ranking second
  - rule-based memory assembly third

Key principle:

Use retrieval to build a typed context packet instead of dumping arbitrary raw text into a prompt.

### 3.7 Model Provider Layer

Responsibilities:

- abstract text generation providers
- abstract image generation providers
- abstract embedding providers
- isolate provider-specific request/response contracts
- make provider selection runtime-configurable per influencer or environment

### 3.8 Validation Layer

Responsibilities:

- reject content that violates canon or style rules
- detect personality drift
- detect forbidden topics/formats
- ensure output satisfies structural requirements
- optionally trigger repair/regeneration

## 4. Logical Data Flow

### 4.1 Influencer creation

1. User creates influencer shell
2. Identity memory is added
3. Canon and style memory are added
4. Initial validation ensures minimum persona completeness
5. Memory versions are published
6. Retrieval summaries and embeddings are built asynchronously

### 4.2 Content generation

1. Client submits generation request with:
   - influencer_id
   - content_type
   - optional campaign/topic/constraints
2. API stores a `generation_request`
3. Worker retrieves relevant memory package
4. Prompt engine assembles a structured prompt
5. Text/image provider generates output
6. Validation layer scores and checks output
7. If valid:
   - save generation artifact
   - embed output
   - link to memory/assets used
8. If invalid:
   - attempt repair or mark failed with reasons

### 4.3 Knowledge ingestion

1. User uploads source documents
2. Document is normalized and chunked
3. Chunks are embedded
4. Metadata and vectors are stored
5. Retrieval index is refreshed

### 4.4 Asset reuse

1. Prior assets are embedded and tagged
2. New image prompt requests query similar assets
3. Asset memory contributes stable appearance anchors
4. Generated asset is stored with provenance and linked back into memory

## 5. Memory Injection Strategy

The system does not concatenate all memories blindly.

Generation uses a `Context Pack` built in layers:

1. Mandatory invariant layer
   - identity summary
   - canon hard rules
   - style hard rules
2. Content-shaping layer
   - style patterns relevant to the requested content type
   - recent successful generations
3. Dynamic situation layer
   - working memory entries
   - active campaign context
   - recent topics to avoid repetition
4. Knowledge layer
   - top-k RAG chunks filtered by influencer and topic
5. Asset layer
   - visual anchors
   - prior asset references
   - prompt motifs that improved consistency

Each layer has token budgets and priority rules. Lower-priority items are dropped first.

## 6. Consistency Enforcement

### 6.1 Prompt-level enforcement

- system template includes persona contract
- canon rules are explicit and machine-checkable
- template sections are separated by type
- generation objective is isolated from persona invariants

### 6.2 Validation enforcement

- structural validator checks schema and formatting
- canon validator checks contradictions against immutable facts
- style validator checks banned phrases, tone, formatting, and target structure
- semantic validator compares output embedding against approved persona exemplars

### 6.3 Repair strategy

For recoverable failures:

1. generate a violation report
2. feed back concise corrections
3. retry with stricter constraints

Hard canon violations are not auto-published even if repaired unless validation passes.

## 7. Deployment Model

Docker Compose services for MVP:

- `api`
- `worker`
- `beat`
- `postgres`
- `redis`
- `frontend`

## 8. Observability

MVP production requirements:

- structured JSON logs
- request and job correlation IDs
- audit trail for every memory update and generation
- job status transitions
- provider latency and error metrics
- validation failure metrics by influencer and content type

## 9. Security and Access

MVP assumptions:

- admin-only platform initially
- JWT authentication for UI/API
- signed asset URLs
- secrets from environment or Docker secrets
- provider credentials isolated in backend only

## 10. Tradeoffs

### Chosen: modular monolith

Why:

- simpler deployment and faster MVP iteration
- easier transactional workflows across generation, validation, and persistence

### Chosen: PostgreSQL + pgvector

Why:

- keeps structured and vector memory in one operational store
- simpler consistency and versioning logic

### Chosen: Celery + Redis

Why:

- production-proven async jobs
- easy retries and queue partitioning

## 11. MVP Boundaries

Included:

- influencer CRUD
- structured memory management with versioning
- document ingestion and retrieval
- content generation and regeneration
- asset provenance and similarity search
- validation and audit history

Deferred but planned:

- multi-tenant org hierarchy
- approval workflows with human reviewers
- automated social publishing integrations
- advanced fine-tuning pipelines
