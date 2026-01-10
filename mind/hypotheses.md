# CIPHER Hypotheses

Generated hypotheses from cross-domain pattern detection.
These are testable predictions that emerge from synthesis.

---

## What Makes a Good Hypothesis?

1. **Specific**: Clear about what is predicted
2. **Testable**: Can be empirically investigated
3. **Falsifiable**: Could be proven wrong
4. **Novel**: Not already established
5. **Cross-domain**: Bridges multiple fields

---

## Active Hypotheses

<!-- Auto-populated from synthesis.hypotheses -->

### H1: Semantic Embedding Unification (Type 2: Unifying Principle)
**Status**: `proposed` | **Domains**: Math, Neuro, Psychology

**Hypothesis**: The distributed representation space used in neural networks (word2vec, transformers) operates on the same mathematical principles as the brain's semantic memory system.

**Reasoning**: Both systems:
- Map concepts to high-dimensional vectors
- Use distance/similarity for meaning
- Show analogical structure (king - man + woman ≈ queen)
- Exhibit compositionality

**Test**: Compare embedding similarity patterns to fMRI activation patterns during semantic tasks.

**Supporting patterns**: Information-theoretic bridges, Network analogies

---

### H2: Entropy as Cross-Domain Invariant (Type 2: Unifying Principle)
**Status**: `proposed` | **Domains**: Math, Biology, Neuro, Art

**Hypothesis**: Shannon entropy provides a universal measure that predicts quality/complexity across all CIPHER domains.

**Reasoning**:
- High-quality academic text has specific entropy signatures
- Biological complexity correlates with information content
- Neural coding efficiency relates to entropy
- Aesthetic appeal may track Kolmogorov complexity

**Test**: Correlate entropy scores across domain-specific quality measures.

**Current evidence**: HashLearning module shows entropy correlates with citation counts.

---

### H3: Active Inference Architecture (Type 1: Mechanism Transfer)
**Status**: `proposed` | **Domains**: Neuro, Math, Psychology

**Hypothesis**: The Free Energy Principle from neuroscience can be implemented as a learning optimization algorithm in CIPHER, improving cross-domain pattern detection.

**Reasoning**:
- Brain minimizes prediction error through active inference
- CIPHER detects patterns but doesn't actively seek them
- Active inference would prioritize high-uncertainty domains
- This mirrors how scientists actually explore knowledge

**Test**: Implement active inference module, compare pattern discovery rate to passive learning.

**Implementation path**:
1. Add uncertainty estimates to all claims
2. Compute expected information gain for potential queries
3. Prioritize API calls by information gain
4. Track improvement in cross-domain discoveries

---

### H4: Contradiction Clustering Reveals Paradigm Boundaries (Type 5: Novel Prediction)
**Status**: `proposed` | **Domains**: All

**Hypothesis**: Clusters of contradictions in the knowledge base mark boundaries between scientific paradigms.

**Reasoning**:
- Paradigm shifts occur when evidence contradicts established theory
- Contradictions cluster around contested topics
- These clusters indicate where scientific understanding is evolving
- Cross-domain contradictions may indicate foundational issues

**Test**: Cluster contradictions by semantic similarity; map to known paradigm debates.

**Expected findings**:
- Consciousness (Neuro/Psychology/Philosophy)
- Free will (Neuro/Psychology)
- Emergence (Math/Biology/Physics)
- Creativity (Art/Psychology/Neuro)

---

### H5: Bridge Concepts Follow Power Law (Type 5: Novel Prediction)
**Status**: `proposed` | **Domains**: Math, All

**Hypothesis**: The distribution of cross-domain bridge concepts follows a power law, with a few highly-connected concepts (information, network, optimization) and many domain-specific ones.

**Reasoning**:
- Network topology in many domains follows power laws
- Known bridges in CIPHER (information, entropy, network) are highly connected
- This would explain why certain concepts appear across all science

**Test**:
1. Count cross-domain connections per concept
2. Plot frequency distribution
3. Fit power law vs exponential

**Implications if true**:
- Focus on hub concepts for maximum cross-domain insight
- Rare bridges may indicate novel discoveries

---

---

## Hypothesis Categories

### Type 1: Mechanism Transfer
*"Mechanism X from domain A also operates in domain B"*

Template: The [mechanism] that produces [effect] in [Domain A] may also
underlie [similar effect] in [Domain B] because [reasoning based on
structural similarity].

### Type 2: Unifying Principle
*"Phenomena X and Y are manifestations of the same underlying principle"*

Template: Both [phenomenon A] in [Domain A] and [phenomenon B] in [Domain B]
may be instances of a more fundamental [principle], evidenced by
[shared features/patterns].

### Type 3: Gap Filling
*"Unknown X in domain A can be inferred from known Y in domain B"*

Template: The unknown [property/mechanism] of [phenomenon A] can be predicted
from [known property/mechanism] of [analogous phenomenon B] because
[structural analogy reasoning].

### Type 4: Contradiction Resolution
*"Apparent contradiction between X and Y is resolved by Z"*

Template: The apparent contradiction between [finding A] and [finding B]
can be resolved if [hidden variable/condition] differs between the studies,
specifically [proposed mechanism].

### Type 5: Novel Prediction
*"If pattern P holds, then previously unobserved Q should exist"*

Template: Given the pattern [P] observed across [domains], we predict
the existence of [Q], which would manifest as [observable features]
in [specific context].

---

## Hypothesis Tracking

### Status Codes
- `proposed`: Newly generated, not yet investigated
- `investigating`: Being actively researched
- `supported`: Evidence found in favor
- `refuted`: Evidence found against
- `modified`: Updated based on new evidence
- `archived`: No longer active

### Evidence Tracking
For each hypothesis, we track:
- Supporting claims (with IDs)
- Refuting claims (with IDs)
- Related experiments/studies
- Status changes and dates

---

## Generation Process

Hypotheses are generated from patterns via:

1. **Convergence patterns** → Unifying principle hypotheses
2. **Divergence patterns** → Contradiction resolution hypotheses
3. **Cross-domain connections** → Mechanism transfer hypotheses
4. **Knowledge gaps** → Gap filling hypotheses
5. **High-novelty patterns** → Novel prediction hypotheses

---

## Priority Queue

Hypotheses are prioritized by:
1. Cross-domain scope (more domains = higher priority)
2. Testability (easier to test = higher priority)
3. Novelty (more surprising = higher priority)
4. Supporting evidence strength

---

## Validation Protocol

When a hypothesis gains/loses support:

1. Update status in database
2. Record evidence (claim IDs)
3. Update this document
4. Generate follow-up questions
5. If supported: Look for extensions
6. If refuted: Analyze why, learn from it

---

*Hypotheses are the engine of understanding. Each one is a question
that reality can answer.*
