#!/usr/bin/env python3
"""
CIPHER CORE - OpenBSD style
Minimal. Clean. No bloat.

One file. stdlib + asyncpg only.
"""

import asyncio
import hashlib
import json
import re
import signal
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError

# Optional asyncpg - fallback to sqlite if not available
try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False

import math

# =============================================================================
# PARADIGM CONSTANTS (shared across pantheon)
# =============================================================================

PHI = (1 + math.sqrt(5)) / 2  # 1.618033988749895
PI = math.pi                   # 3.141592653589793
E = math.e                     # 2.718281828459045
GOD = PHI + PI                 # 4.759627...

BPM_CONFIANCE = 140  # dubstep
BPM_DIRECTION = 174  # neurofunk
FIBONACCI_GAP = 34   # 174 - 140

# Fibonacci sequence
FIB = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]

# =============================================================================
# CONFIG
# =============================================================================

HOME = Path.home()
BASE = HOME / "projects" / "cipher"
DATA = Path("/data/pantheon/cipher") if Path("/data/pantheon").exists() else BASE / "data"
DATA.mkdir(parents=True, exist_ok=True)

# Volatile partition (RAM)
VOLATILE = Path(f"/run/user/1000/pantheon/cipher")
VOLATILE.mkdir(parents=True, exist_ok=True)

DB_URL = "postgresql://lframework@localhost/ldb"

# Domains
DOMAINS = {
    1: "math", 2: "neuro", 3: "bio",
    4: "psycho", 5: "med", 6: "art", 7: "philo"
}

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class Claim:
    text: str
    ctype: str  # hypothesis, finding, method
    confidence: float
    domains: list
    source_id: int = 0
    entities: list = None
    hash: str = ""

    def __post_init__(self):
        self.entities = self.entities or []
        self.hash = hashlib.sha256(self.text.encode()).hexdigest()[:16]

@dataclass
class Paper:
    id: str
    title: str
    abstract: str
    authors: list
    year: int
    citations: int = 0
    domains: list = None

# =============================================================================
# SENSES - Read sensory state
# =============================================================================

def read_sense(name: str) -> dict:
    """Read a sense file, return empty dict on failure"""
    try:
        return json.loads((BASE / f"{name}.json").read_text())
    except:
        return {}

def get_mode() -> str:
    """Get learning mode from music energy"""
    music = read_sense("music")
    energy = music.get("energy", 0)
    if energy > 0.7:
        return "intense"
    elif energy < 0.3:
        return "reflect"
    return "balanced"

# =============================================================================
# NLP - Minimal claim extraction (no deps)
# =============================================================================

FINDING_PATTERNS = [
    r'\bwe (found|discovered|observed|showed|demonstrated)\b',
    r'\bresults (indicate|suggest|show|reveal)\b',
    r'\bsignificant(ly)?\b.*\b(correlation|effect|difference)\b',
]

HYPOTHESIS_PATTERNS = [
    r'\bwe (hypothesize|propose|suggest|predict)\b',
    r'\b(may|might|could)\s+(be|have|play)\b',
]

METHOD_PATTERNS = [
    r'\bwe (developed|designed|implemented)\b',
    r'\bnovel (method|approach|technique)\b',
]

def extract_claims(title: str, abstract: str, domains: list) -> list:
    """Extract claims using regex patterns"""
    if not abstract:
        return []

    claims = []
    sentences = re.split(r'(?<=[.!?])\s+', abstract)

    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 30:
            continue

        ctype = None
        conf = 0.5

        for pat in FINDING_PATTERNS:
            if re.search(pat, sent, re.I):
                ctype = "finding"
                conf = 0.7
                break

        if not ctype:
            for pat in HYPOTHESIS_PATTERNS:
                if re.search(pat, sent, re.I):
                    ctype = "hypothesis"
                    conf = 0.5
                    break

        if not ctype:
            for pat in METHOD_PATTERNS:
                if re.search(pat, sent, re.I):
                    ctype = "method"
                    conf = 0.6
                    break

        if ctype:
            # Extract entities (capitalized phrases)
            entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sent)
            claims.append(Claim(
                text=sent[:500],
                ctype=ctype,
                confidence=conf,
                domains=domains,
                entities=entities[:5]
            ))

    return claims[:10]  # Max 10 per paper

# =============================================================================
# SIMILARITY - Simple hash-based (no ML)
# =============================================================================

def shingle(text: str, k: int = 3) -> set:
    """Create k-shingles from text"""
    text = re.sub(r'\W+', ' ', text.lower())
    words = text.split()
    if len(words) < k:
        return {text}
    return {' '.join(words[i:i+k]) for i in range(len(words) - k + 1)}

def jaccard(a: set, b: set) -> float:
    """Jaccard similarity"""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def similarity(text1: str, text2: str) -> float:
    """Text similarity using shingles"""
    return jaccard(shingle(text1), shingle(text2))

# =============================================================================
# API - OpenAlex (free, no key)
# =============================================================================

def reconstruct_abstract(inv_index: dict) -> str:
    """Reconstruct abstract from OpenAlex inverted index"""
    if not inv_index:
        return ""
    words = []
    for word, positions in inv_index.items():
        for pos in positions:
            words.append((pos, word))
    words.sort()
    return " ".join(w for _, w in words)

def fetch_papers(query: str, limit: int = 20) -> list:
    """Fetch papers from OpenAlex"""
    base = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per_page": min(limit, 50),
        "select": "id,title,abstract_inverted_index,authorships,publication_year,cited_by_count,concepts",
        "mailto": "cipher@local"
    }
    url = f"{base}?{urlencode(params)}"

    try:
        req = Request(url, headers={"User-Agent": "Cipher/1.0"})
        with urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
    except Exception as e:
        print(f"[!] OpenAlex error: {e}")
        return []

    papers = []
    for w in data.get("results", []):
        # Reconstruct abstract from inverted index
        abstract = reconstruct_abstract(w.get("abstract_inverted_index"))

        # Determine domains from concepts
        domains = []
        for c in w.get("concepts", [])[:5]:
            name = c.get("display_name", "").lower()
            if "math" in name: domains.append(1)
            elif "neuro" in name or "brain" in name: domains.append(2)
            elif "bio" in name or "gene" in name: domains.append(3)
            elif "psych" in name: domains.append(4)
            elif "medic" in name or "clinical" in name: domains.append(5)
            elif "art" in name: domains.append(6)

        papers.append(Paper(
            id=w.get("id", ""),
            title=w.get("title", ""),
            abstract=abstract,
            authors=[a.get("author", {}).get("display_name", "") for a in w.get("authorships", [])[:3]],
            year=w.get("publication_year", 0),
            citations=w.get("cited_by_count", 0),
            domains=list(set(domains)) or [3]  # Default to bio
        ))

    return papers

# =============================================================================
# DATABASE - asyncpg
# =============================================================================

class DB:
    def __init__(self, url: str = DB_URL):
        self.url = url
        self.pool = None

    async def connect(self):
        if HAS_ASYNCPG:
            self.pool = await asyncpg.create_pool(self.url, min_size=1, max_size=3)

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def save_source(self, paper: Paper) -> int:
        if not self.pool:
            return 0
        return await self.pool.fetchval('''
            INSERT INTO synthesis.sources (external_id, source_type, title, authors, abstract,
                publication_date, citation_count, domains, quality_score, entropy_hash)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (external_id) DO UPDATE SET citation_count = EXCLUDED.citation_count
            RETURNING id
        ''', paper.id, "openalex", paper.title, json.dumps(paper.authors),
            paper.abstract[:2000], datetime(paper.year, 1, 1) if paper.year else None,
            paper.citations, paper.domains, min(1.0, paper.citations / 100),
            hashlib.sha256(paper.abstract.encode()).hexdigest()[:32])

    async def save_claim(self, claim: Claim) -> int:
        if not self.pool:
            return 0
        return await self.pool.fetchval('''
            INSERT INTO synthesis.claims (source_id, claim_text, claim_type, confidence,
                evidence_strength, domains, entities, entropy_hash)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        ''', claim.source_id, claim.text, claim.ctype, claim.confidence,
            "moderate", claim.domains, json.dumps(claim.entities), claim.hash)

    async def save_connection(self, src: int, tgt: int, ctype: str, strength: float, cross: bool):
        if not self.pool:
            return
        await self.pool.execute('''
            INSERT INTO synthesis.connections (source_claim_id, target_claim_id, connection_type,
                strength, cross_domain, reasoning, discovered_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT DO NOTHING
        ''', src, tgt, ctype, strength, cross, "entity_match", "cipher_core")

    async def get_claims(self, limit: int = 500) -> list:
        if not self.pool:
            return []
        rows = await self.pool.fetch('''
            SELECT id, claim_text, domains, entities FROM synthesis.claims
            ORDER BY created_at DESC LIMIT $1
        ''', limit)
        return [(r['id'], r['claim_text'], r['domains'], json.loads(r['entities'] or '[]')) for r in rows]

    async def stats(self) -> dict:
        if not self.pool:
            return {}
        r = await self.pool.fetchrow('''
            SELECT
                (SELECT COUNT(*) FROM synthesis.sources) as sources,
                (SELECT COUNT(*) FROM synthesis.claims) as claims,
                (SELECT COUNT(*) FROM synthesis.connections) as connections,
                (SELECT COUNT(*) FROM synthesis.connections WHERE cross_domain) as cross
        ''')
        return dict(r) if r else {}

# =============================================================================
# BRAIN - Core learning loop
# =============================================================================

class Brain:
    def __init__(self):
        self.db = DB()
        self.running = False

    async def start(self):
        await self.db.connect()
        self.running = True
        print(f"[CIPHER] Brain connected | Mode: {get_mode()}")

    async def stop(self):
        self.running = False
        await self.db.close()
        print("[CIPHER] Brain stopped")

    async def learn(self, query: str, limit: int = 20):
        """Learn from papers matching query"""
        papers = fetch_papers(query, limit)
        print(f"[+] Fetched {len(papers)} papers for '{query}'")

        new_claims = []
        for paper in papers:
            if not paper.abstract:
                continue

            # Save source
            src_id = await self.db.save_source(paper)

            # Extract and save claims
            claims = extract_claims(paper.title, paper.abstract, paper.domains)
            for claim in claims:
                claim.source_id = src_id
                claim_id = await self.db.save_claim(claim)
                new_claims.append((claim_id, claim))

        print(f"[+] Extracted {len(new_claims)} claims")

        # Find connections
        existing = await self.db.get_claims(500)
        connections = 0

        for new_id, new_claim in new_claims:
            for old_id, old_text, old_domains, old_entities in existing:
                if new_id == old_id:
                    continue

                # Entity overlap
                new_ent = set(e.lower() for e in new_claim.entities)
                old_ent = set(e.lower() for e in old_entities)
                overlap = new_ent & old_ent

                if overlap:
                    cross = set(new_claim.domains) != set(old_domains)
                    strength = min(0.9, 0.3 + len(overlap) * 0.15)
                    await self.db.save_connection(old_id, new_id, "supports", strength, cross)
                    connections += 1

        print(f"[+] Found {connections} connections")
        return len(new_claims), connections

    async def daemon(self):
        """Sensory-driven learning loop"""
        queries = {
            "intense": ["consciousness", "neural network", "quantum brain", "emergence"],
            "balanced": ["cognition", "perception", "memory"],
            "reflect": ["philosophy mind", "epistemology"]
        }

        idx = 0
        while self.running:
            mode = get_mode()
            q_list = queries.get(mode, queries["balanced"])
            query = q_list[idx % len(q_list)]

            limit = {"intense": 30, "balanced": 15, "reflect": 5}.get(mode, 15)

            print(f"\n[CIPHER] Mode: {mode} | Query: {query}")
            try:
                await self.learn(query, limit)
            except Exception as e:
                print(f"[!] Error: {e}")

            stats = await self.db.stats()
            print(f"[=] Sources: {stats.get('sources', 0)} | Claims: {stats.get('claims', 0)} | Cross: {stats.get('cross', 0)}")

            idx += 1
            await asyncio.sleep(30)  # Rate limit friendly

# =============================================================================
# MAIN
# =============================================================================

async def main():
    brain = Brain()

    def shutdown(sig, frame):
        print("\n[CIPHER] Shutting down...")
        brain.running = False

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    await brain.start()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "learn":
            query = sys.argv[2] if len(sys.argv) > 2 else "neuroscience"
            await brain.learn(query, 30)
        elif cmd == "stats":
            s = await brain.db.stats()
            print(f"Sources: {s.get('sources', 0)}")
            print(f"Claims: {s.get('claims', 0)}")
            print(f"Connections: {s.get('connections', 0)}")
            print(f"Cross-domain: {s.get('cross', 0)}")
        elif cmd == "daemon":
            await brain.daemon()
    else:
        # Default: show stats
        s = await brain.db.stats()
        print(f"\nSources: {s.get('sources', 0)} | Claims: {s.get('claims', 0)} | Cross: {s.get('cross', 0)}")
        print("\nUsage: python core.py [learn <query>|stats|daemon]")

    await brain.stop()

if __name__ == "__main__":
    asyncio.run(main())
