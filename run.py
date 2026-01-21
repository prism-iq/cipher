#!/usr/bin/env python3
"""
CIPHER Main Runner
Orchestrates learning sessions across all domains.

Usage:
    python run.py                    # Full learning cycle
    python run.py --domain math      # Learn specific domain
    python run.py --cross-domain     # Focus on cross-domain
    python run.py --patterns         # Run pattern detection only
    python run.py --report           # Generate synthesis report
    python run.py --daemon           # Sensory-driven daemon mode
    python run.py --status           # Show current sensory status
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import config
from tools.cipher_brain import CipherBrain, Domain
from tools.domain_learner import DomainLearner
from tools.pattern_detector import PatternDetector
from tools.senses_bridge import SensesBridge, sensory_learning_loop

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.paths.logs_path / 'cipher.log')
    ]
)
logger = logging.getLogger('cipher')


async def run_full_cycle(max_papers: int = 100):
    """Run complete learning cycle across all domains."""
    logger.info("=" * 60)
    logger.info("CIPHER - Cross-Domain Learning System")
    logger.info(f"Iron Code: {config.iron_code}")
    logger.info("=" * 60)

    # Initialize brain
    brain = CipherBrain(config.db.connection_string)
    await brain.connect()

    # Initialize learner
    learner = DomainLearner(brain, {
        'email': config.api.openalex_email,
        'pubmed_api_key': config.api.pubmed_api_key,
        's2_api_key': config.api.semantic_scholar_api_key,
        'max_papers_per_domain': max_papers
    })

    try:
        # Phase 1: Learn from all domains
        logger.info("\n--- Phase 1: Domain Learning ---")
        sessions = await learner.learn_all_domains(
            max_papers_per_domain=max_papers,
            parallel=True
        )

        for session in sessions:
            if session:
                logger.info(
                    f"{session.domain.name if session.domain else 'Cross'}: "
                    f"{session.papers_fetched} papers, "
                    f"{session.claims_extracted} claims, "
                    f"{session.connections_found} connections"
                )

        # Phase 2: Cross-domain learning
        logger.info("\n--- Phase 2: Cross-Domain Learning ---")
        bridge_concepts = [
            'information entropy',
            'neural network',
            'predictive processing',
            'complexity emergence',
            'optimization'
        ]
        cross_session = await learner.learn_cross_domain(
            concepts=bridge_concepts,
            max_papers=max_papers // 2
        )
        logger.info(
            f"Cross-domain: {cross_session.papers_fetched} papers, "
            f"{cross_session.claims_extracted} claims"
        )

        # Phase 3: Pattern detection
        logger.info("\n--- Phase 3: Pattern Detection ---")
        detector = PatternDetector(config.db.connection_string)
        await detector.connect()

        insights = await detector.detect_all_patterns()
        logger.info(f"Detected {len(insights)} cross-domain insights")

        # Save insights
        await detector.save_insights(insights)

        # Print top insights
        logger.info("\n--- Top Cross-Domain Insights ---")
        for i, insight in enumerate(insights[:5], 1):
            logger.info(f"\n{i}. {insight.title}")
            logger.info(f"   Confidence: {insight.confidence:.2f}, Novelty: {insight.novelty:.2f}")
            logger.info(f"   {insight.description[:200]}...")

        await detector.close()

        # Summary
        summary = await learner.get_learning_summary()
        logger.info("\n--- Session Summary ---")
        logger.info(f"Total papers processed: {summary['total_papers']}")
        logger.info(f"Total claims extracted: {summary['total_claims']}")
        logger.info(f"Total connections found: {summary['total_connections']}")
        logger.info(f"Total patterns detected: {summary['total_patterns']}")

        # Get stats from brain
        stats = await brain.get_stats()
        logger.info("\n--- Knowledge Base Stats ---")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")

    finally:
        await learner.close()
        await brain.close()

    logger.info("\n" + "=" * 60)
    logger.info("Learning cycle complete.")
    logger.info("=" * 60)


async def run_single_domain(domain_name: str, max_papers: int = 100):
    """Run learning for a single domain."""
    # Map domain name to enum
    domain_map = {
        'math': Domain.MATHEMATICS,
        'mathematics': Domain.MATHEMATICS,
        'neuro': Domain.NEUROSCIENCES,
        'neurosciences': Domain.NEUROSCIENCES,
        'bio': Domain.BIOLOGY,
        'biology': Domain.BIOLOGY,
        'psych': Domain.PSYCHOLOGY,
        'psychology': Domain.PSYCHOLOGY,
        'med': Domain.MEDICINE,
        'medicine': Domain.MEDICINE,
        'art': Domain.ART,
    }

    domain = domain_map.get(domain_name.lower())
    if not domain:
        logger.error(f"Unknown domain: {domain_name}")
        logger.info(f"Available: {list(domain_map.keys())}")
        return

    logger.info(f"Learning from domain: {domain.name}")

    brain = CipherBrain(config.db.connection_string)
    await brain.connect()

    learner = DomainLearner(brain, {
        'email': config.api.openalex_email,
        'pubmed_api_key': config.api.pubmed_api_key,
        's2_api_key': config.api.semantic_scholar_api_key,
    })

    try:
        session = await learner.learn_domain(domain, max_papers)
        logger.info(f"\nResults for {domain.name}:")
        logger.info(f"  Papers: {session.papers_fetched}")
        logger.info(f"  Claims: {session.claims_extracted}")
        logger.info(f"  Connections: {session.connections_found}")
        logger.info(f"  Patterns: {session.patterns_detected}")
        if session.errors:
            logger.warning(f"  Errors: {len(session.errors)}")
    finally:
        await learner.close()
        await brain.close()


async def run_pattern_detection():
    """Run pattern detection on existing knowledge."""
    logger.info("Running pattern detection...")

    detector = PatternDetector(config.db.connection_string)
    await detector.connect()

    try:
        insights = await detector.detect_all_patterns()
        logger.info(f"Detected {len(insights)} insights")

        for i, insight in enumerate(insights[:10], 1):
            print(f"\n{i}. {insight.title}")
            print(f"   {insight.source_domain.name} <-> {insight.target_domain.name}")
            print(f"   Confidence: {insight.confidence:.2f}, Novelty: {insight.novelty:.2f}")
            print(f"   {insight.description[:300]}...")

        await detector.save_insights(insights)
        logger.info("Insights saved to database")

    finally:
        await detector.close()


async def generate_report():
    """Generate synthesis report."""
    logger.info("Generating synthesis report...")

    detector = PatternDetector(config.db.connection_string)
    await detector.connect()

    try:
        report = await detector.generate_synthesis_report()

        # Save report
        report_path = config.paths.mind_path / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path.write_text(report)
        logger.info(f"Report saved to: {report_path}")

        # Also print
        print(report)

    finally:
        await detector.close()


async def run_daemon():
    """
    Run sensory-driven daemon mode.

    Cipher learns continuously, modulated by music/senses:
    - hype (high energy)  -> intense cross-domain learning
    - chill (low energy)  -> reflective mode, pattern synthesis
    - groovy (balanced)   -> steady learning

    The music guides the forge.
    """
    import signal

    logger.info("=" * 60)
    logger.info("CIPHER DAEMON - Sensory Learning Mode")
    logger.info(f"Iron Code: {config.iron_code}")
    logger.info("Music guides the forge. The senses modulate.")
    logger.info("=" * 60)

    # Initialize components
    brain = CipherBrain(config.db.connection_string)
    await brain.connect()

    learner = DomainLearner(brain, {
        'email': config.api.openalex_email,
        'pubmed_api_key': config.api.pubmed_api_key,
        's2_api_key': config.api.semantic_scholar_api_key,
    })

    bridge = SensesBridge()

    # Mode change logging
    def on_mode_change(old_mode, new_mode):
        logger.info(f"[SENSES] Mode shift: {old_mode.value} -> {new_mode.value}")
        # Log the current music state
        status = bridge.get_status()
        logger.info(f"[SENSES] Energy: {status['music']['energy']:.2f}, Vibe: {status['music']['vibe']}")

    bridge.on_mode_change(on_mode_change)

    # Signal handler for graceful shutdown
    def shutdown(signum, frame):
        logger.info("Shutdown signal received")
        bridge.stop()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        # Start both the watcher and learning loop
        watcher_task = asyncio.create_task(bridge.watch(interval=0.5))
        learning_task = asyncio.create_task(sensory_learning_loop(
            brain=brain,
            learner=learner,
            bridge=bridge,
            domains=[Domain.NEUROSCIENCES, Domain.BIOLOGY, Domain.PSYCHOLOGY,
                     Domain.MATHEMATICS, Domain.MEDICINE]
        ))

        # Wait for either to complete (usually shutdown)
        await asyncio.gather(watcher_task, learning_task)

    except asyncio.CancelledError:
        logger.info("Daemon cancelled")
    finally:
        bridge.stop()
        await learner.close()
        await brain.close()

    logger.info("Cipher daemon stopped")


def show_status():
    """Show current sensory status."""
    bridge = SensesBridge()
    bridge.update_state()
    status = bridge.get_status()

    print("\n" + "=" * 50)
    print("  CIPHER SENSORY STATUS")
    print("=" * 50)
    print(f"\n  Learning Mode: {status['mode'].upper()}")
    print(f"\n  Music:")
    print(f"    Energy: {status['music']['energy']:.2f}")
    print(f"    Groove: {status['music']['groove']:.2f}")
    print(f"    Vibe:   {status['music']['vibe']}")
    print(f"\n  Other Senses:")
    print(f"    Mic active: {'yes' if status['mic_active'] else 'no'}")
    print(f"    Vision:     {'active' if status['has_vision'] else 'inactive'}")
    print(f"    Screen:     {'active' if status['has_screen'] else 'inactive'}")

    params = bridge.state.get_learning_params()
    print(f"\n  Learning Parameters ({status['mode']}):")
    for k, v in params.items():
        print(f"    {k}: {v}")
    print("=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(description='CIPHER Learning System')
    parser.add_argument('--domain', type=str, help='Learn specific domain')
    parser.add_argument('--cross-domain', action='store_true', help='Focus on cross-domain')
    parser.add_argument('--patterns', action='store_true', help='Run pattern detection')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--daemon', action='store_true', help='Run sensory-driven daemon')
    parser.add_argument('--status', action='store_true', help='Show sensory status')
    parser.add_argument('--max-papers', type=int, default=100, help='Max papers per domain')

    args = parser.parse_args()

    # Ensure directories exist
    config.paths.mind_path.mkdir(parents=True, exist_ok=True)
    config.paths.logs_path.mkdir(parents=True, exist_ok=True)

    if args.status:
        show_status()
    elif args.daemon:
        asyncio.run(run_daemon())
    elif args.domain:
        asyncio.run(run_single_domain(args.domain, args.max_papers))
    elif args.patterns:
        asyncio.run(run_pattern_detection())
    elif args.report:
        asyncio.run(generate_report())
    else:
        asyncio.run(run_full_cycle(args.max_papers))


if __name__ == '__main__':
    main()
