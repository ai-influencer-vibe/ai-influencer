# Memory System Design

## 1. Purpose

The memory system is the core mechanism that preserves identity consistency, prevents canon violations, enables long-term persona evolution, and supports asset reuse.

The design must satisfy four requirements simultaneously:

1. structured editing by humans
2. efficient retrieval by machines
3. immutable history for auditability
4. semantic search for relevant recall

## 2. Memory Principles

### 2.1 Separation by stability

Different memory types change at different rates. The system stores them separately to avoid contamination:

- static memory should not drift because of recent content
- immutable canon should never be silently rewritten
- temporary context should expire or be superseded

### 2.2 Write-once versioning

Updates create new records and versions rather than mutating prior state in place. Published pointers determine which version is currently active.

### 2.3 Retrieval by role, not just similarity

Memory retrieval is controlled by memory class and retrieval policy:

- some memory is always injected
- some memory is conditional
- some memory is only used for validation

### 2.4 Memory compression

Long-running influencer histories can become expensive. Dynamic memories are periodically summarized into durable higher-level notes while raw history remains available.

## 3. Memory Taxonomy

### 3.1 Identity Memory

Purpose:

Defines the stable persona signature and presentation layer.

Fields:

- display_name
- legal_or_stage_name
- pronouns
- age_band
- personality_traits
- tone_of_voice
- speaking_style
- archetype
- audience_profile
- core_values
- catchphrases
- visual_identity_description
- appearance anchors
- brand positioning

Characteristics:

- high priority
- low change frequency
- always available to prompt assembly
- summarized into a compact identity card plus full record

Retrieval use:

- mandatory for every generation
- referenced by validators for drift detection

### 3.2 Canon Memory

Purpose:

Stores immutable truths and prohibitions.

Fields:

- biography
- backstory timeline
- world context
- relationship map
- non-negotiable facts
- forbidden contradictions
- explicit persona rules
- safety boundaries

Characteristics:

- immutable once published
- updates happen by superseding with an explicit canon revision event
- strongest validation priority

Retrieval use:

- injected as hard constraints, not freeform lore
- used by contradiction validator

### 3.3 Style Memory

Purpose:

Encodes how the influencer expresses itself.

Fields:

- writing style descriptors
- sentence length tendencies
- emoji policy
- punctuation policy
- formatting patterns
- preferred hooks
- CTA patterns
- taboo phrases
- content structure templates
- platform-specific style overrides

Characteristics:

- medium change frequency
- may vary by channel and content type
- must be split into global style + per-platform style

Retrieval use:

- selected based on content type and platform
- used both in prompt construction and output validation

### 3.4 Working Memory

Purpose:

Holds short-lived operational context.

Fields:

- active campaigns
- current collaborations
- recent posts
- topic queue
- recently used angles
- unresolved narrative threads
- temporary audience signals

Characteristics:

- dynamic
- time-scoped
- relevance-decays over time
- eligible for summarization and archival

Retrieval use:

- selected by recency, campaign match, and topic overlap
- excluded when stale or conflicting with newer entries

### 3.5 Asset Memory

Purpose:

Anchors visual consistency and reuse of successful assets.

Fields:

- asset identifiers
- asset type
- storage URL
- prompt used
- negative prompt
- model and provider metadata
- seed and settings
- appearance tags
- composition notes
- style motifs
- embedding vector
- similarity links
- approved/reference status

Characteristics:

- multimodal
- tightly linked to visual identity
- used for prompt conditioning and similarity search

Retrieval use:

- similar approved assets are included for image prompt generation
- failed assets may be excluded or used as negative references

### 3.6 Knowledge Memory

Purpose:

Provides topical retrieval beyond core persona memory.

Fields:

- source document
- chunk text
- source type
- tags
- embedding
- freshness metadata
- trust level
- influencer scope

Characteristics:

- RAG-oriented
- chunked and embedded
- not treated as persona truth unless explicitly promoted

Retrieval use:

- retrieved by semantic similarity and metadata filters
- used for factual grounding and campaign support

## 4. Data Model Concepts

The memory system uses four layers of representation:

1. Memory Definition
   - logical category and schema
2. Memory Item
   - a concrete piece of memory for one influencer
3. Memory Version
   - immutable revision of the memory item
4. Memory Projection
   - derived compact summaries and embeddings used for retrieval

This allows human-editable source records and machine-optimized retrieval records to coexist.

## 5. Versioning Strategy

### 5.1 Memory item

Stable logical identity:

- `memory_item.id`
- linked to one influencer
- one memory type

### 5.2 Memory versions

Every update creates:

- incremented version number
- full typed payload snapshot
- change reason
- author
- optional source generation
- status: `draft`, `published`, `archived`

### 5.3 Published pointer

Only one version is the published active version for static memories. Working memory may allow multiple concurrently active entries depending on subtype.

### 5.4 Diffability

Payloads are JSONB with schema validation. Diffs are computed for admin history and approval workflows.

## 6. Retrieval Architecture

Retrieval is a policy-driven pipeline:

### 6.1 Step A: scope filter

Filter by:

- influencer_id
- memory class
- status
- platform
- content_type
- language

### 6.2 Step B: hard inclusion

Always include:

- published identity summary
- published canon rule set
- relevant global style profile

### 6.3 Step C: query-aware retrieval

Retrieve:

- working memory by recency and tag match
- knowledge chunks by vector similarity and trust level
- asset memory by similarity and approved status

### 6.4 Step D: compaction

Convert raw results into a normalized `Context Pack`.

### 6.5 Step E: token budgeting

Keep higher-priority memory and remove low-value details first.

## 7. Context Pack Structure

The generation pipeline uses a machine-readable object:

```json
{
  "identity_card": {
    "name": "string",
    "traits": ["string"],
    "tone": "string",
    "speaking_style": "string",
    "visual_identity": "string"
  },
  "canon_rules": [
    {"rule": "string", "severity": "hard"}
  ],
  "style_profile": {
    "global_rules": ["string"],
    "platform_rules": ["string"],
    "patterns": ["string"],
    "avoid": ["string"]
  },
  "working_context": [
    {"type": "campaign", "summary": "string", "priority": 0.95}
  ],
  "knowledge_context": [
    {"chunk_id": "uuid", "summary": "string", "score": 0.88}
  ],
  "asset_context": [
    {"asset_id": "uuid", "summary": "string", "score": 0.91}
  ],
  "generation_constraints": {
    "content_type": "post",
    "platform": "instagram"
  }
}
```

This is what the prompt engine consumes. The pack is also stored for auditability.

## 8. Memory Update Rules

### 8.1 Identity updates

Allowed for:

- refinement of tone
- audience updates
- visual identity clarification

Requires:

- version note
- consistency validation against canon

### 8.2 Canon updates

Allowed only through explicit canon revision flow.

Requires:

- revision reason
- effective date
- contradiction review

### 8.3 Style updates

Allowed frequently.

Requires:

- content type or platform scope
- sample or rationale when possible

### 8.4 Working memory updates

May be system-generated from campaigns, generations, and operator notes.

Requires:

- TTL or review date where applicable

### 8.5 Asset memory updates

Mostly system-generated.

Requires:

- provenance metadata
- moderation/approval status

### 8.6 Knowledge updates

Created via ingestion pipeline.

Requires:

- source metadata
- chunk lineage

## 9. Validation Against Memory

### 9.1 Pre-generation checks

- influencer has published identity, canon, and style baseline
- memory versions are not in conflicting states
- required asset anchors exist for image prompt generation if configured as mandatory

### 9.2 Post-generation checks

- output does not contradict canon
- output matches style constraints
- output respects formatting rules
- output is not too similar to recent posts
- output embedding stays within persona similarity threshold

### 9.3 Human-review hooks

The platform stores:

- violated rule IDs
- validator explanations
- retry history

## 10. Memory Summarization and Evolution

Working memory must not grow unbounded. The system periodically:

1. groups stale working entries by campaign/topic
2. creates a summary memory item
3. archives raw entries from active retrieval
4. keeps raw entries for audits and future reprocessing

This preserves long-term continuity without bloating prompt context.

## 11. Similarity Search Design

Vectors are stored for:

- knowledge chunks
- asset memory records
- generation outputs
- selected memory projections

Similarity use cases:

- retrieve topical knowledge
- find visual references
- detect repetitive content
- compare outputs with approved persona exemplars

## 12. Failure Modes and Mitigations

### Personality drift

Mitigation:

- mandatory identity injection
- embedding-based drift scoring
- regression tests with golden prompts

### Canon contradiction

Mitigation:

- hard canon validator
- immutable canon storage
- explicit revision workflow

### Memory bloat

Mitigation:

- typed retrieval policies
- summarization jobs
- token budgets per layer

### Asset inconsistency

Mitigation:

- approved reference asset set
- prompt provenance tracking
- similarity-based visual anchor retrieval

## 13. Why this design scales

- memory types can be indexed independently
- retrieval policies can evolve without changing core records
- provider changes do not affect memory structure
- memory history stays auditable
- vector search and structured filters coexist in one model
