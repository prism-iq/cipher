"""
CIPHER Tools Package
Core cognitive components for cross-domain learning and synthesis.
"""

from .hash_learning import HashLearning, compute_entropy, compute_hash, compute_quality
from .cipher_brain import CipherBrain, Domain, Claim, Connection, Pattern
from .domain_learner import DomainLearner, DomainStrategy, DOMAIN_STRATEGIES
from .pattern_detector import PatternDetector, CrossDomainInsight
from .embeddings import (
    EmbeddingService,
    EmbeddingResult,
    SentenceTransformerBackend,
    get_embedding_service,
    embed_text,
    embed_texts,
    compute_similarity
)
from .nlp_extractor import (
    NLPExtractor,
    get_nlp_extractor,
    extract_claims as nlp_extract_claims,
    extract_entities as nlp_extract_entities,
    extract_causal_relations,
    ClaimType,
    EvidenceStrength,
    CausalRelation,
    ScientificEntity,
    ExtractedClaim
)
from .temporal_tracker import (
    TemporalTracker,
    get_temporal_tracker,
    TemporalState,
    EvidenceEvent,
    TemporalPattern,
    ReplicationStatus,
    ClaimStatus
)
from .active_learner import (
    ActiveLearner,
    get_active_learner,
    create_learning_plan,
    LearningStrategy,
    LearningTarget,
    DomainUncertainty,
    ActiveLearningPlan
)

__all__ = [
    # Hash Learning
    'HashLearning',
    'compute_entropy',
    'compute_hash',
    'compute_quality',

    # Brain
    'CipherBrain',
    'Domain',
    'Claim',
    'Connection',
    'Pattern',

    # Domain Learning
    'DomainLearner',
    'DomainStrategy',
    'DOMAIN_STRATEGIES',

    # Pattern Detection
    'PatternDetector',
    'CrossDomainInsight',

    # Embeddings
    'EmbeddingService',
    'EmbeddingResult',
    'SentenceTransformerBackend',
    'get_embedding_service',
    'embed_text',
    'embed_texts',
    'compute_similarity',

    # NLP Extraction
    'NLPExtractor',
    'get_nlp_extractor',
    'nlp_extract_claims',
    'nlp_extract_entities',
    'extract_causal_relations',
    'ClaimType',
    'EvidenceStrength',
    'CausalRelation',
    'ScientificEntity',
    'ExtractedClaim',

    # Temporal Tracking
    'TemporalTracker',
    'get_temporal_tracker',
    'TemporalState',
    'EvidenceEvent',
    'TemporalPattern',
    'ReplicationStatus',
    'ClaimStatus',

    # Active Learning
    'ActiveLearner',
    'get_active_learner',
    'create_learning_plan',
    'LearningStrategy',
    'LearningTarget',
    'DomainUncertainty',
    'ActiveLearningPlan',
]
