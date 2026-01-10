#!/usr/bin/env python3
"""
CIPHER CLI
Command-line interface for interacting with the Cipher system.

Usage:
    python cli.py status          # Show system status
    python cli.py stats           # Show knowledge base statistics
    python cli.py insights        # Show top cross-domain insights
    python cli.py search <query>  # Search claims
    python cli.py learn <domain>  # Trigger learning for domain
    python cli.py think           # Show recent thoughts
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import config


async def show_status():
    """Show system status."""
    import asyncpg

    print("CIPHER System Status")
    print("=" * 50)
    print(f"Iron Code: {config.iron_code}")
    print(f"Base Path: {config.paths.base_path}")
    print()

    # Check database
    print("Database Connection:")
    try:
        conn = await asyncpg.connect(config.db.connection_string)
        version = await conn.fetchval("SELECT version()")
        print(f"  Status: Connected")
        print(f"  Version: {version[:50]}...")
        await conn.close()
    except Exception as e:
        print(f"  Status: Error - {e}")

    # Check directories
    print("\nDirectories:")
    for name, path in [
        ("Mind", config.paths.mind_path),
        ("Tools", config.paths.tools_path),
        ("Logs", config.paths.logs_path),
    ]:
        exists = path.exists()
        print(f"  {name}: {'OK' if exists else 'MISSING'} ({path})")


async def show_stats():
    """Show knowledge base statistics."""
    import asyncpg

    print("CIPHER Knowledge Base Statistics")
    print("=" * 50)

    try:
        conn = await asyncpg.connect(config.db.connection_string)

        # Get stats
        stats = await conn.fetchrow("SELECT * FROM synthesis.get_stats()")

        print(f"\nTotal Sources:           {stats['total_sources']:,}")
        print(f"Total Claims:            {stats['total_claims']:,}")
        print(f"Total Connections:       {stats['total_connections']:,}")
        print(f"Cross-Domain Connections:{stats['cross_domain_connections']:,}")
        print(f"Total Patterns:          {stats['total_patterns']:,}")
        print(f"Open Contradictions:     {stats['open_contradictions']:,}")
        print(f"Open Gaps:               {stats['open_gaps']:,}")

        # Get per-domain stats
        print("\nBy Domain:")
        rows = await conn.fetch("""
            SELECT d.name, COUNT(DISTINCT c.id) as claims
            FROM synthesis.domains d
            LEFT JOIN synthesis.claims c ON d.id = ANY(c.domains)
            GROUP BY d.name
            ORDER BY claims DESC
        """)
        for row in rows:
            print(f"  {row['name']:15} {row['claims']:,} claims")

        await conn.close()

    except Exception as e:
        print(f"Error: {e}")


async def show_insights(limit: int = 10):
    """Show top cross-domain insights."""
    import asyncpg

    print("CIPHER Cross-Domain Insights")
    print("=" * 50)

    try:
        conn = await asyncpg.connect(config.db.connection_string)

        rows = await conn.fetch("""
            SELECT pattern_name, pattern_type, description,
                   confidence, novelty_score, created_at
            FROM synthesis.patterns
            WHERE pattern_type = 'cross_domain' OR
                  (SELECT COUNT(DISTINCT unnest) FROM unnest(domains)) >= 2
            ORDER BY novelty_score * confidence DESC
            LIMIT $1
        """, limit)

        if not rows:
            print("\nNo cross-domain insights found yet.")
            print("Run a learning cycle to discover insights.")
            return

        for i, row in enumerate(rows, 1):
            print(f"\n{i}. {row['pattern_name']}")
            print(f"   Type: {row['pattern_type']}")
            print(f"   Confidence: {row['confidence']:.2f}, Novelty: {row['novelty_score']:.2f}")
            print(f"   {row['description'][:200]}...")

        await conn.close()

    except Exception as e:
        print(f"Error: {e}")


async def search_claims(query: str, limit: int = 20):
    """Search claims in the knowledge base."""
    import asyncpg

    print(f"Searching for: '{query}'")
    print("=" * 50)

    try:
        conn = await asyncpg.connect(config.db.connection_string)

        rows = await conn.fetch("""
            SELECT c.claim_text, c.claim_type, c.confidence,
                   s.title as source_title
            FROM synthesis.claims c
            JOIN synthesis.sources s ON c.source_id = s.id
            WHERE LOWER(c.claim_text) LIKE $1
            ORDER BY c.confidence DESC
            LIMIT $2
        """, f"%{query.lower()}%", limit)

        if not rows:
            print(f"\nNo claims found matching '{query}'")
            return

        print(f"\nFound {len(rows)} claims:\n")
        for row in rows:
            print(f"[{row['claim_type']}] (conf: {row['confidence']:.2f})")
            print(f"  {row['claim_text'][:150]}...")
            print(f"  Source: {row['source_title'][:50]}...")
            print()

        await conn.close()

    except Exception as e:
        print(f"Error: {e}")


async def show_thoughts(limit: int = 20):
    """Show recent thoughts."""
    import asyncpg

    print("CIPHER Recent Thoughts")
    print("=" * 50)

    try:
        conn = await asyncpg.connect(config.db.connection_string)

        rows = await conn.fetch("""
            SELECT thought_type, content, importance, created_at
            FROM synthesis.thoughts
            ORDER BY created_at DESC
            LIMIT $1
        """, limit)

        if not rows:
            print("\nNo thoughts recorded yet.")
            return

        for row in rows:
            ts = row['created_at'].strftime('%Y-%m-%d %H:%M')
            print(f"\n[{row['thought_type']}] ({ts}) imp={row['importance']:.1f}")
            print(f"  {row['content'][:200]}...")

        await conn.close()

    except Exception as e:
        print(f"Error: {e}")


async def trigger_learn(domain: str):
    """Trigger learning for a specific domain."""
    from tools.cipher_brain import CipherBrain, Domain
    from tools.domain_learner import DomainLearner

    domain_map = {
        'math': Domain.MATHEMATICS,
        'neuro': Domain.NEUROSCIENCES,
        'bio': Domain.BIOLOGY,
        'psych': Domain.PSYCHOLOGY,
        'med': Domain.MEDICINE,
        'art': Domain.ART,
    }

    if domain.lower() not in domain_map:
        print(f"Unknown domain: {domain}")
        print(f"Available: {list(domain_map.keys())}")
        return

    target = domain_map[domain.lower()]
    print(f"Starting learning session for: {target.name}")
    print("=" * 50)

    brain = CipherBrain(config.db.connection_string)
    await brain.connect()

    learner = DomainLearner(brain, {
        'email': config.api.openalex_email,
    })

    try:
        session = await learner.learn_domain(target, max_papers=50)
        print(f"\nResults:")
        print(f"  Papers fetched: {session.papers_fetched}")
        print(f"  Claims extracted: {session.claims_extracted}")
        print(f"  Connections found: {session.connections_found}")
        print(f"  Patterns detected: {session.patterns_detected}")
        if session.errors:
            print(f"  Errors: {len(session.errors)}")
    finally:
        await learner.close()
        await brain.close()


# =========================================================================
# SEMANTIC EMBEDDING COMMANDS
# =========================================================================

async def semantic_search(query: str, limit: int = 20, threshold: float = 0.5):
    """Semantic search using embeddings."""
    from tools.cipher_brain import CipherBrain

    print(f"Semantic search for: '{query}'")
    print(f"Threshold: {threshold}, Limit: {limit}")
    print("=" * 50)

    brain = CipherBrain(config.db.connection_string)
    await brain.connect()

    try:
        results = await brain.semantic_search_claims(
            query=query,
            limit=limit,
            threshold=threshold
        )

        if not results:
            print(f"\nNo semantically similar claims found.")
            print("Try lowering the threshold with --threshold 0.3")
            return

        print(f"\nFound {len(results)} similar claims:\n")
        for claim_id, claim_text, similarity in results:
            print(f"[{similarity:.3f}] (ID: {claim_id})")
            print(f"  {claim_text[:150]}...")
            print()

    finally:
        await brain.close()


async def embed_backfill(batch_size: int = 100, limit: int = None):
    """Backfill embeddings for existing claims."""
    from tools.cipher_brain import CipherBrain

    print("Backfilling embeddings for existing claims")
    print("=" * 50)

    brain = CipherBrain(config.db.connection_string)
    await brain.connect()

    try:
        updated = await brain.embed_existing_claims(
            batch_size=batch_size,
            limit=limit
        )
        print(f"\nCompleted! Updated {updated} claims with embeddings.")

    finally:
        await brain.close()


async def find_bridges(threshold: float = 0.75, limit: int = 20):
    """Find cross-domain connections using embedding similarity."""
    from tools.cipher_brain import CipherBrain

    print("Finding cross-domain connections via embeddings")
    print(f"Threshold: {threshold}")
    print("=" * 50)

    brain = CipherBrain(config.db.connection_string)
    await brain.connect()

    try:
        connections = await brain.find_cross_domain_by_embedding(
            threshold=threshold,
            limit=limit
        )

        if not connections:
            print("\nNo cross-domain connections found.")
            print("Try lowering the threshold or run embed-backfill first.")
            return

        print(f"\nFound {len(connections)} potential cross-domain bridges:\n")
        for i, conn in enumerate(connections, 1):
            print(f"{i}. {conn['domain_a']} <-> {conn['domain_b']} (sim: {conn['similarity']:.3f})")
            print(f"   A: {conn['claim_a_text'][:80]}...")
            print(f"   B: {conn['claim_b_text'][:80]}...")
            print()

    finally:
        await brain.close()


async def find_similar(claim_id: int, limit: int = 10, cross_domain: bool = False):
    """Find claims similar to a given claim."""
    from tools.cipher_brain import CipherBrain

    print(f"Finding claims similar to ID: {claim_id}")
    if cross_domain:
        print("(Cross-domain only)")
    print("=" * 50)

    brain = CipherBrain(config.db.connection_string)
    await brain.connect()

    try:
        results = await brain.find_similar_claims(
            claim_id=claim_id,
            limit=limit,
            cross_domain_only=cross_domain
        )

        if not results:
            print("\nNo similar claims found.")
            return

        print(f"\nFound {len(results)} similar claims:\n")
        for cid, text, similarity, domains in results:
            domain_names = [d.name for d in domains]
            print(f"[{similarity:.3f}] (ID: {cid}) Domains: {domain_names}")
            print(f"  {text[:150]}...")
            print()

    finally:
        await brain.close()


async def embedding_stats():
    """Show embedding statistics."""
    import asyncpg

    print("CIPHER Embedding Statistics")
    print("=" * 50)

    try:
        conn = await asyncpg.connect(config.db.connection_string)

        # Count claims with/without embeddings
        total = await conn.fetchval("SELECT COUNT(*) FROM synthesis.claims")
        with_emb = await conn.fetchval(
            "SELECT COUNT(*) FROM synthesis.claims WHERE embedding IS NOT NULL"
        )
        without_emb = total - with_emb

        print(f"\nTotal claims:        {total:,}")
        print(f"With embeddings:     {with_emb:,} ({100*with_emb/total:.1f}%)" if total > 0 else "With embeddings:     0")
        print(f"Without embeddings:  {without_emb:,}")

        # Get embedding model info
        from tools.embeddings import get_embedding_service
        service = get_embedding_service()
        print(f"\nEmbedding Model: {service.model_name}")
        print(f"Dimensions: {service.dimensions}")

        await conn.close()

    except Exception as e:
        print(f"Error: {e}")


# =========================================================================
# TEMPORAL TRACKING COMMANDS
# =========================================================================

async def temporal_stats():
    """Show temporal tracking statistics."""
    import asyncpg

    print("CIPHER Temporal Tracking Statistics")
    print("=" * 50)

    try:
        conn = await asyncpg.connect(config.db.connection_string)

        # Replication status distribution
        print("\nReplication Status Distribution:")
        rows = await conn.fetch("""
            SELECT
                COALESCE(replication_status, 'unreplicated') as status,
                COUNT(*) as count
            FROM synthesis.claims
            GROUP BY replication_status
            ORDER BY count DESC
        """)
        for row in rows:
            print(f"  {row['status']:20} {row['count']:,}")

        # Claim status distribution
        print("\nClaim Lifecycle Status:")
        rows = await conn.fetch("""
            SELECT
                COALESCE(status, 'active') as status,
                COUNT(*) as count
            FROM synthesis.claims
            GROUP BY status
            ORDER BY count DESC
        """)
        for row in rows:
            print(f"  {row['status']:20} {row['count']:,}")

        # Age distribution
        print("\nClaim Age Distribution:")
        rows = await conn.fetch("""
            SELECT
                CASE
                    WHEN EXTRACT(days FROM NOW() - created_at) < 30 THEN '< 1 month'
                    WHEN EXTRACT(days FROM NOW() - created_at) < 180 THEN '1-6 months'
                    WHEN EXTRACT(days FROM NOW() - created_at) < 365 THEN '6-12 months'
                    WHEN EXTRACT(days FROM NOW() - created_at) < 730 THEN '1-2 years'
                    ELSE '> 2 years'
                END as age_group,
                COUNT(*) as count,
                AVG(COALESCE(current_confidence, confidence)) as avg_confidence
            FROM synthesis.claims
            GROUP BY age_group
            ORDER BY count DESC
        """)
        for row in rows:
            conf = row['avg_confidence'] or 0
            print(f"  {row['age_group']:15} {row['count']:,} claims (avg conf: {conf:.2f})")

        await conn.close()

    except Exception as e:
        print(f"Error: {e}")


async def decay_claims():
    """Apply confidence decay to all claims."""
    from tools.temporal_tracker import TemporalTracker

    print("Applying confidence decay to claims...")
    print("=" * 50)

    tracker = TemporalTracker(config.db.connection_string)
    await tracker.connect()

    try:
        updated = await tracker.decay_all_claims()
        print(f"\nUpdated {updated} claims with decayed confidence.")

    finally:
        await tracker.close()


async def aging_claims(min_age: int = 180, max_conf: float = 0.5):
    """Show aging claims that need attention."""
    from tools.temporal_tracker import TemporalTracker

    print(f"Claims older than {min_age} days with confidence < {max_conf}")
    print("=" * 60)

    tracker = TemporalTracker(config.db.connection_string)
    await tracker.connect()

    try:
        claims = await tracker.get_aging_claims(min_age, max_conf)

        if not claims:
            print("\nNo aging claims found matching criteria.")
            return

        print(f"\nFound {len(claims)} aging claims:\n")
        for claim in claims[:20]:
            age = int(claim.get('age_days', 0))
            orig_conf = claim.get('original_confidence', 0) or 0
            curr_conf = claim.get('current_confidence', 0) or 0
            repl = claim.get('replication_status', 'unreplicated')

            print(f"ID {claim['id']} | Age: {age}d | Conf: {orig_conf:.2f} -> {curr_conf:.2f} | Repl: {repl}")
            print(f"  {claim['claim_text'][:70]}...")
            print()

    finally:
        await tracker.close()


async def claim_temporal(claim_id: int):
    """Show temporal state of a specific claim."""
    from tools.temporal_tracker import TemporalTracker

    print(f"Temporal State for Claim ID: {claim_id}")
    print("=" * 50)

    tracker = TemporalTracker(config.db.connection_string)
    await tracker.connect()

    try:
        state = await tracker.get_temporal_state(claim_id)

        if not state:
            print(f"\nClaim {claim_id} not found.")
            return

        print(f"\nClaim ID:            {state.claim_id}")
        print(f"Status:              {state.status.value}")
        print(f"Age:                 {state.age_days} days")
        print(f"Half-life:           {state.half_life_days:.0f} days")
        print(f"\nConfidence:")
        print(f"  Original:          {state.original_confidence:.3f}")
        print(f"  Current:           {state.current_confidence:.3f}")
        print(f"  Trend:             {state.confidence_trend:+.3f}")
        print(f"\nReplication:")
        print(f"  Status:            {state.replication_status.value}")
        print(f"  Successful:        {state.replication_count}")
        print(f"  Failed:            {state.failed_replication_count}")
        print(f"\nCitations:")
        print(f"  Total:             {state.citation_count}")
        print(f"  Velocity:          {state.citation_velocity:.1f}/month")
        print(f"\nTimestamps:")
        print(f"  First seen:        {state.first_seen}")
        print(f"  Last confirmed:    {state.last_confirmed or 'Never'}")
        print(f"  Last cited:        {state.last_cited or 'Never'}")

        if state.superseded_by:
            print(f"\nSuperseded by:       Claim ID {state.superseded_by}")

    finally:
        await tracker.close()


async def detect_paradigm_shifts(days: int = 365):
    """Detect potential paradigm shifts."""
    from tools.temporal_tracker import TemporalTracker

    print(f"Detecting paradigm shifts (last {days} days)")
    print("=" * 50)

    tracker = TemporalTracker(config.db.connection_string)
    await tracker.connect()

    try:
        patterns = await tracker.detect_paradigm_shifts(days)

        if not patterns:
            print("\nNo paradigm shifts detected.")
            return

        print(f"\nFound {len(patterns)} temporal patterns:\n")
        for i, pattern in enumerate(patterns, 1):
            print(f"{i}. [{pattern.pattern_type}] (conf: {pattern.confidence:.2f})")
            print(f"   {pattern.description}")
            print(f"   Claims involved: {len(pattern.claims_involved)}")
            print(f"   Started: {pattern.start_date}")
            print()

    finally:
        await tracker.close()


async def record_replication(claim_id: int, success: bool, partial: bool = False):
    """Record a replication attempt for a claim."""
    from tools.temporal_tracker import TemporalTracker

    status = "successful" if success else "failed"
    if partial:
        status = "partial"

    print(f"Recording {status} replication for Claim ID: {claim_id}")
    print("=" * 50)

    tracker = TemporalTracker(config.db.connection_string)
    await tracker.connect()

    try:
        result = await tracker.record_replication(
            claim_id=claim_id,
            success=success,
            partial=partial
        )

        if result:
            print(f"\nReplication recorded successfully.")
            # Show updated state
            state = await tracker.get_temporal_state(claim_id)
            if state:
                print(f"New replication status: {state.replication_status.value}")
                print(f"New confidence: {state.current_confidence:.3f}")
        else:
            print("\nFailed to record replication.")

    finally:
        await tracker.close()


def main():
    parser = argparse.ArgumentParser(
        description='CIPHER Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py status
  python cli.py stats
  python cli.py insights
  python cli.py search "neural network"
  python cli.py learn neuro
  python cli.py think

Semantic Embedding Commands:
  python cli.py semantic-search "predictive coding in the brain"
  python cli.py embed-backfill
  python cli.py embed-stats
  python cli.py find-bridges --threshold 0.7
  python cli.py similar 42 --cross-domain

Temporal Tracking Commands:
  python cli.py temporal-stats
  python cli.py decay-claims
  python cli.py aging-claims --min-age 365 --max-conf 0.4
  python cli.py claim-temporal 42
  python cli.py paradigm-shifts --days 730
  python cli.py record-replication 42 --success
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Status
    subparsers.add_parser('status', help='Show system status')

    # Stats
    subparsers.add_parser('stats', help='Show knowledge base statistics')

    # Insights
    insights_parser = subparsers.add_parser('insights', help='Show top insights')
    insights_parser.add_argument('-n', type=int, default=10, help='Number of insights')

    # Search
    search_parser = subparsers.add_parser('search', help='Search claims (keyword)')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('-n', type=int, default=20, help='Max results')

    # Learn
    learn_parser = subparsers.add_parser('learn', help='Trigger learning')
    learn_parser.add_argument('domain', help='Domain to learn (math/neuro/bio/psych/med/art)')

    # Think
    think_parser = subparsers.add_parser('think', help='Show recent thoughts')
    think_parser.add_argument('-n', type=int, default=20, help='Number of thoughts')

    # =========================================================================
    # SEMANTIC EMBEDDING COMMANDS
    # =========================================================================

    # Semantic Search
    sem_search = subparsers.add_parser('semantic-search', help='Search using semantic similarity')
    sem_search.add_argument('query', help='Natural language query')
    sem_search.add_argument('-n', type=int, default=20, help='Max results')
    sem_search.add_argument('--threshold', type=float, default=0.5, help='Similarity threshold (0-1)')

    # Embed Backfill
    backfill = subparsers.add_parser('embed-backfill', help='Generate embeddings for existing claims')
    backfill.add_argument('--batch-size', type=int, default=100, help='Batch size')
    backfill.add_argument('--limit', type=int, default=None, help='Max claims to process')

    # Embedding Stats
    subparsers.add_parser('embed-stats', help='Show embedding statistics')

    # Find Bridges
    bridges = subparsers.add_parser('find-bridges', help='Find cross-domain connections via embeddings')
    bridges.add_argument('--threshold', type=float, default=0.75, help='Similarity threshold')
    bridges.add_argument('-n', type=int, default=20, help='Max results')

    # Similar Claims
    similar = subparsers.add_parser('similar', help='Find claims similar to a given claim')
    similar.add_argument('claim_id', type=int, help='Claim ID to find similar claims for')
    similar.add_argument('-n', type=int, default=10, help='Max results')
    similar.add_argument('--cross-domain', action='store_true', help='Only show cross-domain matches')

    # =========================================================================
    # TEMPORAL TRACKING COMMANDS
    # =========================================================================

    # Temporal Stats
    subparsers.add_parser('temporal-stats', help='Show temporal tracking statistics')

    # Decay Claims
    subparsers.add_parser('decay-claims', help='Apply confidence decay to all claims')

    # Aging Claims
    aging = subparsers.add_parser('aging-claims', help='Show aging claims needing attention')
    aging.add_argument('--min-age', type=int, default=180, help='Minimum age in days')
    aging.add_argument('--max-conf', type=float, default=0.5, help='Maximum confidence threshold')

    # Claim Temporal State
    claim_temp = subparsers.add_parser('claim-temporal', help='Show temporal state of a claim')
    claim_temp.add_argument('claim_id', type=int, help='Claim ID')

    # Paradigm Shifts
    paradigm = subparsers.add_parser('paradigm-shifts', help='Detect paradigm shifts')
    paradigm.add_argument('--days', type=int, default=365, help='Look back period in days')

    # Record Replication
    repl = subparsers.add_parser('record-replication', help='Record replication attempt')
    repl.add_argument('claim_id', type=int, help='Claim ID')
    repl.add_argument('--success', action='store_true', help='Replication succeeded')
    repl.add_argument('--failure', action='store_true', help='Replication failed')
    repl.add_argument('--partial', action='store_true', help='Partial replication')

    args = parser.parse_args()

    if args.command == 'status':
        asyncio.run(show_status())
    elif args.command == 'stats':
        asyncio.run(show_stats())
    elif args.command == 'insights':
        asyncio.run(show_insights(args.n))
    elif args.command == 'search':
        asyncio.run(search_claims(args.query, args.n))
    elif args.command == 'learn':
        asyncio.run(trigger_learn(args.domain))
    elif args.command == 'think':
        asyncio.run(show_thoughts(args.n))
    # Semantic Embedding Commands
    elif args.command == 'semantic-search':
        asyncio.run(semantic_search(args.query, args.n, args.threshold))
    elif args.command == 'embed-backfill':
        asyncio.run(embed_backfill(args.batch_size, args.limit))
    elif args.command == 'embed-stats':
        asyncio.run(embedding_stats())
    elif args.command == 'find-bridges':
        asyncio.run(find_bridges(args.threshold, args.n))
    elif args.command == 'similar':
        asyncio.run(find_similar(args.claim_id, args.n, args.cross_domain))
    # Temporal Tracking Commands
    elif args.command == 'temporal-stats':
        asyncio.run(temporal_stats())
    elif args.command == 'decay-claims':
        asyncio.run(decay_claims())
    elif args.command == 'aging-claims':
        asyncio.run(aging_claims(args.min_age, args.max_conf))
    elif args.command == 'claim-temporal':
        asyncio.run(claim_temporal(args.claim_id))
    elif args.command == 'paradigm-shifts':
        asyncio.run(detect_paradigm_shifts(args.days))
    elif args.command == 'record-replication':
        if args.partial:
            asyncio.run(record_replication(args.claim_id, success=True, partial=True))
        elif args.success:
            asyncio.run(record_replication(args.claim_id, success=True, partial=False))
        elif args.failure:
            asyncio.run(record_replication(args.claim_id, success=False, partial=False))
        else:
            print("Error: Must specify --success, --failure, or --partial")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
