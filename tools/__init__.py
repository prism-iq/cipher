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
]
