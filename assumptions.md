# Assumptions and Decisions

## Product assumptions

- the initial MVP is for internal operators, not end consumers
- one admin team manages multiple influencers
- social publishing is out of scope for the first implementation
- approval remains in-platform rather than via external workflow tools

## Technical assumptions

- Python 3.12 is acceptable for the backend
- PostgreSQL with `pgvector` is available in Docker
- Redis is acceptable for queueing and short-lived cache
- Docker Compose is the local and MVP deployment baseline
- local models may be connected later through provider adapters without changing the domain layer

## AI assumptions

- text generation, image generation, and embedding providers may differ per influencer
- not every generation requires image generation
- embeddings will initially use a fixed dimension per configured provider profile; adapters will normalize this
- validation combines deterministic rules and model-assisted semantics

## Scope decisions

- audio/video generation is deferred
- multi-tenant billing is deferred
- human approval UX is minimal in MVP but audit data is preserved
- identity and canon memory are mandatory before content generation is allowed

## Tradeoff decisions

- chose a modular monolith over microservices for faster delivery and lower operational overhead
- chose JSONB payloads for typed memory versions to preserve flexibility while the memory schema evolves
- chose Celery instead of custom async workers for reliability, retries, and queue separation
