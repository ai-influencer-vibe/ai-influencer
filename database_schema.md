# Database Schema Design

## 1. Storage Strategy

PostgreSQL is the primary datastore. `pgvector` enables vector similarity while preserving transactional consistency with relational records.

Schema design goals:

- strict influencer scoping
- explicit version history
- auditability for every generation and memory update
- support for hybrid retrieval
- provider-agnostic provenance

## 2. Extensions

Required PostgreSQL extensions:

- `uuid-ossp`
- `pgvector`

## 3. Core Entities

### 3.1 influencers

Columns:

- `id UUID PK`
- `slug VARCHAR(120) UNIQUE NOT NULL`
- `display_name VARCHAR(255) NOT NULL`
- `status VARCHAR(32) NOT NULL`
- `default_language VARCHAR(16) NOT NULL DEFAULT 'en'`
- `primary_platform VARCHAR(32) NULL`
- `provider_profile_id UUID NULL FK -> provider_profiles.id`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `archived_at TIMESTAMPTZ NULL`

### 3.2 provider_profiles

Columns:

- `id UUID PK`
- `name VARCHAR(120) UNIQUE NOT NULL`
- `text_provider VARCHAR(64) NOT NULL`
- `image_provider VARCHAR(64) NOT NULL`
- `embedding_provider VARCHAR(64) NOT NULL`
- `text_model VARCHAR(128) NOT NULL`
- `image_model VARCHAR(128) NULL`
- `embedding_model VARCHAR(128) NOT NULL`
- `settings JSONB NOT NULL DEFAULT '{}'`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

### 3.3 prompt_templates

Columns:

- `id UUID PK`
- `name VARCHAR(120) NOT NULL`
- `content_type VARCHAR(64) NOT NULL`
- `platform VARCHAR(64) NULL`
- `version INTEGER NOT NULL`
- `status VARCHAR(32) NOT NULL`
- `template_body TEXT NOT NULL`
- `template_schema JSONB NOT NULL`
- `output_schema JSONB NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `superseded_at TIMESTAMPTZ NULL`

Constraint:

- unique `(name, version)`

## 4. Memory Tables

### 4.1 memory_items

Columns:

- `id UUID PK`
- `influencer_id UUID NOT NULL FK -> influencers.id`
- `memory_type VARCHAR(32) NOT NULL`
- `subtype VARCHAR(64) NULL`
- `key VARCHAR(128) NOT NULL`
- `title VARCHAR(255) NOT NULL`
- `is_invariant BOOLEAN NOT NULL DEFAULT FALSE`
- `is_mutable BOOLEAN NOT NULL DEFAULT TRUE`
- `current_version_id UUID NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

Constraint:

- unique `(influencer_id, memory_type, key)`

### 4.2 memory_versions

Columns:

- `id UUID PK`
- `memory_item_id UUID NOT NULL FK -> memory_items.id`
- `version INTEGER NOT NULL`
- `status VARCHAR(32) NOT NULL`
- `payload JSONB NOT NULL`
- `summary TEXT NOT NULL`
- `change_reason TEXT NULL`
- `source VARCHAR(32) NOT NULL`
- `source_generation_id UUID NULL FK -> generation_outputs.id`
- `created_by VARCHAR(255) NOT NULL`
- `effective_at TIMESTAMPTZ NOT NULL`
- `expires_at TIMESTAMPTZ NULL`
- `created_at TIMESTAMPTZ NOT NULL`

Constraint:

- unique `(memory_item_id, version)`

Indexes:

- btree on `(memory_item_id, status, created_at DESC)`
- gin on `payload`

### 4.3 memory_projections

Columns:

- `id UUID PK`
- `memory_version_id UUID NOT NULL FK -> memory_versions.id`
- `influencer_id UUID NOT NULL FK -> influencers.id`
- `projection_type VARCHAR(32) NOT NULL`
- `content TEXT NOT NULL`
- `metadata JSONB NOT NULL DEFAULT '{}'`
- `embedding VECTOR(1536) NULL`
- `created_at TIMESTAMPTZ NOT NULL`

Indexes:

- btree on `(influencer_id, projection_type)`
- ivfflat on `embedding`
- gin on `metadata`

### 4.4 memory_links

Columns:

- `id UUID PK`
- `influencer_id UUID NOT NULL FK -> influencers.id`
- `source_memory_item_id UUID NOT NULL FK -> memory_items.id`
- `target_type VARCHAR(32) NOT NULL`
- `target_id UUID NOT NULL`
- `relationship_type VARCHAR(64) NOT NULL`
- `metadata JSONB NOT NULL DEFAULT '{}'`
- `created_at TIMESTAMPTZ NOT NULL`

## 5. Knowledge Memory Tables

### 5.1 documents

Columns:

- `id UUID PK`
- `influencer_id UUID NOT NULL FK -> influencers.id`
- `title VARCHAR(255) NOT NULL`
- `source_type VARCHAR(32) NOT NULL`
- `source_uri TEXT NULL`
- `mime_type VARCHAR(128) NULL`
- `status VARCHAR(32) NOT NULL`
- `metadata JSONB NOT NULL DEFAULT '{}'`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

### 5.2 document_chunks

Columns:

- `id UUID PK`
- `document_id UUID NOT NULL FK -> documents.id`
- `influencer_id UUID NOT NULL FK -> influencers.id`
- `chunk_index INTEGER NOT NULL`
- `content TEXT NOT NULL`
- `token_count INTEGER NOT NULL`
- `metadata JSONB NOT NULL DEFAULT '{}'`
- `embedding VECTOR(1536) NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`

Constraint:

- unique `(document_id, chunk_index)`

## 6. Asset Tables

### 6.1 assets

Columns:

- `id UUID PK`
- `influencer_id UUID NOT NULL FK -> influencers.id`
- `asset_type VARCHAR(32) NOT NULL`
- `storage_path TEXT NOT NULL`
- `mime_type VARCHAR(128) NOT NULL`
- `sha256 VARCHAR(64) NOT NULL`
- `status VARCHAR(32) NOT NULL`
- `width INTEGER NULL`
- `height INTEGER NULL`
- `duration_seconds INTEGER NULL`
- `metadata JSONB NOT NULL DEFAULT '{}'`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

Constraint:

- unique `(sha256)`

### 6.2 asset_generations

Columns:

- `id UUID PK`
- `asset_id UUID NOT NULL FK -> assets.id`
- `influencer_id UUID NOT NULL FK -> influencers.id`
- `generation_request_id UUID NULL FK -> generation_requests.id`
- `provider VARCHAR(64) NOT NULL`
- `model VARCHAR(128) NOT NULL`
- `prompt TEXT NOT NULL`
- `negative_prompt TEXT NULL`
- `parameters JSONB NOT NULL DEFAULT '{}'`
- `seed VARCHAR(64) NULL`
- `created_at TIMESTAMPTZ NOT NULL`

### 6.3 asset_embeddings

Columns:

- `id UUID PK`
- `asset_id UUID NOT NULL FK -> assets.id`
- `influencer_id UUID NOT NULL FK -> influencers.id`
- `embedding_model VARCHAR(128) NOT NULL`
- `embedding VECTOR(1536) NOT NULL`
- `metadata JSONB NOT NULL DEFAULT '{}'`
- `created_at TIMESTAMPTZ NOT NULL`

Constraint:

- unique `(asset_id, embedding_model)`

## 7. Generation Tables

### 7.1 generation_requests

Columns:

- `id UUID PK`
- `influencer_id UUID NOT NULL FK -> influencers.id`
- `content_type VARCHAR(64) NOT NULL`
- `platform VARCHAR(64) NULL`
- `status VARCHAR(32) NOT NULL`
- `requested_by VARCHAR(255) NOT NULL`
- `input_payload JSONB NOT NULL`
- `provider_profile_snapshot JSONB NOT NULL`
- `prompt_template_id UUID NULL FK -> prompt_templates.id`
- `created_at TIMESTAMPTZ NOT NULL`
- `started_at TIMESTAMPTZ NULL`
- `completed_at TIMESTAMPTZ NULL`

### 7.2 generation_contexts

Columns:

- `id UUID PK`
- `generation_request_id UUID NOT NULL FK -> generation_requests.id`
- `context_pack JSONB NOT NULL`
- `token_budget JSONB NOT NULL`
- `retrieval_trace JSONB NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`

### 7.3 generation_outputs

Columns:

- `id UUID PK`
- `generation_request_id UUID NOT NULL FK -> generation_requests.id`
- `attempt_number INTEGER NOT NULL`
- `status VARCHAR(32) NOT NULL`
- `provider VARCHAR(64) NOT NULL`
- `model VARCHAR(128) NOT NULL`
- `raw_output TEXT NOT NULL`
- `normalized_output JSONB NOT NULL`
- `output_text TEXT NULL`
- `asset_id UUID NULL FK -> assets.id`
- `embedding VECTOR(1536) NULL`
- `created_at TIMESTAMPTZ NOT NULL`

Constraint:

- unique `(generation_request_id, attempt_number)`

### 7.4 validation_results

Columns:

- `id UUID PK`
- `generation_output_id UUID NOT NULL FK -> generation_outputs.id`
- `validator_name VARCHAR(64) NOT NULL`
- `passed BOOLEAN NOT NULL`
- `score NUMERIC(5,4) NULL`
- `severity VARCHAR(16) NOT NULL`
- `details JSONB NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`

## 8. Operational Tables

### 8.1 jobs

Columns:

- `id UUID PK`
- `job_type VARCHAR(64) NOT NULL`
- `queue_name VARCHAR(64) NOT NULL`
- `status VARCHAR(32) NOT NULL`
- `reference_type VARCHAR(32) NULL`
- `reference_id UUID NULL`
- `payload JSONB NOT NULL`
- `error_message TEXT NULL`
- `retry_count INTEGER NOT NULL DEFAULT 0`
- `scheduled_at TIMESTAMPTZ NOT NULL`
- `started_at TIMESTAMPTZ NULL`
- `completed_at TIMESTAMPTZ NULL`
- `created_at TIMESTAMPTZ NOT NULL`

### 8.2 audit_logs

Columns:

- `id UUID PK`
- `entity_type VARCHAR(64) NOT NULL`
- `entity_id UUID NOT NULL`
- `action VARCHAR(64) NOT NULL`
- `actor VARCHAR(255) NOT NULL`
- `payload JSONB NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`

## 9. Relationship Summary

- one `influencer` has many `memory_items`
- one `memory_item` has many `memory_versions`
- one `memory_version` may have many `memory_projections`
- one `influencer` has many `documents`, `assets`, `generation_requests`
- one `generation_request` has one `generation_context` and many `generation_outputs`
- one `generation_output` has many `validation_results`
- one `asset` may have one or many `asset_generations`

## 10. Suggested Enum Domains

Use PostgreSQL enums or application-controlled string enums for:

- influencer status
- memory type
- memory version status
- generation status
- validator severity
- asset status
- document status

Application-level enums are more migration-friendly in early MVP stages.

## 11. Initial Migration Order

1. extensions
2. provider_profiles
3. influencers
4. prompt_templates
5. memory_items
6. generation_requests
7. assets
8. generation_outputs
9. memory_versions
10. documents
11. document_chunks
12. memory_projections
13. generation_contexts
14. validation_results
15. asset_generations
16. asset_embeddings
17. memory_links
18. jobs
19. audit_logs
