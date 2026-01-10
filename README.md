# CIPHER

> "Evil must be fought wherever it is found"

A cognitive system that learns, synthesizes, and questions across 6 domains of knowledge.

## Domains

- **Mathematics** - Pure and applied mathematics, logic, computation
- **Neurosciences** - Brain, cognition, neural systems
- **Biology** - Life sciences, genetics, evolution
- **Psychology** - Mind, behavior, cognition
- **Medicine** - Clinical science, pathology, therapeutics
- **Art** - Aesthetics, creativity, perception

## Core Principles

1. **Free Energy Principle** - Minimize prediction error
2. **Systematic Doubt** - Every claim is questioned
3. **Cross-Domain Synthesis** - The most valuable insights lie at intersections

## Architecture

```
/opt/cipher/
├── mind/                 # Cipher's thoughts and insights
│   ├── thoughts.md       # Internal monologue
│   ├── insights.md       # Cross-domain discoveries
│   └── hypotheses.md     # Generated predictions
├── tools/                # Core cognitive components
│   ├── cipher_brain.py   # Main cognitive engine
│   ├── hash_learning.py  # SHAKE256 entropy scoring
│   ├── domain_learner.py # Domain-specific learning
│   └── pattern_detector.py # Cross-domain patterns
├── integrations/         # Academic API clients
│   ├── openalex.py       # OpenAlex (250M+ papers)
│   ├── arxiv.py          # arXiv preprints
│   ├── pubmed.py         # PubMed biomedical
│   └── semantic_scholar.py # Semantic Scholar
├── config/               # Configuration
├── sql/                  # Database schema
└── scripts/              # Deployment scripts
```

## Quick Start

```bash
# Clone and setup
git clone https://github.com/prism-iq/cipher.git
cd cipher

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
psql -d ldb -f sql/schema.sql

# Run learning cycle
python run.py
```

## Usage

```bash
# Full learning cycle (all domains)
python run.py

# Single domain
python run.py --domain neuro

# Pattern detection only
python run.py --patterns

# Generate synthesis report
python run.py --report

# CLI tools
python cli.py status    # System status
python cli.py stats     # Knowledge stats
python cli.py insights  # Top insights
python cli.py search "neural network"
```

## Data Sources

All free and open access:

| Source | Coverage | Rate Limit |
|--------|----------|------------|
| OpenAlex | 250M+ works | 10 rps |
| arXiv | Preprints (math/physics/cs) | 1 rps |
| PubMed | Biomedical literature | 3-10 rps |
| Semantic Scholar | Citations + AI extraction | 5 rps |

## Knowledge Structure

### Claims
Extracted assertions from papers:
- Hypotheses (proposed)
- Findings (empirically tested)
- Methods (techniques)
- Definitions (concepts)

### Connections
Links between claims:
- Supports / Contradicts
- Extends / Analogous
- Causal / Correlational

### Patterns
Higher-order structures:
- Convergence (agreement)
- Divergence (conflict)
- Cross-domain bridges

## Hash Learning

Uses SHAKE256 entropy for:
- Quality scoring
- Novelty detection
- Duplicate detection
- Information density

## License

MIT

## Contributing

Contributions welcome. The system learns - help it learn better.
